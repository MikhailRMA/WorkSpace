import re
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import base64
import time
import os
import sys

# =============================================
# НАСТРОЙКА SELENIUM ДЛЯ REPLIT
# =============================================

SELENIUM_AVAILABLE = False
SELENIUM_STATUS = "Не проверено"

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    SELENIUM_AVAILABLE = True
    SELENIUM_STATUS = "✅ Selenium доступен"
except ImportError as e:
    SELENIUM_STATUS = f"❌ Selenium недоступен: {e}"

def install_chrome_in_replit():
    """Устанавливает Chrome в Replit"""
    try:
        # Устанавливаем Chrome в Replit
        os.system("apt-get update")
        os.system("apt-get install -y wget")
        os.system("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
        os.system("dpkg -i google-chrome-stable_current_amd64.deb")
        os.system("apt-get install -y -f")
        os.system("apt-get install -y chromium-chromedriver")
        return True
    except Exception as e:
        st.error(f"Ошибка установки Chrome: {e}")
        return False

@st.cache_resource
def setup_driver():
    """Настройка ChromeDriver для Replit"""
    if not SELENIUM_AVAILABLE:
        return None
    
    try:
        chrome_options = Options()
        
        # Опции для Replit
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # В Replit используем системный Chrome
        chrome_options.binary_location = "/usr/bin/google-chrome"
        
        # Пробуем разные пути к chromedriver
        chromedriver_paths = [
            "/usr/bin/chromedriver",
            "/usr/local/bin/chromedriver",
            "/usr/lib/chromium-browser/chromedriver"
        ]
        
        driver = None
        for path in chromedriver_paths:
            try:
                if os.path.exists(path):
                    driver = webdriver.Chrome(executable_path=path, options=chrome_options)
                    st.success(f"✅ ChromeDriver найден: {path}")
                    break
            except:
                continue
        
        if not driver:
            # Если не нашли chromedriver, пробуем без указания пути
            driver = webdriver.Chrome(options=chrome_options)
        
        return driver
        
    except Exception as e:
        st.error(f"Ошибка настройки ChromeDriver: {e}")
        
        # Пробуем установить Chrome
        st.info("🔄 Пробуем установить Chrome...")
        if install_chrome_in_replit():
            return setup_driver()
        return None

# =============================================
# ВАШ ОРИГИНАЛЬНЫЙ CSS
# =============================================

# Настройка страницы
st.set_page_config(
    page_title="OZON SKU Extractor",
    page_icon="https://cdn1.ozone.ru/s3/common-image-storage/bx/box-open-ozon-alt_m.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS в стиле OZON - ТЕМНАЯ ТЕМА ПО УМОЛЧАНИЮ
st.markdown("""
<style>
    /* Цветовая гамма OZON - ТЕМНАЯ ТЕМА ПО УМОЛЧАНИЮ */
    :root {
        --ozon-primary: #005BFF;
        --ozon-primary-dark: #004ACC;
        --ozon-primary-light: #3377FF;
        --ozon-secondary: #FF6B00;
        --ozon-background: #1A1A1A; /* Темный фон по умолчанию */
        --ozon-surface: #2D2D2D; /* Темные карточки */
        --ozon-text: #FFFFFF; /* Белый текст */
        --ozon-text-muted: #B3B3B3;
        --ozon-border: #404040;
        --ozon-shadow: rgba(0, 91, 255, 0.2);
        --ozon-success: #00A650;
        --ozon-warning: #FFB800;
        --ozon-error: #FF3B30;
        --ozon-card-padding: 1.2rem;
        --ozon-font-size-base: 1rem;
        --ozon-font-size-sm: 0.9rem;
        --ozon-font-size-lg: 1.1rem;
        --ozon-border-radius: 8px;
    }
        
    /* Убираем медиа-запрос для темной темы, т.к. теперь это по умолчанию */
    
    /* Адаптация для планшетов */
    @media (max-width: 1024px) {
        :root {
            --ozon-card-padding: 1rem;
            --ozon-font-size-base: 0.95rem;
        }
    }
    
    /* Адаптация для мобильных устройств */
    @media (max-width: 768px) {
        :root {
            --ozon-card-padding: 0.9rem;
            --ozon-font-size-base: 0.9rem;
            --ozon-font-size-sm: 0.85rem;
            --ozon-border-radius: 6px;
        }
    }

    /* Базовые стили для Streamlit */
    .main {
        background-color: var(--ozon-background) !important;
    }
    
    .stApp {
        background-color: var(--ozon-background) !important;
    }
    
    /* Стили для текстовых элементов Streamlit */
    .stTextInput, .stTextArea, .stNumberInput, .stSelectbox {
        color: var(--ozon-text) !important;
    }
    .responsive-img {
        max-width: 10%;
        height: auto;
        display: block;
    }
    .stTextInput label, .stTextArea label, .stNumberInput label, .stSelectbox label {
        color: var(--ozon-text) !important;
    }
    
    /* Заголовки Streamlit */
    h1, h2, h3, h4, h5, h6 {
        color: var(--ozon-text) !important;
    }
    
    /* Основной контент */
    .main .block-container {
        background-color: var(--ozon-background) !important;
        color: var(--ozon-text) !important;
    }
    
    /* Базовые стили */
    .main-header {
        font-size: clamp(1.8rem, 5vw, 2.5rem);
        background: linear-gradient(135deg, var(--ozon-primary), var(--ozon-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        color: var(--ozon-primary); /* Fallback цвет */
        text-align: center;
        margin-bottom: clamp(0.5rem, 2vw, 1rem);
        font-weight: 800;
        line-height: 1.2;
    }
    
    .main-subtitle {
        text-align: center;
        color: var(--ozon-text-muted);
        margin-bottom: clamp(1rem, 3vw, 2rem);
        font-size: var(--ozon-font-size-base);
        line-height: 1.4;
    }
    
    /* Заголовки разделов */
    .section-header {
        background: url('https://brandlab.ozon.ru/images/tild6365-6165-4064-b161-626431393363__pattern_bg-1.png');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: white;
        padding: clamp(1rem, 2.5vw, 1.5rem);
        border-radius: var(--ozon-border-radius);
        margin-bottom: 1rem;
        text-align: center;
        position: relative;
        min-height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: clamp(1.5rem, 1.5vw, 5rem) !important;
        font-weight: 900 !important;
    }
    
    /* Карточки в стиле OZON */
    .ozon-card {
        background: var(--ozon-surface);
        padding: var(--ozon-card-padding);
        border-radius: var(--ozon-border-radius);
        box-shadow: 0 2px 12px var(--ozon-shadow);
        border: 1px solid var(--ozon-border);
        margin: clamp(0.5rem, 1.5vw, 0.8rem) 0;
        color: var(--ozon-text);
        font-size: var(--ozon-font-size-base);
        transition: all 0.3s ease;
    }
    
    .ozon-card:hover {
        box-shadow: 0 4px 20px var(--ozon-shadow);
        transform: translateY(-2px);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 0.8rem;
        gap: 0.5rem;
    }
    
    .card-icon {
        font-size: 1.3em;
        color: var(--ozon-primary);
    }
    
    .card-title {
        margin: 0;
        color: var(--ozon-primary);
        font-size: var(--ozon-font-size-base);
        font-weight: 600;
    }
    
    /* Элементы статуса */
    .ozon-status {
        background: var(--ozon-surface);
        padding: clamp(0.6rem, 1.5vw, 0.8rem);
        border-radius: 6px;
        margin: clamp(0.3rem, 1vw, 0.5rem) 0;
        border-left: 4px solid var(--ozon-primary);
        color: var(--ozon-text);
        font-size: var(--ozon-font-size-sm);
        line-height: 1.4;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .ozon-status strong {
        color: var(--ozon-primary);
    }
    
    .ozon-status code {
        background: var(--ozon-surface);
        color: var(--ozon-primary);
        padding: 0.1rem 0.3rem;
        border-radius: 4px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.85em;
        word-break: break-word;
        border: 1px solid var(--ozon-border);
    }
    
    /* Кнопки в стиле OZON */
    .stButton button {
        background: linear-gradient(135deg, var(--ozon-primary), var(--ozon-primary-dark));
        color: white;
        border: none;
        padding: clamp(0.5rem, 1.5vw, 0.6rem) clamp(1rem, 2.5vw, 1.2rem);
        border-radius: var(--ozon-border-radius);
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        font-size: var(--ozon-font-size-base);
        min-height: 44px;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, var(--ozon-primary-dark), var(--ozon-primary));
        transform: translateY(-2px);
        box-shadow: 0 6px 20px var(--ozon-shadow);
    }
    
    /* Текстовые поля */
    .stTextArea textarea {
        border-radius: var(--ozon-border-radius);
        border: 2px solid var(--ozon-border);
        padding: clamp(0.6rem, 1.5vw, 0.8rem);
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: var(--ozon-font-size-sm);
        background: var(--ozon-surface);
        color: var(--ozon-text);
        min-height: 150px;
        resize: vertical;
        transition: all 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--ozon-primary);
        box-shadow: 0 0 0 3px rgba(0, 91, 255, 0.1);
    }
    
    /* Уведомления */
    .ozon-alert {
        padding: clamp(0.6rem, 1.5vw, 0.8rem);
        border-radius: var(--ozon-border-radius);
        margin: clamp(0.5rem, 1.5vw, 0.8rem) 0;
        font-size: var(--ozon-font-size-base);
        line-height: 1.4;
        border-left: 4px solid;
    }
    
    .ozon-alert-success {
        background: var(--ozon-surface) !important;
        border-left: 4px solid var(--ozon-primary) !important;
        color: #FFFFFF !important;
        padding: clamp(0.6rem, 1.5vw, 0.8rem);
        border-radius: var(--ozon-border-radius);
        margin: clamp(0.5rem, 1.5vw, 0.8rem) 0;
        font-size: var(--ozon-font-size-base);
        line-height: 1.4;
    }

    .ozon-alert-success strong {
        color: #FFFFFF !important;
    }
    
    .ozon-alert-info {
        background: var(--ozon-surface);
        border-left-color: var(--ozon-primary);
        color: var(--ozon-text);
    }
    
    .ozon-alert-warning {
        background: var(--ozon-surface);
        border-left-color: var(--ozon-warning);
        color: var(--ozon-text);
    }
    
    .ozon-alert-error {
        background: var(--ozon-surface);
        border-left-color: var(--ozon-error);
        color: var(--ozon-text);
    }
    
    /* Ссылки для скачивания */
    .ozon-download {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #f91155 !important;
        color: white !important;
        padding: clamp(8px, 2vw, 10px) clamp(16px, 3vw, 20px);
        text-decoration: none;
        border-radius: var(--ozon-border-radius);
        font-weight: 600;
        margin: 8px 0;
        font-size: var(--ozon-font-size-base);
        min-height: 44px;
        gap: 0.5rem;
        transition: all 0.3s ease;
        text-align: center;
        border: none;
        width: 100%;
    }
            
    .ozon-download:hover {
        background: #e0104a !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(249, 17, 85, 0.4);
        color: white;
    }
    
    /* Сайдбар */
    .ozon-sidebar-header {
        background:  url('https://brandlab.ozon.ru/images/tild6365-6165-4064-b161-626431393363__pattern_bg-1.png');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: white;
        padding: clamp(1rem, 2.5vw, 1.5rem);
        border-radius: var(--ozon-border-radius);
        margin-bottom: 1rem;
        text-align: center;
        position: relative;
        min-height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .sidebar-title {
        color: white;
        margin: 0;
        font-size: clamp(1.5rem, 2vw, 2.5rem) !important;
        font-weight: 900;
    }
    
    /* Анимации */
    @keyframes ozonFadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .ozon-fade-in {
        animation: ozonFadeIn 0.4s ease-out;
    }
    
    @keyframes ozonPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .ozon-pulse {
        animation: ozonPulse 2s infinite;
    }
    
    /* Утилиты */
    .text-center { text-align: center; }
    .text-success { color: var(--ozon-success); }
    .text-warning { color: var(--ozon-warning); }
    .text-error { color: var(--ozon-error); }
    .text-primary { color: var(--ozon-primary); }
    .mb-1 { margin-bottom: 0.5rem; }
    .mb-2 { margin-bottom: 1rem; }
    
    /* Специальные стили для очень маленьких экранов */
    @media (max-width: 360px) {
        .card-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.3rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# ФУНКЦИИ ИЗВЛЕЧЕНИЯ SKU
# =============================================

def extract_sku_from_text(text):
    """Извлекает SKU из текста"""
    try:
        # Ищем SKU в ссылках (между '-' и '/')
        pattern_links = r'-(\d{9,10})/'
        sku_from_links = re.findall(pattern_links, text)
        
        # Ищем SKU в любом тексте (9-10 цифр, не начинающихся с 0)
        pattern_anywhere = r'(?<!\d)([1-9]\d{8,9})(?!\d)'
        sku_from_text = re.findall(pattern_anywhere, text)
        
        # Объединяем оба списка
        all_sku = sku_from_links + sku_from_text
        
        # Удаляем дубликаты и проверяем валидность SKU
        unique_sku = []
        seen_sku = set()
        
        for sku in all_sku:
            if sku.isdigit() and sku not in seen_sku:
                unique_sku.append(sku)
                seen_sku.add(sku)
        
        # Сортируем для удобства
        unique_sku.sort()
        return unique_sku
        
    except Exception as e:
        raise Exception(f"Ошибка при извлечении SKU: {str(e)}")

def extract_sku_from_short_url(url):
    """Извлекает SKU из короткой ссылки OZON через Selenium"""
    if not SELENIUM_AVAILABLE:
        raise Exception("Selenium недоступен")
    
    driver = setup_driver()
    if not driver:
        raise Exception("Не удалось инициализировать ChromeDriver")
    
    try:
        st.info(f"🔄 Обрабатываем: {url}")
        
        # Переходим по ссылке
        driver.get(url)
        
        # Ждем загрузки страницы
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Даем время на выполнение JavaScript и редиректы
        time.sleep(3)
        
        # Получаем текущий URL после редиректов
        current_url = driver.current_url
        st.info(f"📋 Финальный URL: {current_url}")
        
        # Ищем SKU в URL по стандартным правилам
        sku_match = re.search(r'-(\d{9,10})/', current_url)
        if sku_match:
            sku = sku_match.group(1)
            st.success(f"✅ Найден SKU: {sku}")
            return sku
        
        # Дополнительные методы поиска SKU
        page_source = driver.page_source
        
        # Ищем в JSON-LD
        json_match = re.search(r'"sku":"(\d{9,10})"', page_source)
        if json_match:
            sku = json_match.group(1)
            st.success(f"✅ Найден SKU в JSON: {sku}")
            return sku
            
        st.warning("❌ SKU не найден на странице")
        return None
        
    except Exception as e:
        st.error(f"❌ Ошибка при обработке {url}: {str(e)}")
        return None
    finally:
        if driver:
            driver.quit()

def process_short_urls(urls_text):
    """Обрабатывает короткие ссылки и извлекает SKU"""
    if not SELENIUM_AVAILABLE:
        return [], "Selenium недоступен. Функция извлечения из коротких ссылок отключена."
    
    driver = setup_driver()
    if not driver:
        return [], "ChromeDriver не инициализирован. Пожалуйста, подождите или перезагрузите приложение."
    
    # Извлекаем ссылки из текста
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, urls_text)
    
    # Фильтруем только короткие ссылки OZON
    short_urls = [url for url in urls if 'ozon.ru/t/' in url or 'ozon.com/t/' in url]
    
    if not short_urls:
        return [], "Не найдено коротких ссылок OZON (формат: https://ozon.ru/t/...)"
    
    results = []
    success_count = 0
    error_count = 0
    
    # Прогресс бар
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Обрабатываем ссылки последовательно
    for i, url in enumerate(short_urls):
        status_text.text(f"Обрабатывается {i+1}/{len(short_urls)}: {url}")
        progress_bar.progress((i) / len(short_urls))
        
        try:
            sku = extract_sku_from_short_url(url)
            if sku:
                results.append(sku)
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            error_count += 1
            st.error(f"❌ Ошибка для {url}: {str(e)}")
        
        # Обновляем прогресс
        progress_bar.progress((i + 1) / len(short_urls))
        
        # Пауза между запросами
        time.sleep(2)
    
    progress_bar.empty()
    status_text.empty()
    
    message = f"Обработано {len(short_urls)} ссылок: ✅ {success_count} успешно, ❌ {error_count} ошибок"
    return results, message

def test_selenium():
    """Тестирует работоспособность Selenium"""
    if not SELENIUM_AVAILABLE:
        return False, "Selenium не установлен"
    
    driver = setup_driver()
    if not driver:
        return False, "Не удалось инициализировать ChromeDriver"
    
    try:
        # Пробуем открыть тестовую страницу
        test_url = "https://httpbin.org/html"
        driver.get(test_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Проверяем что страница загрузилась
        if "Herman Melville" in driver.page_source:
            return True, "✅ Selenium и ChromeDriver работают корректно"
        else:
            return False, "❌ Страница загрузилась, но контент не соответствует ожидаемому"
            
    except Exception as e:
        return False, f"❌ Ошибка при тестировании Selenium: {str(e)}"
    finally:
        if driver:
            driver.quit()

# =============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================

def create_csv_content(sku_list):
    """Создает содержимое CSV файла"""
    csv_content = ""
    for sku in sku_list:
        csv_content += f"{sku}\n"
    return csv_content

def get_csv_download_link(sku_list, filename):
    """Генерирует ссылку для скачивания CSV файла"""
    csv_content = create_csv_content(sku_list)
    b64 = base64.b64encode(csv_content.encode()).decode()
    
    href = f'''
    <div class="ozon-card ozon-fade-in">
        <div class="card-header">
            <span class="card-icon">📊</span>
            <h4 class="card-title">Результаты готовы!</h4>
        </div>
        <div class="ozon-status">
    ✅ Успешно извлечено SKU: <strong>{len(sku_list)}</strong>
        </div>
        <a class="ozon-download ozon-pulse" href="data:file/csv;base64,{b64}" download="{filename}">
            📥 Скачать CSV файл
        </a>
    </div>
    '''
    return href

# =============================================
# ОСНОВНАЯ ФУНКЦИЯ
# =============================================

def main():
    # Яндекс.Метрика
    metrika_code = """
    <script>
        (function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
        m[i].l=1*new Date();
        k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})
        (window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");
    
        ym(104969939, "init", {
            clickmap:true,
            trackLinks:true,
            accurateTrackBounce:true,
            webvisor:true
        });
    </script>
    <noscript><div><img src="https://mc.yandex.ru/watch/104969939" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
    """
    
    st.markdown(metrika_code, unsafe_allow_html=True)

    # Кастомный заголовок
    st.markdown('<div style="display: flex; align-items: center; justify-content: center; gap: 12px;"><img src="https://cdn1.ozone.ru/s3/common-image-storage/bx/box-open-ozon-alt_m.png" alt="Коробка Ozon" style="height: 80px; width: 80px; object-fit: contain;"><h1 style="color: #005BFF; font-size: 2.5rem; text-align: center; font-weight: 800; margin: 0; line-height: 1;">OZON SKU Extractor</h1></div>', unsafe_allow_html=True)

    st.markdown('<p class="main-subtitle">Извлекайте SKU из ссылок OZON и любого текста </p>', unsafe_allow_html=True)
    
    # Сайдбар с карточками
    with st.sidebar:
        st.markdown("""
        <div class="ozon-sidebar-header ozon-fade-in">
            <h3 class="sidebar-title" > Информация</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Карточка "Формат SKU"
        st.markdown("""
        <div class="ozon-card ozon-fade-in">
            <div class="card-header">
                <span class="card-icon">📝</span>
                <h4 class="card-title">Формат SKU</h4>
            </div>
            <div class="ozon-status">
                <strong>Из ссылок OZON:</strong><br>
                <code>...-1650868905/...</code>
            </div>
            <div class="ozon-status">
                <strong>Из текста:</strong><br>
                9-10 цифр, не начинается с 0
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Карточка "Примеры SKU"
        st.markdown("""
        <div class="ozon-card ozon-fade-in">
            <div class="card-header">
                <span class="card-icon">💡</span>
                <h4 class="card-title">Примеры SKU</h4>
            </div>
            <div class="ozon-status text-success">
                <strong>✅ Валидные:</strong><br>
                <code>1650868905</code><br>
                <code>123456789</code><br>
                <code>9876543210</code>
            </div>
            <div class="ozon-status text-error">
                <strong>❌ Невалидные:</strong><br>
                <code>012345678</code> (0 в начале)<br>
                <code>12345678</code> (мало цифр)<br>
                <code>12345678901</code> (много цифр)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Карточка "Быстрые клавиши"
        st.markdown("""
        <div class="ozon-card ozon-fade-in">
            <div class="card-header">
                <span class="card-icon">🚀</span>
                <h4 class="card-title">Быстрые клавиши</h4>
            </div>
            <div class="ozon-status">
                <strong>Ctrl+A</strong> - Выделить все
            </div>
            <div class="ozon-status">
                <strong>Ctrl+C</strong> - Копировать
            </div>
            <div class="ozon-status">
                <strong>Ctrl+V</strong> - Вставить
            </div>
            <div class="ozon-status">
                <strong>Ctrl+Z</strong> - Отменить
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Карточка "Статус Selenium"
        driver = setup_driver()
        status_color = "text-success" if driver else "text-warning"
        status_icon = "✅" if driver else "🔄"
        status_text = "Готов к работе" if driver else "Загрузка..."
        
        st.markdown(f"""
        <div class="ozon-card ozon-fade-in">
            <div class="card-header">
                <span class="card-icon">🔧</span>
                <h4 class="card-title">Статус системы</h4>
            </div>
            <div class="ozon-status {status_color}">
                <strong>Selenium:</strong> {SELENIUM_STATUS}<br>
                <strong>ChromeDriver:</strong> {status_icon} {status_text}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Кнопка тестирования Selenium
        if st.button("🧪 Проверить Selenium", use_container_width=True):
            with st.spinner("Тестируем Selenium..."):
                success, message = test_selenium()
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        # Кнопка установки Chrome (только если нужно)
        if not driver and st.button("🔄 Установить Chrome", use_container_width=True):
            with st.spinner("Устанавливаем Chrome..."):
                if install_chrome_in_replit():
                    st.success("✅ Chrome установлен! Перезагрузите приложение.")
                else:
                    st.error("❌ Ошибка установки Chrome")
        
        st.markdown("---")
        st.markdown("""
        <div class="text-center" style="color: var(--ozon-text-muted); padding: 1.replitconfigmm;">
            <p>With ❤️ by <strong>mroshchupkin and DS</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Адаптивная основная область
    col1, col2 = st.columns([1, 1], gap="medium")
    
    with col1:
        st.markdown('<div class="section-header">📥 Ввод данных</div>', unsafe_allow_html=True)
    
        default_text = """https://www.ozon.ru/product/salfetki-ot-pyaten-na-odezhde-vlazhnye-pyatnovyvodyashchie-sredstvo-ochishchayushchie-1650868905/
https://ozon.ru/t/zqi09te
https://www.ozon.ru/product/noutbuk-apple-macbook-air-13-m1-8gb-256gb-space-gray-1234567890/
https://ozon.ru/t/xYz123ab
https://www.ozon.ru/product/telefon-samsung-galaxy-s21-987654321/

Товары: 9876543210, 555666777, 8889990001."""
    
        input_text = st.text_area(
            "",
            value=default_text,
            height=280,
            placeholder="Вставьте ваш текст здесь...",
            label_visibility="collapsed"
        )
        
        # Две кнопки в ряд
        col1_1, col1_2 = st.columns(2)
        
        with col1_1:
            extract_btn = st.button("🔍 Извлечь SKU из текста", type="primary", use_container_width=True)
        
        with col1_2:
            extract_short_btn = st.button("🔗 Извлечь из коротких ссылок", type="primary", use_container_width=True, 
                                         disabled=not SELENIUM_AVAILABLE)
    
    with col2:
        st.markdown('<div class="section-header">📤 Результаты</div>', unsafe_allow_html=True)
        
        # Инициализация session state
        if 'sku_list' not in st.session_state:
            st.session_state.sku_list = []
        if 'extraction_stats' not in st.session_state:
            st.session_state.extraction_stats = {"found": 0, "duplicates": 0}
        
        # Обработка извлечения SKU из текста
        if extract_btn:
            if not input_text.strip():
                st.markdown("""
                <div class="ozon-alert ozon-alert-warning">
                    <strong>⚠️ Внимание</strong><br>
                    Введите текст для извлечения SKU
                </div>
                """, unsafe_allow_html=True)
            else:
                with st.spinner("🔍 Извлекаем SKU из текста..."):
                    try:
                        sku_list = extract_sku_from_text(input_text)
                        
                        # Статистика
                        original_count = len(re.findall(r'-(\d{9,10})/', input_text)) + len(re.findall(r'(?<!\d)([1-9]\d{8,9})(?!\d)', input_text))
                        duplicate_count = original_count - len(sku_list)
                        
                        st.session_state.sku_list = sku_list
                        st.session_state.extraction_stats = {
                            "found": len(sku_list),
                            "duplicates": duplicate_count
                        }
                        
                    except Exception as e:
                        st.markdown(f"""
                        <div class="ozon-alert ozon-alert-error">
                            <strong>❌ Ошибка</strong><br>
                            {str(e)}
                        </div>
                        """, unsafe_allow_html=True)
        
        # Обработка извлечения SKU из коротких ссылок
        if extract_short_btn:
            if not input_text.strip():
                st.markdown("""
                <div class="ozon-alert ozon-alert-warning">
                    <strong>⚠️ Внимание</strong><br>
                    Введите текст с короткими ссылками
                </div>
                """, unsafe_allow_html=True)
            else:
                with st.spinner("🔗 Обрабатываем короткие ссылки..."):
                    try:
                        sku_list, message = process_short_urls(input_text)
                        
                        if sku_list:
                            st.session_state.sku_list = sku_list
                            st.session_state.extraction_stats = {
                                "found": len(sku_list),
                                "duplicates": 0
                            }
                            
                            st.markdown(f"""
                            <div class="ozon-alert ozon-alert-success">
                                <strong>✅ {message}</strong>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="ozon-alert ozon-alert-warning">
                                <strong>ℹ️ {message}</strong>
                            </div>
                            """, unsafe_allow_html=True)
                            
                    except Exception as e:
                        st.markdown(f"""
                        <div class="ozon-alert ozon-alert-error">
                            <strong>❌ Ошибка</strong><br>
                            {str(e)}
                        </div>
                        """, unsafe_allow_html=True)
        
        # Отображение результатов
        if st.session_state.sku_list:
            stats = st.session_state.extraction_stats
    
            # Статистика
            duplicate_info = f'<div class="ozon-status">♻️ Удалено дубликатов: <strong>{stats["duplicates"]}</strong></div>' if stats["duplicates"] > 0 else ''
    
            st.markdown(f"""
            <div class="ozon-alert ozon-alert-success ozon-fade-in">
                <strong>✅ Успешно извлечено!</strong><br>
                <div style="background: transparent; border: none; padding: 0.5rem 0;">
                    Найдено SKU: <strong>{stats['found']}</strong>
                </div>
                {duplicate_info}
             </div>
            """, unsafe_allow_html=True)
    
            # Карточка с результатами
            st.markdown("""
            <div class="ozon-card ozon-fade-in">
                <div class="card-header">
                    <span class="card-icon">📋</span>
                    <h4 class="card-title">Найденные SKU</h4>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
            result_text = "\n".join(st.session_state.sku_list)
            st.text_area("**Список извлеченных SKU:**", value=result_text, height=200, key="results", label_visibility="collapsed")
    
            # Скачивание
            if st.session_state.sku_list:
                timestamp = (datetime.now() + timedelta(hours=3)).strftime("%d-%m-%Y_%H-%M-%S")
                filename = f"ozon_sku_{timestamp}.csv"
                st.markdown(get_csv_download_link(st.session_state.sku_list, filename), unsafe_allow_html=True)

    # Дополнительная информация
    with st.expander("📊 Подробнее о работе приложения", expanded=False):
        st.markdown("#### 🔧 Как работает извлечение")
    
        st.markdown("""
        <div class="ozon-status">
            <strong>📎 Из ссылок OZON:</strong> ищет паттерн <code>-1650868905/</code> в URL
        </div>
        <div class="ozon-status">
            <strong>📝 Из текста:</strong> находит числа 9-10 цифр, не начинающиеся с 0
        </div>
        <div class="ozon-status">
            <strong>🔗 Из коротких ссылок:</strong> использует Selenium для перехода по ссылке и извлечения SKU из конечного URL
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()