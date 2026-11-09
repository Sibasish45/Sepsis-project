"""
Integration Tests for Prediction API (routes/prediction_routes.py)
"""
import pytest
from app import app

@pytest.fixture
def authenticated_client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Perform Admin login
        client.post("/api/auth/login", json={"username": "admin", "password": "Password@123"})
        yield client

def test_prediction_pipeline_end_to_end(authenticated_client):
    """Test full prediction pipeline via API."""
    # 1. Create Patient
    p_res = authenticated_client.post("/api/patients", json={"full_name": "Sepsis Test Patient", "age": 70, "gender": 1})
    patient_id = p_res.get_json()["data"]["id"]

    # 2. Run Prediction
    vitals_payload = {
        "patient_id": patient_id,
        "HR": 115.0,
        "Temp": 39.2,
        "SBP": 85.0,
        "Resp": 24.0,
        "WBC": 16.0,
        "O2Sat": 92.0
    }

    pred_res = authenticated_client.post("/api/predict", json=vitals_payload)
    assert pred_res.status_code == 200
    data = pred_res.get_json()["data"]

    assert "model" in data
    assert "risk_score_percent" in data["model"]
    assert "sirs" in data
    assert data["sirs"]["score"] >= 2
    assert "disclaimer" in data
