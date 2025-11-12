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
    """Версия для Chromium"""
    
    print("🔧 Инициализация WebDriver для Chromium...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    chrome_options.binary_location = '/usr/bin/chromium'
    
    try:
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
        driver = setup_driver()
        
        if not driver:
            print("❌ Не удалось инициализировать WebDriver")
            return []
        
        url = f"https://kino.mail.ru/series/soon/{year}/{month_str}/"
        print(f"🌐 Открываем: {url}")
        driver.get(url)
        
        # Ждем загрузки блоков с сериалами
        print("⏳ Ожидаем загрузки блоков с сериалами...")
        wait = WebDriverWait(driver, 90)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.p-teaser-event')))
        time.sleep(3)
        
        # Получаем HTML страницы
        page_html = driver.page_source
        
        if len(page_html) < 10000:
            print("❌ Мало данных на странице")
            return []
            
        soup = BeautifulSoup(page_html, 'html.parser')
        
        # Ищем ВСЕ блоки с сериалами
        series_blocks = soup.find_all('div', class_='p-teaser-event')
        print(f"📊 Найдено блоков с сериалами: {len(series_blocks)}")
        
        series_data = []
        
        # Парсим сериалы
        for i, block in enumerate(series_blocks):
            try:
                print(f"🔍 Обрабатываем сериал {i+1}...")
                
                # 1. НАЗВАНИЕ СЕРИАЛА
                title_elem = block.find('a', class_='link-holder')
                title = title_elem.text.strip() if title_elem else "Неизвестно"
                
                # 2. ССЫЛКА НА СЕРИАЛ
                link = "https://kino.mail.ru" + title_elem['href'] if title_elem else ""
                
                # 3. РЕЙТИНГИ 
                rating_kino_mail = "0"
                rating_imdb = "0"
                
                # Ищем блок с рейтингами
                rates_block = block.find('div', class_='p-rates__rating-kino')
                if rates_block:
                    
                    rating_elem = rates_block.find('span', class_='p-rates__rating-value')
                    if rating_elem:
                        rating_kino_mail = rating_elem.text.strip()
                
                # Рейтинг IMDb
                imdb_block = block.find('div', class_='p-rates__rating-imdb')
                if imdb_block:
                    imdb_text = imdb_block.get_text()
                    imdb_match = re.search(r'IMDb\s*(\d+\.\d+|\d+)', imdb_text)
                    rating_imdb = imdb_match.group(1) if imdb_match else "0"
                
                # 4. СТРАНА, ГОД, ПРОДОЛЖИТЕЛЬНОСТЬ, ВОЗРАСТНОЕ ОГРАНИЧЕНИЕ
                country = "Неизвестно"
                parsed_year = str(year)  # Используем переданный год как базовый
                duration = "Неизвестно"
                age_limit = "Неизвестно"
                
                color_black_block = block.find('div', class_='color_black')
                if color_black_block:
                    # Получаем весь текст блока для анализа
                    full_text = color_black_block.get_text()
                    
                    # Ищем все элементы в блоке
                    all_links = color_black_block.find_all('a')
                    
                    # Страна - первая ссылка
                    if len(all_links) > 0:
                        country = all_links[0].text.strip()
                    
                    # Год - вторая ссылка (если есть)
                    if len(all_links) > 1:
                        parsed_year = all_links[1].text.strip()
                    
                    # ПРОДОЛЖИТЕЛЬНОСТЬ
                    duration_span = color_black_block.find('span', class_='link__text')
                    if duration_span:
                        duration = duration_span.text.strip()
                    else:
                        duration_match = re.search(r'(\d+\s*мин\.?)', full_text)
                        if duration_match:
                            duration = duration_match.group(1)
                    
                    # ВОЗРАСТНОЕ ОГРАНИЧЕНИЕ
                    age_elem = color_black_block.find('span', class_='label_restrict')
                    if age_elem:
                        age_limit = age_elem.text.strip()
                    else:
                        age_match = re.search(r'(\d{2}\+)', full_text)
                        if age_match:
                            age_limit = age_match.group(1)
                
                # 5. ДАТА ВЫХОДА
                release_date = f"{year}-{month_str}-01"
                date_block = block.find('div', class_='margin_bottom_5 color_gray')
                if date_block:
                    date_elem = date_block.find('strong')
                    if date_elem:
                        date_text = date_elem.text.strip()
                        date_match = re.search(r'(\d{1,2})', date_text)
                        if date_match:
                            day = date_match.group(1).zfill(2)
                            release_date = f"{year}-{month_str}-{day}"
                
                # 6. СЕЗОН 
                season = "1"  # По умолчанию
                if date_block:
                    season_text = date_block.get_text()
                    # Ищем только номер сезона (например: "1 сезон" -> "1")
                    season_match = re.search(r'(\d+)\s*сезон', season_text)
                    if season_match:
                        season = season_match.group(1)
                
                # 7. ЖАНРЫ
                genres = []
                genre_links = block.find_all('a', class_='badge')
                for genre_link in genre_links:
                    genre_text = genre_link.text.strip()
                    if genre_text and genre_text not in genres:
                        genres.append(genre_text)
                
                genre = ', '.join(genres) if genres else "Неизвестно"
                
                # 8. ЦЕЛЕВОЙ МЕСЯЦ
                target_month = f"{year}-{month_str}"
                
                # Формируем полные данные
                series_info = {
                    'title': title,
                    'link': link,
                    'country': country,
                    'year': parsed_year,
                    'release_date': release_date,
                    'season': season,
                    'rating_kino_mail': float(rating_kino_mail) if rating_kino_mail.replace('.', '').isdigit() else 0.0,
                    'rating_imdb': float(rating_imdb) if rating_imdb.replace('.', '').isdigit() else 0.0,
                    'genre': genre,
                    'duration': duration,
                    'age_limit': age_limit,
                    'target_month': target_month,
                    'parsed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                series_data.append(series_info)
                print(f"✅ {i+1}. {title}")
                print(f"   Страна: {country}, Год: {parsed_year}, Сезон: {season}")
                print(f"   Продолжительность: {duration}, Возраст: {age_limit}")
                print(f"   Рейтинг KinoMail: {rating_kino_mail}, IMDb: {rating_imdb}")
                print(f"   Жанр: {genre}")
                print(f"   Дата выхода: {release_date}")
                
            except Exception as e:
                print(f"❌ Ошибка с сериалом {i+1}: {e}")
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
        time.sleep(3)
    
    return all_data