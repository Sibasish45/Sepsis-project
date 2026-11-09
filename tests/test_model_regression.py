"""
Model Regression Verification Tests (tests/test_model_regression.py)
"""
import pytest
from services.ml_service import ml_service_instance

def test_fixed_vector_regression():
    """Verify that a fixed sample vector produces consistent prediction output."""
    fixed_vitals = {
        "HR": 80.0,
        "O2Sat": 98.0,
        "Temp": 37.0,
        "SBP": 120.0,
        "MAP": 80.0,
        "DBP": 70.0,
        "Resp": 16.0,
        "WBC": 7.5,
        "Age": 50.0,
        "Gender": 0
    }

    res1 = ml_service_instance.predict_risk(fixed_vitals)
    res2 = ml_service_instance.predict_risk(fixed_vitals)

    assert res1["model_probability"] == res2["model_probability"]
    assert res1["risk_category"] == res2["risk_category"]
