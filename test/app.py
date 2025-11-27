import streamlit as st
import os
import subprocess
import sys

def install_chrome():
    """Установка Chrome через скрипт"""
    st.write("**Установка Chrome...**")
    
    try:
        # Скачиваем и устанавливаем Chrome
        commands = [
            ["wget", "-q", "-O", "chrome.deb", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"],
            ["apt-get", "update"],
            ["apt-get", "install", "-y", "./chrome.deb"],
            ["rm", "chrome.deb"]
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                st.warning(f"Команда {cmd} завершилась с кодом {result.returncode}")
        
        # Проверяем установку
        if os.path.exists("/usr/bin/google-chrome"):
            st.success("✅ Chrome установлен!")
            return True
        else:
            st.error("❌ Chrome не установился")
            return False
            
    except Exception as e:
        st.error(f"❌ Ошибка установки: {e}")
        return False

def main():
    st.title("🛠️ Установка Chrome в Streamlit Cloud")
    
    if st.button("Установить Chrome"):
        if install_chrome():
            st.success("Chrome готов к использованию!")
        else:
            st.error("Не удалось установить Chrome")

if __name__ == "__main__":
    main()
