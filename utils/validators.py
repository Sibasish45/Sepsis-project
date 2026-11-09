"""
Input Validation Module for Sepsis CDSS.
Provides Level 1 (Type), Level 2 (Physiological Range), and Level 3 (Missing Handling) checks.
"""
from utils.errors import ValidationError

# Defined Physiological Bounds for Primary Vitals & Labs
PHYSIOLOGICAL_RANGES = {
    "HR": (1.0, 300.0, "Heart Rate (bpm) must be between 1 and 300"),
    "O2Sat": (0.0, 100.0, "Oxygen Saturation (%) must be between 0 and 100"),
    "Temp": (20.0, 45.0, "Temperature (°C) must be between 20 and 45"),
    "SBP": (10.0, 300.0, "Systolic BP (mmHg) must be between 10 and 300"),
    "MAP": (10.0, 250.0, "Mean Arterial Pressure (mmHg) must be between 10 and 250"),
    "DBP": (5.0, 200.0, "Diastolic BP (mmHg) must be between 5 and 200"),
    "Resp": (1.0, 100.0, "Respiratory Rate (breaths/min) must be between 1 and 100"),
    "WBC": (0.01, 200.0, "White Blood Cell count (10^3/uL) must be between 0.01 and 200"),
    "Glucose": (1.0, 1500.0, "Glucose (mg/dL) must be between 1 and 1500"),
    "Age": (0.0, 120.0, "Age (years) must be between 0 and 120"),
    "Gender": (0, 1, "Gender must be 0 (Female) or 1 (Male)"),
}

def validate_patient_input(data):
    """
    Validates patient creation data.
    """
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object.")
        
    full_name = data.get("full_name")
    if not full_name or not str(full_name).strip():
        raise ValidationError("Patient full name is required.")
        
    age = data.get("age")
    if age is None:
        raise ValidationError("Patient age is required.")
    try:
        age_val = float(age)
        if age_val < 0 or age_val > 120:
            raise ValidationError("Age must be between 0 and 120 years.")
    except (ValueError, TypeError):
        raise ValidationError("Age must be a valid number.")

    gender = data.get("gender")
    if gender is None:
        raise ValidationError("Patient gender is required.")
    try:
        gender_val = int(gender)
        if gender_val not in (0, 1):
            raise ValidationError("Gender must be 0 (Female) or 1 (Male).")
    except (ValueError, TypeError):
        raise ValidationError("Gender must be 0 or 1.")

    return True

def validate_vital_inputs(data):
    """
    Level 1 & Level 2 validation for vital sign measurements.
    """
    if not isinstance(data, dict):
        raise ValidationError("Vital input payload must be a JSON object.")

    # Primary Required Inputs for Assessment
    required_keys = ["HR", "Temp", "SBP", "Resp", "WBC"]
    for k in required_keys:
        if k not in data or data[k] is None:
            raise ValidationError(f"Required vital parameter '{k}' is missing.")

    # Validate each present numerical input against physiological ranges
    validated_data = {}
    for param, value in data.items():
        if value is None or value == "":
            continue

        # Level 1: Type Validation
        try:
            val_num = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Parameter '{param}' must be a valid numeric value.")

        # Level 2: Physical Validity Check
        if param in PHYSIOLOGICAL_RANGES:
            min_val, max_val, err_msg = PHYSIOLOGICAL_RANGES[param]
            if val_num < min_val or val_num > max_val:
                raise ValidationError(err_msg)

        validated_data[param] = val_num

    return validated_data
