import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Конфигурация страницы
st.set_page_config(
    page_title="Data Quality Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Собственные стили - минимальные
st.markdown("""
<style>
    .main-header {
        font-size: 28px;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 10px;
    }
    .section-header {
        font-size: 20px;
        font-weight: 500;
        color: #34495e;
        margin: 20px 0 10px 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #3498db;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 15px;
        border-radius: 6px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

class DataQualityApp:
    def __init__(self):
        self.df = None
        self.current_view = "upload"
        
    def init_session_state(self):
        if 'data' not in st.session_state:
            st.session_state.data = None
        if 'analysis_done' not in st.session_state:
            st.session_state.analysis_done = False
    
    def render_sidebar(self):
        with st.sidebar:
            st.markdown("### Навигация")
            
            views = {
                "📥 Загрузить": "upload",
                "👁️ Просмотр": "view", 
                "🔍 Анализ": "analyze",
                "🛠️ Очистка": "clean",
                "📊 Отчет": "report"
            }
            
            for name, key in views.items():
                if st.button(name, use_container_width=True, key=f"btn_{key}"):
                    self.current_view = key
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### Статус")
            if st.session_state.data is not None:
                st.success("✅ Данные загружены")
                st.info(f"📊 {len(st.session_state.data)} строк, {len(st.session_state.data.columns)} столбцов")
            else:
                st.warning("❌ Нет данных")
    
    def upload_view(self):
        st.markdown('<div class="main-header">Загрузка данных</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader("Выберите CSV или Excel файл", type=['csv', 'xlsx'])
            
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        self.df = pd.read_csv(uploaded_file)
                    else:
                        self.df = pd.read_excel(uploaded_file)
                    
                    st.session_state.data = self.df
                    st.success(f"Загружено: {self.df.shape[0]} строк, {self.df.shape[1]} столбцов")
                    
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
        
        with col2:
            st.markdown("**Быстрый старт**")
            if st.button("Тестовые данные", use_container_width=True):
                # Простые тестовые данные
                np.random.seed(42)
                dates = pd.date_range('2023-01-01', periods=100)
                self.df = pd.DataFrame({
                    'date': dates,
                    'sales': np.random.normal(1000, 200, 100),
                    'customers': np.random.randint(50, 200, 100),
                    'region': np.random.choice(['Север', 'Юг', 'Восток', 'Запад'], 100),
                    'product': np.random.choice(['A', 'B', 'C'], 100)
                })
                # Добавляем немного пропусков
                self.df.loc[10:15, 'sales'] = None
                st.session_state.data = self.df
                st.success("Тестовые данные созданы")
    
    def view_view(self):
        if st.session_state.data is None:
            st.warning("Сначала загрузите данные")
            return
            
        st.markdown('<div class="main-header">Просмотр данных</div>', unsafe_allow_html=True)
        
        df = st.session_state.data
        
        # Быстрая статистика
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Строки", df.shape[0])
        with col2:
            st.metric("Столбцы", df.shape[1])
        with col3:
            st.metric("Пропуски", df.isna().sum().sum())
        with col4:
            st.metric("Дубликаты", df.duplicated().sum())
        
        # Просмотр данных
        st.markdown('<div class="section-header">Данные</div>', unsafe_allow_html=True)
        
        view_option = st.radio("Вид:", ["Первые 10", "Последние 10", "Случайные 10"], horizontal=True)
        
        if view_option == "Первые 10":
            st.dataframe(df.head(10), use_container_width=True)
        elif view_option == "Последние 10":
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.dataframe(df.sample(10), use_container_width=True)
        
        # Информация о столбцах
        st.markdown('<div class="section-header">Информация о столбцах</div>', unsafe_allow_html=True)
        
        col_info = []
        for col in df.columns:
            col_info.append({
                'Столбец': col,
                'Тип': str(df[col].dtype),
                'Непустых': df[col].count(),
                'Уникальных': df[col].nunique()
            })
        
        st.dataframe(pd.DataFrame(col_info), use_container_width=True)
    
    def analyze_view(self):
        if st.session_state.data is None:
            st.warning("Сначала загрузите данные")
            return
            
        st.markdown('<div class="main-header">Анализ качества</div>', unsafe_allow_html=True)
        
        df = st.session_state.data
        
        # Анализ пропусков
        st.markdown('<div class="section-header">Пропущенные значения</div>', unsafe_allow_html=True)
        
        missing_data = df.isna().sum()
        missing_percent = (missing_data / len(df)) * 100
        
        missing_df = pd.DataFrame({
            'Столбец': missing_data.index,
            'Пропусков': missing_data.values,
            '%': missing_percent.values
        })
        
        # Показываем только столбцы с пропусками
        missing_with_data = missing_df[missing_df['Пропусков'] > 0]
        
        if len(missing_with_data) > 0:
            st.dataframe(missing_with_data, use_container_width=True)
            
            # Визуализация пропусков
            st.bar_chart(missing_with_data.set_index('Столбец')['%'])
        else:
            st.success("Пропущенных значений не найдено")
        
        # Анализ дубликатов
        st.markdown('<div class="section-header">Дубликаты</div>', unsafe_allow_html=True)
        
        duplicates = df.duplicated().sum()
        st.metric("Полных дубликатов", duplicates)
        
        if duplicates > 0:
            st.dataframe(df[df.duplicated()].head(), use_container_width=True)
        
        # Быстрый анализ числовых данных
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            st.markdown('<div class="section-header">Числовые данные</div>', unsafe_allow_html=True)
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)
    
    def clean_view(self):
        if st.session_state.data is None:
            st.warning("Сначала загрузите данные")
            return
            
        st.markdown('<div class="main-header">Очистка данных</div>', unsafe_allow_html=True)
        
        df = st.session_state.data
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Обработка пропусков**")
            
            missing_cols = df.columns[df.isna().any()].tolist()
            if missing_cols:
                selected_col = st.selectbox("Столбец:", missing_cols)
                
                method = st.selectbox("Метод:", ["Удалить строки", "Заполнить нулями", "Заполнить средним"])
                
                if st.button("Применить", key="clean_missing"):
                    st.info("Функция очистки будет реализована")
            else:
                st.info("Нет столбцов с пропусками")
        
        with col2:
            st.markdown("**Удаление дубликатов**")
            
            duplicates = df.duplicated().sum()
            st.write(f"Найдено дубликатов: {duplicates}")
            
            if duplicates > 0:
                if st.button("Удалить дубликаты", use_container_width=True):
                    # Простая логика удаления дубликатов
                    clean_df = df.drop_duplicates()
                    st.session_state.data = clean_df
                    st.success(f"Удалено {duplicates} дубликатов")
                    st.rerun()
    
    def report_view(self):
        if st.session_state.data is None:
            st.warning("Сначала загрузите данные")
            return
            
        st.markdown('<div class="main-header">Отчет</div>', unsafe_allow_html=True)
        
        df = st.session_state.data
        
        # Простой отчет
        st.markdown("### Сводка по данным")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Основные метрики**")
            st.write(f"- Всего строк: {df.shape[0]}")
            st.write(f"- Всего столбцов: {df.shape[1]}")
            st.write(f"- Пропущенных значений: {df.isna().sum().sum()}")
            st.write(f"- Дубликатов: {df.duplicated().sum()}")
        
        with col2:
            st.markdown("**Типы данных**")
            for dtype in df.dtypes.unique():
                count = (df.dtypes == dtype).sum()
                st.write(f"- {dtype}: {count} столбцов")
        
        # Экспорт
        st.markdown("### Экспорт")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Скачать CSV",
                csv,
                "cleaned_data.csv",
                "text/csv"
            )
        
        with col2:
            st.download_button(
                "Скачать отчет",
                self.generate_text_report(df),
                "data_report.txt",
                "text/plain"
            )
    
    def generate_text_report(self, df):
        report = f"""
Отчет анализа данных
Сгенерирован: {datetime.now().strftime('%Y-%m-%d %H:%M')}

ОСНОВНАЯ ИНФОРМАЦИЯ:
- Строк: {df.shape[0]}
- Столбцов: {df.shape[1]}
- Пропусков: {df.isna().sum().sum()}
- Дубликатов: {df.duplicated().sum()}

СТОЛБЦЫ:
"""
        for col in df.columns:
            report += f"- {col}: {df[col].dtype}, уникальных: {df[col].nunique()}\n"
        
        return report
    
    def run(self):
        self.init_session_state()
        
        # Верхняя навигация
        st.markdown('<div class="main-header">Data Quality Tool</div>', unsafe_allow_html=True)
        
        # Основной контент
        if self.current_view == "upload":
            self.upload_view()
        elif self.current_view == "view":
            self.view_view()
        elif self.current_view == "analyze":
            self.analyze_view()
        elif self.current_view == "clean":
            self.clean_view()
        elif self.current_view == "report":
            self.report_view()

# Запуск приложения
if __name__ == "__main__":
    app = DataQualityApp()
    app.run()