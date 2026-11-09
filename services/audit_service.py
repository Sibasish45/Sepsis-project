"""
System Audit Service for Sepsis CDSS.
Logs security, user authentication, patient modifications, and assessment calculations.
"""
import json
from db import get_db_cursor

class AuditService:
    def log_event(self, action, user_id=None, patient_id=None, vital_record_id=None, prediction_id=None, ip_address=None, user_agent=None, details=None):
        """
        Inserts audit record into audit_logs table.
        """
        details_str = json.dumps(details) if isinstance(details, (dict, list)) else details

        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute(
                    """
                    INSERT INTO audit_logs (user_id, action, patient_id, vital_record_id, prediction_id, ip_address, user_agent, details)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """ if not hasattr(cursor, 'execute') or 'sqlite3' not in str(type(cursor)) else
                    """
                    INSERT INTO audit_logs (user_id, action, patient_id, vital_record_id, prediction_id, ip_address, user_agent, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, action, patient_id, vital_record_id, prediction_id, ip_address, user_agent, details_str)
                )
        except Exception as e:
            print(f"Audit log insertion failed: {e}")

audit_service_instance = AuditService()