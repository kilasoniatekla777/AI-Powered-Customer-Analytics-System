import pandas as pd

from backend.db import engine
from backend.queries import (
    CUSTOMER_FEATURES,
    TOTAL_CUSTOMERS,
    TOTAL_ORDERS,
    TOTAL_REVENUE,
    TOP_CUSTOMERS,
    REPEAT_CUSTOMERS,
    TOP_PRODUCTS,
    TOP_CATEGORIES,
    TOP_SELLERS,
    CUSTOMER_LOCATIONS
)


def run_query(query, title):

    print("\n")
    print("=" * 40)
    print(title)
    print("=" * 40)

    df = pd.read_sql(query, engine)

    print(df)


run_query(
    TOTAL_CUSTOMERS,
    "TOTAL CUSTOMERS"
)


run_query(
    TOTAL_ORDERS,
    "TOTAL ORDERS"
)


run_query(
    TOTAL_REVENUE,
    "TOTAL REVENUE"
)


run_query(
    TOP_CUSTOMERS,
    "TOP CUSTOMERS"
)


run_query(
    REPEAT_CUSTOMERS,
    "REPEAT CUSTOMERS"
)


run_query(
    TOP_PRODUCTS,
    "TOP PRODUCTS"
)


run_query(
    TOP_CATEGORIES,
    "TOP CATEGORIES"
)


run_query(
    TOP_SELLERS,
    "TOP SELLERS"
)


run_query(
    CUSTOMER_LOCATIONS,
    "CUSTOMER LOCATIONS"
)

run_query(
    CUSTOMER_FEATURES,
    "CUSTOMER FEATURES"
)