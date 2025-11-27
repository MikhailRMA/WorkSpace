import streamlit as st
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

st.set_page_config(page_title="Selenium Test - Streamlit Cloud", layout="wide")

def setup_selenium_streamlit_cloud():
    """Настройка Selenium для Streamlit Cloud"""
    chrome_options = Options()
    
    # Конфигурация для Streamlit Cloud
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # В Streamlit Cloud Chrome/Chromium обычно доступен здесь
    chrome_options.binary_location = "/usr/bin/chromium"
    
    return chrome_options

def main():
    st.title("🌐 Selenium в Streamlit Cloud")
    st.write("Тестирование работы Selenium в облачной среде Streamlit")
    
    # Информация о среде
    with st.expander("Информация о среде выполнения"):
        st.write(f"**Python:** {sys.executable}")
        st.write(f"**Рабочая директория:** {os.getcwd()}")
        
        # Проверка наличия Chromium
        chromium_paths = [
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/bin/google-chrome"
        ]
        
        for path in chromium_paths:
            exists = os.path.exists(path)
            status = "✅" if exists else "❌"
            st.write(f"{status} {path}: {'существует' if exists else 'не найден'}")
    
    # Тест Selenium
    st.write("## 🧪 Тест Selenium")
    
    if st.button("🚀 Запустить тест Selenium"):
        with st.spinner("Выполнение теста..."):
            try:
                # Настройка Selenium
                chrome_options = setup_selenium_streamlit_cloud()
                
                st.write("**1. Инициализация ChromeDriver...**")
                
                # В Streamlit Cloud используем системный chromedriver
                from selenium.webdriver.chrome.service import Service
                service = Service("/usr/bin/chromedriver")
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
                st.success("✅ ChromeDriver инициализирован")
                
                # Тест 1: Базовая навигация
                st.write("**2. Тест навигации...**")
                test_url = "https://httpbin.org/html"
                driver.get(test_url)
                st.success(f"✅ Страница загружена: `{driver.title}`")
                
                # Тест 2: Поиск элементов
                st.write("**3. Тест поиска элементов...**")
                h1_element = driver.find_element(By.TAG_NAME, "h1")
                st.success(f"✅ Элемент найден: `{h1_element.text}`")
                
                # Тест 3: JavaScript выполнение
                st.write("**4. Тест выполнения JavaScript...**")
                current_url = driver.execute_script("return window.location.href;")
                st.success(f"✅ JavaScript выполнен: `{current_url}`")
                
                # Тест 4: Скриншот
                st.write("**5. Создание скриншота...**")
                screenshot_path = "selenium_test_streamlit_cloud.png"
                driver.save_screenshot(screenshot_path)
                
                if os.path.exists(screenshot_path):
                    st.image(screenshot_path, caption="Скриншот тестовой страницы")
                    st.success("✅ Скриншот создан")
                else:
                    st.warning("⚠ Скриншот не создан")
                
                # Завершение
                driver.quit()
                st.success("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Selenium работает в Streamlit Cloud!")
                
            except Exception as e:
                st.error(f"❌ Ошибка: {str(e)}")
                
                # Расширенная диагностика
                st.write("## 🔧 Диагностика проблемы")
                
                # Проверка версии Chromium
                try:
                    import subprocess
                    result = subprocess.run(["/usr/bin/chromium", "--version"], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        st.write(f"**Версия Chromium:** {result.stdout.strip()}")
                    else:
                        st.error("Chromium не доступен")
                except:
                    st.error("Не удалось проверить версию Chromium")
                
                # Проверка ChromeDriver
                try:
                    result = subprocess.run(["/usr/bin/chromedriver", "--version"], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        st.write(f"**Версия ChromeDriver:** {result.stdout.strip()}")
                    else:
                        st.error("ChromeDriver не доступен")
                except:
                    st.error("Не удалось проверить версию ChromeDriver")
                
                st.info("""
                **Решение для Streamlit Cloud:**
                1. Убедитесь, что в `packages.txt` указаны:
                   ```
                   chromium
                   chromium-chromedriver
                   ```
                2. В `requirements.txt` указаны:
                   ```
                   selenium>=4.38.0
                   streamlit>=1.28.0
                   ```
                3. Перезапустите приложение в Streamlit Cloud
                """)

    # Альтернативный тест с webdriver-manager
    st.write("## 🔄 Альтернативный тест (с webdriver-manager)")
    
    if st.button("🔄 Запустить тест с webdriver-manager"):
        with st.spinner("Запуск альтернативного теста..."):
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                
                # Используем webdriver-manager для автоматической установки драйвера
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
                driver.get("https://httpbin.org/html")
                st.success(f"✅ Альтернативный тест: `{driver.title}`")
                
                driver.quit()
                st.success("✅ Альтернативный тест пройден!")
                
            except Exception as e:
                st.error(f"❌ Альтернативный тест не удался: {e}")

if __name__ == "__main__":
    main()