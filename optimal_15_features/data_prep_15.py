"""
Dedicated Data Preparation Pipeline for 15 Optimal Clinical Features.
Processes physionet_sepsis_processed.csv / physionet_sepsis_combined.csv into an optimized 15-feature dataset.
"""
import os
import json
import pandas as pd
import numpy as np

OPTIMAL_FEATURES = [
    "HR", "O2Sat", "Temp", "SBP", "MAP", "DBP", "Resp",
    "WBC", "Glucose", "Lactate", "Creatinine", "Platelets",
    "Age", "Gender", "ICULOS"
]

def process_15_features(raw_csv="physionet_sepsis_processed.csv", output_dir="optimal_15_features"):
    os.makedirs(output_dir, exist_ok=True)
    if not os.path.exists(raw_csv):
        raw_csv = "../physionet_sepsis_processed.csv"
    if not os.path.exists(raw_csv):
        raw_csv = "physionet_sepsis_combined.csv"

    print(f"Loading dataset from '{raw_csv}'...")
    df = pd.read_csv(raw_csv)

    print(f"Loaded {len(df):,} rows across {df['Patient_ID'].nunique():,} patients.")
    
    # Keep patient ID, target label, and optimal 15 features
    keep_cols = ['Patient_ID', 'SepsisLabel'] + [c for c in OPTIMAL_FEATURES if c in df.columns]
    df_15 = df[keep_cols].copy()

    # Calculate medians for missing value fallback
    numeric_cols = [c for c in OPTIMAL_FEATURES if c in df_15.columns]
    medians = df_15[numeric_cols].median().to_dict()

    # Save feature metadata json
    meta_path = os.path.join(output_dir, "feature_columns_15.json")
    with open(meta_path, "w") as f:
        json.dump({
            "feature_cols": OPTIMAL_FEATURES,
            "total_features": len(OPTIMAL_FEATURES),
            "target_col": "SepsisLabel",
            "id_col": "Patient_ID",
            "medians": medians
        }, f, indent=4)
    print(f"Saved feature metadata to '{meta_path}'")

    # Export clean 15-feature dataset
    out_csv = os.path.join(output_dir, "physionet_sepsis_15_processed.csv")
    df_15.to_csv(out_csv, index=False)
    print(f"Saved 15-feature dataset to '{out_csv}' ({len(df_15):,} rows).")

if __name__ == "__main__":
    process_15_features()
