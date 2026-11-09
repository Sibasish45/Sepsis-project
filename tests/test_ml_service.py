"""
Unit Tests for ML Inference Service (services/ml_service.py)
"""
import pytest
from services.ml_service import ml_service_instance
from utils.constants import FEATURE_NAMES

def test_ml_service_startup_contract():
    """Verify that ML service loaded model with exactly 15 optimal features matching contract."""
    assert ml_service_instance.model is not None
    assert len(FEATURE_NAMES) == 15
    loaded_features = list(getattr(ml_service_instance.model, "feature_names_in_", []))
    assert loaded_features == FEATURE_NAMES

def test_ml_service_prediction_output():
    """Verify risk prediction outputs valid probability and risk category."""
    sample_vitals = {
        "HR": 115.0,
        "Temp": 39.1,
        "SBP": 88.0,
        "Resp": 24.0,
        "WBC": 15.2,
        "O2Sat": 93.0,
        "Age": 65.0,
        "Gender": 1
    }

    result = ml_service_instance.predict_risk(sample_vitals)

    assert "model_version" in result
    assert "model_probability" in result
    assert 0.0 <= result["model_probability"] <= 1.0
    assert result["risk_category"] in ("Low", "Moderate", "High")
    assert "input_features_snapshot" in result
    assert len(result["input_features_snapshot"]) == 15

