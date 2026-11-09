import os
import json
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)
import joblib

OPTIMAL_FEATURES = [
    "HR", "O2Sat", "Temp", "SBP", "MAP", "DBP", "Resp",
    "WBC", "Glucose", "Lactate", "Creatinine", "Platelets",
    "Age", "Gender", "ICULOS"
]

def load_dataset():
    paths = [
        "physionet_sepsis_processed.csv",
        "physionet_sepsis_combined.csv",
        "../physionet_sepsis_processed.csv",
        "../physionet_sepsis_combined.csv",
        "../../physionet_sepsis_processed.csv",
        "../../physionet_sepsis_combined.csv"
    ]
    for path in paths:
        if os.path.exists(path):
            print(f"Loading dataset from: '{path}'")
            return pd.read_csv(path)
    raise FileNotFoundError("Could not find sepsis dataset CSV file.")

def train_and_evaluate_decision_tree(output_dir="models_comparison/decision_tree"):
    os.makedirs(output_dir, exist_ok=True)
    df = load_dataset()
    if len(df) > 200000:
        df = df.sample(n=200000, random_state=42).reset_index(drop=True)

    X = df[OPTIMAL_FEATURES].copy()
    y = df['SepsisLabel'].values

    # Impute missing values with column medians
    medians = X.median().to_dict()
    X_imputed = X.fillna(medians)

    with open(os.path.join(output_dir, "feature_medians.json"), "w") as f:
        json.dump(medians, f, indent=4)

    # 80/20 Stratified Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_imputed, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Training Single Decision Tree Classifier...")
    model = DecisionTreeClassifier(max_depth=10, class_weight="balanced", random_state=42)

    t0 = time.time()
    model.fit(X_train, y_train)
    train_time = round(time.time() - t0, 4)

    t0 = time.time()
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    inference_latency_ms = round(((time.time() - t0) / len(X_test)) * 1000, 4)

    # 5-Fold Cross Validation (Stratified 100k sample for fast benchmarking)
    sample_size = min(100000, len(X_imputed))
    X_cv_sample, _, y_cv_sample, _ = train_test_split(X_imputed, y, train_size=sample_size, random_state=42, stratify=y)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_cv_sample, y_cv_sample, cv=cv, scoring='roc_auc', n_jobs=-1)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_proba)
    pr_auc = average_precision_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0

    metrics = {
        "model_name": "Single Decision Tree",
        "description": "Single non-linear decision tree (max_depth=10, class_weight='balanced')",
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall_sensitivity": round(float(rec), 4),
        "specificity": round(float(spec), 4),
        "f1_score": round(float(f1), 4),
        "roc_auc": round(float(roc_auc), 4),
        "pr_auc": round(float(pr_auc), 4),
        "cv_roc_auc_mean": round(float(np.mean(cv_scores)), 4),
        "cv_roc_auc_std": round(float(np.std(cv_scores)), 4),
        "training_time_sec": train_time,
        "inference_latency_ms_per_sample": inference_latency_ms,
        "confusion_matrix": {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp)
        }
    }

    metrics_path = os.path.join(output_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)
    print(f"Saved Single Decision Tree metrics to: '{metrics_path}'")

    model_path = os.path.join(output_dir, "decision_tree_model.pkl")
    joblib.dump(model, model_path)
    print(f"Saved Single Decision Tree model to: '{model_path}'")

    # Plot Confusion Matrix
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Oranges',
                xticklabels=['Normal', 'Sepsis'], yticklabels=['Normal', 'Sepsis'])
    plt.title('Decision Tree Confusion Matrix', fontweight='bold')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "confusion_matrix.png"), dpi=300)
    plt.close()

    # Plot simplified Tree Diagram (top 3 levels)
    plt.figure(figsize=(16, 8))
    plot_tree(model, max_depth=3, feature_names=OPTIMAL_FEATURES, class_names=['Normal', 'Sepsis'], filled=True, fontsize=9)
    plt.title('Single Decision Tree Visualization (Top 3 Levels)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "tree_visualization.png"), dpi=300)
    plt.close()
    print(f"Decision Tree training & visualization completed successfully!")

    return metrics

if __name__ == "__main__":
    train_and_evaluate_decision_tree()
