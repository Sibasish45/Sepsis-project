"""
Custom Exceptions and Error Handlers for Sepsis CDSS API.
"""
from flask import jsonify

class APIError(Exception):
    def __init__(self, message, status_code=400, code="API_ERROR", payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.payload = payload

    def to_dict(self):
        rv = {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message
            }
        }
        if self.payload:
            rv["error"]["details"] = self.payload
        return rv

class ValidationError(APIError):
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=400, code="VALIDATION_ERROR", payload=payload)

class AuthenticationError(APIError):
    def __init__(self, message="Authentication required", payload=None):
        super().__init__(message, status_code=401, code="UNAUTHORIZED", payload=payload)

class ForbiddenError(APIError):
    def __init__(self, message="Access denied", payload=None):
        super().__init__(message, status_code=403, code="FORBIDDEN", payload=payload)

class NotFoundError(APIError):
    def __init__(self, message="Resource not found", payload=None):
        super().__init__(message, status_code=404, code="NOT_FOUND", payload=payload)

class ModelError(APIError):
    def __init__(self, message="Model inference failed", payload=None):
        super().__init__(message, status_code=500, code="MODEL_ERROR", payload=payload)

def register_error_handlers(app):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": "The requested API endpoint was not found."
            }
        }), 404

    @app.errorhandler(500)
    def handle_500(e):
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred."
            }
        }), 500
