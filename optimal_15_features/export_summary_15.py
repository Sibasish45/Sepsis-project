"""
Export Summary Script for 15 Optimal Features.
Reads physionet_sepsis_processed.csv and generates a clean JSON dataset summary with statistics and sample rows.
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

FEATURE_UNITS = {
    "HR": "bpm",
    "O2Sat": "%",
    "Temp": "°C",
    "SBP": "mmHg",
    "MAP": "mmHg",
    "DBP": "mmHg",
    "Resp": "bpm",
    "WBC": "k/µL",
    "Glucose": "mg/dL",
    "Lactate": "mmol/L",
    "Creatinine": "mg/dL",
    "Platelets": "k/µL",
    "Age": "years",
    "Gender": "0/1",
    "ICULOS": "hours"
}

def export_summary(csv_path="physionet_sepsis_processed.csv", output_dir="optimal_15_features"):
    os.makedirs(output_dir, exist_ok=True)
    if not os.path.exists(csv_path):
        csv_path = "../physionet_sepsis_processed.csv"
    if not os.path.exists(csv_path):
        csv_path = "physionet_sepsis_combined.csv"

    print(f"Loading dataset from '{csv_path}'...")
    df = pd.read_csv(csv_path)

    total_rows = len(df)
    total_patients = int(df['Patient_ID'].nunique())
    sepsis_cases = int((df.groupby('Patient_ID')['SepsisLabel'].max() == 1).sum())
    total_sepsis_hours = int((df['SepsisLabel'] == 1).sum())

    # Compute Feature Statistics
    stats = {}
    for feat in OPTIMAL_FEATURES:
        if feat in df.columns:
            series = df[feat].dropna()
            stats[feat] = {
                "unit": FEATURE_UNITS.get(feat, ""),
                "count": int(len(series)),
                "missing_pct": round(float((df[feat].isnull().sum() / total_rows) * 100), 2),
                "mean": round(float(series.mean()), 2) if len(series) > 0 else 0.0,
                "std": round(float(series.std()), 2) if len(series) > 0 else 0.0,
                "min": round(float(series.min()), 2) if len(series) > 0 else 0.0,
                "median": round(float(series.median()), 2) if len(series) > 0 else 0.0,
                "max": round(float(series.max()), 2) if len(series) > 0 else 0.0
            }

    # Sample representative rows (250 Sepsis positive rows + 250 Normal rows)
    sepsis_rows = df[df['SepsisLabel'] == 1]
    normal_rows = df[df['SepsisLabel'] == 0]

    n_sepsis = min(250, len(sepsis_rows))
    n_normal = min(250, len(normal_rows))

    sample_df = pd.concat([
        sepsis_rows.sample(n=n_sepsis, random_state=42) if n_sepsis > 0 else sepsis_rows,
        normal_rows.sample(n=n_normal, random_state=42) if n_normal > 0 else normal_rows
    ]).sample(frac=1.0, random_state=42) # shuffle

    sample_columns = ['Patient_ID', 'ICULOS'] + [c for c in OPTIMAL_FEATURES if c in df.columns] + ['SepsisLabel']
    sample_records = []

    for _, row in sample_df[sample_columns].iterrows():
        row_dict = row.to_dict()
        rec = {}
        for col in sample_columns:
            val = row_dict.get(col)
            if val is None or pd.isna(val):
                rec[col] = None
            elif isinstance(val, (int, np.integer)):
                rec[col] = int(val)
            elif isinstance(val, (float, np.floating)):
                rec[col] = round(float(val), 2)
            else:
                rec[col] = str(val)
        sample_records.append(rec)

    export_data = {
        "summary": {
            "total_records": total_rows,
            "total_patients": total_patients,
            "sepsis_patients": sepsis_cases,
            "sepsis_positive_hours": total_sepsis_hours,
            "sepsis_rate_pct": round((sepsis_cases / total_patients) * 100, 2),
            "feature_count": len(OPTIMAL_FEATURES),
            "features": OPTIMAL_FEATURES,
            "source_file": os.path.basename(csv_path)
        },
        "feature_stats": stats,
        "sample_records": sample_records
    }

    # Save to optimal_15_features/dataset_summary_15.json
    out_json = os.path.join(output_dir, "dataset_summary_15.json")
    with open(out_json, "w") as f:
        json.dump(export_data, f, indent=2)
    print(f"Exported summary JSON to '{out_json}' with {len(sample_records)} sample rows.")

    # Also save to dataset_summary_export.json in project root
    with open("dataset_summary_export.json", "w") as f:
        json.dump(export_data, f, indent=2)
    print("Updated root 'dataset_summary_export.json'.")

if __name__ == "__main__":
    export_summary()
