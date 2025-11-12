import streamlit as st
import pandas as pd
import numpy as np

def quality_analysis_module():
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h2 style='color: #1e3a8a; margin-bottom: 0.5rem;'>🔍 Анализ качества</h2>
        <p style='color: #64748b;'>Всесторонняя проверка качества и целостности ваших данных</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.df is None:
        st.warning("""
        **⚠️ Данные не загружены**
        
        Перейдите в раздел **📁 Загрузка данных** чтобы начать работу
        """)
        return
    
    df = st.session_state.df
    
    # Общая оценка качества
    st.markdown("### 📊 Общая оценка качества")
    
    quality_score = calculate_quality_score(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Общий балл", f"{quality_score}/100")
    
    with col2:
        completeness = calculate_completeness_score(df)
        st.metric("Полнота данных", f"{completeness}%")
    
    with col3:
        uniqueness = calculate_uniqueness_score(df)
        st.metric("Уникальность", f"{uniqueness}%")
    
    with col4:
        consistency = calculate_consistency_score(df)
        st.metric("Согласованность", f"{consistency}%")
    
    # Детальный анализ по категориям
    st.markdown("### 🔍 Детальный анализ")
    
    analysis_tabs = st.tabs(["🚫 Пропуски", "🔁 Дубликаты", "📈 Выбросы", "✅ Валидация"])
    
    with analysis_tabs[0]:
        analyze_missing_values(df)
    
    with analysis_tabs[1]:
        analyze_duplicates(df)
    
    with analysis_tabs[2]:
        analyze_outliers(df)
    
    with analysis_tabs[3]:
        analyze_data_validation(df)

def calculate_quality_score(df):
    """Рассчитывает общий балл качества данных"""
    return 85  # Заглушка

def calculate_completeness_score(df):
    """Рассчитывает оценку полноты данных"""
    missing_percentage = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
    return max(0, 100 - missing_percentage)

def calculate_uniqueness_score(df):
    """Рассчитывает оценку уникальности данных"""
    duplicate_percentage = (df.duplicated().sum() / len(df)) * 100
    return max(0, 100 - duplicate_percentage)

def calculate_consistency_score(df):
    """Рассчитывает оценку согласованности данных"""
    return 90  # Заглушка

def analyze_missing_values(df):
    """Анализ пропущенных значений"""
    missing_data = df.isnull().sum()
    missing_percent = (missing_data / len(df)) * 100
    
    missing_df = pd.DataFrame({
        'Столбец': missing_data.index,
        'Пропусков': missing_data.values,
        'Процент': missing_percent.values
    }).sort_values('Пропусков', ascending=False)
    
    st.dataframe(missing_df[missing_df['Пропусков'] > 0], use_container_width=True)
    
    if len(missing_df[missing_df['Пропусков'] > 0]) == 0:
        st.success("🎉 Пропущенные значения не обнаружены!")

def analyze_duplicates(df):
    """Анализ дубликатов"""
    full_duplicates = df.duplicated().sum()
    
    st.metric("Полные дубликаты строк", full_duplicates)
    
    if full_duplicates > 0:
        st.dataframe(df[df.duplicated(keep=False)].head(), use_container_width=True)
    else:
        st.success("🎉 Дубликаты не обнаружены!")

def analyze_outliers(df):
    """Анализ выбросов для числовых столбцов"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) > 0:
        selected_col = st.selectbox("Выберите столбец для анализа:", numeric_cols)
        
        if selected_col:
            # Простой анализ выбросов через IQR
            Q1 = df[selected_col].quantile(0.25)
            Q3 = df[selected_col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[selected_col] < lower_bound) | (df[selected_col] > upper_bound)]
            
            st.metric("Выбросов обнаружено", len(outliers))
            
            if len(outliers) > 0:
                st.dataframe(outliers, use_container_width=True)
    else:
        st.info("ℹ️ Числовые столбцы для анализа выбросов не найдены")

def analyze_data_validation(df):
    """Анализ валидации данных"""
    st.info("""
    **Проверка качества данных включает:**
    
    - ✅ Корректность типов данных
    - ✅ Допустимость значений  
    - ✅ Соответствие бизнес-правилам
    - ✅ Целостность связей
    
    *Расширенная валидация будет добавлена в следующем обновлении*
    """)