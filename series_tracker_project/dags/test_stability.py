from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import time

def stable_operation():
    print("DAG выполняется стабильно")
    return "Success"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'test_stability',
    default_args=default_args,
    description='Тест стабильности Airflow',
    schedule_interval=timedelta(minutes=5),
    catchup=False,
    tags=['test'],
) as dag:

    test_task = PythonOperator(
        task_id='stable_task',
        python_callable=stable_operation,
    )

    test_task