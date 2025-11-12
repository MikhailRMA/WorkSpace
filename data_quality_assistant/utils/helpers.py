import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

def load_sample_data():
    """Генерация демо-данных для тестирования"""
    fake = Faker('ru_RU')
    np.random.seed(42)
    
    data = []
    for i in range(100):
        # Создаем реалистичные данные с преднамеренными проблемами качества
        row = {
            'id': i + 1,
            'customer_name': fake.name(),
            'email': fake.email() if random.random() > 0.1 else None,  # 10% пропусков
            'age': max(18, min(80, int(np.random.normal(35, 10))) if random.random() > 0.05 else None,  # 5% пропусков
            'city': fake.city(),
            'salary': max(20000, np.random.normal(50000, 20000)) if random.random() > 0.08 else None,  # 8% пропусков
            'purchase_amount': max(0, np.random.normal(1000, 500)),
            'last_purchase': fake.date_between(start_date='-2y', end_date='today'),
            'customer_segment': random.choice(['A', 'B', 'C', 'D', None]),  # Некоторые пропуски
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    return df

def generate_python_code(steps, df_name='df'):
    """Генерация Python кода на основе выполненных шагов"""
    code_lines = [
        "import pandas as pd",
        "import numpy as np",
        "",
        f"# Обработка данных для {df_name}",
        f"{df_name}_processed = {df_name}.copy()",
        ""
    ]
    
    for i, step in enumerate(steps, 1):
        code_lines.append(f"# Шаг {i}: {step['description']}")
        code_lines.append(step['code'])
        code_lines.append("")
    
    code_lines.append(f"# Результат: {df_name}_processed")
    
    return "\n".join(code_lines)