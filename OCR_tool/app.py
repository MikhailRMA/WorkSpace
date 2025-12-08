import streamlit as st
import os
import tempfile
import base64
from datetime import datetime
import zipfile
import io
import sys
import subprocess

# ==================== КОНФИГУРАЦИЯ ====================
# Настройки страницы
st.set_page_config(
    page_title="PDF OCR Extractor | OZON Style",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ПРОВЕРКА ЗАВИСИМОСТЕЙ ====================
def check_dependencies():
    """Проверяет и настраивает зависимости"""
    issues = []
    
    # 1. Проверяем Tesseract в системе
    try:
        result = subprocess.run(['which', 'tesseract'], 
                               capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            issues.append("❌ Tesseract не найден в системе")
        else:
            tesseract_path = result.stdout.strip()
            st.session_state.tesseract_path = tesseract_path
    except:
        issues.append("❌ Не удалось проверить Tesseract")
    
    # 2. Проверяем Python пакеты
    try:
        import fitz  # PyMuPDF
    except ImportError:
        issues.append("❌ PyMuPDF (fitz) не установлен")
    
    try:
        import pytesseract
        # Устанавливаем путь к Tesseract
        if 'tesseract_path' in st.session_state:
            pytesseract.pytesseract.tesseract_cmd = st.session_state.tesseract_path
    except ImportError:
        issues.append("❌ pytesseract не установлен")
    
    try:
        from PIL import Image
    except ImportError:
        issues.append("❌ Pillow (PIL) не установлен")
    
    return issues

# ==================== СТИЛИ OZON ====================
def apply_ozon_style():
    st.markdown("""
    <style>
        /* Основные стили */
        .main, .stApp {
            background-color: #1A1A1A !important;
            color: white !important;
        }
        
        .main-header {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #005BFF, #FF6B00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            margin-bottom: 1rem;
            font-weight: 800;
        }
        
        .main-subtitle {
            text-align: center;
            color: #B3B3B3;
            margin-bottom: 2rem;
        }
        
        .section-header {
            background: linear-gradient(135deg, #005BFF, #004ACC);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            text-align: center;
            font-weight: 900;
        }
        
        .ozon-card {
            background: #2D2D2D;
            padding: 1.2rem;
            border-radius: 8px;
            border: 1px solid #404040;
            margin: 0.8rem 0;
            color: white;
            transition: all 0.3s ease;
        }
        
        .stButton button {
            background: linear-gradient(135deg, #005BFF, #004ACC);
            color: white;
            border: none;
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .stButton button:hover {
            background: linear-gradient(135deg, #004ACC, #005BFF);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 91, 255, 0.2);
        }
        
        .footer {
            text-align: center;
            color: #B3B3B3;
            font-size: 0.9rem;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #404040;
        }
        
        .heart {
            color: #FF6B00;
        }
        
        .error-box {
            background: #FF6B0020;
            border: 2px solid #FF6B00;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .success-box {
            background: #005BFF20;
            border: 2px solid #005BFF;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
    </style>
    """, unsafe_allow_html=True)

apply_ozon_style()

# ==================== ИНИЦИАЛИЗАЦИЯ ====================
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'result_text' not in st.session_state:
    st.session_state.result_text = ""
if 'total_pages' not in st.session_state:
    st.session_state.total_pages = 0

# ==================== ОСНОВНЫЕ ФУНКЦИИ ====================
def extract_text_from_pdf(pdf_path, dpi=300, lang="rus", progress_bar=None, status_text=None):
    """Извлекает текст из PDF с помощью OCR"""
    try:
        import fitz
        from PIL import Image
        import pytesseract
        
        # Устанавливаем путь к Tesseract если еще не установлен
        if 'tesseract_path' in st.session_state:
            pytesseract.pytesseract.tesseract_cmd = st.session_state.tesseract_path
        
        extracted_text = ""
        page_texts = []
        
        # Открываем PDF
        pdf = fitz.open(pdf_path)
        total_pages = len(pdf)
        st.session_state.total_pages = total_pages
        
        for page_num in range(total_pages):
            if progress_bar:
                progress = (page_num + 1) / total_pages
                progress_bar.progress(progress)
            
            if status_text:
                status_text.text(f"📄 Обработка страницы {page_num + 1} из {total_pages}")
            
            try:
                # Конвертируем страницу в изображение
                page = pdf.load_page(page_num)
                pix = page.get_pixmap(dpi=dpi)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Применяем OCR
                text = pytesseract.image_to_string(img, lang=lang)
                page_texts.append(text)
                
                extracted_text += f"\n{'='*50}\n📄 СТРАНИЦА {page_num + 1}\n{'='*50}\n\n{text}\n"
                
            except Exception as page_error:
                page_texts.append("")
                extracted_text += f"\n{'='*50}\n📄 СТРАНИЦА {page_num + 1} - ОШИБКА\n{'='*50}\n\nОшибка: {page_error}\n"
                continue
        
        pdf.close()
        return extracted_text, page_texts
        
    except Exception as e:
        return f"❌ Ошибка при обработке PDF: {e}", []

def create_zip_archive(page_texts):
    """Создает ZIP архив"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, text in enumerate(page_texts):
            filename = f"страница_{i+1:03d}.txt"
            zip_file.writestr(filename, text)
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

# ==================== ГЛАВНЫЙ ИНТЕРФЕЙС ====================
def main():
    # Проверяем зависимости
    issues = check_dependencies()
    
    # Шапка
    st.markdown('<h1 class="main-header">📄 PDF OCR Extractor</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Извлечение текста из отсканированных PDF с помощью Tesseract OCR</p>', unsafe_allow_html=True)
    
    # Если есть проблемы - показываем инструкцию
    if issues:
        st.markdown('<div class="error-box">', unsafe_allow_html=True)
        st.error("## ⚠️ Проблемы с зависимостями")
        
        for issue in issues:
            st.write(f"- {issue}")
        
        st.markdown("""
        ### 🔧 Решение:
        
        1. **Убедитесь, что в корне проекта есть папка `.streamlit/` с файлом `apt-packages`**
        2. **Содержимое `apt-packages`:**
        ```
        tesseract-ocr
        tesseract-ocr-rus
        tesseract-ocr-eng
        poppler-utils
        ```
        3. **Перезапустите приложение на Streamlit Cloud**
        4. **Дождитесь завершения установки системных пакетов (2-5 минут)**
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Если все ок - показываем успешное сообщение
    if 'tesseract_path' in st.session_state:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.success(f"✅ Все зависимости установлены!")
        st.info(f"**Tesseract путь:** `{st.session_state.tesseract_path}`")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Основной интерфейс
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="section-header"><span>1</span> Загрузка PDF файла</div>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Выберите PDF файл", type=['pdf'])
        
        if uploaded_file:
            st.info(f"📎 **Загружен:** {uploaded_file.name} ({uploaded_file.size/1024:.1f} KB)")
            
            if st.button("🚀 Начать обработку", use_container_width=True):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    pdf_path = tmp_file.name
                
                try:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    extracted_text, page_texts = extract_text_from_pdf(
                        pdf_path, dpi=300, lang="rus",
                        progress_bar=progress_bar, status_text=status_text
                    )
                    
                    st.session_state.result_text = extracted_text
                    st.session_state.page_texts = page_texts
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success(f"✅ Обработка завершена! Распознано {len(page_texts)} страниц")
                    
                except Exception as e:
                    st.error(f"❌ Ошибка: {e}")
                finally:
                    if os.path.exists(pdf_path):
                        os.unlink(pdf_path)
    
    with col2:
        st.markdown('<div class="section-header"><span>2</span> Результаты</div>', unsafe_allow_html=True)
        
        if st.session_state.result_text:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = uploaded_file.name.replace('.pdf', '')
            
            # Полный текст
            full_filename = f"{base_name}_текст_{timestamp}.txt"
            b64_full = base64.b64encode(st.session_state.result_text.encode()).decode()
            st.markdown(f'<a href="data:text/plain;base64,{b64_full}" download="{full_filename}"><button>📥 Скачать полный текст</button></a>', unsafe_allow_html=True)
            
            # ZIP архив
            if hasattr(st.session_state, 'page_texts'):
                zip_data = create_zip_archive(st.session_state.page_texts)
                zip_filename = f"{base_name}_страницы_{timestamp}.zip"
                b64_zip = base64.b64encode(zip_data).decode()
                st.markdown(f'<a href="data:application/zip;base64,{b64_zip}" download="{zip_filename}"><button style="background: linear-gradient(135deg, #FF6B00, #FF8C00);">📦 Скачать постранично (ZIP)</button></a>', unsafe_allow_html=True)
    
    # Футер
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <strong>📌 Для коллег:</strong><br>
        <a href="https://extractor-sku-by-mroshchupkin.streamlit.app/" target="_blank">🛍️ Extractor SKU</a> | 
        <a href="https://brand-detected-by-mroshchupkin.streamlit.app/" target="_blank">🏷️ Brand Detector</a><br>
        With <span class="heart">❤️</span> by mroshchupkin and DS<br>
        <small>Powered by Tesseract OCR | v1.0</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()