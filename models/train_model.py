"""
train_model.py
----------------
Trains a simple, explainable ML pipeline that classifies SMS / Email / URL
text into one of three categories: safe, suspicious, fraud.

Pipeline: TF-IDF Vectorizer  ->  Logistic Regression (multi-class)

Why this approach (beginner-friendly explanation for the report):
- TF-IDF converts text into numeric features based on word importance.
- Logistic Regression is fast, interpretable (we can inspect word weights),
  and works well on small/medium text datasets - perfect for a hackathon MVP.
- We also keep a hand-curated keyword list (see utils/ml_utils.py) that is
  used to (a) generate a human-readable "why" explanation for every
  prediction, and (b) specifically flag Digital Arrest style scams which
  are a distinct, high-priority pattern for this hackathon problem
  statement (PS6).

Run:
    python train_model.py
Outputs:
    fraud_model.pkl       -> trained LogisticRegression model
    vectorizer.pkl        -> fitted TfidfVectorizer
    model_report.txt      -> accuracy / classification report for the README
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    data_path = os.path.join(BASE_DIR, "dataset.csv")
    df = pd.read_csv(data_path)
    df = df.dropna()

    X = df["text"]
    y = df["label"]

    # Small dataset -> keep a modest test split so training still has enough
    # examples of every class.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),   # unigrams + bigrams help catch phrases like "digital arrest"
        max_features=3000,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(X_train_vec, y_train)

    y_pred = model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    print("Accuracy:", acc)
    print(report)

    joblib.dump(model, os.path.join(BASE_DIR, "fraud_model.pkl"))
    joblib.dump(vectorizer, os.path.join(BASE_DIR, "vectorizer.pkl"))

    with open(os.path.join(BASE_DIR, "model_report.txt"), "w") as f:
        f.write(f"Accuracy: {acc:.2f}\n\n")
        f.write(report)

    print("\nModel and vectorizer saved to /models")


if __name__ == "__main__":
    main()
