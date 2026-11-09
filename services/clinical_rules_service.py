"""
Clinical Rules Service for Sepsis CDSS.
Generates non-prescriptive decision-support follow-up indicators.
"""

class ClinicalRulesService:
    def generate_follow_up_indicators(self, ml_output, sirs_output, vitals_dict):
        """
        Builds clinical decision-support follow-up indicators.
        """
        indicators = []

        risk_category = ml_output.get("risk_category")
        prob_percent = ml_output.get("model_risk_score_percent")
        sirs_score = sirs_output.get("sirs_score")

        # 1. Model Risk Assessment Indicator
        if risk_category == "High":
            indicators.append({
                "severity": "high",
                "title": "High Sepsis Risk Score Detected",
                "message": f"ML model score is elevated at {prob_percent}%. Consider prompt clinical assessment according to institutional protocol."
            })
        elif risk_category == "Moderate":
            indicators.append({
                "severity": "medium",
                "title": "Moderate Sepsis Risk Score Detected",
                "message": f"ML model score is {prob_percent}%. Monitor patient vitals closely and reassess per clinical judgment."
            })
        else:
            indicators.append({
                "severity": "low",
                "title": "Low Sepsis Risk Score",
                "message": f"ML model score is low at {prob_percent}%. Routine clinical observation recommended."
            })

        # 2. SIRS Criteria Indicator
        if sirs_score >= 2:
            indicators.append({
                "severity": "high" if sirs_score >= 3 else "medium",
                "title": f"SIRS Criteria Positive ({sirs_score}/4 Met)",
                "message": f"Patient meets {sirs_score} out of 4 SIRS criteria. Review vital sign trends and inflammatory markers."
            })

        # 3. Blood Pressure / Hypotension Warning
        sbp = vitals_dict.get("SBP")
        map_val = vitals_dict.get("MAP")
        if (sbp is not None and sbp < 90.0) or (map_val is not None and map_val < 65.0):
            indicators.append({
                "severity": "high",
                "title": "Hypotension Alert",
                "message": "Systolic BP < 90 mmHg or MAP < 65 mmHg recorded. Evaluate tissue perfusion and hemodynamic status."
            })

        # 4. Elevated Lactate Warning (if present)
        lactate = vitals_dict.get("Lactate")
        if lactate is not None and lactate > 2.0:
            indicators.append({
                "severity": "high" if lactate >= 4.0 else "medium",
                "title": "Elevated Blood Lactate",
                "message": f"Blood lactate level is {lactate} mmol/L. Review laboratory result for potential anaerobic metabolism or hypoperfusion."
            })

        # 5. Hypoxemia Warning
        o2sat = vitals_dict.get("O2Sat")
        if o2sat is not None and o2sat < 92.0:
            indicators.append({
                "severity": "high",
                "title": "Hypoxemia Alert",
                "message": f"Oxygen Saturation is low at {o2sat}%. Assess respiratory support and airway."
            })

        return indicators

clinical_rules_service_instance = ClinicalRulesService()
