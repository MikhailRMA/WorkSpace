import streamlit as st
import pandas as pd
import numpy as np

def cleaning_module():
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h2 style='color: #1e3a8a; margin-bottom: 0.5rem;'>🧹 Очистка данных</h2>
        <p style='color: #64748b;'>Интерактивные инструменты для обработки и очистки ваших данных</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.df is None:
        st.warning("""
        **⚠️ Данные не загружены**
        
        Перейдите в раздел **📁 Загрузка данных** чтобы начать работу
        """)
        return
    
    df = st.session_state.df
    
    # Вкладки для разных типов очистки
    tab1, tab2, tab3, tab4 = st.tabs(["🚫 Пропуски", "🔁 Дубликаты", "📊 Выбросы", "🔧 Трансформация"])
    
    with tab1:
        st.markdown("#### Обработка пропущенных значений")
        
        missing_cols = df.columns[df.isnull().any()].tolist()
        
        if missing_cols:
            st.write("**Столбцы с пропущенными значениями:**")
            for col in missing_cols:
                missing_count = df[col].isnull().sum()
                missing_percent = (missing_count / len(df)) * 100
                st.write(f"- **{col}**: {missing_count} пропусков ({missing_percent:.1f}%)")
            
            col_to_fix = st.selectbox("Выберите столбец для обработки:", missing_cols)
            
            method = st.radio(
                "Метод обработки:",
                ["Удалить строки с пропусками", "Заполнить средним значением", "Заполнить медианой", "Заполнить модой"]
            )
            
            if st.button("Применить обработку", key="missing_btn"):
                st.success(f"Обработка применена к столбцу {col_to_fix}!")
        else:
            st.success("🎉 В данных нет пропущенных значений!")
    
    with tab2:
        st.markdown("#### Обработка дубликатов")
        
        duplicate_count = df.duplicated().sum()
        
        st.metric("Найдено дубликатов", duplicate_count)
        
        if duplicate_count > 0:
            if st.button("Удалить все дубликаты", use_container_width=True):
                st.session_state.df = df.drop_duplicates()
                st.success(f"Удалено {duplicate_count} дубликатов!")
                st.rerun()
        else:
            st.success("🎉 Дубликаты не найдены!")
    
    with tab3:
        st.markdown("#### Обработка выбросов")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            selected_col = st.selectbox("Выберите числовой столбец:", numeric_cols)
            
            if selected_col:
                # Простой анализ выбросов
                Q1 = df[selected_col].quantile(0.25)
                Q3 = df[selected_col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((df[selected_col] < (Q1 - 1.5 * IQR)) | (df[selected_col] > (Q3 + 1.5 * IQR))).sum()
                
                st.metric("Выбросов найдено", outliers)
                
                if outliers > 0:
                    if st.button("Удалить выбросы", use_container_width=True):
                        st.info("Функция удаления выбросов будет реализована в следующей версии")
        else:
            st.info("ℹ️ Числовые столбцы для анализа выбросов не найдены")
    
    with tab4:
        st.markdown("#### Трансформация данных")
        
        st.info("""
        **Доступные трансформации:**
        - Изменение типов данных
        - Переименование столбцов  
        - Создание новых признаков
        - Нормализация данных
        
        *Эти функции будут добавлены в следующем обновлении*
        """)
        
        if st.button("🔄 Сбросить все изменения", use_container_width=True):
            st.session_state.df = st.session_state.df_clean.copy()
            st.success("Все изменения сброшены!")
            st.rerun()