# 🛒 E-commerce SQL Analysis Project

Полный анализ эффективности интернет-магазина с использованием SQL. Проект демонстрирует извлечение бизнес-инсайтов из сырых данных и построение интерактивного дашборда.

## 📊 Демо


**Интерактивный дашборд:** [Tableau Public Dashboard](https://public.tableau.com/app/profile/petr.count/viz/E-com_17609722447200/KPIDashboard)

## 🎯 Цели проекта

- **Анализ ключевых метрик** e-commerce бизнеса 
- **Выявление трендов** и точек роста бизнеса
- **Создание дашборда** для мониторинга показателей

## 📁 Структура проекта
e-com_analysis_sql/
├── data/ # Исходные данные
│ ├── customers.csv
│ ├── products.csv
│ ├── orders.csv
│ └── order_items.csv
├── scripts/
│ ├── 01_create_tables # Создание БД и таблиц
│ ├── 02_import_data # импорт данных
│ ├── 03analysis.sql # Анализ
│ └── tableau_dashboard.twb # Файл дашборда Tableau
├── results/
│ ├── 1 revenue # Экспорт результатов
│ ├── 2 monthly_revenue.csv # Экспорт результатов
│ ├── 3 daily_revenue.csv # Экспорт результатов
│ ├── 4 country_revenue.csv # Экспорт результатов
│ ├── 5 repeat_customers.csv # Экспорт результатов
│ ├── 6 top10_customers.csv # Экспорт результатов
│ ├── 7 top10_product.csv # Экспорт результатов
│ ├── 8 top_profit_product.csv # Экспорт результатов
│ ├── 9 top_category.csv # Экспорт результатов
│ ├── 10 avg_check.csv # Экспорт результатов
│ └── 11 seasonality.csv # Экспорт результатов
└── 
│   Analytical_report.md #Аналитический отчет
└── data_dictionary.md # Описание данных

