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
    page_title="Brand Detector",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
            # Добавьте больше брендов по необходимости
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

def main_page():
    """Главная страница - загрузка и обработка данных"""
    st.title("🛍️ Автоматическое определение брендов")
    st.write("Загрузите ваш Excel файл для автоматического заполнения брендов")
    
    uploaded_file = st.file_uploader("Выберите файл", type=['xlsx', 'xls', 'csv'])
    
    if uploaded_file:
        # Загрузка данных
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.session_state.original_data = df.copy()
            
            # Проверка необходимых колонок
            required_columns = ['название', 'описание', 'бренд']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"В файле отсутствуют необходимые колонки: {', '.join(missing_columns)}")
                return
            
            st.subheader("Предпросмотр данных")
            st.dataframe(df.head(), use_container_width=True)
            
            # Статистика до обработки
            show_data_quality_report(df, "До обработки")
            
            # Обработка
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Заполнить бренды автоматически", type="primary", use_container_width=True):
                    with st.spinner("Обрабатываю данные..."):
                        # Сбрасываем логи перед новой обработкой
                        st.session_state.detector.logs = []
                        
                        processed_df = st.session_state.detector.fill_brands(df)
                        metrics = st.session_state.detector.calculate_quality_metrics(
                            st.session_state.original_data, processed_df
                        )
                        
                        st.session_state.processed_data = processed_df
                        
                        st.success("Обработка завершена!")
            
            # Результаты после обработки
            if st.session_state.processed_data is not None:
                st.subheader("Результаты обработки")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    show_data_quality_report(st.session_state.processed_data, "После обработки")
                
                with col2:
                    show_improvement_metrics()
                
                st.subheader("Обработанные данные")
                st.dataframe(st.session_state.processed_data.head(10), use_container_width=True)
                
                # Скачивание результата
                download_section()
                        
        except Exception as e:
            st.error(f"Ошибка при загрузке файла: {str(e)}")

def show_data_quality_report(df, title):
    """Показ отчета о качестве данных"""
    total_rows = len(df)
    filled_brands = df['бренд'].notna().sum()
    coverage = (filled_brands / total_rows) * 100
    
    st.metric(
        label=f"{title} - Заполнено брендов",
        value=f"{filled_brands}/{total_rows}",
        delta=f"{coverage:.1f}%"
    )
    
    # Топ брендов
    if filled_brands > 0:
        brand_counts = df['бренд'].value_counts().head(5)
        st.write("**Топ-5 брендов:**")
        for brand, count in brand_counts.items():
            if pd.notna(brand):
                st.write(f"- {brand}: {count}")

def show_improvement_metrics():
    """Показ метрик улучшения"""
    metrics = st.session_state.detector.performance_metrics
    
    if 'improvement' in metrics:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="Новых брендов заполнено",
                value=metrics['improvement'],
                delta=f"{metrics['improvement_percentage']:.1f}%"
            )
        
        with col2:
            st.metric(
                label="Общее покрытие",
                value=f"{metrics['new_coverage']:.1f}%",
                delta=f"+{metrics['improvement_percentage']:.1f}%"
            )

def download_section():
    """Секция скачивания результатов"""
    st.subheader("Скачать результаты")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Скачивание Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            st.session_state.processed_data.to_excel(writer, index=False, sheet_name='Обработанные данные')
        output.seek(0)
        
        st.download_button(
            label="📥 Скачать Excel",
            data=output,
            file_name=f"обработанные_данные_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        # Скачивание CSV
        csv_data = st.session_state.processed_data.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Скачать CSV",
            data=csv_data,
            file_name=f"обработанные_данные_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

def dictionary_management():
    """Управление словарем брендов"""
    st.title("📚 Управление словарем брендов")
    
    detector = st.session_state.detector
    
    # Текущий словарь
    st.subheader("Текущий словарь брендов")
    
    if not detector.brand_dict:
        st.info("Словарь брендов пуст. Добавьте первый бренд.")
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
    st.subheader("Добавить или изменить бренд")
    
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
                st.success(f"Бренд '{brand_name}' добавлен!")
                st.rerun()
            else:
                st.warning("Заполните название бренда и ключевые слова")
    
    with col2:
        if st.button("🔄 Обновить бренд", use_container_width=True):
            if brand_name and keywords_input:
                if brand_name in detector.brand_dict:
                    keywords = [k.strip() for k in keywords_input.split(',')]
                    detector.brand_dict[brand_name] = keywords
                    st.success(f"Бренд '{brand_name}' обновлен!")
                    st.rerun()
                else:
                    st.warning(f"Бренд '{brand_name}' не найден в словаре")
            else:
                st.warning("Заполните название бренда и ключевые слова")
    
    with col3:
        if st.button("🗑️ Удалить бренд", use_container_width=True):
            if brand_name and brand_name in detector.brand_dict:
                del detector.brand_dict[brand_name]
                st.success(f"Бренд '{brand_name}' удален!")
                st.rerun()
            else:
                st.warning("Введите название существующего бренда")
    
    # Импорт/экспорт словаря
    st.subheader("Импорт/экспорт словаря")
    
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
                st.success("Словарь успешно импортирован!")
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка при импорте: {str(e)}")

def analytics_and_logs():
    """Аналитика и логирование"""
    st.title("📊 Аналитика и логирование")
    
    detector = st.session_state.detector
    
    if not detector.logs:
        st.info("Логи обработки пока отсутствуют. Обработайте данные на главной странице.")
        return
    
    # Метрики производительности
    st.subheader("Метрики обработки")
    
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
    st.subheader("Эффективность ключевых слов")
    
    if detector.logs:
        # Анализ логов
        log_df = pd.DataFrame(detector.logs)
        keyword_usage = log_df['keyword'].value_counts().reset_index()
        keyword_usage.columns = ['keyword', 'count']
        
        # График использования ключевых слов
        fig = px.bar(
            keyword_usage.head(10),
            x='keyword',
            y='count',
            title="Топ-10 самых частых ключевых слов"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Распределение по брендам
        brand_usage = log_df['brand'].value_counts().reset_index()
        brand_usage.columns = ['brand', 'count']
        
        fig2 = px.pie(
            brand_usage,
            values='count',
            names='brand',
            title="Распределение найденных брендов"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Детальные логи
    st.subheader("Детальные логи обработки")
    
    log_df = pd.DataFrame(detector.logs)
    if not log_df.empty:
        log_df['timestamp'] = log_df['timestamp'].dt.strftime('%H:%M:%S')
        st.dataframe(log_df[['timestamp', 'row_index', 'brand', 'keyword', 'text_snippet']], 
                    use_container_width=True)
        
        # Поиск по логам
        search_term = st.text_input("Поиск по логам")
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
    init_session_state()
    
    # Боковая панель навигации
    with st.sidebar:
        st.title("🛍️ Brand Detector")
        st.write("---")
        
        page = st.radio(
            "Навигация",
            ["Главная", "Управление словарем", "Аналитика и логи"],
            icons=["🏠", "📚", "📊"]
        )
        
        st.write("---")
        st.write("**Статистика:**")
        
        detector = st.session_state.detector
        st.write(f"Брендов в словаре: {len(detector.brand_dict)}")
        
        total_keywords = sum(len(keywords) for keywords in detector.brand_dict.values())
        st.write(f"Ключевых слов: {total_keywords}")
        
        if detector.logs:
            st.write(f"Логов обработки: {len(detector.logs)}")
    
    # Отображение выбранной страницы
    if page == "Главная":
        main_page()
    elif page == "Управление словарем":
        dictionary_management()
    elif page == "Аналитика и логи":
        analytics_and_logs()

if __name__ == "__main__":
    main()