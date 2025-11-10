-- 1 Какова общая выручка и количество заказов?
SELECT 
    COUNT(DISTINCT order_id) as Количество_заказов,
    SUM(revenue) as Общая_выручка,
    ROUND(AVG(revenue), 2) as Средняя_выручка,
    COUNT(DISTINCT customer_id) as Уникальные_покупатели
FROM orders;

-- 2 Как меняется выручка по месяцам?
SELECT 
    TO_CHAR(order_date, 'YYYY-MM') as Месяц,
    COUNT(DISTINCT order_id) as Количество_заказов,
    SUM(revenue) as Месячная_выручка,
    ROUND(AVG(revenue), 2) as Средняя_выручка
FROM orders
GROUP BY TO_CHAR(order_date, 'YYYY-MM')
ORDER BY Месяц;

-- 3 Какие дни недели самые прибыльные?
SELECT 
    TO_CHAR(order_date, 'Day') as День_недели,
    COUNT(DISTINCT order_id) as Количество_заказов,
    SUM(revenue) as Ежедневная_выручка,
    ROUND(AVG(revenue), 2) as Средняя_Выручка
FROM orders
GROUP BY TO_CHAR(order_date, 'Day')
ORDER BY Ежедневная_выручка DESC;

-- 4 Из каких стран наши клиенты и где мы зарабатываем больше?
SELECT
    c.country as Страна,
    ROUND(AVG(o.revenue), 2) as Средний_чек,
    ROUND(
        COUNT(DISTINCT c.customer_id) * 100.0 / 
        (SELECT COUNT(DISTINCT customer_id) FROM customers)
    , 2) as "Доля_покупателей_%"
FROM customers c
JOIN orders o USING(customer_id)
GROUP BY c.country
ORDER BY Общая_выручка DESC;

-- 5 Сколько клиентов возвращаются за второй покупкой?
WITH orders_customer AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) as Количество_заказов
    FROM orders 
    GROUP BY customer_id
)
SELECT 
    CASE 
        WHEN Количество_заказов = 1 THEN 'Однократные'
        WHEN Количество_заказов = 2 THEN 'Двукратные'
        WHEN Количество_заказов >= 3 THEN 'Многократные'  
    END as Типы_покупателей,
    COUNT(*) as Количество_покупателей,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders_customer), 2) as "%_от_общего_количества"
FROM orders_customer
GROUP BY Типы_покупателей
ORDER BY Типы_покупателей;

-- 6 Кто наши самые ценные клиенты?
SELECT 
    c.customer_id,
    c.name,
    c.country,
    COUNT(o.order_id) as Количесво_заказов,
    SUM(o.revenue) as Общая_выручка,
	ROUND((SUM(o.revenue) / SUM(SUM(o.revenue)) OVER()) * 100, 2) as Доля_от_общей_выручки_в_процентах,
    RANK() OVER (ORDER BY SUM(o.revenue) DESC) as Ранг_по_выручке
FROM customers c
JOIN orders o USING (customer_id)
GROUP BY c.customer_id, c.name, c.country
ORDER BY Общая_выручка DESC
LIMIT 10;

-- 7 Какие товары самые популярные?
SELECT 
    p.product_id,
    p.product_name,
    COUNT(oi.order_id) as Количество_покупок,
    SUM(oi.quantity*oi.price) as Выручка
FROM order_items oi
JOIN products  p USING(product_id)
GROUP BY p.product_id
ORDER BY Количество_покупок DESC
LIMIT 10;

-- 8 Какие товары приносят больше всего денег?
SELECT 
    p.product_id,
    p.product_name,
    SUM(oi.quantity*oi.price) as Выручка
FROM order_items oi
JOIN products  p USING(product_id)
GROUP BY p.product_id
ORDER BY Выручка DESC
LIMIT 10;

-- 9 Какие категории товаров самые прибыльные?
SELECT
    p.category,
    ROUND(AVG(p.price),2) as Средняя_цена,
    COUNT(DISTINCT p.product_id) as Количество_товаров,
    SUM(oi.quantity) as Количество_продаж,
    SUM(oi.quantity * oi.price) as Выручка,
    ROUND(
    SUM(oi.quantity * oi.price)*100.0/
    (SELECT SUM(quantity * price) FROM order_items)
    ,2) as  Процент_выручки
FROM products p
JOIN order_items oi USING(product_id)
GROUP BY p.category
ORDER BY Выручка DESC;

-- 10 Какой средний чек у наших клиентов
SELECT 
    CASE 
        WHEN revenue < 50 THEN 'Менее 50'
        WHEN revenue BETWEEN 50 AND 100 THEN '50-100'
        WHEN revenue BETWEEN 100 AND 200 THEN '100-200'
        WHEN revenue BETWEEN 200 AND 500 THEN '200-500'
        ELSE 'Более 500'
    END as Выручка,
    COUNT(*) as Количество_заказов,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2) as Процент
FROM orders
GROUP BY Выручка
ORDER BY MIN(revenue);

-- 11 Есть ли сезонность в наших продажах?
SELECT 
    EXTRACT(MONTH FROM order_date) as Число_месяца,
    TO_CHAR(order_date, 'Month') as Месяц,
    COUNT(DISTINCT order_id) as Количестов_заказов,
    SUM(revenue) as Месячная_выручка
FROM orders
GROUP BY EXTRACT(MONTH FROM order_date), TO_CHAR(order_date, 'Month')
ORDER BY Число_месяца;


