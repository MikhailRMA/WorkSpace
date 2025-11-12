
from helpers.database import init_database, get_db_connection
import psycopg2

def setup_database():
    """Создание базы данных если она не существует"""
    try:
        # Пытаемся подключиться к существующей базе
        init_database()
        print("✅ База данных готова к работе")
        
    except psycopg2.OperationalError as e:
        if "database" in str(e) and "does not exist" in str(e):
            print("База данных не существует, создаем...")
            create_database()
        else:
            raise e

def create_database():
    """Создание новой базы данных"""
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    # Подключаемся к postgres БД для создания новой БД
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database='postgres',
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password')
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    db_name = os.getenv('DB_NAME', 'series_tracker')
    
    try:
        cursor.execute(f'CREATE DATABASE {db_name}')
        print(f"✅ База данных '{db_name}' создана успешно")
    except psycopg2.errors.DuplicateDatabase:
        print(f"✅ База данных '{db_name}' уже существует")
    finally:
        cursor.close()
        conn.close()
    
    # Инициализируем структуру новой базы
    init_database()

if __name__ == "__main__":
    setup_database()