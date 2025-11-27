import streamlit as st
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

st.set_page_config(page_title="Selenium в Streamlit Cloud", layout="wide")

st.title("🚀 Рабочий Selenium в Streamlit Cloud")
st.write("Адаптированная версия на основе рабочего примера")

@st.cache_resource
def get_driver():
    """Инициализация драйвера с правильными настройками для Streamlit Cloud"""
    options = Options()
    
    # Критически важные настройки для Streamlit Cloud
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920,1080")
    
    # Используем Chromium через webdriver-manager
    service = Service(
        ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
    )
    
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def test_basic_navigation():
    """Тест базовой навигации"""
    try:
        driver = get_driver()
        
        st.write("### 1. Тест загрузки страницы")
        driver.get("https://httpbin.org/html")
        st.success(f"✅ Страница загружена: {driver.title}")
        
        st.write("### 2. Тест поиска элементов")
        h1_element = driver.find_element(By.TAG_NAME, "h1")
        st.success(f"✅ Найден H1: {h1_element.text}")
        
        st.write("### 3. Тест выполнения JavaScript")
        current_url = driver.execute_script("return window.location.href;")
        st.success(f"✅ JavaScript выполнен: {current_url}")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Ошибка: {e}")
        return False

def test_advanced_features():
    """Тест расширенных функций"""
    try:
        driver = get_driver()
        
        st.write("### 4. Тест взаимодействия с формами")
        driver.get("https://httpbin.org/forms/post")
        
        # Находим и заполняем поле
        input_field = driver.find_element(By.NAME, "custname")
        input_field.send_keys("Test User")
        st.success("✅ Поле формы заполнено")
        
        st.write("### 5. Тест скриншота")
        driver.save_screenshot("selenium_test.png")
        st.image("selenium_test.png", caption="Скриншот страницы")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Ошибка: {e}")
        return False

def test_real_website():
    """Тест на реальном сайте"""
    try:
        driver = get_driver()
        
        st.write("### 6. Тест на реальном сайте")
        driver.get("https://httpbin.org/")
        
        # Находим несколько элементов
        links = driver.find_elements(By.TAG_NAME, "a")
        st.success(f"✅ Найдено ссылок: {len(links)}")
        
        # Показываем некоторые ссылки
        link_texts = [link.text for link in links[:5] if link.text]
        st.write("Примеры ссылок:", link_texts)
        
        return True
        
    except Exception as e:
        st.error(f"❌ Ошибка: {e}")
        return False

# Основной интерфейс
st.write("## 🧪 Выберите тесты для запуска")

if st.button("🚀 Запустить все тесты"):
    with st.spinner("Выполнение тестов..."):
        results = []
        
        results.append(test_basic_navigation())
        time.sleep(2)  # Пауза между тестами
        
        results.append(test_advanced_features())
        time.sleep(2)
        
        results.append(test_real_website())
        
        if all(results):
            st.balloons()
            st.success("🎉 Все тесты пройдены успешно!")
        else:
            st.error("❌ Некоторые тесты не пройдены")

if st.button("🧪 Базовый тест"):
    with st.spinner("Запуск базового теста..."):
        if test_basic_navigation():
            st.success("✅ Базовый тест пройден!")
        else:
            st.error("❌ Базовый тест не пройден")

if st.button("📄 Показать код драйвера"):
    st.code("""
@st.cache_resource
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    service = Service(
        ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
    )
    
    return webdriver.Chrome(service=service, options=options)
    """)

# Информация о среде
with st.expander("🔧 Информация о настройке"):
    st.write("""
    **Ключевые моменты для работы Selenium в Streamlit Cloud:**
    
    1. **packages.txt** должен содержать:
       ```
       chromium
       chromium-driver
       ```
    
    2. **requirements.txt** должен содержать:
       ```
       streamlit
       seleniumbase
       webdriver-manager
       ```
    
    3. **Использовать ChromeType.CHROMIUM** в webdriver-manager
    
    4. **Правильные аргументы Chrome:**
       - `--headless`
       - `--no-sandbox` 
       - `--disable-dev-shm-usage`
       - `--disable-gpu`
    
    5. **@st.cache_resource** для переиспользования драйвера
    """)

st.write("---")
st.write("Если этот вариант не работает, убедитесь что:")
st.write("1. Файлы `packages.txt` и `requirements.txt` загружены в корень репозитория")
st.write("2. Приложение перезапущено в Streamlit Cloud")
st.write("3. В логах нет ошибок установки зависимостей")
