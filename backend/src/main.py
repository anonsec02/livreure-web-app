import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.auth import auth_bp
from src.routes.api import api_bp
from src.routes.user import user_bp
from src.routes.customer import customer_bp
from src.routes.restaurant import restaurant_bp
from src.routes.delivery_agent import delivery_agent_bp
from src.routes.admin import admin_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes with specific configuration
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(customer_bp, url_prefix='/api')
app.register_blueprint(restaurant_bp, url_prefix='/api')
app.register_blueprint(delivery_agent_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

# Database configuration
database_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
os.makedirs(os.path.dirname(database_path), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Import all models to ensure they are registered
from src.models.customer import Customer, CustomerAddress
from src.models.restaurant import Restaurant, MenuItem
from src.models.delivery_agent import DeliveryAgent
from src.models.order import Order, OrderItem
from src.models.admin import Admin

# Create database tables
with app.app_context():
    db.create_all()
    
    # Create default admin user if not exists
    admin = Admin.query.filter_by(email='admin@livreure.mr').first()
    if not admin:
        from werkzeug.security import generate_password_hash
        admin = Admin(
            username='admin',
            full_name='مدير النظام',
            email='admin@livreure.mr',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: admin@livreure.mr / admin123")

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'message': 'Livreure API is running',
        'version': '2.0.0'
    }), 200

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    static_folder_path = app.static_folder
    if static_folder_path and os.path.exists(os.path.join(static_folder_path, filename)):
        return send_from_directory(static_folder_path, filename)
    return jsonify({'error': 'File not found'}), 404

# Default route for API
@app.route('/api/', methods=['GET'])
def api_info():
    return jsonify({
        'success': True,
        'message': 'Welcome to Livreure API',
        'version': '2.0.0',
        'endpoints': {
            'auth': '/api/auth/*',
            'restaurants': '/api/restaurants',
            'orders': '/api/orders',
            'customer': '/api/customer/*',
            'restaurant': '/api/restaurant/*',
            'delivery': '/api/delivery/*',
            'admin': '/api/admin/*'
        }
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'message': 'Bad request'
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'message': 'Unauthorized'
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'message': 'Forbidden'
    }), 403

if __name__ == '__main__':
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Livreure API server on port {port}")
    print(f"Debug mode: {debug}")
    print(f"Database: {database_path}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

