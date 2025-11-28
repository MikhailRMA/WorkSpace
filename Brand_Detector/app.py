import pandas as pd
import streamlit as st
import re
import json
import io
from datetime import datetime

# Настройка страницы
st.set_page_config(
    page_title="Brand Detector - OZON Style",
    page_icon="https://cdn1.ozone.ru/s3/common-image-storage/bx/tag-logo-blue_m.png",
    layout="wide"
)

# CSS стили OZON
def apply_ozon_style():
    st.markdown("""
    <style>
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
            min-height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .sidebar-title {
            color: white;
            margin: 0;
            font-size: 2rem !important;
            font-weight: 900;
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
    </style>
    """, unsafe_allow_html=True)

class BrandDetector:
    def __init__(self):
        self.brand_dict = {}
        self.logs = []
        self.performance_metrics = {}
        
    def load_default_brands(self):
        self.brand_dict = {
            "Nike": ["nike", "найк", "nike air", "air max"],
            "Adidas": ["adidas", "адидас", "adidas originals", "superstar"],
            "Apple": ["apple", "эпл", "iphone", "macbook", "ipad"],
            "Samsung": ["samsung", "самсунг", "galaxy", "note", "s series"],
            "Sony": ["sony", "сони", "playstation", "xperia"],
            "Xiaomi": ["xiaomi", "ксиаоми", "redmi", "mi", "poco"],
            "Lenovo": ["lenovo", "леново", "thinkpad", "ideapad"],
            "HP": ["hp", "hewlett packard", "hp pavilion"],
            "Dell": ["dell", "делл", "inspiron", "xps"],
            "Asus": ["asus", "асус", "rog", "zenbook"]
        }
    
    def find_brand(self, text, log_match=False, row_idx=None):
        text = str(text).lower()
        found_brand = None
        matched_keyword = None
        
        for brand, keywords in self.brand_dict.items():
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if re.search(r'\b' + re.escape(keyword_lower) + r'\b', text):
                    found_brand = brand
                    matched_keyword = keyword
                    
                    if log_match and row_idx is not None:
                        self.logs.append({
                            'timestamp': datetime.now(),
                            'row_index': row_idx,
                            'brand': brand,
                            'keyword': keyword,
                            'text_snippet': text[:100] + '...' if len(text) > 100 else text
                        })
                    break
            if found_brand:
                break
                
        return found_brand
    
    def fill_brands(self, df, log_matches=True):
        result_df = df.copy()
        processed_count = 0
        
        for idx in result_df.index:
            original_brand = result_df.loc[idx, 'бренд']
            
            if pd.notna(original_brand) and str(original_brand).strip():
                continue
                
            name_text = str(result_df.loc[idx, 'название'])
            desc_text = str(result_df.loc[idx, 'описание'])
            combined_text = f"{name_text} {desc_text}"
            
            brand = self.find_brand(combined_text, log_matches, idx)
            if brand:
                result_df.loc[idx, 'бренд'] = brand
                processed_count += 1
                
        self.performance_metrics['processed_rows'] = processed_count
        self.performance_metrics['total_rows'] = len(result_df)
        
        return result_df
    
    def calculate_quality_metrics(self, original_df, processed_df):
        original_filled = original_df['бренд'].notna().sum()
        processed_filled = processed_df['бренд'].notna().sum()
        new_filled = processed_filled - original_filled
        
        metrics = {
            'original_coverage': (original_filled / len(original_df)) * 100,
            'new_coverage': (processed_filled / len(processed_df)) * 100,
            'improvement': new_filled,
            'improvement_percentage': (new_filled / len(original_df)) * 100
        }
        
        self.performance_metrics.update(metrics)
        return metrics

def init_session_state():
    if 'detector' not in st.session_state:
        st.session_state.detector = BrandDetector()
        st.session_state.detector.load_default_brands()
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'uploaded_filename' not in st.session_state:
        st.session_state.uploaded_filename = None
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False

def clear_session_data():
    """Очистка данных сессии"""
    st.session_state.uploaded_data = None
    st.session_state.processed_data = None
    st.session_state.uploaded_filename = None
    st.session_state.show_results = False
    if 'detector' in st.session_state:
        st.session_state.detector.logs = []

def show_instructions():
    """Показ инструкций для пользователя"""
    st.markdown('<div class="section-header">📋 Как работает приложение</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="ozon-card">
            <div class="card-header">
                <span class="card-icon">1️⃣</span>
                <h3 class="card-title">Загрузка данных</h3>
            </div>
            <p>Загрузите Excel или CSV файл с обязательными колонками:</p>
            <ul>
                <li><strong>название</strong> - название товара</li>
                <li><strong>описание</strong> - описание товара</li>
                <li><strong>бренд</strong> - бренд (может быть пустым)</li>
            </ul>
            <p><em>просто переименуйте ваши столбцы и загрузите файл, порядок размещения неважен</em></p>
           
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="ozon-card">
            <div class="card-header">
                <span class="card-icon">2️⃣</span>
                <h3 class="card-title">Автоматическое определение</h3>
            </div>
            <p>Приложение анализирует текст и находит упоминания брендов по ключевым словам:</p>
            <ul>
                <li>Ищет в названии и описании</li>
                <li>Использует интеллектуальный поиск</li>
                <li>Учитывает различные написания</li>
            </ul>
            <em>Перед работой добавьте в словарь ваш Бренд и его возможные вариации написания в столбцах(название, описание)</em>
            <em>Перед работой добавьте в словарь ваш Бренд и его возможные вариации написания в столбцах(название, описание)</em>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="ozon-card">
            <div class="card-header">
                <span class="card-icon">3️⃣</span>
                <h3 class="card-title">Результаты и аналитика</h3>
            </div>
            <p>Получите готовые данные с заполненными брендами:</p>
            <ul>
                <li>Скачайте обработанный файл</li>
                <li>Просмотрите аналитику эффективности</li>
                <li>Настройте словарь под ваши нужды</li>
            </ul>
            <em>Экспортируйте словарь перед закрытием страницы, чтобы в новой сессии импортировать его, если предстоит работать с теми же брендами. На данный момент в базе не сохраняются автоматически ваши словари</em>
        </div>
        """, unsafe_allow_html=True)

def show_example_section():
    """Показ примера использования в спойлере"""
    with st.expander("📋 **Пример использования (раскройте для просмотра)**", expanded=False):
        st.markdown("""
        ### 🎯 Как это работает на практике
        
        **Всего 3 простых шага:**
        """)
        
        # Шаг 1
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown('<div class="step-number">1</div>', unsafe_allow_html=True)
        with col2:
            st.markdown("""
            **Добавьте бренды в словарь**
            - Перейдите во вкладку "Управление словарем"
            - Добавьте ваш бренд и ключевые слова
            - Например: `Lacoste`, `lacoste`, `лакост`, `крокодил`
            """)
        
        # Шаг 2
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown('<div class="step-number">2</div>', unsafe_allow_html=True)
        with col2:
            st.markdown("""
            **Загрузите файл и обработайте**
            - Загрузите CSV/Excel файл с колонками: название, описание, бренд
            - Нажмите кнопку "Заполнить бренды автоматически"
            """)
        
        # Шаг 3
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown('<div class="step-number">3</div>', unsafe_allow_html=True)
        with col2:
            st.markdown("""
            **Скачайте результаты**
            - Получите обработанный файл с заполненными брендами
            - Скачайте в формате Excel или CSV
            """)
        
        st.markdown("---")
        
        # Пример таблиц
        st.markdown("### 📊 Пример преобразования данных")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### **До обработки**")
            example_before = pd.DataFrame({
                'название': [
                    'Кроссовки Nike Air Max', 
                    'Смартфон Samsung Galaxy', 
                    'Ноутбук Apple MacBook'
                ],
                'описание': [
                    'Спортивные кроссовки для бега', 
                    'Новый флагман с камерой 108 Мп', 
                    '13 дюймов, процессор M2'
                ],
                'бренд': ['', '', '']
            })
            st.dataframe(example_before, use_container_width=True)
        
        with col2:
            st.markdown("#### **После обработки**")
            example_after = pd.DataFrame({
                'название': [
                    'Кроссовки Nike Air Max', 
                    'Смартфон Samsung Galaxy', 
                    'Ноутбук Apple MacBook'
                ],
                'описание': [
                    'Спортивные кроссовки для бега', 
                    'Новый флагман с камерой 108 Мп', 
                    '13 дюймов, процессор M2'
                ],
                'бренд': ['Nike', 'Samsung', 'Apple']
            })
            st.dataframe(example_after, use_container_width=True)
        
        st.markdown("""
        ---
        **💡 Совет:** Приложение автоматически найдет упоминания брендов в тексте 
        и заполнит пустые ячейки в столбце "бренд"
        """)

def main_page():
    """Главная страница - загрузка и обработка данных"""
    
    # Заголовок и инструкции
    st.markdown('<div style="display: flex; align-items: center; justify-content: center; gap: 12px;"><img src="https://cdn1.ozone.ru/s3/common-image-storage/bx/kettlebell-logo-blue_m.png" alt="Коробка Ozon" style="height: 80px; width: 80px; object-fit: contain;"><h1 style="color: #005BFF; font-size: 2.5rem; text-align: center; font-weight: 800; margin: 0; line-height: 1;">OZON Brand Detector</h1></div>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Автоматическое определение брендов в товарных данных</p>', unsafe_allow_html=True)
    
    show_instructions()
    
    # Добавляем пример использования
    show_example_section()
    
    # Если уже есть загруженные данные, показываем их
    if st.session_state.uploaded_data is not None:
        show_existing_data()
    else:
        show_file_uploader()
    
    # Если есть обработанные данные, показываем результаты
    if st.session_state.show_results and st.session_state.processed_data is not None:
        show_results()

def show_file_uploader():
    """Показ загрузчика файлов"""
    st.markdown('<div class="section-header">📁 Загрузка данных</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Выберите Excel или CSV файл", 
        type=['xlsx', 'xls', 'csv'],
        help="Файл должен содержать колонки: название, описание, бренд"
    )
    
    if uploaded_file:
        process_uploaded_file(uploaded_file)

def process_uploaded_file(uploaded_file):
    """Обработка загруженного файла"""
    try:
        # Загрузка файла
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Сохраняем данные в сессии
        st.session_state.uploaded_data = df
        st.session_state.uploaded_filename = uploaded_file.name
        st.session_state.processed_data = None
        st.session_state.show_results = False
        
        # Показываем данные
        show_data_preview(df)
        
    except Exception as e:
        st.error(f"❌ Ошибка при загрузке файла: {str(e)}")

def show_existing_data():
    """Показ уже загруженных данных"""
    st.markdown('<div class="section-header">📁 Загруженные данные</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="uploaded-file-info">
        <strong>Текущий файл:</strong> {st.session_state.uploaded_filename}<br>
        <strong>Записей:</strong> {len(st.session_state.uploaded_data)}
    </div>
    """, unsafe_allow_html=True)
    
    # Кнопка для загрузки нового файла
    if st.button("📁 Загрузить другой файл"):
        clear_session_data()
        st.rerun()
    
    # Показываем превью данных
    show_data_preview(st.session_state.uploaded_data)
    
    # Обработка
    st.markdown('<div class="section-header">⚡ Обработка данных</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Заполнить бренды автоматически", use_container_width=True):
            with st.spinner("🔍 Анализирую данные..."):
                # Сбрасываем логи перед новой обработкой
                st.session_state.detector.logs = []
                
                processed_df = st.session_state.detector.fill_brands(st.session_state.uploaded_data)
                metrics = st.session_state.detector.calculate_quality_metrics(
                    st.session_state.uploaded_data, processed_df
                )
                
                st.session_state.processed_data = processed_df
                st.session_state.show_results = True
                
                st.markdown(f"""
                <div class="ozon-alert-success">
                    <strong>✅ Обработка завершена успешно!</strong><br>
                    Заполнено {metrics['improvement']} новых брендов<br>
                    Общее покрытие: {metrics['new_coverage']:.1f}%
                </div>
                """, unsafe_allow_html=True)
                st.rerun()

def show_data_preview(df):
    """Показ превью данных и статистики"""
    # Предпросмотр данных
    st.markdown("### 👀 Предпросмотр данных")
    st.dataframe(df.head(), use_container_width=True)
    
    # Статистика
    st.markdown("### 📊 Статистика данных")
    col1, col2, col3 = st.columns(3)
    
    total_rows = len(df)
    filled_brands = df['бренд'].notna().sum()
    empty_brands = total_rows - filled_brands
    coverage = (filled_brands / total_rows) * 100
    
    with col1:
        st.metric("Всего записей", total_rows)
    with col2:
        st.metric("Заполнено брендов", filled_brands)
    with col3:
        st.metric("Пустых брендов", empty_brands)

def show_results():
    """Показ результатов обработки"""
    processed_df = st.session_state.processed_data
    original_df = st.session_state.uploaded_data
    
    st.markdown('<div class="section-header">📈 Результаты обработки</div>', unsafe_allow_html=True)
    
    # Вычисляем метрики
    total_processed = len(processed_df)
    filled_processed = processed_df['бренд'].notna().sum()
    
    if original_df is not None:
        filled_original = original_df['бренд'].notna().sum()
        new_filled = filled_processed - filled_original
        coverage_before = (filled_original / total_processed) * 100
    else:
        new_filled = st.session_state.detector.performance_metrics.get('processed_rows', 0)
        coverage_before = 0
    
    coverage_after = (filled_processed / total_processed) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="ozon-card">
            <div class="card-header">
                <span class="card-icon">📊</span>
                <h3 class="card-title">Итоговая статистика</h3>
            </div>
            <div class="ozon-status">
                <strong>Всего записей:</strong> {total_processed}<br>
                <strong>Заполнено брендов:</strong> {filled_processed}<br>
                <strong>Покрытие данных:</strong> {coverage_after:.1f}%<br>
                <strong>Улучшение:</strong> +{coverage_after - coverage_before:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Топ брендов
        if filled_processed > 0:
            brand_counts = processed_df['бренд'].value_counts().head(5)
            brands_html = ""
            for brand, count in brand_counts.items():
                if pd.notna(brand):
                    brands_html += f"<strong>{brand}:</strong> {count} записей<br>"
            
            st.markdown(f"""
            <div class="ozon-card">
                <div class="card-header">
                    <span class="card-icon">🏆</span>
                    <h3 class="card-title">Топ-5 брендов</h3>
                </div>
                <div class="ozon-status">
                    {brands_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Предпросмотр обработанных данных
    st.markdown("### 👁️ Предпросмотр обработанных данных")
    st.dataframe(st.session_state.processed_data.head(10), use_container_width=True)
    
    # Скачивание результата
    st.markdown('<div class="section-header">💾 Скачать результаты</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Скачивание Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            st.session_state.processed_data.to_excel(writer, index=False, sheet_name='Обработанные данные')
        output.seek(0)
        
        st.download_button(
            label="📥 Скачать Excel файл",
            data=output,
            file_name=f"обработанные_данные_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        # Скачивание CSV
        csv_data = st.session_state.processed_data.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Скачать CSV файл",
            data=csv_data,
            file_name=f"обработанные_данные_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

def dictionary_management():
    """Управление словарем брендов"""
    st.markdown('<div class="section-header">📚 Управление словарем брендов</div>', unsafe_allow_html=True)
    
    detector = st.session_state.detector
    
    # Информация о словаре
    col1, col2 = st.columns(2)
    
    with col1:
        total_brands = len(detector.brand_dict)
        total_keywords = sum(len(keywords) for keywords in detector.brand_dict.values())
        
        st.markdown(f"""
        <div class="ozon-card">
            <div class="card-header">
                <span class="card-icon">📊</span>
                <h3 class="card-title">Статистика словаря</h3>
            </div>
            <div class="ozon-status">
                <strong>Брендов в словаре:</strong> {total_brands}<br>
                <strong>Всего ключевых слов:</strong> {total_keywords}<br>
                <strong>Среднее слов на бренд:</strong> {total_keywords/total_brands:.1f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="ozon-card">
            <div class="card-header">
                <span class="card-icon">💡</span>
                <h3 class="card-title">Советы по настройке</h3>
            </div>
            <div class="ozon-status">
                • Добавляйте различные написания<br>
                • Включайте популярные модели<br>
                • Используйте транслит и синонимы<br>
                • Тестируйте на реальных данных
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Текущий словарь
    st.markdown("### 🏷️ Текущий словарь брендов")
    st.markdown("""    <div><p>Экспортируйте словарь перед закрытием страницы, чтобы в новой сессии импортировать его, если предстоит работать с теми же брендами. На данный момент в базе не сохраняются автоматически ваши словари</p></div> """, unsafe_allow_html=True)
    st.markdown(""" <div><em>Если хотите, чтобы ваш словарь был в приложении или просто готовы поделиться с коллегами, присылайте файл словаря на почту mroshchupkin@ozon.ru с указанием темы письма "Словарь брендов"</em> </div>""", unsafe_allow_html=True)
    if not detector.brand_dict:
        st.info("ℹ️ Словарь брендов пуст. Добавьте первый бренд.")
    else:
        # Отображение в виде таблицы для редактирования
        brand_data = []
        for brand, keywords in detector.brand_dict.items():
            brand_data.append({
                'Бренд': brand,
                'Ключевые слова': ', '.join(keywords),
                'Количество ключевых слов': len(keywords)
            })
        
        df_brands = pd.DataFrame(brand_data)
        st.dataframe(df_brands, use_container_width=True)
    
    # Добавление/редактирование брендов
    st.markdown("### ✏️ Добавить или изменить бренд")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        brand_name = st.text_input("Название бренда", placeholder="Например: Samsung")
    
    with col2:
        keywords_input = st.text_input(
            "Ключевые слова (через запятую)", 
            placeholder="samsung, самсунг, galaxy, note"
        )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("➕ Добавить бренд", use_container_width=True):
            if brand_name and keywords_input:
                keywords = [k.strip() for k in keywords_input.split(',')]
                detector.brand_dict[brand_name] = keywords
                st.success(f"✅ Бренд '{brand_name}' добавлен!")
                st.rerun()
            else:
                st.warning("⚠️ Заполните название бренда и ключевые слова")
    
    with col2:
        if st.button("🔄 Обновить бренд", use_container_width=True):
            if brand_name and keywords_input:
                if brand_name in detector.brand_dict:
                    keywords = [k.strip() for k in keywords_input.split(',')]
                    detector.brand_dict[brand_name] = keywords
                    st.success(f"✅ Бренд '{brand_name}' обновлен!")
                    st.rerun()
                else:
                    st.warning(f"⚠️ Бренд '{brand_name}' не найден в словаре")
            else:
                st.warning("⚠️ Заполните название бренда и ключевые слова")
    
    with col3:
        if st.button("🗑️ Удалить бренд", use_container_width=True):
            if brand_name and brand_name in detector.brand_dict:
                del detector.brand_dict[brand_name]
                st.success(f"✅ Бренд '{brand_name}' удален!")
                st.rerun()
            else:
                st.warning("⚠️ Введите название существующего бренда")
    
    # Импорт/экспорт словаря
    st.markdown("### 🔄 Импорт/экспорт словаря")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Экспорт
        dict_json = json.dumps(detector.brand_dict, ensure_ascii=False, indent=2)
        st.download_button(
            label="📤 Экспорт словаря (JSON)",
            data=dict_json,
            file_name=f"brand_dictionary_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Импорт
        uploaded_dict = st.file_uploader("Импорт JSON словаря", type=['json'])
        if uploaded_dict:
            try:
                imported_dict = json.load(uploaded_dict)
                detector.brand_dict.update(imported_dict)
                st.success("✅ Словарь успешно импортирован!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Ошибка при импорте: {str(e)}")

def analytics_and_logs():
    """Аналитика и логирование"""
    st.markdown('<div class="section-header">📊 Аналитика и логирование</div>', unsafe_allow_html=True)
    
    detector = st.session_state.detector
    
    if not detector.logs:
        st.info("""
        ℹ️ **Логи обработки пока отсутствуют.** 
        
        Для получения аналитики:
        1. Перейдите на главную страницу
        2. Загрузите файл с данными  
        3. Запустите обработку брендов
        """)
        return
    
    # Метрики производительности
    st.markdown("### 📈 Метрики обработки")
    
    if detector.performance_metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = detector.performance_metrics
        
        with col1:
            st.metric("Обработано строк", metrics.get('total_rows', 0))
        with col2:
            st.metric("Заполнено брендов", metrics.get('processed_rows', 0))
        with col3:
            st.metric("Эффективность", 
                     f"{(metrics.get('processed_rows', 0) / metrics.get('total_rows', 1) * 100):.1f}%")
        with col4:
            st.metric("Всего логов", len(detector.logs))
    
    # Визуализация сработавших ключевых слов
    st.markdown("### 🔍 Эффективность ключевых слов")
    
    if detector.logs:
        # Анализ логов
        log_df = pd.DataFrame(detector.logs)
        keyword_usage = log_df['keyword'].value_counts().reset_index()
        keyword_usage.columns = ['keyword', 'count']
        
        # Таблица использования ключевых слов
        if not keyword_usage.empty:
            st.markdown("#### Топ-10 самых частых ключевых слов")
            st.dataframe(keyword_usage.head(10), use_container_width=True)
        
        # Распределение по брендам
        brand_usage = log_df['brand'].value_counts().reset_index()
        brand_usage.columns = ['brand', 'count']
        
        if not brand_usage.empty:
            st.markdown("#### Распределение найденных брендов")
            st.dataframe(brand_usage, use_container_width=True)
    
    # Детальные логи
    st.markdown("### 📝 Детальные логи обработки")
    
    log_df = pd.DataFrame(detector.logs)
    if not log_df.empty:
        log_df['timestamp'] = log_df['timestamp'].dt.strftime('%H:%M:%S')
        st.dataframe(log_df[['timestamp', 'row_index', 'brand', 'keyword', 'text_snippet']], 
                    use_container_width=True)
        
        # Поиск по логам
        search_term = st.text_input("🔍 Поиск по логам (бренд, ключевое слово, текст)")
        if search_term:
            filtered_logs = log_df[
                log_df['brand'].str.contains(search_term, case=False, na=False) |
                log_df['keyword'].str.contains(search_term, case=False, na=False) |
                log_df['text_snippet'].str.contains(search_term, case=False, na=False)
            ]
            st.write(f"Найдено {len(filtered_logs)} записей:")
            st.dataframe(filtered_logs, use_container_width=True)

def main():
    """Главная функция приложения"""
    # Применяем стили OZON
    apply_ozon_style()
    
    # Инициализация состояния
    init_session_state()
    
    # Боковая панель навигации
    with st.sidebar:
        st.markdown("""
        <div class="ozon-sidebar-header">
            <h1 class="sidebar-title">Информация</h1>
        </div>
        """, unsafe_allow_html=True)
        
       
        
        page = st.radio(
            "Навигация",
            ["Главная", "Управление словарем", "Аналитика и логи"]
        )
        
        st.write("---")
        
        # Статистика в сайдбаре
        detector = st.session_state.detector
        
        # Информация о загруженном файле
        if st.session_state.uploaded_filename:
            st.markdown(f"""
            <div class="uploaded-file-info">
                <strong>📁 Загруженный файл:</strong><br>
                {st.session_state.uploaded_filename}<br>
                <small>Записей: {len(st.session_state.uploaded_data) if st.session_state.uploaded_data is not None else 0}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🗑️ Очистить данные"):
                clear_session_data()
                st.rerun()
        
        # Общая статистика
        st.markdown(f"""
        <div class="ozon-status">
            <strong>Статистика:</strong><br>
            Брендов: {len(detector.brand_dict)}<br>
            Ключевых слов: {sum(len(keywords) for keywords in detector.brand_dict.values())}<br>
            Логов: {len(detector.logs)}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("""
        <div class="text-center" style="color: var(--ozon-text-muted); padding: 1rem;">
            <p>With ❤️ by <strong>mroshchupkin and DS</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Отображение выбранной страницы
    if page == "Главная":
        main_page()
    elif page == "Управление словарем":
        dictionary_management()
    elif page == "Аналитика и логи":
        analytics_and_logs()

if __name__ == "__main__":
    main()