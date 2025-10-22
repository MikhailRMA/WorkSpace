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

│ ├── 1_revenue.csv # Общая выручка

│ ├── 2_monthly_revenue.csv # Выручка по месяцам

│ ├── 3_daily_revenue.csv # Выручка по дням

│ ├── 4_country_revenue.csv # Выручка по странам

│ ├── 5_repeat_customers.csv # Анализ повторных покупок

│ ├── 6_top10_customers.csv # Топ-10 клиентов

│ ├── 7_top10_product.csv # Топ-10 товаров по продажам

│ ├── 8_top_profit_product.csv # Топ товаров по прибыли

│ ├── 9_top_category.csv # Топ категорий

│ ├── 10_avg_check.csv # Средний чек

│ └── 11_seasonality.csv # Сезонность продаж

└── 

│   Analytical_report.md #Аналитический отчет

└── data_dictionary.md # Описание данных



