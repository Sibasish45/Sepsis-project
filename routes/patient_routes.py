"""
Patient Directory & Medical History API Routes for Sepsis CDSS.
"""
from flask import Blueprint, request, jsonify, session
from services.patient_service import patient_service_instance
from services.audit_service import audit_service_instance
from utils.security import login_required
from utils.validators import validate_patient_input

patient_bp = Blueprint("patient", __name__)

@patient_bp.route("/api/patients", methods=["GET"])
@login_required
def list_patients():
    """Retrieves list of patients with optional search query."""
    search_q = request.args.get("search")
    patients = patient_service_instance.list_patients(search_query=search_q)
    return jsonify({
        "success": True,
        "count": len(patients),
        "data": patients
    })

@patient_bp.route("/api/patients", methods=["POST"])
@login_required
def create_patient():
    """Creates a new patient profile."""
    data = request.get_json() or {}
    validate_patient_input(data)

    new_patient = patient_service_instance.create_patient(
        name=data["full_name"],
        age=data["age"],
        gender=data["gender"],
        medical_history=data.get("medical_history", ""),
        dob=data.get("date_of_birth")
    )

    audit_service_instance.log_event(
        action="PATIENT_CREATED",
        user_id=session.get("user_id"),
        patient_id=new_patient["id"],
        ip_address=request.remote_addr,
        details={"patient_code": new_patient["patient_code"], "name": new_patient["full_name"]}
    )

    return jsonify({
        "success": True,
        "message": "Patient created successfully.",
        "data": new_patient
    }), 201

@patient_bp.route("/api/patients/<int:patient_id>", methods=["GET"])
@login_required
def get_patient(patient_id):
    """Retrieves patient profile details."""
    patient = patient_service_instance.get_patient_by_id(patient_id)
    return jsonify({
        "success": True,
        "data": patient
    })

@patient_bp.route("/api/patients/<int:patient_id>/vitals", methods=["GET"])
@login_required
def get_patient_vitals_history(patient_id):
    """Retrieves historical vital sign readings and predictions for a patient."""
    history = patient_service_instance.get_patient_history(patient_id)
    return jsonify({
        "success": True,
        "patient_id": patient_id,
        "count": len(history),
        "data": history
    })
