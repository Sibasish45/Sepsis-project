"""
Patient Management Service for Sepsis CDSS.
Handles patient creation, search, retrieval, and historical vital records fetching.
"""
import uuid
from db import get_db_cursor
from utils.errors import NotFoundError, ValidationError

class PatientService:
    def generate_patient_code(self):
        """Generates unique patient code like PAT-1001."""
        return f"PAT-{str(uuid.uuid4().hex[:6]).upper()}"

    def create_patient(self, name, age, gender, medical_history="", dob=None):
        """Creates a new patient profile."""
        patient_code = self.generate_patient_code()
        
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO patients (patient_code, full_name, age, gender, date_of_birth, medical_history)
                VALUES (%s, %s, %s, %s, %s, %s)
                """ if not hasattr(cursor, 'execute') or 'sqlite3' not in str(type(cursor)) else
                """
                INSERT INTO patients (patient_code, full_name, age, gender, date_of_birth, medical_history)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (patient_code, name, age, gender, dob, medical_history)
            )
            patient_id = cursor.lastrowid

        return self.get_patient_by_id(patient_id)

    def get_patient_by_id(self, patient_id):
        """Retrieves patient by primary key ID."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                "SELECT * FROM patients WHERE id = %s" if not hasattr(cursor, 'execute') or 'sqlite3' not in str(type(cursor)) else
                "SELECT * FROM patients WHERE id = ?",
                (patient_id,)
            )
            patient = cursor.fetchone()
            
        if not patient:
            raise NotFoundError(f"Patient with ID {patient_id} not found.")

        return dict(patient) if isinstance(patient, dict) else dict(zip([col[0] for col in cursor.description], patient))

    def get_patient_by_code(self, patient_code):
        """Retrieves patient by unique code."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                "SELECT * FROM patients WHERE patient_code = %s" if not hasattr(cursor, 'execute') or 'sqlite3' not in str(type(cursor)) else
                "SELECT * FROM patients WHERE patient_code = ?",
                (patient_code,)
            )
            patient = cursor.fetchone()

        if not patient:
            raise NotFoundError(f"Patient code '{patient_code}' not found.")

        return dict(patient) if isinstance(patient, dict) else dict(zip([col[0] for col in cursor.description], patient))

    def list_patients(self, search_query=None, limit=50):
        """Lists patient directory with optional search filter."""
        with get_db_cursor(commit=False) as cursor:
            if search_query:
                param = f"%{search_query}%"
                cursor.execute(
                    """
                    SELECT p.*, 
                           pr.risk_category as last_risk_category, 
                           pr.model_probability as last_model_probability,
                           pr.prediction_time as last_assessment_time
                    FROM patients p
                    LEFT JOIN vital_records vr ON vr.id = (
                        SELECT id FROM vital_records WHERE patient_id = p.id ORDER BY recorded_at DESC LIMIT 1
                    )
                    LEFT JOIN predictions pr ON pr.vital_record_id = vr.id
                    WHERE p.full_name LIKE %s OR p.patient_code LIKE %s
                    ORDER BY p.created_at DESC LIMIT %s
                    """ if not hasattr(cursor, 'execute') or 'sqlite3' not in str(type(cursor)) else
                    """
                    SELECT p.*, 
                           pr.risk_category as last_risk_category, 
                           pr.model_probability as last_model_probability,
                           pr.prediction_time as last_assessment_time
                    FROM patients p
                    LEFT JOIN vital_records vr ON vr.id = (
                        SELECT id FROM vital_records WHERE patient_id = p.id ORDER BY recorded_at DESC LIMIT 1
                    )
                    LEFT JOIN predictions pr ON pr.vital_record_id = vr.id
                    WHERE p.full_name LIKE ? OR p.patient_code LIKE ?
                    ORDER BY p.created_at DESC LIMIT ?
                    """,
                    (param, param, limit)
                )
            else:
                cursor.execute(
                    """
                    SELECT p.*, 
                           pr.risk_category as last_risk_category, 
                           pr.model_probability as last_model_probability,
                           pr.prediction_time as last_assessment_time
                    FROM patients p
                    LEFT JOIN vital_records vr ON vr.id = (
                        SELECT id FROM vital_records WHERE patient_id = p.id ORDER BY recorded_at DESC LIMIT 1
                    )
                    LEFT JOIN predictions pr ON pr.vital_record_id = vr.id
                    ORDER BY p.created_at DESC LIMIT %s
                    """ if not hasattr(cursor, 'execute') or 'sqlite3' not in str(type(cursor)) else
                    """
                    SELECT p.*, 
                           pr.risk_category as last_risk_category, 
                           pr.model_probability as last_model_probability,
                           pr.prediction_time as last_assessment_time
                    FROM patients p
                    LEFT JOIN vital_records vr ON vr.id = (
                        SELECT id FROM vital_records WHERE patient_id = p.id ORDER BY recorded_at DESC LIMIT 1
                    )
                    LEFT JOIN predictions pr ON pr.vital_record_id = vr.id
                    ORDER BY p.created_at DESC LIMIT ?
                    """,
                    (limit,)
                )

            rows = cursor.fetchall()
            results = []
            for r in rows:
                row_dict = dict(r) if isinstance(r, dict) else dict(zip([col[0] for col in cursor.description], r))
                results.append(row_dict)
            return results

    def get_patient_history(self, patient_id):
        """Fetches vital records and prediction history for a patient."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                """
                SELECT vr.*, pr.model_version, pr.model_probability, pr.risk_category, pr.sirs_score, pr.sirs_status, pr.prediction_time
                FROM vital_records vr
                JOIN predictions pr ON pr.vital_record_id = vr.id
                WHERE vr.patient_id = %s
                ORDER BY vr.recorded_at DESC
                """ if not hasattr(cursor, 'execute') or 'sqlite3' not in str(type(cursor)) else
                """
                SELECT vr.*, pr.model_version, pr.model_probability, pr.risk_category, pr.sirs_score, pr.sirs_status, pr.prediction_time
                FROM vital_records vr
                JOIN predictions pr ON pr.vital_record_id = vr.id
                WHERE vr.patient_id = ?
                ORDER BY vr.recorded_at DESC
                """,
                (patient_id,)
            )
            rows = cursor.fetchall()
            history = []
            for r in rows:
                row_dict = dict(r) if isinstance(r, dict) else dict(zip([col[0] for col in cursor.description], r))
                history.append(row_dict)
            return history

patient_service_instance = PatientService()
