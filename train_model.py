import os
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
from utils.constants import FEATURE_NAMES

print("Loading the dataset...")
csv_path = 'physionet_sepsis_processed.csv' if os.path.exists('physionet_sepsis_processed.csv') else 'physionet_sepsis_combined.csv'
df = pd.read_csv(csv_path)

print(f"Loaded dataset from {csv_path}. Selecting 15 optimal features: {FEATURE_NAMES}")

# 1. Define Features (X) and Target (y)
X = df[FEATURE_NAMES].copy()
y = df['SepsisLabel']

# Calculate and save feature medians for fallback imputation
medians = X.median().to_dict()
os.makedirs('model', exist_ok=True)
with open('model/feature_medians.json', 'w') as f:
    json.dump(medians, f, indent=4)
print("Saved feature medians to model/feature_medians.json")

# Fill any remaining NaNs with medians for model fitting
X = X.fillna(medians)

# 2. Train/Test Split (80% for training, 20% for testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 3. Initialize and train the Random Forest model
print("Training the Random Forest model on 15 optimal features...")
model = RandomForestClassifier(n_estimators=100, max_depth=15, class_weight='balanced', random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# 4. Evaluate the Model
print("\n--- Model Evaluation ---")
predictions = model.predict(X_test)
print(classification_report(y_test, predictions))

print("Saving the model as sepsis_model.pkl...")
joblib.dump(model, 'sepsis_model.pkl')
print("Model training complete! Ready for Sepsis CDSS integration.")