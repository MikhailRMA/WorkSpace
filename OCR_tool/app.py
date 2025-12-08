import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import os
import tempfile
import base64
from datetime import datetime
import zipfile
import io
import sys
import subprocess

# ==================== КОНФИГУРАЦИЯ TESSERACT ====================
# Автоматически находим Tesseract в Replit
def setup_tesseract():
    """Находит и настраивает Tesseract"""
    # Проверяем стандартные пути
    possible_paths = [
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
        '/bin/tesseract',
        '/nix/store/*/bin/tesseract',  # Для Nix
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Пробуем через which
    try:
        result = subprocess.run(['which', 'tesseract'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return None

# Настраиваем Tesseract
tesseract_path = setup_tesseract()
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    st.session_state.tesseract_available = True
    st.session_state.tesseract_path = tesseract_path
else:
    st.session_state.tesseract_available = False
    st.session_state.tesseract_path = None

# Настройки страницы
st.set_page_config(
    page_title="📄 PDF OCR Extractor | OZON Style",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== СТИЛИ OZON ====================
def apply_ozon_style():
    st.markdown("""
    <style>
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
        .ozon-card:hover {
            box-shadow: 0 4px 20px rgba(0, 91, 255, 0.2);
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
            color: #005BFF;
        }
        .card-title {
            margin: 0;
            color: #005BFF;
            font-weight: 600;
        }
        .ozon-status {
            background: #2D2D2D;
            padding: 0.8rem;
            border-radius: 6px;
            margin: 0.5rem 0;
            border-left: 4px solid #005BFF;
            color: white;
        }
        .ozon-status strong {
            color: #005BFF;
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
        .ozon-sidebar-header {
            background: linear-gradient(135deg, #005BFF, #004ACC);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            text-align: center;
            position: relative;
            min-height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }
        .sidebar-title {
            color: white;
            margin: 0;
            font-size: 1.8rem !important;
            font-weight: 900;
        }
        .site-icon {
            width: 60px;
            height: 60px;
            margin-bottom: 10px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid white;
        }
        .uploaded-file-info {
            background: #2D2D2D;
            padding: 0.8rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            border-left: 4px solid #005BFF;
        }
        .step-number {
            background: #005BFF;
            color: white;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-right: 10px;
            font-weight: bold;
        }
        .stats-card {
            background: linear-gradient(135deg, #005BFF20, #FF6B0020);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border: 1px solid #404040;
        }
        .tool-link {
            display: block;
            background: #2D2D2D;
            color: white;
            padding: 12px 15px;
            margin: 8px 0;
            border-radius: 8px;
            text-decoration: none;
            border-left: 4px solid #005BFF;
            transition: all 0.3s ease;
        }
        .tool-link:hover {
            background: #3D3D3D;
            transform: translateX(5px);
            text-decoration: none;
            color: white;
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
            animation: heartbeat 1.5s infinite;
        }
        @keyframes heartbeat {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        .status-box {
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
        }
        .status-success {
            background: rgba(0, 91, 255, 0.2);
            border: 2px solid #005BFF;
        }
        .status-error {
            background: rgba(255, 107, 0, 0.2);
            border: 2px solid #FF6B00;
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
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = 0
if 'total_pages_processed' not in st.session_state:
    st.session_state.total_pages_processed = 0

# ==================== ФУНКЦИИ OCR ====================
def extract_text_from_pdf(pdf_path, dpi=300, lang="rus", progress_bar=None, status_text=None):
    """Извлекает текст из PDF с помощью OCR"""
    extracted_text = ""
    page_texts = []
    
    try:
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
                page = pdf.load_page(page_num)
                pix = page.get_pixmap(dpi=dpi)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                text = pytesseract.image_to_string(img, lang=lang)
                page_texts.append(text)
                extracted_text += f"\n{'='*50}\n📄 СТРАНИЦА {page_num + 1}\n{'='*50}\n\n{text}\n"
                
            except Exception as page_error:
                page_texts.append("")
                extracted_text += f"\n{'='*50}\n📄 СТРАНИЦА {page_num + 1} - ОШИБКА\n{'='*50}\n\n{page_error}\n"
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

# ==================== ОСНОВНОЙ ИНТЕРФЕЙС ====================
def main():
    # Боковая панель
    with st.sidebar:
        # Заголовок
        st.markdown('''
        <div class="ozon-sidebar-header">
            <h1 class="sidebar-title">📄 PDF OCR</h1>
            <p style="margin: 0; color: rgba(255,255,255,0.8);">Extractor</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Статус Tesseract
        if st.session_state.tesseract_available:
            st.markdown(f'''
            <div class="status-box status-success">
                <h4>✅ Tesseract готов</h4>
                <p><strong>Путь:</strong> {st.session_state.tesseract_path}</p>
                <p><strong>Тип:</strong> Бесплатное open-source</p>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="status-box status-error">
                <h4>❌ Tesseract не найден</h4>
                <p>Для установки в Shell Replit выполните:</p>
                <code>apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-rus</code>
            </div>
            ''', unsafe_allow_html=True)
        
        # Настройки
        st.markdown('''
        <div class="ozon-card">
            <div class="card-header">
                <span class="card-icon">⚙️</span>
                <h3 class="card-title">Настройки OCR</h3>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        dpi = st.slider("Качество (DPI)", 150, 600, 300, 50)
        language = st.selectbox("Язык", ["rus", "eng", "rus+eng", "fra", "deu", "spa"], index=0)
        
        # Статистика
        st.markdown(f'''
        <div class="ozon-card">
            <div class="card-header">
                <span class="card-icon">📊</span>
                <h3 class="card-title">Статистика</h3>
            </div>
            <div class="ozon-status">
                <strong>Обработано файлов:</strong> {st.session_state.processed_files}<br>
                <strong>Всего страниц:</strong> {st.session_state.total_pages_processed}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Другие инструменты
        st.markdown('''
        <div class="ozon-card">
            <div class="card-header">
                <span class="card-icon">🔗</span>
                <h3 class="card-title">Другие инструменты</h3>
            </div>
            <div style="margin-top: 10px;">
                <a href="https://extractor-sku-by-mroshchupkin.streamlit.app/" target="_blank" class="tool-link">
                    🛍️ <strong>Extractor SKU</strong>
                </a>
                <a href="https://brand-detected-by-mroshchupkin.streamlit.app/" target="_blank" class="tool-link">
                    🏷️ <strong>Brand Detector</strong>
                </a>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Футер
        st.markdown('''
        <div class="footer">
            With <span class="heart">❤️</span> by mroshchupkin and DS<br>
            <small>Powered by Tesseract OCR</small>
        </div>
        ''', unsafe_allow_html=True)

    # Основная область
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h1 class="main-header">📄 PDF OCR Extractor</h1>', unsafe_allow_html=True)
        st.markdown('<p class="main-subtitle">Извлечение текста из отсканированных PDF файлов</p>', unsafe_allow_html=True)
        
        # Проверка доступности Tesseract
        if not st.session_state.tesseract_available:
            st.error("""
            ## ⚠️ Tesseract не установлен!
            
            **Для установки в Replit:**
            
            1. Откройте **Shell** (терминал) в Replit
            2. Выполните команду:
            ```bash
            apt-get update
            apt-get install -y tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng
            ```
            3. Перезапустите приложение (нажмите Stop → Run)
            
            **Или добавьте в `replit.nix`:**
            ```nix
            { pkgs }: {
              deps = [
                pkgs.tesseract
                pkgs.tesseract4
              ];
            }
            ```
            """)
            st.stop()
        
        # Загрузка файла
        st.markdown('''
        <div class="section-header">
            <span class="step-number">1</span> Загрузка PDF файла
        </div>
        ''', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Выберите PDF файл", type=['pdf'])
        
        if uploaded_file:
            file_info = f"**📎 Файл:** {uploaded_file.name}<br>**📊 Размер:** {uploaded_file.size/1024:.1f} KB"
            st.markdown(f'<div class="uploaded-file-info">{file_info}</div>', unsafe_allow_html=True)
            
            if st.button("🚀 Начать обработку OCR", use_container_width=True):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(uploaded_file.getvalue())
                    pdf_path = tmp.name
                
                try:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    extracted_text, page_texts = extract_text_from_pdf(
                        pdf_path, dpi=dpi, lang=language,
                        progress_bar=progress_bar, status_text=status_text
                    )
                    
                    # Обновляем статистику
                    st.session_state.processed_files += 1
                    st.session_state.total_pages_processed += len(page_texts)
                    
                    # Сохраняем результат
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
        st.markdown('''
        <div class="section-header">
            <span class="step-number">2</span> Результаты
        </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.result_text:
            total_chars = len(st.session_state.result_text)
            total_words = len(st.session_state.result_text.split())
            
            st.markdown(f'''
            <div class="stats-card">
                <h4>📊 Статистика:</h4>
                <strong>📄 Страниц:</strong> {st.session_state.total_pages}<br>
                <strong>🔤 Символов:</strong> {total_chars:,}<br>
                <strong>📝 Слов:</strong> {total_words:,}<br>
                <strong>⚡ DPI:</strong> {dpi}<br>
                <strong>🌐 Язык:</strong> {language}
            </div>
            ''', unsafe_allow_html=True)
            
            # Скачивание
            st.markdown('''
            <div class="section-header">
                <span class="step-number">3</span> Скачать
            </div>
            ''', unsafe_allow_html=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = uploaded_file.name.replace('.pdf', '')
            
            # Полный текст
            full_filename = f"{base_name}_текст_{timestamp}.txt"
            b64_full = base64.b64encode(st.session_state.result_text.encode()).decode()
            st.markdown(f'''
            <a href="data:text/plain;base64,{b64_full}" download="{full_filename}" style="text-decoration: none;">
                <button style="background: linear-gradient(135deg, #005BFF, #004ACC); color: white; border: none; padding: 10px; border-radius: 8px; width: 100%; margin: 5px 0; cursor: pointer;">
                    📥 Полный текст
                </button>
            </a>
            ''', unsafe_allow_html=True)
            
            # ZIP архив
            if hasattr(st.session_state, 'page_texts'):
                zip_data = create_zip_archive(st.session_state.page_texts)
                zip_filename = f"{base_name}_страницы_{timestamp}.zip"
                b64_zip = base64.b64encode(zip_data).decode()
                st.markdown(f'''
                <a href="data:application/zip;base64,{b64_zip}" download="{zip_filename}" style="text-decoration: none;">
                    <button style="background: linear-gradient(135deg, #FF6B00, #FF8C00); color: white; border: none; padding: 10px; border-radius: 8px; width: 100%; margin: 5px 0; cursor: pointer;">
                        📦 По страницам (ZIP)
                    </button>
                </a>
                ''', unsafe_allow_html=True)
            
            # Предпросмотр
            with st.expander("👁️ Предпросмотр текста"):
                preview = st.session_state.result_text[:2000] + "..." if len(st.session_state.result_text) > 2000 else st.session_state.result_text
                st.text_area("", preview, height=300, label_visibility="collapsed")

if __name__ == "__main__":
    main()