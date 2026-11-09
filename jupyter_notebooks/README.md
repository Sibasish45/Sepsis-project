# Sepsis CDSS - Jupyter Notebooks Suite

This directory contains the production-grade Jupyter Notebooks for training, benchmarking, and evaluating machine learning models on the PhysioNet Sepsis dataset.

## Notebook Directory Structure

| File | Purpose | Corresponding Python Script | Key Outputs |
| :--- | :--- | :--- | :--- |
| [`01_data_stitching_and_preprocessing.ipynb`](01_data_stitching_and_preprocessing.ipynb) | Ingestion of raw PhysioNet `.psv` files, EDA, outlier cleaning, patient time-series imputation, clinical feature engineering (SIRS, Shock Index, qSOFA, 3h deltas). | `stitch_data.py`, `data_prep.py` | `physionet_sepsis_processed.csv`, `sepsis_scaler.pkl`, `feature_columns.json` |
| [`02_random_forest_model_training.ipynb`](02_random_forest_model_training.ipynb) | Primary CDSS model training: extracts 15 optimal features, computes medians, fits class-balanced Random Forest, and serializes production model. | `train_model.py`, `optimal_15_features/train_model_15.py` | `sepsis_model.pkl`, `model/feature_medians.json` |
| [`03_models_benchmarking_and_comparison.ipynb`](03_models_benchmarking_and_comparison.ipynb) | Benchmarking suite comparing Logistic Regression, Single Decision Tree, and Random Forest Classifier across 5-fold CV, AUROC, AUPRC, and confusion matrices. | `models_comparison/compare_models.py`, `optimal_15_features/compare_models_15.py` | Comparative tables, ROC curves, PR curves, Confusion matrix heatmaps |
| [`04_complete_end_to_end_pipeline.ipynb`](04_complete_end_to_end_pipeline.ipynb) | Master end-to-end interactive notebook combining data preprocessing, feature engineering, model training, evaluation, and startup verification. | Full pipeline | All production artifacts (`sepsis_model.pkl`, `feature_medians.json`, `physionet_sepsis_processed.csv`) |

## Quick Start

1. Install required packages:
   ```bash
   pip install -r ../requirements.txt
   ```

2. Start Jupyter:
   ```bash
   jupyter notebook
   ```

3. Open any notebook and select the `Python 3 (ipykernel)` kernel. All notebooks automatically configure their working directory to the project root, so all file paths (`physionet_sepsis_processed.csv`, `model/`, `sepsis_model.pkl`) resolve cleanly.
