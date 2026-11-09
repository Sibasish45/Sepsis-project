"""
Authentication & System Utility API Routes for Sepsis CDSS.
"""
import os
from flask import Blueprint, request, jsonify, session
from services.auth_service import auth_service_instance
from services.audit_service import audit_service_instance
from utils.security import login_required, role_required
from utils.errors import ValidationError
from db import USE_SQLITE_FALLBACK
from services.ml_service import ml_service_instance

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring system status."""
    db_status = "sqlite_fallback" if USE_SQLITE_FALLBACK else "connected"
    model_status = "loaded" if ml_service_instance.model is not None else "failed"

    return jsonify({
        "status": "healthy",
        "database": db_status,
        "model": model_status,
        "model_version": ml_service_instance.model_version
    })

@auth_bp.route("/api/session", methods=["GET"])
def get_session():
    """Returns current logged-in user session information."""
    if "user_id" not in session:
        return jsonify({"authenticated": False, "user": None})

    user = auth_service_instance.get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        return jsonify({"authenticated": False, "user": None})

    return jsonify({
        "authenticated": True,
        "user": user
    })

@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    """Staff Login Endpoint."""
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        raise ValidationError("Both username and password are required.")

    user = auth_service_instance.authenticate_user(username, password)

    # Establish Secure Flask Session
    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["user_role"] = user["role"]
    session["full_name"] = user["full_name"]
    session.permanent = True

    # Audit Log
    audit_service_instance.log_event(
        action="LOGIN_SUCCESS",
        user_id=user["id"],
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else None
    )

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "user": user
    })

@auth_bp.route("/api/auth/logout", methods=["POST"])
def logout():
    """Staff Logout Endpoint."""
    user_id = session.get("user_id")
    if user_id:
        audit_service_instance.log_event(
            action="LOGOUT",
            user_id=user_id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string if request.user_agent else None
        )
    session.clear()
    return jsonify({"success": True, "message": "Logout successful."})

@auth_bp.route("/api/auth/register", methods=["POST"])
@login_required
@role_required(["ADMIN"])
def register():
    """Admin-only Staff Registration Endpoint."""
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    role = data.get("role", "NURSE")

    if not username or not email or not password or not full_name:
        raise ValidationError("All fields (username, email, password, full_name) are required.")

    current_role = session.get("user_role", "")
    user = auth_service_instance.register_user(
        username=username,
        email=email,
        password=password,
        full_name=full_name,
        role=role,
        creator_role=current_role
    )

    audit_service_instance.log_event(
        action="USER_CREATED",
        user_id=session["user_id"],
        ip_address=request.remote_addr,
        details={"created_user": username, "role": role}
    )

    return jsonify({
        "success": True,
        "message": f"User '{username}' registered successfully.",
        "data": user
    }), 201
