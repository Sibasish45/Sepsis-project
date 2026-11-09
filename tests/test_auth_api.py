"""
Integration Tests for Authentication API (routes/auth_routes.py)
"""
import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Verify GET /api/health returns 200 and healthy status."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"

def test_login_failure(client):
    """Verify invalid login attempt returns 401."""
    res = client.post("/api/auth/login", json={"username": "wrong", "password": "bad"})
    assert res.status_code == 401

def test_login_success(client):
    """Verify valid login attempt returns 200."""
    res = client.post("/api/auth/login", json={"username": "admin", "password": "Password@123"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
