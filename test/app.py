import streamlit as st
import asyncio
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Web Scraping в Streamlit Cloud", layout="wide")

def setup_playwright():
    """Установка Playwright браузеров"""
    import subprocess
    import sys
    
    # Устанавливаем браузеры для Playwright
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                      capture_output=True, check=True)
        return True
    except Exception as e:
        st.error(f"Ошибка установки браузеров: {e}")
        return False

async def test_playwright():
    """Тест Playwright"""
    try:
        from playwright.async_api import async_playwright
        
        st.write("**1. Запуск Playwright...**")
        async with async_playwright() as p:
            st.write("**2. Запуск браузера...**")
            browser = await p.chromium.launch(headless=True)
            
            st.write("**3. Создание страницы...**")
            page = await browser.new_page()
            
            st.write("**4. Навигация...**")
            await page.goto("https://httpbin.org/html", timeout=30000)
            
            st.write("**5. Получение содержимого...**")
            title = await page.title()
            st.success(f"✅ Заголовок: {title}")
            
            # Получаем HTML и парсим BeautifulSoup
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            h1_text = soup.find('h1').text
            st.success(f"✅ Найден элемент: {h1_text}")
            
            st.write("**6. Создание скриншота...**")
            await page.screenshot(path="playwright_success.png")
            st.image("playwright_success.png", caption="Скриншот Playwright")
            
            await browser.close()
            return True
            
    except Exception as e:
        st.error(f"❌ Ошибка Playwright: {e}")
        return False

def test_requests_beautifulsoup():
    """Тест Requests + BeautifulSoup"""
    try:
        st.write("**1. Отправка запроса...**")
        response = requests.get("https://httpbin.org/html", timeout=10)
        response.raise_for_status()
        
        st.write("**2. Парсинг HTML...**")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        st.write("**3. Извлечение данных...**")
        title = soup.title.string if soup.title else "No title"
        h1_text = soup.find('h1').text
        
        st.success(f"✅ Заголовок: {title}")
        st.success(f"✅ H1: {h1_text}")
        
        # Показываем часть HTML
        st.write("**4. Пример HTML:**")
        st.code(str(soup.find('body'))[:500] + "...", language='html')
        
        return True
        
    except Exception as e:
        st.error(f"❌ Ошибка: {e}")
        return False

def main():
    st.title("🌐 Рабочие решения для Streamlit Cloud")
    
    st.write("""
    Selenium не работает в Streamlit Cloud из-за отсутствия системных браузеров.
    Вот рабочие альтернативы:
    """)
    
    # Requests + BeautifulSoup
    st.write("## 🚀 Вариант 1: Requests + BeautifulSoup")
    st.write("**Идеально для статических сайтов**")
    
    if st.button("🧪 Запустить тест Requests + BeautifulSoup"):
        with st.spinner("Тестирование..."):
            if test_requests_beautifulsoup():
                st.success("🎉 Requests + BeautifulSoup работает отлично!")
                st.balloons()
    
    # Playwright
    st.write("## 🔄 Вариант 2: Playwright")
    st.write("**Для динамических сайтов с JavaScript**")
    
    if st.button("🧪 Запустить тест Playwright"):
        with st.spinner("Установка и тестирование Playwright... Это займет ~1 минуту"):
            if setup_playwright():
                # Запускаем асинхронную функцию
                import asyncio
                success = asyncio.run(test_playwright())
                if success:
                    st.success("🎉 Playwright работает отлично!")
                    st.balloons()
    
    # Сравнение методов
    st.write("## 📊 Сравнение методов")
    
    comparison_data = {
        "Метод": ["Requests + BeautifulSoup", "Playwright", "Selenium"],
        "Поддержка JavaScript": ["❌ Нет", "✅ Полная", "✅ Полная"],
        "Скорость": ["✅ Быстро", "⚠ Средняя", "⚠ Медленная"],
        "Стабильность в Cloud": ["✅ Отличная", "✅ Хорошая", "❌ Не работает"],
        "Сложность": ["✅ Низкая", "⚠ Средняя", "⚠ Высокая"]
    }
    
    st.table(comparison_data)
    
    # Примеры использования
    st.write("## 💡 Примеры кода")
    
    with st.expander("Requests + BeautifulSoup пример"):
        st.code("""
import requests
from bs4 import BeautifulSoup

# Простой парсинг
response = requests.get("https://example.com")
soup = BeautifulSoup(response.content, 'html.parser')

# Извлечение данных
title = soup.title.text
links = [a['href'] for a in soup.find_all('a', href=True)]
        """)
    
    with st.expander("Playwright пример"):
        st.code("""
import asyncio
from playwright.async_api import async_playwright

async def scrape_dynamic_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://example.com")
        content = await page.content()
        
        await browser.close()
        return content

# Запуск
result = asyncio.run(scrape_dynamic_page())
        """)

if __name__ == "__main__":
    main()
