import argparse
from datetime import datetime
from helpers.parser import parse_series_by_month, parse_previous_months
from helpers.database import save_to_database

def main():
    parser = argparse.ArgumentParser(description='Парсинг данных о сериалах')
    parser.add_argument('--year', type=int, help='Год для парсинга')
    parser.add_argument('--month', type=int, help='Месяц для парсинга')
    parser.add_argument('--months-back', type=int, default=6, 
                       help='Количество предыдущих месяцев для парсинга')
    
    args = parser.parse_args()
    
    if args.year and args.month:
        # Парсинг конкретного месяца
        print(f"Парсинг данных за {args.year}-{args.month:02d}")
        series_data = parse_series_by_month(args.year, args.month)
    else:
        # Парсинг нескольких предыдущих месяцев
        print(f"Парсинг данных за последние {args.months_back} месяцев")
        series_data = parse_previous_months(args.months_back)
    
    if series_data:
        save_to_database(series_data)
        print(f"Успешно сохранено {len(series_data)} сериалов в базу данных")
    else:
        print("Не удалось получить данные")

if __name__ == "__main__":
    main()