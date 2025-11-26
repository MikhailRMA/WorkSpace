import pandas as pd
import streamlit as st
import re
import json
import io
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Настройка страницы
st.set_page_config(
    page_title="Brand Detector - OZON Style",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Применение CSS стилей OZON
def apply_ozon_style():
    st.markdown("""
    <style>
        :root {
            --ozon-primary: #005BFF;
            --ozon-primary-dark: #004ACC;
            --ozon-secondary: #FF6B00;
            --ozon-background: #1A1A1A;
            --ozon-surface: #2D2D2D;
            --ozon-text: #FFFFFF;
            --ozon-text-muted: #B3B3B3;
            --ozon-border: #404040;
            --ozon-shadow: rgba(0, 91, 255, 0.2);
            --ozon-success: #00A650;
            --ozon-warning: #FFB800;
            --ozon-error: #FF3B30;
            --ozon-card-padding: 1.2rem;
            --ozon-font-size-base: 1rem;
            --ozon-font-size-sm: 0.9rem;
            --ozon-border-radius: 8px;
        }

        .main, .stApp {
            background-color: var(--ozon-background) !important;
        }
        
        .stTextInput, .stTextArea, .stNumberInput, .stSelectbox {
            color: var(--ozon-text) !important;
        }
        
        .stTextInput label, .stTextArea label, .stNumberInput label, .stSelectbox label {
            color: var(--ozon-text) !important;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: var(--ozon-text) !important;
        }
        
        .main .block-container {
            background-color: var(--ozon-background) !important;
            color: var(--ozon-text) !important;
        }
        
        .main-header {
            font-size: clamp(1.8rem, 5vw, 2.5rem);
            background: linear-gradient(135deg, var(--ozon-primary), var(--ozon-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            color: var(--ozon-primary);
            text-align: center;
            margin-bottom: clamp(0.5rem, 2vw, 1rem);
            font-weight: 800;
            line-height: 1.2;
        }
        
        .main-subtitle {
            text-align: center;
            color: var(--ozon-text-muted);
            margin-bottom: clamp(1rem, 3vw, 2rem);
            font-size: var(--ozon-font-size-base);
            line-height: 1.4;
        }
        
        .section-header {
            background: linear-gradient(135deg, var(--ozon-primary), var(--ozon-primary-dark));
            color: white;
            padding: clamp(1rem, 2.5vw, 1.5rem);
            border-radius: var(--ozon-border-radius);
            margin-bottom: 1rem;
            text-align: center;
            position: relative;
            min-height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: clamp(1.5rem, 1.5vw, 5rem) !important;
            font-weight: 900 !important;
        }
        
        .ozon-card {
            background: var(--ozon-surface);
            padding: var(--ozon-card-padding);
            border-radius: var(--ozon-border-radius);
            box-shadow: 0 2px 12px var(--ozon-shadow);
            border: 1px solid var(--ozon-border);
            margin: clamp(0.5rem, 1.5vw, 0.8rem) 0;
            color: var(--ozon-text);
            font-size: var(--ozon-font-size-base);
            transition: all 0.3s ease;
        }
        
        .ozon-card:hover {
            box-shadow: 0 4px 20px var(--ozon-shadow);
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
            color: var(--ozon-primary);
        }
        
        .card-title {
            margin: 0;
            color: var(--ozon-primary);
            font-size: var(--ozon-font-size-base);
            font-weight: 600;
        }
        
        .ozon-status {
            background: var(--ozon-surface);
            padding: clamp(0.6rem, 1.5vw, 0.8rem);
            border-radius: 6px;
            margin: clamp(0.3rem, 1vw, 0.5rem) 0;
            border-left: 4px solid var(--ozon-primary);
            color: var(--ozon-text);
            font-size: var(--ozon-font-size-sm);
            line-height: 1.4;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        
        .ozon-status strong {
            color: var(--ozon-primary);
        }
        
        .ozon-status code {
            background: var(--ozon-surface);
            color: var(--ozon-primary);
            padding: 0.1rem 0.3rem;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.85em;
            word-break: break-word;
            border: 1px solid var(--ozon-border);
        }
        
        .stButton button {
            background: linear-gradient(135deg, var(--ozon-primary), var(--ozon-primary-dark));
            color: white;
            border: none;
            padding: clamp(0.5rem, 1.5vw, 0.6rem) clamp(1rem, 2.5vw, 1.2rem);
            border-radius: var(--ozon-border-radius);
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
            font-size: var(--ozon-font-size-base);
            min-height: 44px;
        }
        
        .stButton button:hover {
            background: linear-gradient(135deg, var(--ozon-primary-dark), var(--ozon-primary));
            transform: translateY(-2px);
            box-shadow: 0 6px 20px var(--ozon-shadow);
        }
        
        .stTextArea textarea {
            border-radius: var(--ozon-border-radius);
            border: 2px solid var(--ozon-border);
            padding: clamp(0.6rem, 1.5vw, 0.8rem);
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: var(--ozon-font-size-sm);
            background: var(--ozon-surface);
            color: var(--ozon-text);
            min-height: 150px;
            resize: vertical;
            transition: all 0.3s ease;
        }
        
        .stTextArea textarea:focus {
            border-color: var(--ozon-primary);
            box-shadow: 0 0 0 3px rgba(0, 91, 255, 0.1);
        }
        
        .ozon-alert {
            padding: clamp(0.6rem, 1.5vw, 0.8rem);
            border-radius: var(--ozon-border-radius);
            margin: clamp(0.5rem, 1.5vw, 0.8rem) 0;
            font-size: var(--ozon-font-size-base);
            line-height: 1.4;
            border-left: 4px solid;
        }
        
        .ozon-alert-success {
            background: var(--ozon-surface) !important;
            border-left: 4px solid var(--ozon-primary) !important;
            color: #FFFFFF !important;
            padding: clamp(0.6rem, 1.5vw, 0.8rem);
            border-radius: var(--ozon-border-radius);
            margin: clamp(0.5rem, 1.5vw, 0.8rem) 0;
            font-size: var(--ozon-font-size-base);
            line-height: 1.4;
        }

        .ozon-alert-success strong {
            color: #FFFFFF !important;
        }
        
        .ozon-alert-info {
            background: var(--ozon-surface);
            border-left-color: var(--ozon-primary);
            color: var(--ozon-text);
        }
        
        .ozon-alert-warning {
            background: var(--ozon-surface);
            border-left-color: var(--ozon-warning);
            color: var(--ozon-text);
        }
        
        .ozon-alert-error {
            background: var(--ozon-surface);
            border-left-color: var(--ozon-error);
            color: var(--ozon-text);
        }
        
        .ozon-download {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: #f91155 !important;
            color: white !important;
            padding: clamp(8px, 2vw, 10px) clamp(16px, 3vw, 20px);
            text-decoration: none;
            border-radius: var(--ozon-border-radius);
            font-weight: 600;
            margin: 8px 0;
            font-size: var(--ozon-font-size-base);
            min-height: 44px;
            gap: 0.5rem;
            transition: all 0.3s ease;
            text-align: center;
            border: none;
            width: 100%;
        }
                
        .ozon-download:hover {
            background: #e0104a !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(249, 17, 85, 0.4);
            color: white;
        }
        
        .ozon-sidebar-header {
            background: linear-gradient(135deg, var(--ozon-primary), var(--ozon-primary-dark));
            color: white;
            padding: clamp(1rem, 2.5vw, 1.5rem);
            border-radius: var(--ozon-border-radius);
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
            font-size: clamp(1.5rem, 2vw, 2.5rem) !important;
            font-weight: 900;
        }
        
        @keyframes ozonFadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .ozon-fade-in {
            animation: ozonFadeIn 0.4s ease-out;
        }
        
        @keyframes ozonPulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .ozon-pulse {
            animation: ozonPulse 2s infinite;
        }
        
        .text-center { text-align: center; }
        .text-success { color: var(--ozon-success); }
        .text-warning { color: var(--ozon-warning); }
        .text-error { color: var(--ozon-error); }
        .text-primary { color: var(--ozon-primary); }
        .mb-1 { margin-bottom: 0.5rem; }
        .mb-2 { margin-bottom: 1rem; }
    </style>
    """, unsafe_allow_html=True)

class BrandDetector:
    def __init__(self):
        self.brand_dict = {}
        self.logs = []
        self.performance_metrics = {}
        
    def load_default_brands(self):
        """Загрузка стандартного словаря брендов"""
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
        """Поиск бренда в тексте с логированием"""
        text = str(text).lower()
        found_brand = None
        matched_keyword = None
        
        for brand, keywords in self.brand_dict.items():
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Используем регулярные выражения для поиска целых слов
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
        """Заполнение брендов с логированием"""
        result_df = df.copy()
        processed_count = 0
        
        for idx in result_df.index:
            original_brand = result_df.loc[idx, 'бренд']
            
            # Пропускаем если бренд уже заполнен
            if pd.notna(original_brand) and str(original_brand).strip():
                continue
                
            # Объединяем название и описание для поиска
            name_text = str(result_df.loc[idx, 'название'])
            desc_text = str(result_df.loc[idx, 'описание'])
            combined_text = f"{name_text} {desc_text}"
            
            # Ищем бренд
            brand = self.find_brand(combined_text, log_matches, idx)
            if brand:
                result_df.loc[idx, 'бренд'] = brand
                processed_count += 1
                
        self.performance_metrics['processed_rows'] = processed_count
        self.performance_metrics['total_rows'] = len(result_df)
        
        return result_df
    
    def calculate_quality_metrics(self, original_df, processed_df):
        """Расчет метрик качества"""
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
    """Инициализация состояния сессии"""
    if 'detector' not in st.session_state:
        st.session_state.detector = BrandDetector()
        st.session_state.detector.load_default_brands()
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'original_data' not in st.session_state:
        st.session_state.original_data = None

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
            <p>Загрузите Excel или CSV файл с колонками:</p>
            <ul>
                <li><strong>название</strong> - название товара</li>
                <li><strong>описание</strong> - описание товара</li>
                <li><strong>бренд</strong> - бренд (может быть пустым)</li>
            </ul>
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
        </div>
        """, unsafe_allow_html=True)

def main_page():
    """Главная страница - загрузка и обработка данных"""
    
    # Заголовок и инструкции
    st.markdown('<h1 class="main-header">🛍️ Brand Detector</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Автоматическое определение брендов в товарных данных • Стиль OZON</p>', unsafe_allow_html=True)
    
    show_instructions()
    
    # Загрузка файла
    st.markdown('<div class="section-header">📁 Загрузка данных</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Выберите Excel или CSV файл", 
        type=['xlsx', 'xls', 'csv'],
        help="Файл должен содержать колонки: название, описание, бренд"
    )
    
    if uploaded_file:
        try:
            # Загрузка данных
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.session_state.original_data = df.copy()
            
            # Проверка необходимых колонок
            required_columns = ['название', 'описание', 'бренд']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ В файле отсутствуют необходимые колонки: {', '.join(missing_columns)}")
                st.info("""
                **Требуемые колонки:**
                - `название` - название товара
                - `описание` - описание товара  
                - `бренд` - бренд товара (может быть пустым)
                """)
                return
            
            # Предпросмотр данных
            st.markdown('<div class="section-header">👀 Предпросмотр данных</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.dataframe(df.head(), use_container_width=True)
            
            with col2:
                # Статистика до обработки
                total_rows = len(df)
                filled_brands = df['бренд'].notna().sum()
                empty_brands = total_rows - filled_brands
                coverage = (filled_brands / total_rows) * 100
                
                st.markdown(f"""
                <div class="ozon-card">
                    <div class="card-header">
                        <span class="card-icon">📊</span>
                        <h3 class="card-title">Статистика</h3>
                    </div>
                    <div class="ozon-status">
                        <strong>Всего записей:</strong> {total_rows}<br>
                        <strong>Заполнено брендов:</strong> {filled_brands}<br>
                        <strong>Пустых брендов:</strong> {empty_brands}<br>
                        <strong>Покрытие:</strong> {coverage:.1f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Обработка
            st.markdown('<div class="section-header">⚡ Обработка данных</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Заполнить бренды автоматически", type="primary", use_container_width=True):
                    with st.spinner("🔍 Анализирую данные..."):
                        # Сбрасываем логи перед новой обработкой
                        st.session_state.detector.logs = []
                        
                        processed_df = st.session_state.detector.fill_brands(df)
                        metrics = st.session_state.detector.calculate_quality_metrics(
                            st.session_state.original_data, processed_df
                        )
                        
                        st.session_state.processed_data = processed_df
                        
                        st.markdown(f"""
                        <div class="ozon-alert-success">
                            <strong>✅ Обработка завершена успешно!</strong><br>
                            Заполнено {metrics['improvement']} новых брендов<br>
                            Общее покрытие: {metrics['new_coverage']:.1f}%
                        </div>
                        """, unsafe_allow_html=True)
            
            # Результаты после обработки
            if st.session_state.processed_data is not None:
                st.markdown('<div class="section-header">📈 Результаты обработки</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Статистика после обработки
                    processed_df = st.session_state.processed_data
                    total_rows = len(processed_df)
                    filled_brands = processed_df['бренд'].notna().sum()
                    coverage = (filled_brands / total_rows) * 100
                    
                    st.markdown(f"""
                    <div class="ozon-card">
                        <div class="card-header">
                            <span class="card-icon">📊</span>
                            <h3 class="card-title">Итоговая статистика</h3>
                        </div>
                        <div class="ozon-status">
                            <strong>Всего записей:</strong> {total_rows}<br>
                            <strong>Заполнено брендов:</strong> {filled_brands}<br>
                            <strong>Покрытие данных:</strong> {coverage:.1f}%<br>
                            <strong>Улучшение:</strong> +{metrics['improvement_percentage']:.1f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Топ брендов
                    if filled_brands > 0:
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
                        
        except Exception as e:
            st.error(f"❌ Ошибка при загрузке файла: {str(e)}")

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
        
        # График использования ключевых слов
        if not keyword_usage.empty:
            fig = px.bar(
                keyword_usage.head(10),
                x='keyword',
                y='count',
                title="Топ-10 самых частых ключевых слов",
                color='count',
                color_continuous_scale='blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Распределение по брендам
        brand_usage = log_df['brand'].value_counts().reset_index()
        brand_usage.columns = ['brand', 'count']
        
        if not brand_usage.empty:
            fig2 = px.pie(
                brand_usage,
                values='count',
                names='brand',
                title="Распределение найденных брендов"
            )
            st.plotly_chart(fig2, use_container_width=True)
    
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
            <h1 class="sidebar-title">🛍️</h1>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="ozon-card">
            <h3 class="card-title">Brand Detector</h3>
            <p>Автоматическое определение брендов в товарных данных</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        
        page = st.radio(
            "Навигация",
            ["Главная", "Управление словарем", "Аналитика и логи"],
            icons=["🏠", "📚", "📊"]
        )
        
        st.write("---")
        
        # Статистика в сайдбаре
        detector = st.session_state.detector
        st.markdown("""
        <div class="ozon-status">
            <strong>Статистика:</strong><br>
            Брендов: {brands}<br>
            Ключевых слов: {keywords}<br>
            Логов: {logs}
        </div>
        """.format(
            brands=len(detector.brand_dict),
            keywords=sum(len(keywords) for keywords in detector.brand_dict.values()),
            logs=len(detector.logs)
        ), unsafe_allow_html=True)
    
    # Отображение выбранной страницы
    if page == "Главная":
        main_page()
    elif page == "Управление словарем":
        dictionary_management()
    elif page == "Аналитика и логи":
        analytics_and_logs()

if __name__ == "__main__":
    main()
