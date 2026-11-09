"""
Main Flask Application for Sepsis Clinical Decision Support System (CDSS).
"""
from flask import Flask, render_template, session, redirect, url_for
from config import Config
from utils.errors import register_error_handlers
from routes.auth_routes import auth_bp
from routes.patient_routes import patient_bp
from routes.prediction_routes import prediction_bp
from routes.dashboard_routes import dashboard_bp
from services.ml_service import ml_service_instance

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.from_object(Config)

# Register Error Handlers
register_error_handlers(app)

# Register API Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(prediction_bp)
app.register_blueprint(dashboard_bp)

@app.route("/")
def index():
    """Main Application View."""
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("index.html")

@app.route("/login")
def login_page():
    """Staff Login View."""
    if "user_id" in session:
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/dataset-viewer")
def dataset_viewer_page():
    """Interactive Dataset Table View."""
    return render_template("dataset_table_viewer.html")


if __name__ == "__main__":
    print(f"Starting Sepsis CDSS Application server...")
    print(f"Model version loaded: {ml_service_instance.model_version}")
    app.run(host="127.0.0.1", port=5000, debug=True)
