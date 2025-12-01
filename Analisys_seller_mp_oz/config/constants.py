from pathlib import Path

# Базовые пути с использованием pathlib
PROJECT_ROOT = Path(__file__).parent.parent  # Папка проекта
DATA_RAW = PROJECT_ROOT / 'data' / 'raw'
DATA_PROCESSED = PROJECT_ROOT / 'data' / 'processed'

# Пути к файлам
PRODUCTS_PATH = DATA_RAW / 'anonymous_seller_product.csv'
SALES_PATH = DATA_RAW / 'anonymous_oz_sales_data.csv'
PROCESSED_DATA_PATH = DATA_PROCESSED / 'merged_data.csv'

# Параметры анализа
ABC_THRESHOLDS = [0.8, 0.95]  # A: 0-80%, B: 80-95%, C: 95-100%
XYZ_THRESHOLDS = [0.1, 0.25]  # X: CV<0.1, Y: 0.1<=CV<0.25, Z: CV>=0.25

# Цветовые схемы для визуализаций
COLORS = {
    'abc': {'A': '#FF6B6B', 'B': '#4ECDC4', 'C': '#45B7D1'},
    'xyz': {'X': '#96CEB4', 'Y': '#FFEAA7', 'Z': '#DDA0DD'},
    'segments': {'Champions': '#2E86AB', 'Loyal': '#A23B72', 'Potential': '#F18F01'}
}

# Бизнес-параметры для открытого проекта
SHIPPING_COST_PER_ITEM = 50  # стоимость доставки за единицу
PACKAGING_COST = 30  # стоимость упаковки


