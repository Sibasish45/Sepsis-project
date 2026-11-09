"""
System Constants and Feature Specifications for Sepsis CDSS.
"""

FEATURE_NAMES = [
    "HR", "O2Sat", "Temp", "SBP", "MAP", "DBP", "Resp",
    "WBC", "Glucose", "Lactate", "Creatinine", "Platelets",
    "Age", "Gender", "ICULOS"
]

# Configurable Risk Category Thresholds
LOW_THRESHOLD = 0.30
HIGH_THRESHOLD = 0.70

# SIRS Criteria Thresholds
SIRS_HR_THRESHOLD = 90.0
SIRS_TEMP_LOW = 36.0
SIRS_TEMP_HIGH = 38.0
SIRS_RESP_THRESHOLD = 20.0
SIRS_WBC_LOW = 4.0
SIRS_WBC_HIGH = 12.0

# System Disclaimer
CLINICAL_DISCLAIMER = "Decision-support output only. Not a clinical diagnosis."
