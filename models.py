# models.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import numpy as np

def build_churn_model(rfm):
    # basic checks
    if rfm is None or rfm.empty:
        return None, {"error":"rfm dataframe is empty"}

    rfm = rfm.copy()
    # ensure numeric
    for c in ['recency','frequency','monetary']:
        if c not in rfm.columns:
            rfm[c] = 0

    rfm["churn"] = (rfm["recency"] > 60).astype(int)

    X = rfm[["recency", "frequency", "monetary"]].fillna(0)
    y = rfm["churn"].fillna(0).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    report = classification_report(y_test, model.predict(X_test), output_dict=True)

    return model, report
