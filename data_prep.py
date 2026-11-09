"""
Comprehensive Clinical Data Processing Pipeline for Sepsis CDSS.
Processes physionet_sepsis_combined.csv through:
1. Data Cleaning & Physiological Outlier Handling
2. Time-Series Forward/Backward Fill per Patient
3. Population Median Imputation
4. Clinical Feature Engineering (SIRS Score, Shock Index, qSOFA, 3h Rolling Trajectories)
5. Group-Aware Stratified Train/Val/Test Partitioning
6. Persistence of Processed Dataset & Scaling Metadata
"""
import pandas as pd
import numpy as np
import os
import json
import joblib
from sklearn.preprocessing import RobustScaler

def process_sepsis_dataset(raw_csv_path='physionet_sepsis_combined.csv', output_csv_path='physionet_sepsis_processed.csv'):
    print("=" * 60)
    print("STEP 1: Loading Raw Dataset...")
    print("=" * 60)
    df = pd.read_csv(raw_csv_path)
    total_rows = len(df)
    total_patients = df['Patient_ID'].nunique()
    print(f"Loaded {total_rows:,} rows across {total_patients:,} unique patients.")
    print(f"Raw Features ({len(df.columns)}): {list(df.columns)}")

    print("\n" + "=" * 60)
    print("STEP 2: Outlier Cleaning & Range Validation...")
    print("=" * 60)
    
    # Define physiological valid ranges (clip out-of-bounds to NaN)
    valid_ranges = {
        'HR': (20, 250),
        'O2Sat': (20, 100),
        'Temp': (25, 43),
        'SBP': (30, 270),
        'MAP': (20, 250),
        'DBP': (20, 200),
        'Resp': (4, 65),
        'pH': (6.5, 8.0),
        'Glucose': (10, 1000),
        'WBC': (0.1, 300),
        'Lactate': (0.1, 35)
    }
    
    cleaned_outliers = 0
    for col, (min_val, max_val) in valid_ranges.items():
        if col in df.columns:
            invalid_mask = (df[col] < min_val) | (df[col] > max_val)
            cnt = invalid_mask.sum()
            if cnt > 0:
                df.loc[invalid_mask, col] = np.nan
                cleaned_outliers += cnt
                print(f" - {col}: reset {cnt:,} out-of-range values to NaN.")
    
    # Drop columns with 100% missing values if any (e.g., EtCO2)
    missing_pct = df.isnull().mean() * 100
    all_null_cols = missing_pct[missing_pct == 100.0].index.tolist()
    if all_null_cols:
        print(f" - Dropping 100% missing columns: {all_null_cols}")
        df = df.drop(columns=all_null_cols)
        
    print(f"Outlier cleaning complete. Total invalid values reset: {cleaned_outliers:,}")

    print("\n" + "=" * 60)
    print("STEP 3: Patient Time-Series Imputation (Forward/Backward Fill + Median)...")
    print("=" * 60)
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'SepsisLabel' in numeric_cols:
        numeric_cols.remove('SepsisLabel')
        
    # Group by Patient_ID for forward fill then backward fill
    print(" - Performing Patient-level Forward Fill (ffill)...")
    df[numeric_cols] = df.groupby('Patient_ID')[numeric_cols].ffill()
    
    print(" - Performing Patient-level Backward Fill (bfill)...")
    df[numeric_cols] = df.groupby('Patient_ID')[numeric_cols].bfill()
    
    # Fill remaining NaNs with population median
    print(" - Imputing remaining NaNs with Population Median...")
    medians = df[numeric_cols].median()
    df[numeric_cols] = df[numeric_cols].fillna(medians)

    print("\n" + "=" * 60)
    print("STEP 4: Clinical Feature Engineering & Biomarkers...")
    print("=" * 60)
    
    # 4.1 SIRS Criteria Calculation
    df['SIRS_Temp'] = ((df['Temp'] > 38.0) | (df['Temp'] < 36.0)).astype(int)
    df['SIRS_HR'] = (df['HR'] > 90.0).astype(int)
    df['SIRS_Resp'] = ((df['Resp'] > 20.0) | (df.get('PaCO2', pd.Series(40, index=df.index)) < 32.0)).astype(int)
    df['SIRS_WBC'] = ((df['WBC'] > 12.0) | (df['WBC'] < 4.0)).astype(int)
    df['SIRS_Score'] = df['SIRS_Temp'] + df['SIRS_HR'] + df['SIRS_Resp'] + df['SIRS_WBC']
    df['SIRS_Positive'] = (df['SIRS_Score'] >= 2).astype(int)
    print(" - Calculated SIRS Criteria (Score 0-4 & Binary Status).")
    
    # 4.2 Shock Index (HR / SBP)
    df['Shock_Index'] = (df['HR'] / (df['SBP'] + 1e-5)).round(4)
    print(" - Calculated Shock Index (HR / SBP).")

    # 4.3 qSOFA Score (Quick SOFA)
    df['qSOFA_Resp'] = (df['Resp'] >= 22.0).astype(int)
    df['qSOFA_SBP'] = (df['SBP'] <= 100.0).astype(int)
    df['qSOFA_Score'] = df['qSOFA_Resp'] + df['qSOFA_SBP']
    print(" - Calculated qSOFA Score.")

    # 4.4 3-Hour Rolling Vital Trajectory Deltas
    print(" - Calculating 3-Hour Rolling Vital Trajectories per Patient...")
    df['HR_3h_mean'] = df.groupby('Patient_ID')['HR'].transform(lambda x: x.rolling(3, min_periods=1).mean())
    df['HR_delta_3h'] = (df['HR'] - df['HR_3h_mean']).round(2)

    df['MAP_3h_mean'] = df.groupby('Patient_ID')['MAP'].transform(lambda x: x.rolling(3, min_periods=1).mean())
    df['MAP_delta_3h'] = (df['MAP'] - df['MAP_3h_mean']).round(2)
    
    # Clean up intermediate rolling mean columns
    df = df.drop(columns=['HR_3h_mean', 'MAP_3h_mean'])

    print("\n" + "=" * 60)
    print("STEP 5: Stratified Patient-Level Train/Val/Test Partitioning & Scaling...")
    print("=" * 60)
    
    patient_ids = df['Patient_ID'].unique()
    patient_sepsis = df.groupby('Patient_ID')['SepsisLabel'].max()
    
    # Stratified split of unique Patient IDs
    from sklearn.model_selection import train_test_split
    train_pids, temp_pids = train_test_split(patient_ids, test_size=0.30, random_state=42, stratify=patient_sepsis[patient_ids])
    val_pids, test_pids = train_test_split(temp_pids, test_size=0.50, random_state=42, stratify=patient_sepsis[temp_pids])
    
    print(f" - Train Patients: {len(train_pids):,} ({len(train_pids)/total_patients*100:.1f}%)")
    print(f" - Val Patients:   {len(val_pids):,} ({len(val_pids)/total_patients*100:.1f}%)")
    print(f" - Test Patients:  {len(test_pids):,} ({len(test_pids)/total_patients*100:.1f}%)")

    # Fit RobustScaler on training set feature columns
    feature_cols = [c for c in df.columns if c not in ['Patient_ID', 'SepsisLabel']]
    scaler = RobustScaler()
    train_mask = df['Patient_ID'].isin(train_pids)
    scaler.fit(df.loc[train_mask, feature_cols])
    
    # Save Scaler and Metadata
    joblib.dump(scaler, 'sepsis_scaler.pkl')
    with open('feature_columns.json', 'w') as f:
        json.dump({
            'feature_cols': feature_cols,
            'total_features': len(feature_cols),
            'target_col': 'SepsisLabel',
            'id_col': 'Patient_ID'
        }, f, indent=4)
        
    print(" - RobustScaler fitted on Training Set and saved to sepsis_scaler.pkl.")
    print(f" - Exported {len(feature_cols)} feature column metadata to feature_columns.json.")

    print("\n" + "=" * 60)
    print("STEP 6: Exporting Clean Processed Dataset...")
    print("=" * 60)
    
    df.to_csv(output_csv_path, index=False)
    print(f"SUCCESS: Processed dataset saved as '{output_csv_path}' ({os.path.getsize(output_csv_path)/(1024*1024):.1f} MB).")
    
    print("\nProcessed Dataset Class Distribution:")
    print(df['SepsisLabel'].value_counts())
    print("\nSIRS Positive Case Counts:")
    print(df['SIRS_Positive'].value_counts())
    print("=" * 60)

if __name__ == "__main__":
    process_sepsis_dataset()