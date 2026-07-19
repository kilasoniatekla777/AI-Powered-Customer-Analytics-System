import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

from backend.db import engine

# Load data
query = "SELECT * FROM customer_features;"
customers = pd.read_sql(query, engine)

features = [
    "number_of_orders",
    "total_spent",
    "average_review_score",
    "recency_days"
]

X = customers[features].copy()
X = X.fillna({
    "number_of_orders": 0,
    "total_spent": 0,
    "average_review_score": X["average_review_score"].mean(),
    "recency_days": X["recency_days"].mean()
})

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Test k=2 through 9
inertia_scores = []
silhouette_scores = []
k_range = range(2, 10)

for k in k_range:
    kmeans_test = KMeans(n_clusters=k, random_state=42)
    labels = kmeans_test.fit_predict(X_scaled)
    inertia_scores.append(kmeans_test.inertia_)
    sil = silhouette_score(X_scaled, labels, sample_size=5000, random_state=42)
    silhouette_scores.append(sil)
    print(f"k={k}: inertia={kmeans_test.inertia_:.1f}, silhouette={sil:.4f}")

plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
plt.plot(k_range, inertia_scores, marker='o')
plt.xlabel("k")
plt.ylabel("Inertia")
plt.title("Elbow Method")

plt.subplot(1, 2, 2)
plt.plot(k_range, silhouette_scores, marker='o', color='orange')
plt.xlabel("k")
plt.ylabel("Silhouette Score")
plt.title("Silhouette Score by k")

plt.tight_layout()
plt.show()

# Result: k=5 gave the best silhouette score (0.4155), so that's what
# we use in visualize_clusters.py