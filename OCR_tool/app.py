import streamlit as st
import os
import tempfile
import base64
from datetime import datetime
import zipfile
import io
from pdf2image import convert_from_path, convert_from_bytes
import pytesseract
from PIL import Image

# Настройка пути к Tesseract для Streamlit Cloud
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

st.set_page_config(
    page_title="PDF OCR Extractor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS стили OZON
def apply_ozon_style():
    st.markdown("""
    <style>
        /* Основные стили */
        .main, .stApp {
            background-color: #1A1A1A !important;
            color: white !important;
        }
        .stTextInput, .stTextArea, .stNumberInput, .stSelectbox {
            color: var(--ozon-text) !important;
        }
        .stTextInput label, .stTextArea label, .stNumberInput label, .stSelectbox label {
            color: white !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: white !important;
        }
        .main .block-container {
            background-color: #1A1A1A !important;
            color: white !important;
        }
        
        /* Заголовок */
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
        
        /* Секции */
        .section-header {
            background: linear-gradient(135deg, #005BFF, #004ACC);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            text-align: center;
            font-weight: 900;
        }
        
        /* Карточки */
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
        
        /* Статус */
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
        
        /* Кнопки */
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
        
        /* Оповещения */
        .ozon-alert-success {
            background: #2D2D2D !important;
            border-left: 4px solid #005BFF !important;
            color: #FFFFFF !important;
            padding: 0.8rem;
            border-radius: 8px;
            margin: 0.8rem 0;
        }
        .ozon-alert-success strong {
            color: #FFFFFF !important;
        }
        
        /* Сайдбар */
        .ozon-sidebar-header {
            background: url('https://brandlab.ozon.ru/images/tild6365-6165-4064-b161-626431393363__pattern_bg-1.png');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
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
            border: 3px solid #005BFF;
        }
        
        /* Информация о файле */
        .uploaded-file-info {
            background: #2D2D2D;
            padding: 0.8rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            border-left: 4px solid #005BFF;
        }
        
        /* Номера шагов */
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
        
        /* Дополнительные стили */
        .file-card {
            background: #2D2D2D;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            border-left: 5px solid #005BFF;
        }
        .progress-container {
            background: #2D2D2D;
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
        }
        .stats-card {
            background: linear-gradient(135deg, #005BFF20, #FF6B0020);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border: 1px solid #404040;
        }
        
        /* Ссылки на другие инструменты */
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
        
        /* Футер */
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
        
        /* Информация о Tesseract */
        .tesseract-info {
            background: linear-gradient(135deg, #005BFF10, #FF6B0010);
            border: 1px solid #005BFF30;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }
        
        /* Контейнеры для ссылок */
        .tools-container {
            margin-top: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

# Применяем стили
apply_ozon_style()

# Инициализация сессионных состояний
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'result_text' not in st.session_state:
    st.session_state.result_text = ""
if 'total_pages' not in st.session_state:
    st.session_state.total_pages = 0
if 'processed_pages' not in st.session_state:
    st.session_state.processed_pages = 0

# Функция для извлечения текста с использованием pdf2image
def extract_text_from_pdf(pdf_path, dpi=300, lang="rus", progress_bar=None, status_text=None):
    """Извлекает текст из PDF с помощью OCR через pdf2image"""
    extracted_text = ""
    page_texts = []
    
    try:
        # Конвертируем PDF в изображения
        images = convert_from_path(pdf_path, dpi=dpi)
        total_pages = len(images)
        st.session_state.total_pages = total_pages
        
        for page_num, image in enumerate(images):
            if progress_bar:
                progress = (page_num + 1) / total_pages
                progress_bar.progress(progress)
            
            if status_text:
                status_text.text(f"📄 Обработка страницы {page_num + 1} из {total_pages}")
            
            try:
                # Применяем OCR к изображению
                text = pytesseract.image_to_string(image, lang=lang)
                page_texts.append(text)
                
                # Добавляем в общий текст
                extracted_text += f"\n{'='*50}\n📄 СТРАНИЦА {page_num + 1}\n{'='*50}\n\n{text}\n"
                
            except Exception as page_error:
                page_texts.append("")
                extracted_text += f"\n{'='*50}\n📄 СТРАНИЦА {page_num + 1} - ОШИБКА\n{'='*50}\n\nОшибка обработки: {page_error}\n"
                continue
        
        return extracted_text, page_texts
        
    except Exception as e:
        return f"❌ Ошибка при обработке PDF: {e}", []


# Функция для создания загружаемого файла
def get_download_link(text, filename):
    """Генерирует ссылку для скачивания текстового файла"""
    b64 = base64.b64encode(text.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64}" download="{filename}">📥 Скачать {filename}</a>'
    return href

# Функция для создания ZIP архива с текстами по страницам
def create_zip_archive(page_texts):
    """Создает ZIP архив с отдельными файлами для каждой страницы"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, text in enumerate(page_texts):
            filename = f"страница_{i+1:03d}.txt"
            zip_file.writestr(filename, text)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

# Основной интерфейс
def main():
    # Боковая панель
    with st.sidebar:
        # Заголовок с иконкой
        st.markdown(f'''
        <div class="ozon-sidebar-header">
            <img src="https://cdn1.ozone.ru/s3/common-image-storage/bx/char_cat-box-four_m.png" 
                 class="site-icon" 
                 alt="PDF OCR Icon">
            <h1 class="sidebar-title">PDF OCR Extractor</h1>
        </div>
        ''', unsafe_allow_html=True)
        
        # Информация о Tesseract
        st.markdown("""
        <div class="tesseract-info">
            <h4>🧠 Технология</h4>
            <p><strong>Используется ядро:</strong> Tesseract OCR</p>
            <p><em>Бесплатная open-source система оптического распознавания символов</em></p>
            <p style="font-size: 0.8rem; color: #B3B3B3; margin-top: 8px;">
                Версия: {version}<br>
                Поддерживает 100+ языков
            </p>
        </div>
        """.format(version=pytesseract.get_tesseract_version()), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="ozon-card">
            <div class="card-header">
                <span class="card-icon">⚙️</span>
                <h3 class="card-title">Настройки OCR</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Настройки DPI
        dpi = st.slider("Качество сканирования (DPI)", min_value=150, max_value=600, value=300, step=50,
                       help="Более высокое DPI улучшает качество распознавания, но замедляет обработку")
        
        # Выбор языка
        language = st.selectbox(
            "Язык распознавания",
            options=["rus", "eng", "rus+eng", "fra", "deu", "spa"],
            index=0,
            help="Выберите язык текста в PDF"
        )
        
        # Статистика
        st.markdown("""
        <div class="ozon-card">
            <div class="card-header">
                <span class="card-icon">📊</span>
                <h3 class="card-title">Статистика</h3>
            </div>
            <div class="ozon-status">
                <strong>Обработано файлов:</strong> {file_count}<br>
                <strong>Всего страниц:</strong> {total_pages}<br>
                <strong>Версия Tesseract:</strong> {tess_version}
            </div>
        </div>
        """.format(
            file_count=st.session_state.get('processed_files', 0),
            total_pages=st.session_state.get('total_pages_processed', 0),
            tess_version=pytesseract.get_tesseract_version()
        ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Другие инструменты
        st.markdown("""
        <div class="ozon-card">
            <div class="card-header">
                <span class="card-icon">🔗</span>
                <h3 class="card-title">Другие инструменты</h3>
            </div>
            <div class="tools-container">
                <a href="https://extractor-sku-by-mroshchupkin.streamlit.app/" target="_blank" class="tool-link">
                    🛍️ <strong>Extractor SKU</strong><br>
                    <small>Извлечение артикулов и данных</small>
                </a>
                <a href="https://brand-detected-by-mroshchupkin.streamlit.app/" target="_blank" class="tool-link">
                    🏷️ <strong>Brand Detector</strong><br>
                    <small>Определение брендов в тексте</small>
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Инструкция
        st.markdown("---")
        st.markdown("""
        <div style="color: #B3B3B3; font-size: 0.9rem;">
        <strong>📌 Инструкция:</strong><br>
        1. Загрузите PDF файл<br>
        2. Настройте параметры<br>
        3. Нажмите "Начать обработку"<br>
        4. Скачайте результат
        </div>
        """, unsafe_allow_html=True)
        
        # Футер
        st.markdown("""
        <div class="footer">
            With <span class="heart">❤️</span> by mroshchupkin and DS<br>
            <small style="color: #808080;">v1.0 | Powered by Tesseract OCR</small>
        </div>
        """, unsafe_allow_html=True)

    # Основная область
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h1 class="main-header">📄 PDF OCR Extractor</h1>', unsafe_allow_html=True)
        st.markdown('<p class="main-subtitle">Извлечение текста из отсканированных PDF файлов с помощью Tesseract OCR</p>', unsafe_allow_html=True)
        
        # Информация о Tesseract на главной
        st.markdown("""
        <div class="tesseract-info">
            <h4>✅ Бесплатное ядро Tesseract OCR</h4>
            <p>Это приложение использует <strong>Tesseract OCR</strong> — открытую систему оптического распознавания символов, разработанную Google.</p>
            <p><strong>Преимущества:</strong></p>
            <ul style="margin-left: 20px; color: #B3B3B3;">
                <li>Бесплатное и открытое ПО</li>
                <li>Поддержка 100+ языков</li>
                <li>Высокая точность распознавания</li>
                <li>Не требует лицензионных отчислений</li>
                <li>Постоянно обновляется сообществом</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="section-header">
            <span class="step-number">1</span> Загрузка PDF файла
        </div>
        """, unsafe_allow_html=True)
        
        # Загрузка файла
        uploaded_file = st.file_uploader(
            "Выберите PDF файл",
            type=['pdf'],
            help="Загрузите отсканированный PDF файл для распознавания текста"
        )
        
        if uploaded_file:
            file_details = {
                "Имя файла": uploaded_file.name,
                "Размер файла": f"{uploaded_file.size / 1024:.2f} КБ",
                "Тип файла": uploaded_file.type
            }
            
            st.markdown(f"""
            <div class="uploaded-file-info">
                <strong>📎 Загружен файл:</strong> {file_details['Имя файла']}<br>
                <strong>📊 Размер:</strong> {file_details['Размер файла']}<br>
                <strong>🔍 Тип:</strong> {file_details['Тип файла']}
            </div>
            """, unsafe_allow_html=True)
            
            # Кнопка начала обработки
            if st.button("🚀 Начать обработку", use_container_width=True):
                st.session_state.processing = True
                st.session_state.result_text = ""
                
                # Сохраняем временный файл
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    pdf_path = tmp_file.name
                
                try:
                    # Индикатор прогресса
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Извлекаем текст
                    extracted_text, page_texts = extract_text_from_pdf(
                        pdf_path, 
                        dpi=dpi, 
                        lang=language,
                        progress_bar=progress_bar,
                        status_text=status_text
                    )
                    
                    # Обновляем статистику
                    if 'processed_files' not in st.session_state:
                        st.session_state.processed_files = 0
                    st.session_state.processed_files += 1
                    
                    if 'total_pages_processed' not in st.session_state:
                        st.session_state.total_pages_processed = 0
                    st.session_state.total_pages_processed += len(page_texts)
                    
                    # Сохраняем результат
                    st.session_state.result_text = extracted_text
                    st.session_state.page_texts = page_texts
                    
                    # Удаляем временный файл
                    os.unlink(pdf_path)
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success(f"✅ Обработка завершена! Распознано {len(page_texts)} страниц")
                    
                except Exception as e:
                    st.error(f"❌ Ошибка при обработке: {e}")
                    if os.path.exists(pdf_path):
                        os.unlink(pdf_path)
    
    with col2:
        st.markdown("""
        <div class="section-header">
            <span class="step-number">2</span> Результаты
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.result_text:
            # Показываем статистику
            total_chars = len(st.session_state.result_text)
            total_words = len(st.session_state.result_text.split())
            total_pages = st.session_state.total_pages
            
            st.markdown(f"""
            <div class="stats-card">
                <h4>📊 Статистика распознавания:</h4>
                <strong>📄 Страниц:</strong> {total_pages}<br>
                <strong>🔤 Символов:</strong> {total_chars:,}<br>
                <strong>📝 Слов:</strong> {total_words:,}<br>
                <strong>⚡ DPI:</strong> {dpi}<br>
                <strong>🌐 Язык:</strong> {language}
            </div>
            """, unsafe_allow_html=True)
            
            # Кнопки скачивания
            st.markdown("""
            <div class="section-header">
                <span class="step-number">3</span> Скачать результат
            </div>
            """, unsafe_allow_html=True)
            
            # Подготовка имени файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = uploaded_file.name.replace('.pdf', '')
            
            col_dl1, col_dl2 = st.columns(2)
            
            with col_dl1:
                # Скачать полный текст
                full_filename = f"{base_filename}_полный_текст_{timestamp}.txt"
                b64_full = base64.b64encode(st.session_state.result_text.encode()).decode()
                href_full = f'<a href="data:text/plain;base64,{b64_full}" download="{full_filename}" style="text-decoration: none;"><button style="background: linear-gradient(135deg, #005BFF, #004ACC); color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; width: 100%; cursor: pointer;">📥 Полный текст</button></a>'
                st.markdown(href_full, unsafe_allow_html=True)
            
            with col_dl2:
                # Скачать ZIP с отдельными страницами
                zip_data = create_zip_archive(st.session_state.page_texts)
                zip_filename = f"{base_filename}_по_страницам_{timestamp}.zip"
                b64_zip = base64.b64encode(zip_data).decode()
                href_zip = f'<a href="data:application/zip;base64,{b64_zip}" download="{zip_filename}" style="text-decoration: none;"><button style="background: linear-gradient(135deg, #FF6B00, #FF8C00); color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; width: 100%; cursor: pointer;">📦 По страницам (ZIP)</button></a>'
                st.markdown(href_zip, unsafe_allow_html=True)
            
            # Предпросмотр текста
            with st.expander("👁️ Предпросмотр текста", expanded=False):
                preview_text = st.session_state.result_text[:2000] + "..." if len(st.session_state.result_text) > 2000 else st.session_state.result_text
                st.text_area("Текст", preview_text, height=300, label_visibility="collapsed")
        
        # Информация о точности
        if not st.session_state.result_text:
            st.markdown("""
            <div class="ozon-card">
                <div class="card-header">
                    <span class="card-icon">💡</span>
                    <h3 class="card-title">Советы по точности</h3>
                </div>
                <p style="color: #B3B3B3; font-size: 0.9rem;">
                    <strong>Для лучшего распознавания:</strong><br>
                    • Используйте DPI 300+ для мелкого текста<br>
                    • Убедитесь, что PDF четкий<br>
                    • Выбирайте правильный язык<br>
                    • Обрабатывайте по одному файлу за раз
                </p>
            </div>
            """, unsafe_allow_html=True)

# Запуск приложения
if __name__ == "__main__":
    # Проверка наличия Tesseract
    try:
        pytesseract.get_tesseract_version()
        main()
    except Exception as e:
        st.error(f"""
        ⚠️ Tesseract OCR не установлен или не настроен!
        
        **Ошибка:** {e}
        
        Для работы приложения необходимо:
        1. **Установить Tesseract OCR:** https://github.com/UB-Mannheim/tesseract/wiki
        2. **Добавить путь к Tesseract** в системную переменную PATH
        3. Или указать путь вручную в настройках
        
        **Временное решение** (добавьте в код перед запуском):
        ```python
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        ```
        
        **Примечание:** Это приложение использует **бесплатное open-source ядро Tesseract OCR**, 
        что позволяет обрабатывать PDF без лицензионных ограничений.
        """)