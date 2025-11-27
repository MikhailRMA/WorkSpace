import streamlit as st
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

st.set_page_config(page_title="Selenium в Streamlit Cloud", layout="wide")

def setup_selenium():
    """Настройка Selenium для Streamlit Cloud"""
    chrome_options = Options()
    
    # Критически важные параметры для Streamlit Cloud
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-software-rasterizer")
    
    # Дополнительные параметры для стабильности
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    return chrome_options

def test_selenium_webdriver_manager():
    """Тест Selenium с использованием только webdriver-manager"""
    try:
        st.write("**1. Инициализация webdriver-manager...**")
        
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        # Настройка опций
        chrome_options = setup_selenium()
        
        st.write("**2. Установка ChromeDriver через webdriver-manager...**")
        service = Service(ChromeDriverManager().install())
        
        st.write("**3. Запуск ChromeDriver...**")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        st.success("✅ ChromeDriver запущен!")
        
        # Тестируем
        st.write("**4. Тест навигации...**")
        test_url = "https://httpbin.org/html"
        driver.get(test_url)
        
        title = driver.title
        st.success(f"✅ Страница загружена: `{title}`")
        
        st.write("**5. Тест поиска элементов...**")
        h1_element = driver.find_element(By.TAG_NAME, "h1")
        h1_text = h1_element.text
        st.success(f"✅ Элемент найден: `{h1_text}`")
        
        st.write("**6. Тест выполнения JavaScript...**")
        page_url = driver.execute_script("return window.location.href;")
        st.success(f"✅ JavaScript выполнен: `{page_url}`")
        
        st.write("**7. Создание скриншота...**")
        screenshot_path = "selenium_success.png"
        driver.save_screenshot(screenshot_path)
        
        if os.path.exists(screenshot_path):
            st.image(screenshot_path, caption="Скриншот тестовой страницы")
            st.success("✅ Скриншот создан")
            # Очищаем файл после показа
            os.remove(screenshot_path)
        else:
            st.warning("⚠ Скриншот не создан, но тест пройден")
        
        driver.quit()
        return True
        
    except Exception as e:
        st.error(f"❌ Ошибка: {str(e)}")
        
        # Расширенная диагностика
        st.write("## 🔧 Диагностика проблемы")
        st.code(f"""
Ошибка: {e}
Python: {sys.executable}
Рабочая директория: {os.getcwd()}
Доступные файлы: {os.listdir('.')}
        """)
        
        return False

def main():
    st.title("🚀 Selenium в Streamlit Cloud - Финальное решение")
    st.write("""
    Эта версия использует ТОЛЬКО webdriver-manager без попыток установки системных пакетов.
    Streamlit Cloud автоматически предоставляет среду для работы Chrome.
    """)
    
    # Информация о среде
    with st.expander("🔍 Информация о среде выполнения"):
        st.write(f"**Python:** `{sys.executable}`")
        st.write(f"**Рабочая директория:** `{os.getcwd()}`")
        st.write(f"**Платформа:** `{sys.platform}`")
        
        # Проверка установленных пакетов
        st.write("**Проверка пакетов:**")
        try:
            import selenium
            st.success(f"✅ Selenium: {selenium.__version__}")
        except ImportError:
            st.error("❌ Selenium не установлен")
            
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            st.success("✅ webdriver-manager доступен")
        except ImportError:
            st.error("❌ webdriver-manager не установлен")
    
    st.write("---")
    
    # Основной тест
    st.write("## 🧪 Основной тест Selenium")
    st.write("""
    Этот тест использует webdriver-manager для автоматической загрузки и настройки ChromeDriver.
    В Streamlit Cloud среда уже настроена для работы Chrome в headless-режиме.
    """)
    
    if st.button("🚀 Запустить тест Selenium (webdriver-manager)"):
        with st.spinner("Выполнение теста... Это может занять 10-30 секунд"):
            success = test_selenium_webdriver_manager()
            
            if success:
                st.balloons()
                st.success("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Selenium работает в Streamlit Cloud!")
                st.balloons()
            else:
                st.error("❌ Тест не пройден. Смотрите диагностику выше.")
    
    st.write("---")
    
    # Альтернативы
    st.write("## 🔄 Если Selenium не работает - альтернативы")
    
    if st.button("🧪 Протестировать альтернативу (Requests + BeautifulSoup)"):
        try:
            import requests
            from bs4 import BeautifulSoup
            
            st.write("**Тест Requests + BeautifulSoup...**")
            response = requests.get("https://httpbin.org/html", timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            h1_text = soup.find('h1').text
            
            st.success(f"✅ Requests test passed: {h1_text}")
            st.info("""
            ✅ Этот подход работает без браузера!
            
            **Преимущества:**
            - Быстрее и надежнее
            - Меньше ресурсов
            - Всегда работает в облачных средах
            
            **Недостатки:**
            - Не выполняет JavaScript
            - Не взаимодействует с динамическим контентом
            """)
            
        except Exception as e:
            st.error(f"❌ Requests test failed: {e}")

if __name__ == "__main__":
    main()
