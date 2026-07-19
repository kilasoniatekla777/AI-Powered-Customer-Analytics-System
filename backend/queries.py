# =========================
# Business Overview
# =========================

TOTAL_CUSTOMERS = """
SELECT COUNT(*) AS total_customers
FROM olist_order_customer_dataset;
"""


TOTAL_ORDERS = """
SELECT COUNT(*) AS total_orders
FROM olist_orders_dataset;
"""


TOTAL_REVENUE = """
SELECT 
    SUM(price) AS total_revenue
FROM olist_order_items_dataset;
"""


AVERAGE_ORDER_VALUE = """
SELECT
    AVG(order_total) AS average_order_value
FROM
(
    SELECT
        order_id,
        SUM(price) AS order_total
    FROM olist_order_items_dataset
    GROUP BY order_id
) AS orders;
"""


# =========================
# Product Analysis
# =========================

TOP_CATEGORIES = """
SELECT
    p.product_category_name,
    COUNT(*) AS sales
FROM olist_order_items_dataset oi
JOIN olist_products_dataset p
ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY sales DESC
LIMIT 10;
"""

# =========================
# Customer Analysis
# =========================

TOP_CUSTOMERS = """
SELECT
    o.customer_id,
    SUM(oi.price) AS total_spent
FROM olist_orders_dataset o
JOIN olist_order_items_dataset oi
ON o.order_id = oi.order_id
GROUP BY o.customer_id
ORDER BY total_spent DESC
LIMIT 10;
"""


REPEAT_CUSTOMERS = """
SELECT
    c.customer_unique_id,
    COUNT(o.order_id) AS number_of_orders
FROM olist_order_customer_dataset c
JOIN olist_orders_dataset o
ON c.customer_id = o.customer_id
GROUP BY c.customer_unique_id
HAVING COUNT(o.order_id) > 1
ORDER BY number_of_orders DESC
LIMIT 10;
"""

CUSTOMER_LOCATIONS = """
SELECT
    customer_state,
    COUNT(*) AS customers
FROM olist_order_customer_dataset
GROUP BY customer_state
ORDER BY customers DESC
LIMIT 10;
"""


# =========================
# Product Analysis
# =========================

TOP_PRODUCTS = """
SELECT
    product_id,
    COUNT(*) AS number_of_sales
FROM olist_order_items_dataset
GROUP BY product_id
ORDER BY number_of_sales DESC
LIMIT 10;
"""


TOP_CATEGORIES = """
SELECT
    p.product_category_name,
    COUNT(*) AS sales
FROM olist_order_items_dataset oi
JOIN olist_products_dataset p
ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY sales DESC
LIMIT 10;
"""


TOP_SELLERS = """
SELECT
    seller_id,
    SUM(price) AS revenue
FROM olist_order_items_dataset
GROUP BY seller_id
ORDER BY revenue DESC
LIMIT 10;
"""

CUSTOMER_FEATURES = """
SELECT *
FROM customer_features;
"""