import pandas as pd
from backend.db import engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix


query = "SELECT * FROM customer_features;"
customers = pd.read_sql(query, engine)

# Define churn: 1 if recency is above the median, else 0
threshold = customers["recency_days"].median()
customers["churned"] = (customers["recency_days"] > threshold).astype(int)

print(f"Churn threshold: {threshold} days")
print(customers["churned"].value_counts())


features = [
    "number_of_orders",
    "total_spent",
    "average_review_score"
]

X = customers[features].copy()
y = customers["churned"]

# Handle missing values
X = X.fillna({
    "average_review_score": X["average_review_score"].mean()
})

# Split into train/test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Scale features (fit only on training data — important!)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("Train size:", X_train_scaled.shape)
print("Test size:", X_test_scaled.shape)

# Train the model
model = LogisticRegression(random_state=42)
model.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test_scaled)

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))