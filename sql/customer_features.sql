CREATE VIEW customer_features AS
SELECT
    c.customer_unique_id,
    COUNT(DISTINCT o.order_id) AS number_of_orders,
    SUM(oi.price) AS total_spent,
    AVG(r.review_score) AS average_review_score,
    MAX(o.order_purchase_timestamp) AS last_purchase_date
FROM olist_order_customer_dataset c
JOIN olist_orders_dataset o
ON c.customer_id = o.customer_id
JOIN olist_order_items_dataset oi
ON o.order_id = oi.order_id
LEFT JOIN olist_order_reviews_dataset r
ON o.order_id = r.order_id
GROUP BY c.customer_unique_id;