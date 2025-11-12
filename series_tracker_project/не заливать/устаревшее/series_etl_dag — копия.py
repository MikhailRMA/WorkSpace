from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

from helpers_parser import parse_series_by_month, parse_previous_months
from helpers_database import save_to_database, get_series_stats
from helpers_email_sender import send_series_report

default_args = {
    'owner': 'series_tracker',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

def wait_for_user_input(**context):
    """
    Ждем пользовательский ввод через конфиг UI
    Если нет данных - ждем 1 минуту и парсим текущий месяц
    """
    try:
        dag_run = context.get('dag_run')
        
        # Проверяем параметры из UI
        if dag_run and dag_run.conf:
            months = dag_run.conf.get('months', [])
            months_back = dag_run.conf.get('months_back')
            year = dag_run.conf.get('year')
            month = dag_run.conf.get('month')
            
            if months:
                print(f"✅ Получены месяцы из UI: {months}")
                context['ti'].xcom_push(key='months', value=months)
                return "parse_multiple_months"
            elif months_back:
                print(f"✅ Получен months_back из UI: {months_back}")
                context['ti'].xcom_push(key='months_back', value=months_back)
                return "parse_previous_months"
            elif year and month:
                print(f"✅ Получен месяц из UI: {year}-{month:02d}")
                context['ti'].xcom_push(key='year', value=year)
                context['ti'].xcom_push(key='month', value=month)
                return "parse_single_month"
        
        # Если параметров нет - ждем 1 минуту
        print("⏳ Ожидаем параметры для парсинга...")
        return "wait_timer"
        
    except Exception as e:
        print(f"❌ Ошибка при проверке параметров: {e}")
        return "parse_current_month"

def wait_timer(**context):
    """
    Ждем 1 минуту и затем парсим текущий месяц
    """
    print("⏰ Таймер: ждем 1 минуту...")
    # В реальности здесь будет пауза, но в Airflow лучше использовать TimeDeltaSensor
    # Для простоты сразу переходим к парсингу текущего месяца
    return "parse_current_month"

def parse_single_month(**context):
    """Парсинг одного месяца из UI"""
    try:
        year = context['ti'].xcom_pull(key='year')
        month = context['ti'].xcom_pull(key='month')
        
        if not year or not month:
            print("❌ Не получены параметры месяца")
            return 0
        
        print(f"🎯 Парсинг указанного месяца: {year}-{month:02d}")
        series_data = parse_series_by_month(year, month)
        
        if series_data:
            save_to_database(series_data)
            context['ti'].xcom_push(key='parsed_months', value=[f"{year}-{month:02d}"])
            context['ti'].xcom_push(key='total_series', value=len(series_data))
            print(f"✅ Сохранено {len(series_data)} сериалов за {year}-{month:02d}")
            return len(series_data)
        else:
            print(f"❌ Не удалось получить данные за {year}-{month:02d}")
            return 0
            
    except Exception as e:
        print(f"❌ Ошибка парсинга указанного месяца: {e}")
        return 0

def parse_multiple_months(**context):
    """Парсинг нескольких месяцев из UI"""
    try:
        months = context['ti'].xcom_pull(key='months')
        
        if not months:
            print("❌ Не получены месяцы для парсинга")
            return 0
        
        total_series = 0
        parsed_months = []
        
        for month_config in months:
            year = month_config.get('year', datetime.now().year)
            month = month_config.get('month')
            
            if not month:
                continue
                
            print(f"🎯 Парсинг месяца: {year}-{month:02d}")
            series_data = parse_series_by_month(year, month)
            
            if series_data:
                save_to_database(series_data)
                total_series += len(series_data)
                parsed_months.append(f"{year}-{month:02d}")
                print(f"✅ Сохранено {len(series_data)} сериалов за {year}-{month:02d}")
            
            # Пауза между запросами
            import time
            time.sleep(2)
        
        context['ti'].xcom_push(key='parsed_months', value=parsed_months)
        context['ti'].xcom_push(key='total_series', value=total_series)
        print(f"✅ Всего сохранено {total_series} сериалов за {len(parsed_months)} месяцев")
        return total_series
        
    except Exception as e:
        print(f"❌ Ошибка парсинга нескольких месяцев: {e}")
        return 0

def parse_previous_months_task(**context):
    """Парсинг предыдущих месяцев из UI"""
    try:
        months_back = context['ti'].xcom_pull(key='months_back') or 6
        
        print(f"🔄 Парсинг последних {months_back} месяцев")
        series_data = parse_previous_months(months_back)
        
        if series_data:
            save_to_database(series_data)
            context['ti'].xcom_push(key='parsed_months', value=[f"last_{months_back}_months"])
            context['ti'].xcom_push(key='total_series', value=len(series_data))
            print(f"✅ Сохранено {len(series_data)} сериалов за последние {months_back} месяцев")
            return len(series_data)
        else:
            print("❌ Не удалось получить данные")
            return 0
            
    except Exception as e:
        print(f"❌ Ошибка парсинга предыдущих месяцев: {e}")
        return 0

def parse_current_month(**context):
    """Парсинг текущего месяца (если нет ввода от пользователя)"""
    try:
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        
        print(f"🔄 Автоматический парсинг текущего месяца: {year}-{month:02d}")
        series_data = parse_series_by_month(year, month)
        
        if series_data:
            save_to_database(series_data)
            context['ti'].xcom_push(key='parsed_months', value=[f"{year}-{month:02d}"])
            context['ti'].xcom_push(key='total_series', value=len(series_data))
            print(f"✅ Сохранено {len(series_data)} сериалов за текущий месяц")
            return len(series_data)
        else:
            print("❌ Не удалось получить данные за текущий месяц")
            return 0
            
    except Exception as e:
        print(f"❌ Ошибка парсинга текущего месяца: {e}")
        return 0

def generate_report(**context):
    """Генерация и отправка отчета"""
    try:
        # Получаем информацию о спарсенных месяцах
        parsed_months = context['ti'].xcom_pull(key='parsed_months')
        total_series = context['ti'].xcom_pull(key='total_series')
        
        if not parsed_months or not total_series:
            print("❌ Нет данных для отчета")
            return
        
        # Собираем статистику
        stats = {
            'parsed_months': parsed_months,
            'total_series': total_series,
            'months_count': len(parsed_months),
            'parsed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Добавляем детальную статистику если это один месяц
        if len(parsed_months) == 1 and not parsed_months[0].startswith('last_'):
            try:
                year, month = map(int, parsed_months[0].split('-'))
                detailed_stats = get_series_stats(year, month)
                stats.update(detailed_stats)
            except:
                pass
        
        # Отправляем отчет
        send_series_report(stats)
        print(f"✅ Отчет за {len(parsed_months)} месяцев отправлен")
        
    except Exception as e:
        print(f"❌ Ошибка генерации отчета: {e}")

with DAG(
    'series_complete_etl',
    default_args=default_args,
    description='Полный ETL: парсинг с ожиданием ввода + сохранение + отчет',
    schedule_interval=None,
    catchup=False,
    tags=['series', 'complete', 'etl'],
    params={
        'year': datetime.now().year,
        'month': datetime.now().month,
        'months_back': 6,
        'months': []
    }
) as dag:

    start = DummyOperator(task_id='start')
    
    check_input = BranchPythonOperator(
        task_id='check_user_input',
        python_callable=wait_for_user_input,
        provide_context=True,
    )
    
    wait_timer_task = DummyOperator(task_id='wait_timer')
    
    parse_single_month_task = PythonOperator(  # ИСПРАВЛЕНО ИМЯ
        task_id='parse_single_month',
        python_callable=parse_single_month,  # ИСПРАВЛЕНО ИМЯ
        provide_context=True,
    )
    
    parse_multiple_months_task = PythonOperator(
        task_id='parse_multiple_months',
        python_callable=parse_multiple_months,
        provide_context=True,
    )
    
    parse_previous_months_task = PythonOperator(
        task_id='parse_previous_months',
        python_callable=parse_previous_months_task,
        provide_context=True,
    )
    
    parse_current_month_task = PythonOperator(
        task_id='parse_current_month',
        python_callable=parse_current_month,
        provide_context=True,
    )
    
    report_task = PythonOperator(
        task_id='generate_report',
        python_callable=generate_report,
        provide_context=True,
    )
    
    end = DummyOperator(task_id='end')
    
    # Настройка зависимостей
    start >> check_input
    
    # Если есть ввод от пользователя
    check_input >> [parse_single_month_task, parse_multiple_months_task, parse_previous_months_task, wait_timer_task]
    
    # Если нет ввода - ждем и парсим текущий
    wait_timer_task >> parse_current_month_task
    
    # Все пути ведут к отчету и завершению
    [parse_single_month_task, parse_multiple_months_task, parse_previous_months_task, parse_current_month_task] >> report_task
    report_task >> end