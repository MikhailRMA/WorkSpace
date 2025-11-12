from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import sys
import os
import time
import traceback

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
    Если нет данных - парсим текущий месяц
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
        
        # Автоматический запуск - парсим текущий месяц
        print("🔄 Автоматический запуск - парсим текущий месяц")
        return "parse_current_month"
        
    except Exception as e:
        print(f"❌ Ошибка при проверке параметров: {e}")
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
        print(f"🔍 Детали ошибки: {traceback.format_exc()}")
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
            else:
                print(f"⚠️ Не удалось получить данные за {year}-{month:02d}")
            
            time.sleep(2)
        
        if total_series > 0:
            context['ti'].xcom_push(key='parsed_months', value=parsed_months)
            context['ti'].xcom_push(key='total_series', value=total_series)
            print(f"✅ Всего сохранено {total_series} сериалов за {len(parsed_months)} месяцев")
            return total_series
        else:
            print("❌ Не удалось получить данные ни за один месяц")
            return 0
        
    except Exception as e:
        print(f"❌ Ошибка парсинга нескольких месяцев: {e}")
        print(f"🔍 Детали ошибки: {traceback.format_exc()}")
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
        print(f"🔍 Детали ошибки: {traceback.format_exc()}")
        return 0

def parse_current_month(**context):
    """Парсинг текущего месяца"""
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
        print(f"🔍 Детали ошибки: {traceback.format_exc()}")
        return 0

def generate_report(**context):
    """Генерация и отправка отчета"""
    try:
        print("🔍 Начало генерации отчета...")
        
        # Получаем информацию о спарсенных месяцах
        parsed_months = context['ti'].xcom_pull(key='parsed_months', task_ids='parse_current_month')
        total_series = context['ti'].xcom_pull(key='total_series', task_ids='parse_current_month')
        
        print(f"📊 Данные для отчета: months={parsed_months}, series={total_series}")
        
        if not parsed_months or not total_series:
            print("❌ Нет данных для отчета")
            return
        
        # Получаем детальную статистику
        try:
            if parsed_months and isinstance(parsed_months, list) and len(parsed_months) == 1:
                year, month = map(int, parsed_months[0].split('-'))
                detailed_stats = get_series_stats(year, month)
            else:
                detailed_stats = {}
        except Exception as e:
            print(f"⚠️ Не удалось получить детальную статистику: {e}")
            detailed_stats = {}
        
        # Статистика для отчета
        total_series_count = total_series
        avg_rating_kino = detailed_stats.get('avg_rating_kino', 0)
        avg_rating_imdb = detailed_stats.get('avg_rating_imdb', 0)
        countries_count = detailed_stats.get('countries_count', 0)
        top_genres = detailed_stats.get('top_genres', {})
        top_series = detailed_stats.get('top_rated_series', [])
        monthly_trend = detailed_stats.get('monthly_trend', [])
        
        # Формируем HTML
        genres_html = ""
        for genre, count in list(top_genres.items())[:5]:
            genres_html += f"<li>{genre}: {count} сериалов</li>"
        
        series_html = ""
        for i, series in enumerate(top_series[:5], 1):
            series_html += f"""
            <tr>
                <td>{i}</td>
                <td>{series.get('title', 'N/A')}</td>
                <td>{series.get('rating_kino', 0)}</td>
                <td>{series.get('rating_imdb', 0)}</td>
                <td>{series.get('release_date', 'N/A')}</td>
            </tr>
            """
        
        trend_html = ""
        for trend in monthly_trend[:6]:
            trend_html += f"""
            <tr>
                <td>{trend.get('target_month', 'N/A')}</td>
                <td>{trend.get('series_count', 0)}</td>
                <td>{trend.get('avg_rating', 0)}</td>
            </tr>
            """
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
                .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db; }}
                .table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                .table th, .table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                .table th {{ background: #34495e; color: white; }}
                .highlight {{ color: #e74c3c; font-weight: bold; }}
                .info-section {{ background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎬 Отчет по сериалам</h1>
                <p>Автоматический отчет от {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
            </div>
            
            <div class="info-section">
                <h3>📅 Информация о парсинге</h3>
                <p><strong>Обработанные периоды:</strong> {', '.join(parsed_months) if isinstance(parsed_months, list) else parsed_months}</p>
                <p><strong>Всего месяцев:</strong> {len(parsed_months) if isinstance(parsed_months, list) else 1}</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>📊 Всего сериалов</h3>
                    <p class="highlight">{total_series_count}</p>
                </div>
                <div class="stat-card">
                    <h3>⭐ Рейтинг KinoMail</h3>
                    <p class="highlight">{avg_rating_kino:.1f}</p>
                </div>
                <div class="stat-card">
                    <h3>🎯 Рейтинг IMDb</h3>
                    <p class="highlight">{avg_rating_imdb:.1f}</p>
                </div>
                <div class="stat-card">
                    <h3>🌍 Стран</h3>
                    <p class="highlight">{countries_count}</p>
                </div>
            </div>
            
            <h2>🏆 Топ сериалов</h2>
            <table class="table">
                <tr>
                    <th>#</th>
                    <th>Название</th>
                    <th>KinoMail</th>
                    <th>IMDb</th>
                    <th>Дата выхода</th>
                </tr>
                {series_html if series_html else '<tr><td colspan="5">Нет данных</td></tr>'}
            </table>
            
            <h2>🎭 Популярные жанры</h2>
            <ul>
                {genres_html if genres_html else '<li>Нет данных</li>'}
            </ul>
            
            <h2>📈 Тренды по месяцам</h2>
            <table class="table">
                <tr>
                    <th>Месяц</th>
                    <th>Кол-во сериалов</th>
                    <th>Средний рейтинг</th>
                </tr>
                {trend_html if trend_html else '<tr><td colspan="3">Нет данных</td></tr>'}
            </table>
            
            <hr>
            <p><em>Это автоматически сгенерированный отчет. Не отвечайте на это письмо.</em></p>
        </body>
        </html>
        """
        
        # Собираем статистику для отправки
        stats = {
            'parsed_months': parsed_months,
            'total_series': total_series_count,
            'avg_rating_kino': avg_rating_kino,
            'avg_rating_imdb': avg_rating_imdb,
            'countries_count': countries_count,
            'top_genres': top_genres,
            'top_rated_series': top_series,
            'monthly_trend': monthly_trend,
            'parsed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Отправляем отчет
        send_series_report(stats)
        print(f"✅ Отчет за {len(parsed_months) if isinstance(parsed_months, list) else 1} месяцев отправлен")
        
    except Exception as e:
        print(f"❌ Критическая ошибка генерации отчета: {e}")
        print(f"🔍 Детали ошибки: {traceback.format_exc()}")

with DAG(
    'series_complete_etl',
    default_args=default_args,
    description='Полный ETL: парсинг с ожиданием ввода + сохранение + отчет',
    schedule_interval='0 12 1 * *',
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
    )
    
    parse_single_month_task = PythonOperator(  
        task_id='parse_single_month',
        python_callable=parse_single_month,
    )
    
    parse_multiple_months_task = PythonOperator(
        task_id='parse_multiple_months',
        python_callable=parse_multiple_months,
    )
    
    parse_previous_months_task = PythonOperator(
        task_id='parse_previous_months',
        python_callable=parse_previous_months_task,
    )
    
    parse_current_month_task = PythonOperator(
        task_id='parse_current_month',
        python_callable=parse_current_month,
    )
    
    report_task = PythonOperator(
        task_id='generate_report',
        python_callable=generate_report,
    )
    
    end = DummyOperator(task_id='end')
    
    # КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ ДЛЯ AIRFLOW 2.7+
    start >> check_input
    
    # ВСЕ задачи должны быть связаны с BranchPythonOperator
    check_input >> [
        parse_single_month_task, 
        parse_multiple_months_task, 
        parse_previous_months_task, 
        parse_current_month_task
    ]
    
    # ВСЕ парсинговые задачи ведут к отчету
    parse_single_month_task >> report_task
    parse_multiple_months_task >> report_task
    parse_previous_months_task >> report_task
    parse_current_month_task >> report_task
    
    report_task >> end