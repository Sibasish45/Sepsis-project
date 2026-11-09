"""
ML Inference Service for Sepsis CDSS.
Loads trained Random Forest model and performs 15-feature ordered prediction.
"""
import os
import json
import joblib
import numpy as np
from utils.constants import FEATURE_NAMES, LOW_THRESHOLD, HIGH_THRESHOLD
from utils.errors import ModelError

class MLService:
    def __init__(self, model_path="sepsis_model.pkl", medians_path="model/feature_medians.json"):
        self.model_path = model_path
        self.medians_path = medians_path
        self.model = None
        self.medians = {}
        self.model_version = "RF_v2.0_Optimal15"
        self.initialize_model()

    def initialize_model(self):
        """
        Loads sepsis model and verifies feature contract at startup.
        """
        if not os.path.exists(self.model_path):
            raise ModelError(f"Model file '{self.model_path}' not found.")

        try:
            self.model = joblib.load(self.model_path)
        except Exception as e:
            raise ModelError(f"Failed to load model file: {str(e)}")

        # Startup Contract Check: Verify exact features match expected optimal list
        loaded_features = list(getattr(self.model, "feature_names_in_", []))
        if loaded_features != FEATURE_NAMES:
            raise ModelError(
                f"Startup Contract Mismatch: Model features do not match expected {len(FEATURE_NAMES)} features.\n"
                f"Expected: {FEATURE_NAMES}\nLoaded: {loaded_features}"
            )

        # Load Pre-calculated Feature Medians
        if os.path.exists(self.medians_path):
            try:
                with open(self.medians_path, "r") as f:
                    self.medians = json.load(f)
            except Exception as e:
                print(f"Warning: Could not read feature medians: {e}")

    def prepare_feature_vector(self, vitals_input):
        """
        Constructs complete 40-feature vector with exact ordering and median imputation.
        """
        feature_dict = {}
        for feature in FEATURE_NAMES:
            if feature in vitals_input and vitals_input[feature] is not None:
                feature_dict[feature] = float(vitals_input[feature])
            else:
                # Level 3 Imputation: Fallback to dataset median
                median_val = self.medians.get(feature)
                if median_val is None:
                    median_val = 0.0
                feature_dict[feature] = float(median_val)

        # Form 1x40 ordered DataFrame matching feature names contract
        import pandas as pd
        ordered_values = [feature_dict[feat] for feat in FEATURE_NAMES]
        feature_df = pd.DataFrame([ordered_values], columns=FEATURE_NAMES)

        return feature_df, feature_dict

    def predict_risk(self, vitals_input):
        """
        Calculates Sepsis Risk Probability and Risk Category.
        """
        if self.model is None:
            self.initialize_model()

        feature_matrix, complete_features_snapshot = self.prepare_feature_vector(vitals_input)

        try:
            probabilities = self.model.predict_proba(feature_matrix)
            # Sepsis positive class probability (index 1)
            probability = float(probabilities[0][1])
        except Exception as e:
            raise ModelError(f"Prediction inference failed: {str(e)}")

        # Determine Risk Category from Configurable Thresholds
        if probability < LOW_THRESHOLD:
            risk_category = "Low"
        elif probability < HIGH_THRESHOLD:
            risk_category = "Moderate"
        else:
            risk_category = "High"

        return {
            "model_version": self.model_version,
            "model_probability": round(probability, 5),
            "model_risk_score_percent": round(probability * 100, 1),
            "risk_category": risk_category,
            "input_features_snapshot": complete_features_snapshot
        }

# Global Service Singleton
ml_service_instance = MLService()
