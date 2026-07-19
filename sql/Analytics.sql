-- Total customers
SELECT COUNT(*) AS total_customers
FROM olist_customers_dataset;


-- Total orders
SELECT COUNT(*) AS total_orders
FROM olist_orders_dataset;


-- Total products
SELECT COUNT(*) AS total_products
FROM olist_products_dataset;


SELECT
    SUM(price) AS total_revenue
FROM olist_order_items_dataset;


SELECT
    AVG(order_total) AS average_order_value
FROM
(
    SELECT
        order_id,
        SUM(price) AS order_total
    FROM olist_order_items_dataset
    GROUP BY order_id
) orders;


SELECT
    product_id,
    COUNT(*) AS number_of_sales
FROM olist_order_items_dataset
GROUP BY product_id
ORDER BY number_of_sales DESC
LIMIT 10;


SELECT
    p.product_category_name,
    COUNT(*) AS sales
FROM olist_order_items_dataset oi
JOIN olist_products_dataset p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY sales DESC
LIMIT 10;


SELECT
    customer_state,
    COUNT(*) AS customers
FROM olist_customers_dataset
GROUP BY customer_state
ORDER BY customers DESC;


