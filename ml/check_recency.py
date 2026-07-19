import pandas as pd
from backend.db import engine

query = "SELECT * FROM customer_features;"
customers = pd.read_sql(query, engine)

print(customers["recency_days"].describe())
print("\nPercentiles:")
for p in [25, 50, 75, 90]:
    print(f"{p}th percentile: {customers['recency_days'].quantile(p/100):.0f} days")