from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Добавляем путь к helpers
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

def parse_current_month():
    """Парсинг данных за текущий месяц"""
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    
    print(f"Запуск парсинга за {year}-{month:02d}")
    series_data = parse_series_by_month(year, month)
    
    if series_data:
        save_to_database(series_data)
        print(f"Успешно сохранено {len(series_data)} сериалов")
    else:
        print("Не удалось получить данные")
    
    return len(series_data)

def generate_and_send_report():
    """Генерация и отправка отчета"""
    current_date = datetime.now()
    stats = get_series_stats(current_date.year, current_date.month)
    send_series_report(stats)

with DAG(
    'series_monthly_etl',
    default_args=default_args,
    description='Ежемесячный парсинг сериалов и отправка отчетов',
    schedule_interval='0 0 1 * *',  # Запуск 1 числа каждого месяца
    catchup=False,
    tags=['series', 'parsing', 'reporting']
) as dag:

    parse_task = PythonOperator(
        task_id='parse_current_month_series',
        python_callable=parse_current_month,
    )

    report_task = PythonOperator(
        task_id='generate_and_send_report',
        python_callable=generate_and_send_report,
    )

    parse_task >> report_task
