from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import pandas as pd
import time 
import re
from datetime import datetime, timedelta

 

def setup_driver():
    """Исправленная версия для Chromium в контейнере БЕЗ webdriver-manager"""
    
    
    print("🔧 Инициализация WebDriver для Chromium...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.binary_location = '/usr/bin/chromium'
    
    # Явно указываем использование Chromium
    chrome_options.binary_location = '/usr/bin/chromium'
    
    try:
        # БЕЗ Service - используем системный драйвер
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(90)
        driver.implicitly_wait(10)
        print("✅ WebDriver для Chromium успешно инициализирован")
        return driver
    except Exception as e:
        print(f"❌ Ошибка инициализации WebDriver: {e}")
        return None

def parse_series_by_month(year=None, month=None):
    """
    Универсальный парсер сериалов по году и месяцу
    """
    from datetime import datetime
    
    # Если год и месяц не указаны, используем текущие
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    # Форматируем месяц для URL (двухзначный)
    month_str = str(month).zfill(2)
    
    print(f"🎯 Реальный парсинг {year}-{month:02d}")
    
    driver = None
    try:
        # ИСПОЛЬЗУЕМ НАШУ ФУНКЦИЮ setup_driver
        driver = setup_driver()
        
        if not driver:
            print("❌ Не удалось инициализировать WebDriver")
            return []
        
        url = f"https://kino.mail.ru/series/soon/{year}/{month_str}/"
        print(f"🌐 Открываем: {url}")
        driver.get(url)
        
        # Ждем загрузки блоков с сериалами
        print("⏳ Ожидаем загрузки...")
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        import time
        time.sleep(3)
        
        # Получаем HTML страницы
        page_html = driver.page_source
        
        if len(page_html) < 10000:
            print("❌ Мало данных на странице")
            return []
            
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(page_html, 'html.parser')
        
        # Ищем ВСЕ блоки с сериалами
        series_blocks = soup.find_all('div', class_='p-teaser-event')
        print(f"📊 Найдено блоков с сериалами: {len(series_blocks)}")
        
        series_data = []
        
        # Парсим сериалы
        for i, block in enumerate(series_blocks):   # Обработаем первые 5 для теста
            try:
                print(f"🔍 Обрабатываем сериал {i+1}...")
                
                # 1. НАЗВАНИЕ СЕРИАЛА
                title_elem = block.find('a', class_='link-holder')
                title = title_elem.text.strip() if title_elem else "Неизвестно"
                
                print(f"   📺 {title}")
                
                # Добавляем базовые данные
                series_data.append({
                    'title': title,
                    'year': year,
                    'month': month,
                    'release_date': f"{year}-{month_str}-01",
                    'parsed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
            except Exception as e:
                print(f"   ❌ Ошибка с сериалом {i+1}: {e}")
                continue
        
        print(f"✅ Успешно спаршено {len(series_data)} сериалов")
        return series_data
        
    except Exception as e:
        print(f"❌ Ошибка парсинга: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
                print("✅ WebDriver закрыт")
            except:
                print("⚠️ Ошибка при закрытии WebDriver")
def parse_previous_months(months_back=6):
    """
    Парсинг данных за предыдущие месяцы
    
    Args:
        months_back (int): Сколько месяцев назад парсить
    
    Returns:
        list: Объединенные данные за все месяцы
    """
    all_data = []
    current_date = datetime.now()
    
    for i in range(months_back):
        target_date = current_date - timedelta(days=30*i)
        year = target_date.year
        month = target_date.month
        
        print(f"Парсим данные за {year}-{month:02d}")
        monthly_data = parse_series_by_month(year, month)
        all_data.extend(monthly_data)
        
        # Пауза между запросами
        time.sleep(2)
    
    return all_data