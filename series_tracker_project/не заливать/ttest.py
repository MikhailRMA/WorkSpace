from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def test_basic_selenium():
    """Простой тест Selenium"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = '/usr/bin/chromium'
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://httpbin.org/html")
        print("✅ Простой сайт загружен")
        print(f"Заголовок: {driver.title}")
        driver.quit()
        return "SUCCESS"
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return "FAILED"

def test_target_site():
    """Тест целевого сайта"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = '/usr/bin/chromium'
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    
    try:
        driver.get("https://kino.mail.ru/series/soon/2025/11/")
        print(f"✅ Сайт загружен, заголовок: {driver.title}")
        
        page_source = driver.page_source
        print(f"Размер страницы: {len(page_source)} символов")
        
        if len(page_source) < 1000:
            print("❌ Мало контента - возможна блокировка")
            return "FAILED - LOW CONTENT"
        else:
            print("✅ Контент присутствует")
            return "SUCCESS"
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return f"FAILED - {e}"
    finally:
        driver.quit()

default_args = {
    'owner': 'test',
    'start_date': datetime(2024, 1, 1),
}

with DAG(
    'test_selenium',
    default_args=default_args,
    description='Тест Selenium и Chromium',
    schedule_interval=None,
    catchup=False,
) as dag:

    test1 = PythonOperator(
        task_id='test_basic_selenium',
        python_callable=test_basic_selenium,
    )

    test2 = PythonOperator(
        task_id='test_target_site',
        python_callable=test_target_site,
    )

    test1 >> test2