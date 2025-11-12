 # 🎬 Series Tracker - ETL Pipeline для анализа сериалов

>  ETL система для сбора и анализа данных о сериалах с полным циклом от парсинга до автоматизированной отчетности

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Airflow](https://img.shields.io/badge/Apache-Airflow-017CEE?logo=apacheairflow)](https://airflow.apache.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker)](https://docker.com)

## 📊 О чем этот проект?

Реальная ETL система, которая:
- **Ежемесячно парсит** 100+ сериалов с Kino.Mail.ru
- **Автоматически обновляет** базу данных PostgreSQL  
- **Отправляет аналитические отчеты** на email
- **Работает в Docker** с оркестрацией через Airflow

## Разработана полноценная аналитическая система, которая решает реальные задачи

## 📊 Пример отчета

### HTML версия
[monthly_report_2024_11.html](https://github.com/MikhailRMA/WorkSpace/blob/main/series_tracker_project/examples/demo_report.html) - полный интерактивный отчет

## 🛠 Технологический стек

# Основные технологии:
- Python 3.13 (пакеты: selenium, beautifulsoup4, pandas, sqlalchemy)
- Apache Airflow 2.7+ (оркестрация ETL процессов)
- PostgreSQL 13 (хранение и анализ данных)
- Docker + Docker Compose (контейнеризация)

# Ключевые навыки:
- ETL/ELT пайплайны
- Парсинг веб-данных
- Проектирование БД
- Автоматизация процессов

## 📈 Что можно проанализировать?
Система собирает богатый набор данных для анализа:

📅 Динамика премьер по времени

🌍 География производства сериалов

⭐ Распределение рейтингов

🎭 Популярность жанров

## 🔧 Архитектура проекта

series_tracker_project/

├── dags/                               # Airflow ETL пайплайны

│   ├── series_etl_dag.py               # парсинг предыдущиг месяцев    

│   ├── monthly report.py               # Основной DAG с ежемесячным отчетом

│   └── helpers/                        # Вспомогательные модули

│       ├── helpers_database.py

│       ├── helpers_email_sender.py

│       ├── helpers_parser.py

│       └── parser_previous_months.py

├── requirements.txt

├──  .env

├──  README.md

├──  manager.bat                          # запуск airflow, posgres

├──  create_project.bat                   # создание архетиктуры проекта 

├──  init_connections.py                  # инициализация подключения к бд

├── docker-compose-postgres.yml           # Конфигурация сервисов

└── docker-compose-airflow.yml            # Конфигурация сервисов


## Ключевые компоненты:

`helpers_parser.py` - умный парсинг с обработкой ошибок

`helpers_database.py` - работа с PostgreSQL и миграциями

`helpers_email_sender.py` - генерация и отправка отчетов

## 🎯 Чем горжусь в этом проекте
- Реальное использование - системой пользуются коллеги для отслеживания новинок

- Production качество - обработка ошибок, логирование, мониторинг

- Масштабируемость - легко добавить новые источники данных

- Полный цикл - от сырых данных до готовой аналитики

## 🚧 Что планирую улучшить
- ML-рекомендации на основе предпочтений

- Telegram-бот для уведомлений о выходе серий

- Дашборд с визуализацией в Grafana

- Прогнозирование рейтингов сериалов

## Сложности: 
- Обработка JavaScript-рендеринга
- Вынужденный переход на парсинг с chromium