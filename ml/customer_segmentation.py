import pandas as pd
import joblib
from backend.db import engine
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler




#  Load data from PostgreSQL

query = """
SELECT *
FROM customer_features;
"""


df = pd.read_sql(
    query,
    engine
)


print("Original data:")
print(df.head())

print("\nColumns:")
print(df.columns)


#  Select ML features

features = df[
    [
        "number_of_orders",
        "total_spent",
        "average_review_score"
    ]
]


# Handle missing values

features = features.fillna(0)


#  Scale features

scaler = StandardScaler()

scaled_features = scaler.fit_transform(features)


#  Train K-Means

model = KMeans(
    n_clusters=4,
    random_state=42
)


df["customer_cluster"] = model.fit_predict(
    scaled_features
)


#  Show customers with clusters

print("\nCustomer segments:")
print(df.head())


#  Save results

df.to_csv(
    "data/customer_segments.csv",
    index=False
)


print("\nSaved customer_segments.csv")


#  Analyze clusters

cluster_summary = df.groupby(
    "customer_cluster"
)[
    [
        "number_of_orders",
        "total_spent",
        "average_review_score"
    ]
].mean()


joblib.dump(
    model,
    "models/customer_segmentation.pkl"
)


print("\nCluster Summary:")
print(cluster_summary)
print("Model saved")