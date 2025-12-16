paramer
selct q1, q2
from sale
WHERE date = '11.12.12'
ORDER BY

slelct product_id, 
    price, 
    revenue,
    avg(revenue) over(
    PARTITION BY emp 
    ORDER BY date 
    BETWEEN 3 patent and following 7) 

    SELECT
        order_id,
        customer_id,
        order_date,
        order_amount,
        sum(amount) OVER(
                PARTITION BY customer_id
                ORDER BY order_date
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )
    FROM orders
    ORDER BY customer_id, order_date

    SELECT product_id,
        date,
        price,
        MAX(price) OVER(
            PARTITION BY product_id ORDER BY data
            RANGE BETWEEN INTERVAl '30 days' PRECEDING AND CURRENT ROW 
        ) as max_price,

        MIN(price) OVER(
            PARTITION BY product_id ORDER BY data
            RANGE BETWEEN INTERVAl '30 days' PRECEDING AND CURRENT ROW 
        ) as min_price,

        LAST_VALUE(price) OVER(
            PARTITION BY product_id ORDER BY data
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )

    FROM daily_prices;

    SELECT product_id,
        COUNT(DISTINCT sale) as diff_price
    FROM daily_prices
    WHERE date BETWEEN INTERVAl '30 days'
    GROUP BY product_id
    HAVING COUNT(DISTINCT sale) > 5
    ORDER BY product_id;

WITH prod_stat AS ( 
    SELECT product_id,
        SUM(revenue) as total_rev,
        SUM(revenue) / SUM(SUM(revenue)) OVER() as share
    FROM 
    WHERE has_discount IS NOT NULL
    GROUP BY product_id
)
SELECT product_id,
    total_rev,
        CASE 
            WHEN share >= 0.70  THEN  'High sensitivity'
            WHEN share >= 0.30 AND < 0.70  THEN 'Medium sensitivity'
            WHEN share < 0.30 THEN 'Low sensitivity'
            ELSE  'нет выручки'
        END as segment_sens
    FROM prod_stat


SELECT date_trunc('month', date) as month,
    COUNT(DISTINCT product_id) as sum_prod
FROM sale
GROUP BY date_trunc('month', date)
ORDER BY COUNT(DISTINCT product_id)

WITH last_sale as (
    SELECT DISTINCT product_id,
        last_value(date) OVER(PARTITION BY product_id ORDER BY date) as last_date
    FROM sale
)

SELECT product_id, last_date, CURRENT_DATE - last_date as date_out_sale
FROM last_sale
WHERE last_date < CURRENT_DATE - INTERVAL '30 days' 

SELECT date_trunc('day', date) as day, avg(revenue) as avg_revenue
group by date_trunc('day', date)

SELECT p.category,
    SUM(s.revenue) as total_revenue,
    ROUND(AVG(((s.discount_sum/s.quantity)/p.base_price)*100), 2) as avg_sale,
    ROUND(100.0 * 
        SUM(CASE WHEN s.discount_sum > 0 THEN s.revenue END) / 
        SUM(s.revenue), 2) as discount_share
FROM products p
JOIN table sale s USING(product_id)
WHERE s.date  >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
AND s.date < DATE_TRUNC('month', CURRENT_DATE)
GROUP BY p.category
