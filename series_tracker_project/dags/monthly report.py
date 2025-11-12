from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import sys
import os
import traceback

sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

from helpers_parser import parse_series_by_month
from helpers_database import save_to_database, get_series_stats
from helpers_email_sender import send_series_report

default_args = {
    'owner': 'series_tracker',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def parse_current_month(**context):
    """Парсинг текущего месяца для ежемесячного отчета"""
    try:
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        
        print(f"🔄 Ежемесячный парсинг: {year}-{month:02d}")
        series_data = parse_series_by_month(year, month)
        
        if series_data:
            save_to_database(series_data)
            context['ti'].xcom_push(key='parsed_months', value=[f"{year}-{month:02d}"])
            context['ti'].xcom_push(key='total_series', value=len(series_data))
            context['ti'].xcom_push(key='current_year', value=year)
            context['ti'].xcom_push(key='current_month', value=month)
            print(f"✅ Сохранено {len(series_data)} сериалов за {year}-{month:02d}")
            return len(series_data)
        else:
            print("❌ Не удалось получить данные за текущий месяц")
            return 0
            
    except Exception as e:
        print(f"❌ Ошибка парсинга текущего месяца: {e}")
        print(f"🔍 Детали ошибки: {traceback.format_exc()}")
        return 0

def generate_monthly_report(**context):
    """Генерация ежемесячного отчета с полным списком сериалов"""
    try:
        print("🔍 Начало генерации ежемесячного отчета...")
        
        # Получаем информацию о текущем месяце
        parsed_months = context['ti'].xcom_pull(key='parsed_months', task_ids='parse_current_month')
        total_series = context['ti'].xcom_pull(key='total_series', task_ids='parse_current_month')
        current_year = context['ti'].xcom_pull(key='current_year', task_ids='parse_current_month')
        current_month = context['ti'].xcom_pull(key='current_month', task_ids='parse_current_month')
        
        print(f"📊 Данные для отчета: months={parsed_months}, series={total_series}")
        
        if not parsed_months or not total_series:
            print("❌ Нет данных для отчета")
            return
        
        # Получаем детальную статистику за текущий месяц
        try:
            print(f"🔄 Получение статистики за {current_year}-{current_month:02d}...")
            current_stats = get_series_stats(current_year, current_month)
            print(f"📈 Статистика получена: {current_stats.get('total_series', 0)} сериалов")
            
        except Exception as e:
            print(f"⚠️ Не удалось получить статистику за текущий месяц: {e}")
            current_stats = {}
        
        # Собираем статистику для отправки
        stats = {
            'parsed_months': parsed_months,
            'total_series': total_series,
            'avg_rating_kino': current_stats.get('avg_rating_kino'),
            'avg_rating_imdb': current_stats.get('avg_rating_imdb'),
            'countries_count': current_stats.get('countries_count', 0),
            'top_genres': current_stats.get('top_genres', {}),
            'all_series': current_stats.get('all_series', []),
            'current_year': current_year,
            'current_month': current_month,
            'report_type': 'monthly'  # Важно: указываем тип отчета
        }
        
        # Отправляем отчет через helpers_email_sender
        send_series_report(stats)
        print(f"✅ Ежемесячный отчет за {current_year}-{current_month:02d} отправлен")
        
    except Exception as e:
        print(f"❌ Ошибка генерации ежемесячного отчета: {e}")
        print(f"🔍 Детали ошибки: {traceback.format_exc()}")

# Создаем DAG для ежемесячных отчетов
with DAG(
    'series_monthly_report',
    default_args=default_args,
    description='Ежемесячный автоматический парсинг и отчет по новым сериалам',
    schedule_interval='0 12 1 * *',  
    catchup=False,
    tags=['series', 'monthly', 'report', 'automation'],
) as dag:

    start = DummyOperator(task_id='start')
    
    parse_task = PythonOperator(
        task_id='parse_current_month',
        python_callable=parse_current_month,
    )
    
    report_task = PythonOperator(
        task_id='generate_monthly_report',
        python_callable=generate_monthly_report,
    )
    
    end = DummyOperator(task_id='end')
    
    # Зависимости
    start >> parse_task >> report_task >> end

    # Документация DAG
    dag.doc_md = """
    # Ежемесячный отчет по сериалам
    
    Автоматический DAG для ежемесячного парсинга новых сериалов и генерации отчетов.
    
    ## Расписание
    - Запускается 1 числа каждого месяца в 12:00 UTC
    - Парсит данные за текущий месяц
    - Генерирует отчет с полным списком сериалов
    """