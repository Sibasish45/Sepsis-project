"""
Dashboard Analytics API Routes for Sepsis CDSS.
"""
from flask import Blueprint, jsonify
from db import get_db_cursor
from utils.security import login_required

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/api/dashboard/stats", methods=["GET"])
@login_required
def get_dashboard_stats():
    """Returns system aggregate metrics and recent high-risk alert feed."""
    with get_db_cursor(commit=False) as cursor:
        # Total Patients
        cursor.execute("SELECT COUNT(*) as count FROM patients")
        total_patients = cursor.fetchone()
        total_patients_count = list(total_patients.values())[0] if isinstance(total_patients, dict) else total_patients[0]

        # Total Assessments
        cursor.execute("SELECT COUNT(*) as count FROM predictions")
        total_assessments = cursor.fetchone()
        total_assessments_count = list(total_assessments.values())[0] if isinstance(total_assessments, dict) else total_assessments[0]

        # High Risk Assessments
        cursor.execute("SELECT COUNT(*) as count FROM predictions WHERE risk_category = 'High'")
        high_risk_assessments = cursor.fetchone()
        high_risk_count = list(high_risk_assessments.values())[0] if isinstance(high_risk_assessments, dict) else high_risk_assessments[0]

        # SIRS Positive Cases (>= 2)
        cursor.execute("SELECT COUNT(*) as count FROM predictions WHERE sirs_score >= 2")
        sirs_positive = cursor.fetchone()
        sirs_positive_count = list(sirs_positive.values())[0] if isinstance(sirs_positive, dict) else sirs_positive[0]

        # Risk Category Distribution
        cursor.execute("SELECT risk_category, COUNT(*) as count FROM predictions GROUP BY risk_category")
        dist_rows = cursor.fetchall()
        distribution = {"Low": 0, "Moderate": 0, "High": 0}
        for r in dist_rows:
            row_dict = dict(r) if isinstance(r, dict) else dict(zip([col[0] for col in cursor.description], r))
            category = row_dict.get("risk_category")
            if category in distribution:
                distribution[category] = row_dict.get("count", 0)

        # Recent High/Moderate Risk Alert Feed (last 10)
        cursor.execute(
            """
            SELECT pr.id as prediction_id, pr.model_probability, pr.risk_category, pr.sirs_score, pr.sirs_status, pr.prediction_time,
                   p.patient_code, p.full_name, p.id as patient_id
            FROM predictions pr
            JOIN vital_records vr ON vr.id = pr.vital_record_id
            JOIN patients p ON p.id = vr.patient_id
            ORDER BY pr.prediction_time DESC LIMIT 10
            """
        )
        recent_rows = cursor.fetchall()
        alerts = []
        for r in recent_rows:
            alerts.append(dict(r) if isinstance(r, dict) else dict(zip([col[0] for col in cursor.description], r)))

    return jsonify({
        "success": True,
        "data": {
            "total_patients": total_patients_count,
            "total_assessments": total_assessments_count,
            "high_risk_count": high_risk_count,
            "sirs_positive_count": sirs_positive_count,
            "distribution": distribution,
            "recent_alerts": alerts
        }
    })
