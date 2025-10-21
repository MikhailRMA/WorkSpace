-- Импорт данных (пути указывайте абсолютные или относительные)
COPY customers(customer_id, name, country, signup_date) 
FROM 'C:\Program Files\PostgreSQL\17\data\base\customer.csv' DELIMITER ',' CSV HEADER;

COPY products(product_id, product_name, category, price) 
FROM 'C:\Program Files\PostgreSQL\17\data\base\product.csv' DELIMITER ',' CSV HEADER;

COPY orders(order_id, customer_id, order_date, revenue) 
FROM 'C:\Program Files\PostgreSQL\17\data\base\order.csv' DELIMITER ',' CSV HEADER;

COPY order_items(order_id, product_id, quantity, price) 
FROM 'C:\Program Files\PostgreSQL\17\data\base\order_items.csv' DELIMITER ',' CSV HEADER;

-- Проверка импорта
SELECT COUNT(*) as total_customers FROM customers;
SELECT COUNT(*) as total_products FROM products;
SELECT COUNT(*) as total_orders FROM orders;
SELECT COUNT(*) as total_order_items FROM order_items;
