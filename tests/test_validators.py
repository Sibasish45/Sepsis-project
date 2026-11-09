"""
Unit Tests for Input Validators (utils/validators.py)
"""
import pytest
from utils.validators import validate_vital_inputs, validate_patient_input
from utils.errors import ValidationError

def test_validator_out_of_range_rejection():
    """Verify out-of-range vitals trigger ValidationError (Level 2 check)."""
    invalid_hr = {"HR": -10.0, "Temp": 37.0, "SBP": 120.0, "Resp": 18.0, "WBC": 7.0}
    with pytest.raises(ValidationError):
        validate_vital_inputs(invalid_hr)

    invalid_o2sat = {"HR": 80.0, "O2Sat": 500.0, "Temp": 37.0, "SBP": 120.0, "Resp": 18.0, "WBC": 7.0}
    with pytest.raises(ValidationError):
        validate_vital_inputs(invalid_o2sat)

def test_validator_valid_inputs():
    """Verify valid vitals pass validation cleanly."""
    valid_payload = {"HR": 85.0, "O2Sat": 98.0, "Temp": 37.2, "SBP": 118.0, "Resp": 18.0, "WBC": 8.0}
    res = validate_vital_inputs(valid_payload)
    assert res["HR"] == 85.0
    assert res["O2Sat"] == 98.0
