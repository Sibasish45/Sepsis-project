"""
Dedicated Random Forest Model Trainer for 15 Optimal Features.
"""
import os
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

OPTIMAL_FEATURES = [
    "HR", "O2Sat", "Temp", "SBP", "MAP", "DBP", "Resp",
    "WBC", "Glucose", "Lactate", "Creatinine", "Platelets",
    "Age", "Gender", "ICULOS"
]

def train_15_model(csv_path="physionet_sepsis_processed.csv", output_dir="optimal_15_features"):
    os.makedirs(output_dir, exist_ok=True)
    if not os.path.exists(csv_path):
        csv_path = "../physionet_sepsis_processed.csv"
    if not os.path.exists(csv_path):
        csv_path = "physionet_sepsis_combined.csv"

    print(f"Loading dataset from '{csv_path}' for 15-feature model training...")
    df = pd.read_csv(csv_path)

    X = df[OPTIMAL_FEATURES].copy()
    y = df['SepsisLabel']

    # Compute and save medians
    medians = X.median().to_dict()
    medians_path = os.path.join(output_dir, "feature_medians_15.json")
    with open(medians_path, "w") as f:
        json.dump(medians, f, indent=4)
    print(f"Saved feature medians to '{medians_path}'")

    X = X.fillna(medians)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("Training Random Forest model on 15 optimal features...")
    rf = RandomForestClassifier(n_estimators=100, max_depth=15, class_weight='balanced', random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)

    print("\n--- 15-Feature Model Evaluation ---")
    predictions = rf.predict(X_test)
    print(classification_report(y_test, predictions))

    model_path = os.path.join(output_dir, "sepsis_model_15.pkl")
    joblib.dump(rf, model_path)
    print(f"Saved trained 15-feature model to '{model_path}'")

if __name__ == "__main__":
    train_15_model()
