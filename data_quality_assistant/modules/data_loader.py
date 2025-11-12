import streamlit as st
import pandas as pd
import io

def load_data_module():
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h2 style='color: #1e3a8a; margin-bottom: 0.5rem;'>📁 Загрузка данных</h2>
        <p style='color: #64748b;'>Начните работу с загрузки ваших данных или используйте демо-набор для обучения</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Две колонки для загрузки
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Карточка загрузки файла
        with st.container():
            st.markdown("### 📤 Загрузите ваш файл")
            
            uploaded_file = st.file_uploader(
                "Перетащите файл сюда или нажмите для выбора",
                type=['csv', 'xlsx'],
                help="Поддерживаются CSV и Excel файлы до 200MB",
                label_visibility="collapsed"
            )
            
            if uploaded_file is not None:
                try:
                    # Индикатор загрузки
                    with st.spinner("Обрабатываем ваши данные..."):
                        if uploaded_file.name.endswith('.csv'):
                            df = pd.read_csv(uploaded_file)
                        else:
                            df = pd.read_excel(uploaded_file)
                    
                    st.session_state.df = df
                    st.session_state.df_clean = df.copy()
                    st.session_state.processing_steps = []
                    
                    # Успешная загрузка
                    st.success(f"""
                    **✅ Данные успешно загружены!**
                    
                    - **Файл:** {uploaded_file.name}
                    - **Размер:** {df.shape[0]} строк, {df.shape[1]} столбцов
                    - **Объем:** {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB
                    """)
                    
                    # Быстрый переход к обзору
                    if st.button("🚀 Перейти к обзору данных", use_container_width=True):
                        st.session_state.current_module = "👀 Обзор данных"
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"**❌ Ошибка при загрузке:** {str(e)}")
    
    with col2:
        # Информационная панель
        st.markdown("### 💡 Советы")
        
        tips = [
            "📝 **Поддерживаемые форматы:** CSV, Excel",
            "🔍 **Проверьте:** что файл содержит заголовки столбцов", 
            "⚡ **Рекомендация:** для начала используйте демо-данные",
            "📚 **Обучение:** каждый шаг сопровождается пояснениями"
        ]
        
        for tip in tips:
            st.markdown(f"<div style='padding: 0.5rem 0;'>{tip}</div>", unsafe_allow_html=True)
        
        # Демо-данные
        st.markdown("---")
        st.markdown("### 🎓 Обучающий набор")
        st.markdown("""
        Попробуйте наш демо-набор данных, чтобы познакомиться с инструментом:
        - 📊 Реалистичные бизнес-данные
        - 🔍 Примеры типичных проблем качества
        - 🎯 Готовые сценарии анализа
        """)
    
    # Если данные загружены, показываем быстрый превью
    if st.session_state.df is not None:
        st.markdown("---")
        st.markdown("### 👀 Быстрый просмотр")
        
        df = st.session_state.df
        
        # Мини-метрики
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Строки", df.shape[0])
        with col2:
            st.metric("Столбцы", df.shape[1])
        with col3:
            missing_total = df.isnull().sum().sum()
            st.metric("Пропуски", missing_total)
        with col4:
            duplicates = df.duplicated().sum()
            st.metric("Дубликаты", duplicates)
        
        # Превью таблицы
        with st.expander("📋 Посмотреть первые 5 строк"):
            st.dataframe(df.head(), use_container_width=True)

def get_data_info(df):
    """Возвращает базовую информацию о данных"""
    if df is None:
        return None
    
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    
    return {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'info': info_str,
        'memory_usage': df.memory_usage(deep=True).sum()
    }