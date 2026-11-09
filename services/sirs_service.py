"""
SIRS (Systemic Inflammatory Response Syndrome) Clinical Rules Service.
Evaluates 4 independent clinical SIRS criteria with strict boundary handling.
"""
from utils.constants import (
    SIRS_HR_THRESHOLD, SIRS_TEMP_LOW, SIRS_TEMP_HIGH,
    SIRS_RESP_THRESHOLD, SIRS_WBC_LOW, SIRS_WBC_HIGH
)

class SIRSService:
    def evaluate_sirs(self, vitals_dict):
        """
        Evaluates SIRS criteria score (0-4) and criteria details.
        """
        criteria = {
            "heart_rate": {
                "name": "Heart Rate > 90 bpm",
                "met": False,
                "value": vitals_dict.get("HR")
            },
            "temperature": {
                "name": "Temperature < 36.0°C or > 38.0°C",
                "met": False,
                "value": vitals_dict.get("Temp")
            },
            "respiratory_rate": {
                "name": "Respiratory Rate > 20 breaths/min",
                "met": False,
                "value": vitals_dict.get("Resp")
            },
            "wbc": {
                "name": "WBC < 4.0 or > 12.0 (10^3/uL)",
                "met": False,
                "value": vitals_dict.get("WBC")
            }
        }

        sirs_score = 0

        # 1. Heart Rate Criterion (> 90 bpm)
        hr = vitals_dict.get("HR")
        if hr is not None and hr > SIRS_HR_THRESHOLD:
            criteria["heart_rate"]["met"] = True
            sirs_score += 1

        # 2. Temperature Criterion (< 36.0°C or > 38.0°C)
        temp = vitals_dict.get("Temp")
        if temp is not None and (temp < SIRS_TEMP_LOW or temp > SIRS_TEMP_HIGH):
            criteria["temperature"]["met"] = True
            sirs_score += 1

        # 3. Respiratory Rate Criterion (> 20 breaths/min)
        resp = vitals_dict.get("Resp")
        if resp is not None and resp > SIRS_RESP_THRESHOLD:
            criteria["respiratory_rate"]["met"] = True
            sirs_score += 1

        # 4. WBC Criterion (< 4.0 or > 12.0)
        wbc = vitals_dict.get("WBC")
        if wbc is not None and (wbc < SIRS_WBC_LOW or wbc > SIRS_WBC_HIGH):
            criteria["wbc"]["met"] = True
            sirs_score += 1

        sirs_status = f"SIRS Criteria Met ({sirs_score}/4)" if sirs_score >= 2 else f"SIRS Criteria Negative ({sirs_score}/4)"

        return {
            "sirs_score": sirs_score,
            "sirs_status": sirs_status,
            "criteria_met_count": sirs_score,
            "criteria_total": 4,
            "criteria_breakdown": criteria
        }

sirs_service_instance = SIRSService()
