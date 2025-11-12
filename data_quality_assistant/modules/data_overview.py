import streamlit as st
import pandas as pd
import numpy as np

def overview_module():
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h2 style='color: #1e3a8a; margin-bottom: 0.5rem;'>👀 Обзор данных</h2>
        <p style='color: #64748b;'>Изучите структуру и основные характеристики ваших данных</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.df is None:
        st.warning("""
        **⚠️ Данные не загружены**
        
        Перейдите в раздел **📁 Загрузка данных** чтобы начать работу
        """)
        return
    
    df = st.session_state.df
    
    # Основные метрики в красивом оформлении
    st.markdown("### 📊 Основные показатели")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Всего строк", 
            value=df.shape[0],
            help="Количество записей в данных"
        )
    with col2:
        st.metric(
            label="Всего столбцов", 
            value=df.shape[1],
            help="Количество характеристик в данных"
        )
    with col3:
        st.metric(
            label="Объем памяти", 
            value=f"{df.memory_usage(deep=True).sum() / 1024**2:.1f} MB",
            help="Размер данных в памяти"
        )
    with col4:
        st.metric(
            label="Полных дубликатов", 
            value=df.duplicated().sum(),
            help="Количество полностью одинаковых строк"
        )
    
    # Вкладки для разного типа информации
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Просмотр данных", "🔧 Структура", "📈 Статистика", "📚 Обучение"])
    
    with tab1:
        st.markdown("#### Предварительный просмотр")
        
        preview_col1, preview_col2 = st.columns([1, 1])
        
        with preview_col1:
            st.markdown("**Первые 10 строк:**")
            st.dataframe(df.head(10), use_container_width=True, height=300)
        
        with preview_col2:
            st.markdown("**Случайная выборка:**")
            st.dataframe(df.sample(min(10, len(df))), use_container_width=True, height=300)
    
    with tab2:
        st.markdown("#### Информация о столбцах")
        
        # Детальная информация о столбцах
        col_info = pd.DataFrame({
            'Столбец': df.columns,
            'Тип данных': df.dtypes.values,
            'Непустых значений': df.count().values,
            'Уникальных значений': [df[col].nunique() for col in df.columns],
            'Пропущенных значений': df.isnull().sum().values
        })
        
        st.dataframe(col_info, use_container_width=True)
    
    with tab3:
        st.markdown("#### Статистика по числовым данным")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)
        else:
            st.info("""
            **ℹ️ Числовые данные не найдены**
            
            В ваших данных нет числовых столбцов для статистического анализа.
            """)
    
    with tab4:
        st.markdown("#### 📚 Почему важен обзор данных?")
        
        educational_content = [
            {
                "title": "🎯 Понимание структуры",
                "content": "Помогает понять какие данные доступны и как они организованы"
            },
            {
                "title": "🔍 Выявление проблем", 
                "content": "Позволяет быстро найти пропуски, аномалии и некорректные типы"
            },
            {
                "title": "📋 Планирование анализа",
                "content": "Определяет какие методы и подходы можно применить к данным"
            },
            {
                "title": "⚡ Оценка качества",
                "content": "Показывает достаточно ли данных для решения вашей задачи"
            }
        ]
        
        for item in educational_content:
            with st.expander(f"**{item['title']}**"):
                st.write(item['content'])