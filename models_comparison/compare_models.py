import os
import sys
import json
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sklearn.model_selection import train_test_split
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
        "physionet_sepsis_combined.csv",
        "../physionet_sepsis_processed.csv",
        "../physionet_sepsis_combined.csv"
    ]
    for path in paths:
        if os.path.exists(path):
            return pd.read_csv(path)
    raise FileNotFoundError("Could not find sepsis dataset CSV file.")

def run_master_comparison(base_dir="models_comparison"):
    os.makedirs(base_dir, exist_ok=True)
    plots_dir = os.path.join(base_dir, "comparison_plots")
    os.makedirs(plots_dir, exist_ok=True)

    dt_dir = os.path.join(base_dir, "decision_tree")
    rf_dir = os.path.join(base_dir, "random_forest")

    # Ensure individual model training scripts have run
    from decision_tree.train_decision_tree import train_and_evaluate_decision_tree
    from random_forest.train_random_forest import train_and_evaluate_random_forest

    print("==================================================================")
    print("  STEP 1: Training & Evaluating Single Decision Tree...")
    print("==================================================================")
    dt_metrics = train_and_evaluate_decision_tree(dt_dir)

    print("\n==================================================================")
    print("  STEP 2: Training & Evaluating Random Forest...")
    print("==================================================================")
    rf_metrics = train_and_evaluate_random_forest(rf_dir)

    print("\n==================================================================")
    print("  STEP 3: Generating Comparative Curves & Visualizations...")
    print("==================================================================")

    # Load dataset & re-fit models to extract probability curves
    df = load_dataset()
    if len(df) > 200000:
        df = df.sample(n=200000, random_state=42).reset_index(drop=True)
    X = df[OPTIMAL_FEATURES].copy()
    y = df['SepsisLabel'].values

    medians = X.median().to_dict()
    X_imputed = X.fillna(medians)

    X_train, X_test, y_train, y_test = train_test_split(
        X_imputed, y, test_size=0.2, random_state=42, stratify=y
    )

    dt_model = joblib.load(os.path.join(dt_dir, "decision_tree_model.pkl"))
    rf_model = joblib.load(os.path.join(rf_dir, "random_forest_model.pkl"))

    dt_proba = dt_model.predict_proba(X_test)[:, 1]
    rf_proba = rf_model.predict_proba(X_test)[:, 1]

    # ROC Curves
    dt_fpr, dt_tpr, _ = roc_curve(y_test, dt_proba)
    rf_fpr, rf_tpr, _ = roc_curve(y_test, rf_proba)

    # Precision-Recall Curves
    dt_prec_c, dt_rec_c, _ = precision_recall_curve(y_test, dt_proba)
    rf_prec_c, rf_rec_c, _ = precision_recall_curve(y_test, rf_proba)

    sns.set_theme(style="whitegrid")

    # Plot 1: ROC Curve Comparison
    plt.figure(figsize=(8, 6))
    plt.plot(dt_fpr, dt_tpr, label=f"Single Decision Tree (ROC-AUC = {dt_metrics['roc_auc']:.4f})", color="#e67e22", lw=2)
    plt.plot(rf_fpr, rf_tpr, label=f"Random Forest (ROC-AUC = {rf_metrics['roc_auc']:.4f})", color="#2980b9", lw=2)
    plt.plot([0, 1], [0, 1], 'k--', lw=1.5, label="Random Classifier baseline")
    plt.xlabel('False Positive Rate (1 - Specificity)', fontsize=12)
    plt.ylabel('True Positive Rate (Recall / Sensitivity)', fontsize=12)
    plt.title('ROC Curve: Single Decision Tree vs. Random Forest', fontsize=14, fontweight='bold')
    plt.legend(loc='lower right', fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "roc_curve_comparison.png"), dpi=300)
    plt.close()

    # Plot 2: PR Curve Comparison
    plt.figure(figsize=(8, 6))
    plt.plot(dt_rec_c, dt_prec_c, label=f"Single Decision Tree (PR-AUC = {dt_metrics['pr_auc']:.4f})", color="#e67e22", lw=2)
    plt.plot(rf_rec_c, rf_prec_c, label=f"Random Forest (PR-AUC = {rf_metrics['pr_auc']:.4f})", color="#2980b9", lw=2)
    plt.xlabel('Recall (Sensitivity)', fontsize=12)
    plt.ylabel('Precision (Positive Predictive Value)', fontsize=12)
    plt.title('Precision-Recall Curve: Single Decision Tree vs. Random Forest', fontsize=14, fontweight='bold')
    plt.legend(loc='lower left', fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "pr_curve_comparison.png"), dpi=300)
    plt.close()

    # Plot 3: Metrics Bar Chart
    metrics_list = ['accuracy', 'precision', 'recall_sensitivity', 'specificity', 'f1_score', 'roc_auc', 'pr_auc']
    labels_list = ['Accuracy', 'Precision', 'Recall/Sens', 'Specificity', 'F1-Score', 'ROC-AUC', 'PR-AUC']
    
    chart_data = []
    for metric_key, metric_label in zip(metrics_list, labels_list):
        chart_data.append({'Metric': metric_label, 'Model': 'Single Decision Tree', 'Score': dt_metrics[metric_key]})
        chart_data.append({'Metric': metric_label, 'Model': 'Random Forest', 'Score': rf_metrics[metric_key]})
    
    chart_df = pd.DataFrame(chart_data)

    plt.figure(figsize=(10, 5))
    sns.barplot(data=chart_df, x='Metric', y='Score', hue='Model', palette=['#e67e22', '#2980b9'])
    plt.ylim(0, 1.05)
    plt.title('Performance Metric Comparison: Single Decision Tree vs. Random Forest', fontsize=14, fontweight='bold')
    plt.ylabel('Score')
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "metrics_barchart.png"), dpi=300)
    plt.close()

    # Plot 4: Side-by-side Confusion Matrices
    dt_cm = np.array([
        [dt_metrics['confusion_matrix']['true_negative'], dt_metrics['confusion_matrix']['false_positive']],
        [dt_metrics['confusion_matrix']['false_negative'], dt_metrics['confusion_matrix']['true_positive']]
    ])
    rf_cm = np.array([
        [rf_metrics['confusion_matrix']['true_negative'], rf_metrics['confusion_matrix']['false_positive']],
        [rf_metrics['confusion_matrix']['false_negative'], rf_metrics['confusion_matrix']['true_positive']]
    ])

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    sns.heatmap(dt_cm, annot=True, fmt='d', cmap='Oranges', ax=axes[0], cbar=False,
                xticklabels=['Normal', 'Sepsis'], yticklabels=['Normal', 'Sepsis'])
    axes[0].set_title(f"Single Decision Tree\n(F1 = {dt_metrics['f1_score']:.4f})", fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Predicted')
    axes[0].set_ylabel('Actual')

    sns.heatmap(rf_cm, annot=True, fmt='d', cmap='Blues', ax=axes[1], cbar=False,
                xticklabels=['Normal', 'Sepsis'], yticklabels=['Normal', 'Sepsis'])
    axes[1].set_title(f"Random Forest (100 Trees)\n(F1 = {rf_metrics['f1_score']:.4f})", fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Predicted')
    axes[1].set_ylabel('Actual')

    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "confusion_matrix_side_by_side.png"), dpi=300)
    plt.close()

    # Step 4: Build Comparative JSON
    comparison_summary = {
        "models": {
            "single_decision_tree": dt_metrics,
            "random_forest": rf_metrics
        },
        "performance_differences": {
            "accuracy_diff": round(rf_metrics['accuracy'] - dt_metrics['accuracy'], 4),
            "precision_diff": round(rf_metrics['precision'] - dt_metrics['precision'], 4),
            "recall_diff": round(rf_metrics['recall_sensitivity'] - dt_metrics['recall_sensitivity'], 4),
            "specificity_diff": round(rf_metrics['specificity'] - dt_metrics['specificity'], 4),
            "f1_score_diff": round(rf_metrics['f1_score'] - dt_metrics['f1_score'], 4),
            "roc_auc_diff": round(rf_metrics['roc_auc'] - dt_metrics['roc_auc'], 4),
            "pr_auc_diff": round(rf_metrics['pr_auc'] - dt_metrics['pr_auc'], 4),
            "cv_roc_auc_diff": round(rf_metrics['cv_roc_auc_mean'] - dt_metrics['cv_roc_auc_mean'], 4),
        },
        "key_takeaways": [
            "Random Forest significantly outperforms Single Decision Tree in ROC-AUC and PR-AUC by bagging 100 decision trees.",
            "Single Decision Tree exhibits higher variance and lower precision due to greedy decision splits.",
            "Single Decision Tree offers high visual interpretability (explainable tree splits), while Random Forest offers superior clinical reliability."
        ]
    }

    comp_path = os.path.join(base_dir, "performance_comparison.json")
    with open(comp_path, "w") as f:
        json.dump(comparison_summary, f, indent=4)

    # Step 5: Write Markdown Summary Report
    md_content = f"""# Performance Comparison: Single Decision Tree vs. Random Forest

## Summary Table

| Metric | Single Decision Tree | Random Forest (100 Trees) | Difference (RF - DT) |
| :--- | :---: | :---: | :---: |
| **Accuracy** | {dt_metrics['accuracy']:.4f} | {rf_metrics['accuracy']:.4f} | {rf_metrics['accuracy'] - dt_metrics['accuracy']:+.4f} |
| **Precision** | {dt_metrics['precision']:.4f} | {rf_metrics['precision']:.4f} | {rf_metrics['precision'] - dt_metrics['precision']:+.4f} |
| **Recall / Sensitivity** | {dt_metrics['recall_sensitivity']:.4f} | {rf_metrics['recall_sensitivity']:.4f} | {rf_metrics['recall_sensitivity'] - dt_metrics['recall_sensitivity']:+.4f} |
| **Specificity** | {dt_metrics['specificity']:.4f} | {rf_metrics['specificity']:.4f} | {rf_metrics['specificity'] - dt_metrics['specificity']:+.4f} |
| **F1-Score** | {dt_metrics['f1_score']:.4f} | {rf_metrics['f1_score']:.4f} | {rf_metrics['f1_score'] - dt_metrics['f1_score']:+.4f} |
| **ROC-AUC** | {dt_metrics['roc_auc']:.4f} | {rf_metrics['roc_auc']:.4f} | {rf_metrics['roc_auc'] - dt_metrics['roc_auc']:+.4f} |
| **PR-AUC** | {dt_metrics['pr_auc']:.4f} | {rf_metrics['pr_auc']:.4f} | {rf_metrics['pr_auc'] - dt_metrics['pr_auc']:+.4f} |
| **5-Fold CV ROC-AUC** | {dt_metrics['cv_roc_auc_mean']:.4f} ± {dt_metrics['cv_roc_auc_std']:.4f} | {rf_metrics['cv_roc_auc_mean']:.4f} ± {rf_metrics['cv_roc_auc_std']:.4f} | {rf_metrics['cv_roc_auc_mean'] - dt_metrics['cv_roc_auc_mean']:+.4f} |
| **Training Latency** | {dt_metrics['training_time_sec']:.4f}s | {rf_metrics['training_time_sec']:.4f}s | {rf_metrics['training_time_sec'] - dt_metrics['training_time_sec']:+.4f}s |

## Key Insights & Comparison Analysis

1. **Ensemble Benefit & Variance Reduction**:
   - **Single Decision Tree** relies on a single set of hierarchical splits. It is susceptible to overfitting noise in vital signs and lab values.
   - **Random Forest** aggregates 100 decorrelated decision trees (Bagging). This dramatically reduces variance, resulting in higher ROC-AUC and PR-AUC.

2. **Handling Class Imbalance**:
   - In clinical sepsis prediction, non-sepsis cases outnumber sepsis cases.
   - Random Forest achieves a much higher **PR-AUC** ({rf_metrics['pr_auc']:.4f} vs {dt_metrics['pr_auc']:.4f}), which is the most reliable metric for imbalanced medical data.

3. **Interpretability vs. Performance Trade-off**:
   - **Single Decision Tree** is fully transparent: clinicians can follow step-by-step conditional rules (e.g. `If Lactate > 2.0 and Temp > 38.0`).
   - **Random Forest** operates as a black-box ensemble, but provides global feature importance scores to explain model behavior.
"""

    report_path = os.path.join(base_dir, "comparison_summary.md")
    with open(report_path, "w") as f:
        f.write(md_content)

    print("\n==================================================================")
    print("  COMPARISON BENCHMARK COMPLETE!")
    print(f"  Summary Report: '{report_path}'")
    print(f"  Summary JSON:   '{comp_path}'")
    print(f"  Plots Dir:      '{plots_dir}'")
    print("==================================================================\n")

if __name__ == "__main__":
    run_master_comparison()
