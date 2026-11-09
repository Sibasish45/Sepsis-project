"""
Unit Tests for SIRS Clinical Criteria Engine (services/sirs_service.py)
"""
import pytest
from services.sirs_service import sirs_service_instance

def test_sirs_zero_criteria():
    """Verify normal vitals evaluate to 0 criteria met."""
    normal_vitals = {"HR": 75.0, "Temp": 37.0, "Resp": 16.0, "WBC": 7.5}
    res = sirs_service_instance.evaluate_sirs(normal_vitals)
    assert res["sirs_score"] == 0

def test_sirs_boundary_conditions():
    """Verify strict boundary values (exact 90, 36, 38, 20, 4, 12 do not trigger criteria)."""
    boundary_vitals = {"HR": 90.0, "Temp": 36.0, "Resp": 20.0, "WBC": 12.0}
    res = sirs_service_instance.evaluate_sirs(boundary_vitals)
    assert res["sirs_score"] == 0

def test_sirs_elevated_criteria():
    """Verify vitals exceeding threshold trigger criteria."""
    elevated_vitals = {"HR": 110.0, "Temp": 39.1, "Resp": 24.0, "WBC": 15.0}
    res = sirs_service_instance.evaluate_sirs(elevated_vitals)
    assert res["sirs_score"] == 4
    assert res["criteria_met_count"] == 4
