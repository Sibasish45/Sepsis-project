"""
Prediction Orchestration Service for Sepsis CDSS.
Coordinates Validation -> ML Inference -> SIRS Evaluation -> Clinical Rules -> Atomic DB Persistence & Audit.
"""
import json
from db import get_db_cursor
from utils.validators import validate_vital_inputs
from utils.constants import CLINICAL_DISCLAIMER
from services.patient_service import patient_service_instance
from services.ml_service import ml_service_instance
from services.sirs_service import sirs_service_instance
from services.clinical_rules_service import clinical_rules_service_instance
from services.audit_service import audit_service_instance

class PredictionService:
    def execute_prediction_pipeline(self, raw_input, user_id, ip_address=None, user_agent=None):
        """
        Executes complete transactional prediction workflow.
        """
        patient_id = raw_input.get("patient_id")
        if not patient_id:
            from utils.errors import ValidationError
            raise ValidationError("patient_id is required for assessment.")

        # 1. Verify Patient Existence & Fetch Patient Demographics
        patient = patient_service_instance.get_patient_by_id(patient_id)
        
        # Merge patient demographics (Age, Gender) into vitals payload if not provided
        vitals_payload = dict(raw_input)
        if "Age" not in vitals_payload or vitals_payload["Age"] is None:
            vitals_payload["Age"] = patient["age"]
        if "Gender" not in vitals_payload or vitals_payload["Gender"] is None:
            vitals_payload["Gender"] = patient["gender"]

        # 2. Level 1 & Level 2 Input Validation
        validated_vitals = validate_vital_inputs(vitals_payload)

        # 3. Execute ML Risk Model Inference
        ml_result = ml_service_instance.predict_risk(validated_vitals)

        # 4. Execute SIRS Criteria Evaluation
        sirs_result = sirs_service_instance.evaluate_sirs(validated_vitals)

        # 5. Generate Clinical Follow-Up Indicators
        follow_up_indicators = clinical_rules_service_instance.generate_follow_up_indicators(
            ml_result, sirs_result, validated_vitals
        )

        # 6. Atomic Database Transaction
        input_json_str = json.dumps(ml_result["input_features_snapshot"])

        with get_db_cursor(commit=True) as cursor:
            # Step 6a: Insert Vital Record
            cursor.execute(
                """
                INSERT INTO vital_records (
                    patient_id, recorded_by, hr, o2sat, temp, sbp, map_val, dbp, resp, wbc, glucose, iculos, input_features_json
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """ if not hasattr(cursor, 'execute') or 'sqlite3' not in str(type(cursor)) else
                """
                INSERT INTO vital_records (
                    patient_id, recorded_by, hr, o2sat, temp, sbp, map_val, dbp, resp, wbc, glucose, iculos, input_features_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    patient_id,
                    user_id,
                    validated_vitals.get("HR"),
                    validated_vitals.get("O2Sat"),
                    validated_vitals.get("Temp"),
                    validated_vitals.get("SBP"),
                    validated_vitals.get("MAP"),
                    validated_vitals.get("DBP"),
                    validated_vitals.get("Resp"),
                    validated_vitals.get("WBC"),
                    validated_vitals.get("Glucose"),
                    validated_vitals.get("ICULOS"),
                    input_json_str
                )
            )
            vital_record_id = cursor.lastrowid

            # Step 6b: Insert Prediction Output
            cursor.execute(
                """
                INSERT INTO predictions (
                    vital_record_id, model_version, model_probability, risk_category, sirs_score, sirs_status
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """ if not hasattr(cursor, 'execute') or 'sqlite3' not in str(type(cursor)) else
                """
                INSERT INTO predictions (
                    vital_record_id, model_version, model_probability, risk_category, sirs_score, sirs_status
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    vital_record_id,
                    ml_result["model_version"],
                    ml_result["model_probability"],
                    ml_result["risk_category"],
                    sirs_result["sirs_score"],
                    sirs_result["sirs_status"]
                )
            )
            prediction_id = cursor.lastrowid

        # 7. Record System Audit Log
        audit_service_instance.log_event(
            action="PREDICTION_GENERATED",
            user_id=user_id,
            patient_id=patient_id,
            vital_record_id=vital_record_id,
            prediction_id=prediction_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "risk_category": ml_result["risk_category"],
                "model_probability": ml_result["model_probability"],
                "sirs_score": sirs_result["sirs_score"]
            }
        )

        # 8. Structure Standardized API Response Payload
        return {
            "prediction_id": prediction_id,
            "vital_record_id": vital_record_id,
            "patient": {
                "id": patient["id"],
                "patient_code": patient["patient_code"],
                "full_name": patient["full_name"],
                "age": patient["age"],
                "gender": patient["gender"]
            },
            "model": {
                "version": ml_result["model_version"],
                "risk_score_probability": ml_result["model_probability"],
                "risk_score_percent": ml_result["model_risk_score_percent"],
                "risk_category": ml_result["risk_category"]
            },
            "sirs": {
                "score": sirs_result["sirs_score"],
                "total": sirs_result["criteria_total"],
                "status": sirs_result["sirs_status"],
                "criteria_breakdown": sirs_result["criteria_breakdown"]
            },
            "follow_up_indicators": follow_up_indicators,
            "disclaimer": CLINICAL_DISCLAIMER
        }

prediction_service_instance = PredictionService()
