import os
import sys
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.auth import auth_bp
from src.routes.api import api_bp

# Import new models to ensure they are created
from src.notifications import Notification
from src.order_tracking import OrderTracking

# DON'T CHANGE THE FOLLOWING LINES
# This is to ensure that the application can be run from the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.append(project_root)
# DON'T CHANGE THE ABOVE LINES

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///livreure.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "livreure-mauritania-secret-2024")

db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(api_bp, url_prefix="/api")

# Register new API blueprints
from src.routes.notifications_api import notifications_bp
from src.routes.tracking_api import tracking_bp

app.register_blueprint(notifications_bp, url_prefix="/api")
app.register_blueprint(tracking_bp, url_prefix="/api")

# Serve static files for the frontend
@app.route("/<path:filename>")
def serve_frontend(filename):
    return send_from_directory(os.path.join(project_root), filename)

@app.route("/")
def serve_index():
    return send_from_directory(os.path.join(project_root), "index.html")

@app.route("/admin-dashboard/<path:filename>")
def serve_admin_dashboard(filename):
  return send_from_directory(os.path.join(project_root, "admin-dashboard"), filename)

@app.route("/admin-dashboard/")
def serve_admin_index():
    return send_from_directory(os.path.join(project_root, "admin-dashboard"), "index.html")

@app.route("/api/health")
def health_check():
    return jsonify({"status": "ok", "message": "Backend is running!"}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=os.environ.get("PORT", 5000))

