"""
Sepsis Prediction API Routes for Sepsis CDSS.
"""
from flask import Blueprint, request, jsonify, session
from services.prediction_service import prediction_service_instance
from utils.security import login_required

prediction_bp = Blueprint("prediction", __name__)

@prediction_bp.route("/api/predict", methods=["POST"])
@login_required
def predict_sepsis():
    """
    Sepsis Risk Prediction & Assessment Endpoint.
    Executes input validation, ML inference, SIRS rules, and transactional persistence.
    """
    raw_data = request.get_json() or {}
    user_id = session.get("user_id")
    ip_addr = request.remote_addr
    u_agent = request.user_agent.string if request.user_agent else None

    result = prediction_service_instance.execute_prediction_pipeline(
        raw_input=raw_data,
        user_id=user_id,
        ip_address=ip_addr,
        user_agent=u_agent
    )

    return jsonify({
        "success": True,
        "message": "Sepsis risk assessment completed.",
        "data": result
    }), 200
