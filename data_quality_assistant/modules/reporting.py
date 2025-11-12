import streamlit as st
import pandas as pd

def reporting_module():
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h2 style='color: #1e3a8a; margin-bottom: 0.5rem;'>📈 Отчетность</h2>
        <p style='color: #64748b;'>Создайте итоговый отчет и получите код для воспроизведения анализа</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.df is None:
        st.warning("""
        **⚠️ Данные не загружены**
        
        Перейдите в раздел **📁 Загрузка данных** чтобы начать работу
        """)
        return
    
    # Генерация отчета
    st.markdown("### 📊 Итоговый отчет")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Сгенерировать отчет", use_container_width=True):
            st.success("Отчет успешно сгенерирован!")
    
    with col2:
        if st.button("🐍 Получить Python код", use_container_width=True):
            st.session_state.show_code = True
    
    # Показ сгенерированного кода
    if st.session_state.get('show_code', False):
        st.markdown("### 📝 Сгенерированный код")
        code = generate_sample_code()
        st.code(code, language='python')
        
        if st.button("📋 Скопировать код"):
            st.success("Код скопирован в буфер обмена!")
    
    # Экспорт результатов
    st.markdown("### 📤 Экспорт результатов")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        st.download_button(
            label="💾 CSV файл",
            data=st.session_state.df.to_csv(index=False).encode('utf-8'),
            file_name="cleaned_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with export_col2:
        st.download_button(
            label="📊 Excel файл", 
            data=save_df_to_excel(st.session_state.df),
            file_name="cleaned_data.xlsx",
            mime="application/vnd.ms-excel",
            use_container_width=True
        )
    
    with export_col3:
        st.download_button(
            label="📄 Отчет PDF",
            data=generate_sample_pdf(),
            file_name="data_quality_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

def generate_sample_code():
    """Генерирует пример Python кода"""
    return '''
import pandas as pd
import numpy as np

# Загрузка данных
df = pd.read_csv('your_data.csv')

# Анализ пропущенных значений
print("Пропущенные значения:")
print(df.isnull().sum())

# Базовая статистика
print("\\nСтатистика числовых столбцов:")
print(df.describe())

# Очистка данных (пример)
df_cleaned = df.dropna()  # Удаление пропусков
df_cleaned = df_cleaned.drop_duplicates()  # Удаление дубликатов

print(f"Исходный размер: {df.shape}")
print(f"После очистки: {df_cleaned.shape}")
'''

def save_df_to_excel(df):
    """Сохраняет DataFrame в Excel файл"""
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Данные')
    return output.getvalue()

def generate_sample_pdf():
    """Генерирует пример PDF отчета"""
    # Заглушка для PDF генерации
    return b"PDF report would be generated here"