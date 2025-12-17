# 📊 Sales Performance Dashboard | Power BI

Интерактивный дашборд для анализа прибыльности продаж, клиентской базы и эффективности менеджеров.

## 🚀 Демо

![Dashboard Preview](https://github.com/MikhailRMA/WorkSpace/blob/main/Analys_dashbord_PowerBI/Screenshoot.png)  


## 📁 Проект в цифрах

- **Таблиц в модели:** 5
- **DAX-мер:** 15+
- **Визуализаций:** 12
- **Этапов в Power Query:** 8

## 🛠️ Стек технологий

- **ETL:** Power Query (M Language)
- **Визуализация:** Power BI
- **Язык запросов:** DAX
- **Контроль версий:** Git / GitHub

## 📈 Ключевые метрики (DAX)

```dax
Revenue = SUM(Sales[Amount])
Profit = [Revenue] - SUM(Sales[Cost])
Margin = DIVIDE([Profit], [Revenue], 0)
Avg Check = DIVIDE([Revenue], DISTINCTCOUNT(Sales[OrderID]))
Logistics Cost = SUM(Costs[Delivery])
```
## 🔧 Data Pipeline
Raw Data → Power Query → Star Schema → DAX Measures → Interactive Dashboard

## 📊 Основные визуализации
| Визуализация	| Назначение	| Фичи |
| --- | --- | --- |
| KPI Cards	| Сводка по метрикам	| Conditional formatting |
| Time Series Chart	| Динамика продаж	| YoY сравнение |
| Drill-down Bar Chart	| Анализ по товарам | Категория → Подкатегория → Товар |
| Map Visualization	| География продаж	| Интеграция с Bing Maps |
| ABC Analysis Table	| Ранжирование товаров	| Pareto (80/20) |
| Problem Managers Table	| Выявление убытков	| Фильтр по отрицательной прибыли |

## 📚 Что я освоил в этом проекте
#### Data Cleaning: Работа с пропусками, дубликатами, типами данных

#### Data Modeling: Создание звездообразной схемы, календарной таблицы

#### DAX: Расчетные меры, функции времени, ранжирование

#### UI/UX: Проектирование интуитивного дашборда


#### Business Analysis: ABC-анализ, выявление проблемных зон
