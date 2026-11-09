import pandas as pd
import glob
import os

path_a = './archive/training_setA/training_setA/*.psv'
path_b = './archive/training_setB/*.psv'

all_files = glob.glob(path_a) + glob.glob(path_b)
dataframes = []

print(f"Found {len(all_files)} patient files. Starting concatenation...")

for file in all_files:
    # .psv means pipe-separated 
    df = pd.read_csv(file, sep='|') 
    
    # Extract the filename (e.g., 'p000001') to use as a unique Patient ID
    patient_id = os.path.basename(file).split('.')[0]
    df['Patient_ID'] = patient_id 
    
    dataframes.append(df)

# Combine them all into one massive dataframe
print("Combining files... this might take a minute depending on your RAM.")
combined_df = pd.concat(dataframes, ignore_index=True)

combined_df.to_csv('physionet_sepsis_combined.csv', index=False)
print("Success! Data saved as physionet_sepsis_combined.csv")