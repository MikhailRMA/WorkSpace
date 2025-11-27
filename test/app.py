import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

st.set_page_config(page_title="Selenium в Streamlit Cloud", layout="wide")

st.title("🚀 Рабочий Selenium в Streamlit Cloud")
st.write("Точная копия рабочего примера с GitHub")

"""
## Web scraping on Streamlit Cloud with Selenium

Это минимальный рабочий пример использования Selenium и Chrome в Streamlit Cloud.
"""

with st.echo():
    @st.cache_resource
    def get_driver():
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        service = Service(
            ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        )
        
        return webdriver.Chrome(service=service, options=options)

    driver = get_driver()
    driver.get("http://example.com")

    st.code(driver.page_source)
