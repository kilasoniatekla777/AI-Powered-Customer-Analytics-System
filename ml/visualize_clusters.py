import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

from backend.db import engine


# ==========================
# Load data
# ==========================

query = "SELECT * FROM customer_features;"
customers = pd.read_sql(query, engine)

print(customers.shape)


# ==========================
# Prepare features
# ==========================

features = [
    "number_of_orders",
    "total_spent",
    "average_review_score",
    "recency_days"
]

X = customers[features].copy()

print("\nMissing values:")
print(X.isna().sum())

X = X.fillna({
    "number_of_orders": 0,
    "total_spent": 0,
    "average_review_score": X["average_review_score"].mean(),
    "recency_days": X["recency_days"].mean()
})


# ==========================
# Scale
# ==========================

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


# ==========================
# KMeans clustering
# k=5 chosen based on silhouette analysis in ml/find_best_k.py
# (silhouette score = 0.4155, best among k=2-9)
# ==========================

kmeans = KMeans(n_clusters=5, random_state=42)
customers["customer_cluster"] = kmeans.fit_predict(X_scaled)

customers_clustered = customers


# ==========================
# Cluster statistics
# ==========================

print("\nCustomer distribution by cluster:")
for cluster in sorted(customers_clustered["customer_cluster"].unique()):
    count = sum(customers_clustered["customer_cluster"] == cluster)
    print(f"Cluster {cluster}: {count} customers")

print("\nCluster profile (average values):")
cluster_profile = customers_clustered.groupby("customer_cluster")[features].mean()
print(cluster_profile)


# ==========================
# PCA for visualization
# ==========================

pca = PCA(n_components=2)
pca_result = pca.fit_transform(X_scaled)

customers_clustered["PCA1"] = pca_result[:, 0]
customers_clustered["PCA2"] = pca_result[:, 1]


# ==========================
# Visualization
# ==========================

plt.figure(figsize=(10, 7))

sns.scatterplot(
    data=customers_clustered,
    x="PCA1",
    y="PCA2",
    hue="customer_cluster",
    palette="viridis",
    s=80
)

plt.title("Customer Segments Visualization (PCA)")
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.legend(title="Cluster")

plt.show()