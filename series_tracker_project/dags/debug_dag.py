from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def debug_environment():
    """Диагностика чем окружение DAG отличается от терминала"""
    import sys, os, subprocess
    
    print("=== DAG ENVIRONMENT ===")
    print("Python:", sys.executable)
    print("PATH:", os.environ.get('PATH'))
    print("PWD:", os.getcwd())
    print("User:", os.environ.get('USER'))
    
    # Проверим доступ к /usr/bin
    print("=== FILESYSTEM ACCESS ===")
    result = subprocess.run(['ls', '-la', '/usr/bin/chromium'], capture_output=True, text=True)
    print("Chromium exists:", result.returncode == 0)
    print("Chromium ls:", result.stdout)
    
    # Проверим Selenium
    print("=== SELENIUM CHECK ===")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print("✅ Selenium imports work")
        
        # Простая проверка
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Пробуем разные варианты
        try:
            driver = webdriver.Chrome(options=options)
            print("✅ Selenium CAN create driver (simple)")
            driver.quit()
        except Exception as e:
            print(f"❌ Simple driver failed: {e}")
            
        # С binary location
        try:
            options.binary_location = '/usr/bin/chromium'
            driver = webdriver.Chrome(options=options)
            print("✅ Selenium CAN create driver (with binary)")
            driver.quit()
        except Exception as e:
            print(f"❌ Binary driver failed: {e}")
            
    except Exception as e:
        print(f"❌ Selenium imports failed: {e}")
    
    # Проверим команды
    print("=== SYSTEM CHECKS ===")
    commands = [
        ['which', 'chromium'],
        ['chromium', '--version'],
        ['which', 'python'],
        ['python', '--version']
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            print(f"{' '.join(cmd)}: {result.stdout.strip()}")
        except Exception as e:
            print(f"{' '.join(cmd)}: FAILED - {e}")

default_args = {
    'owner': 'debug',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
}

with DAG(
    'debug_environment',
    default_args=default_args,
    description='Диагностика окружения DAG',
    schedule_interval=None,
    catchup=False,
    tags=['debug'],
) as dag:

    debug_task = PythonOperator(
        task_id='debug_environment',
        python_callable=debug_environment,
    )

    debug_task