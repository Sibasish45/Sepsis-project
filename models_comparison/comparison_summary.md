# Performance Comparison: Single Decision Tree vs. Random Forest

## Summary Table

| Metric | Single Decision Tree | Random Forest (100 Trees) | Difference (RF - DT) |
| :--- | :---: | :---: | :---: |
| **Accuracy** | 0.8087 | 0.9548 | +0.1461 |
| **Precision** | 0.0729 | 0.2458 | +0.1729 |
| **Recall / Sensitivity** | 0.6591 | 0.5131 | -0.1460 |
| **Specificity** | 0.8121 | 0.9647 | +0.1526 |
| **F1-Score** | 0.1312 | 0.3323 | +0.2011 |
| **ROC-AUC** | 0.7652 | 0.9164 | +0.1512 |
| **PR-AUC** | 0.1157 | 0.3306 | +0.2149 |
| **5-Fold CV ROC-AUC** | 0.7033 ± 0.0081 | 0.8505 ± 0.0060 | +0.1472 |
| **Training Latency** | 0.8001s | 5.3783s | +4.5782s |

## Key Insights & Comparison Analysis

1. **Ensemble Benefit & Variance Reduction**:
   - **Single Decision Tree** relies on a single set of hierarchical splits. It is susceptible to overfitting noise in vital signs and lab values.
   - **Random Forest** aggregates 100 decorrelated decision trees (Bagging). This dramatically reduces variance, resulting in higher ROC-AUC and PR-AUC.

2. **Handling Class Imbalance**:
   - In clinical sepsis prediction, non-sepsis cases outnumber sepsis cases.
   - Random Forest achieves a much higher **PR-AUC** (0.3306 vs 0.1157), which is the most reliable metric for imbalanced medical data.

3. **Interpretability vs. Performance Trade-off**:
   - **Single Decision Tree** is fully transparent: clinicians can follow step-by-step conditional rules (e.g. `If Lactate > 2.0 and Temp > 38.0`).
   - **Random Forest** operates as a black-box ensemble, but provides global feature importance scores to explain model behavior.
