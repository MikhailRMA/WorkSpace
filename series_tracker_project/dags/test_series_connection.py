from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import sys
import os

# Добавляем путь к helpers
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

def test_series_connection():
    """Тестируем подключение к БД сериалов"""
    try:
        hook = PostgresHook(postgres_conn_id='postgres_series')
        conn = hook.get_conn()
        cursor = conn.cursor()
        
        # Проверим подключение
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        print(f"✅ Подключение к БД: {db_name}")
        
        # Проверим таблицы
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [table[0] for table in cursor.fetchall()]
        print(f"✅ Таблицы в БД: {tables}")
        
        cursor.close()
        conn.close()
        
        return f"Успешное подключение к {db_name}. Таблицы: {tables}"
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        raise

with DAG(
    'test_series_connection',
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['test'],
) as dag:

    test_task = PythonOperator(
        task_id='test_connection',
        python_callable=test_series_connection,
    )