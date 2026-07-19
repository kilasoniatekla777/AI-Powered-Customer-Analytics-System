import pandas as pd
from backend.db import engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix


query = """
SELECT review_comment_message, review_score
FROM olist_order_reviews_dataset
WHERE review_comment_message IS NOT NULL
AND review_score != 3;
"""

reviews = pd.read_sql(query, engine)

reviews["sentiment"] = (reviews["review_score"] >= 4).astype(int)

print(reviews.shape)
print(reviews["sentiment"].value_counts())
print(reviews.head())

X_text = reviews["review_comment_message"]
y = reviews["sentiment"]

X_train_text, X_test_text, y_train, y_test = train_test_split(
    X_text, y, test_size=0.2, random_state=42, stratify=y
)

vectorizer = TfidfVectorizer(max_features=5000)
X_train = vectorizer.fit_transform(X_train_text)
X_test = vectorizer.transform(X_test_text)

print("Train shape:", X_train.shape)
print("Test shape:", X_test.shape)


model = LogisticRegression(random_state=42, max_iter=1000)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))