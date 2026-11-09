"""
Research Model Comparison Script for Sepsis CDSS.
Trains and compares Logistic Regression, Decision Tree, and Random Forest models on 15 optimal clinical features.
Generates comprehensive performance metrics, 5-fold cross-validation scores, confusion matrices, and ROC/PR curves.
"""
import os
import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    roc_curve, precision_recall_curve
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
        "../physionet_sepsis_processed.csv",
        "physionet_sepsis_combined.csv",
        "../physionet_sepsis_combined.csv"
    ]
    for path in paths:
        if os.path.exists(path):
            print(f"Loading dataset from: '{path}'")
            return pd.read_csv(path)
    raise FileNotFoundError("Could not find sepsis dataset CSV file.")

def run_model_comparison(output_dir="optimal_15_features"):
    os.makedirs(output_dir, exist_ok=True)
    plots_dir = os.path.join(output_dir, "research_plots")
    os.makedirs(plots_dir, exist_ok=True)

    df = load_dataset()

    X = df[OPTIMAL_FEATURES].copy()
    y = df['SepsisLabel'].values

    # Impute missing values with column medians
    medians = X.median().to_dict()
    X_imputed = X.fillna(medians)

    # Save feature medians
    with open(os.path.join(output_dir, "feature_medians_15.json"), "w") as f:
        json.dump(medians, f, indent=4)

    # Train / Test Split (80/20 Stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X_imputed, y, test_size=0.2, random_state=42, stratify=y
    )

    # Feature Scaling (StandardScaler required for Logistic Regression, harmless/neutral for Tree models)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    joblib.dump(scaler, os.path.join(output_dir, "sepsis_scaler_15.pkl"))

    # Define the 3 Research Models
    models = {
        "Logistic Regression": {
            "model": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
            "use_scaled": True,
            "desc": "Linear probabilistic classifier (baseline linear model)"
        },
        "Decision Tree": {
            "model": DecisionTreeClassifier(max_depth=10, class_weight="balanced", random_state=42),
            "use_scaled": False,
            "desc": "Single non-linear decision tree (baseline tree model)"
        },
        "Random Forest": {
            "model": RandomForestClassifier(n_estimators=100, max_depth=15, class_weight="balanced", random_state=42, n_jobs=-1),
            "use_scaled": False,
            "desc": "Bagged ensemble of 100 decision trees (selected production model)"
        }
    }

    results = {}
    curve_data = {}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    print("\n=======================================================")
    print("      STARTING MULTI-MODEL RESEARCH BENCHMARKING       ")
    print("=======================================================\n")

    for name, config in models.items():
        print(f"--- Evaluating {name} ---")
        clf = config["model"]
        use_scaled = config["use_scaled"]

        X_tr = X_train_scaled if use_scaled else X_train
        X_te = X_test_scaled if use_scaled else X_test

        # 1. Measure Training Latency
        t0 = time.time()
        clf.fit(X_tr, y_train)
        train_time = round(time.time() - t0, 4)

        # 2. Measure Inference Latency & Predictions
        t0 = time.time()
        y_pred = clf.predict(X_te)
        y_proba = clf.predict_proba(X_te)[:, 1]
        inference_time_ms = round(((time.time() - t0) / len(X_te)) * 1000, 4)

        # 3. 5-Fold Cross Validation (ROC-AUC)
        X_full = scaler.fit_transform(X_imputed) if use_scaled else X_imputed
        cv_scores = cross_val_score(clf, X_full, y, cv=cv, scoring='roc_auc', n_jobs=-1)

        # 4. Metrics Calculation
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_proba)
        pr_auc = average_precision_score(y_test, y_proba)
        cm = confusion_matrix(y_test, y_pred)

        # Specificity = TN / (TN + FP)
        tn, fp, fn, tp = cm.ravel()
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0

        results[name] = {
            "description": config["desc"],
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
            "inference_latency_ms_per_sample": inference_time_ms,
            "confusion_matrix": {
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp)
            }
        }

        # Store curves
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        precision_curve, recall_curve, _ = precision_recall_curve(y_test, y_proba)
        curve_data[name] = {
            "fpr": fpr, "tpr": tpr,
            "precision_curve": precision_curve, "recall_curve": recall_curve,
            "cm": cm
        }

        print(f"  Accuracy:         {acc:.4f}")
        print(f"  Precision:        {prec:.4f}")
        print(f"  Recall (Sens):    {rec:.4f}")
        print(f"  Specificity:      {spec:.4f}")
        print(f"  F1-Score:         {f1:.4f}")
        print(f"  ROC-AUC:          {roc_auc:.4f}")
        print(f"  PR-AUC:           {pr_auc:.4f}")
        print(f"  5-Fold CV ROC-AUC:{np.mean(cv_scores):.4f} +/- {np.std(cv_scores):.4f}")
        print(f"  Train Time:       {train_time}s\n")

        # Save individual model pickle
        model_filename = name.lower().replace(" ", "_") + "_15.pkl"
        joblib.dump(clf, os.path.join(output_dir, model_filename))

    # Save summary JSON
    summary_path = os.path.join(output_dir, "model_comparison_results.json")
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Saved numerical metrics summary to: '{summary_path}'")

    # Generate Visualization Plots
    sns.set_theme(style="whitegrid")
    
    # Plot 1: ROC Curves Comparison
    plt.figure(figsize=(8, 6))
    for name in models.keys():
        plt.plot(
            curve_data[name]["fpr"], curve_data[name]["tpr"],
            lw=2, label=f"{name} (AUC = {results[name]['roc_auc']:.4f})"
        )
    plt.plot([0, 1], [0, 1], 'k--', lw=1.5, label='Random Chance')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate (1 - Specificity)', fontsize=12)
    plt.ylabel('True Positive Rate (Recall / Sensitivity)', fontsize=12)
    plt.title('Receiver Operating Characteristic (ROC) Curve Comparison', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right", fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "roc_curves_comparison.png"), dpi=300)
    plt.close()

    # Plot 2: Precision-Recall Curves Comparison
    plt.figure(figsize=(8, 6))
    for name in models.keys():
        plt.plot(
            curve_data[name]["recall_curve"], curve_data[name]["precision_curve"],
            lw=2, label=f"{name} (PR-AUC = {results[name]['pr_auc']:.4f})"
        )
    plt.xlabel('Recall (Sensitivity)', fontsize=12)
    plt.ylabel('Precision (Positive Predictive Value)', fontsize=12)
    plt.title('Precision-Recall (PR) Curve Comparison (Imbalanced Sepsis Data)', fontsize=14, fontweight='bold')
    plt.legend(loc="lower left", fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "pr_curves_comparison.png"), dpi=300)
    plt.close()

    # Plot 3: Confusion Matrices Grid
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for idx, name in enumerate(models.keys()):
        cm = curve_data[name]["cm"]
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx], cbar=False,
                    xticklabels=['Normal', 'Sepsis'], yticklabels=['Normal', 'Sepsis'])
        axes[idx].set_title(f"{name}\n(F1 = {results[name]['f1_score']:.3f})", fontsize=12, fontweight='bold')
        axes[idx].set_xlabel('Predicted Label')
        axes[idx].set_ylabel('True Label')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "confusion_matrices_comparison.png"), dpi=300)
    plt.close()

    # Plot 4: Metrics Bar Chart Comparison
    metrics_names = ['Accuracy', 'Precision', 'Recall / Sens', 'F1-Score', 'ROC-AUC', 'PR-AUC']
    plot_df_list = []
    for name in models.keys():
        m = results[name]
        vals = [m['accuracy'], m['precision'], m['recall_sensitivity'], m['f1_score'], m['roc_auc'], m['pr_auc']]
        for mn, val in zip(metrics_names, vals):
            plot_df_list.append({'Model': name, 'Metric': mn, 'Score': val})
    plot_df = pd.DataFrame(plot_df_list)

    plt.figure(figsize=(10, 5))
    sns.barplot(data=plot_df, x='Metric', y='Score', hue='Model', palette='viridis')
    plt.ylim([0.0, 1.05])
    plt.title('Performance Metrics Comparison Across Models', fontsize=14, fontweight='bold')
    plt.ylabel('Score')
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "metrics_barchart.png"), dpi=300)
    plt.close()

    print(f"Saved all 4 comparison plots into directory: '{plots_dir}'")
    print("\nModel comparison benchmark completed successfully!")

if __name__ == "__main__":
    run_model_comparison()
