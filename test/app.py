import streamlit as st
import os
import sys
import subprocess

st.set_page_config(page_title="Selenium Diagnostics", layout="wide")

st.title("🔧 Полная диагностика Selenium в Streamlit Cloud")

# Проверка системы
st.write("## 1. Проверка системы")

def check_system_dependencies():
    """Проверка системных зависимостей"""
    st.write("### Проверка библиотек и пакетов:")
    
    libs_to_check = [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser", 
        "/usr/bin/chromedriver",
        "/usr/lib/x86_64-linux-gnu/libnss3.so",
        "/usr/lib/x86_64-linux-gnu/libatk-1.0.so",
        "/usr/lib/x86_64-linux-gnu/libgconf-2.so"
    ]
    
    for lib in libs_to_check:
        exists = os.path.exists(lib)
        status = "✅" if exists else "❌"
        st.write(f"{status} {lib}")

def check_ldd():
    """Проверка зависимостей через ldd"""
    try:
        st.write("### Проверка зависимостей chromedriver:")
        result = subprocess.run(["ldd", "/usr/bin/chromedriver"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            st.text_area("Зависимости chromedriver:", result.stdout, height=200)
        else:
            st.error("Не удалось проверить зависимости chromedriver")
    except Exception as e:
        st.error(f"Ошибка проверки зависимостей: {e}")

# Запускаем диагностику
check_system_dependencies()
check_ldd()

st.write("## 2. Тест Selenium с разными конфигурациями")

def test_selenium_variant(variant_name, setup_function):
    """Тестирование разных вариантов настройки Selenium"""
    st.write(f"### {variant_name}")
    
    try:
        driver = setup_function()
        driver.get("https://httpbin.org/html")
        title = driver.title
        st.success(f"✅ {variant_name} работает: {title}")
        driver.quit()
        return True
    except Exception as e:
        st.error(f"❌ {variant_name} не работает: {str(e)}")
        return False

# Вариант 1: Базовый с Chromium
def setup_basic_chromium():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.core.os_manager import ChromeType
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    service = Service(
        ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
    )
    
    return webdriver.Chrome(service=service, options=options)

# Вариант 2: С явным указанием пути к chromium
def setup_explicit_chromium():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    
    options = Options()
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

# Вариант 3: Минимальная конфигурация
def setup_minimal():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Пробуем использовать системный chromedriver
    return webdriver.Chrome(options=options)

# Запуск тестов
if st.button("🧪 Запустить все тесты Selenium"):
    results = []
    
    with st.spinner("Тестирование..."):
        results.append(test_selenium_variant("Базовый Chromium", setup_basic_chromium))
        results.append(test_selenium_variant("Явный путь к Chromium", setup_explicit_chromium))
        results.append(test_selenium_variant("Минимальная конфигурация", setup_minimal))
    
    if any(results):
        st.success("🎉 Хотя бы один тест прошел!")
    else:
        st.error("❌ Все тесты не прошли")

st.write("## 3. Альтернативное решение")

st.write("""
Если Selenium не работает, рассмотрите эти альтернативы:

### 🔄 Playwright
```python
import asyncio
from playwright.async_api import async_playwright

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://example.com")
        content = await page.content()
        await browser.close()
        return content

# Запуск
result = asyncio.run(scrape())
