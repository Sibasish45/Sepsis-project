"""
Security and Session Authorization Decorators for Sepsis CDSS.
"""
from functools import wraps
from flask import session, request
from utils.errors import AuthenticationError, ForbiddenError

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            raise AuthenticationError("Authentication session expired or invalid.")
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    """
    Decorator to restrict API route access to specific roles.
    e.g. @role_required(['ADMIN', 'DOCTOR'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                raise AuthenticationError("Authentication session required.")
            user_role = session.get("user_role")
            if user_role not in allowed_roles:
                raise ForbiddenError(f"Action requires one of the following roles: {', '.join(allowed_roles)}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator
