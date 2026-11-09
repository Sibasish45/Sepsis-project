"""
Integration Tests for Patient API (routes/patient_routes.py)
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

def test_patient_crud(authenticated_client):
    """Test patient creation and list retrieval."""
    # 1. Create Patient
    payload = {
        "full_name": "Test Patient Alpha",
        "age": 60,
        "gender": 1,
        "medical_history": "Hypertension"
    }
    create_res = authenticated_client.post("/api/patients", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.get_json()["data"]
    assert created_data["full_name"] == "Test Patient Alpha"
    patient_id = created_data["id"]

    # 2. Retrieve Patient List
    list_res = authenticated_client.get("/api/patients")
    assert list_res.status_code == 200
    assert list_res.get_json()["count"] > 0
