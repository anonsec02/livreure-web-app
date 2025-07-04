from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from src.models.user import db, User
from src.models.customer import Customer
from src.models.restaurant import Restaurant
from src.models.delivery_agent import DeliveryAgent
from src.models.admin import Admin

auth_bp = Blueprint('auth', __name__)

# JWT Secret Key (should be in environment variables in production)
JWT_SECRET = 'your-secret-key-here'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user_id = data['user_id']
            current_user_type = data['user_type']
            
            # Get user based on type
            if current_user_type == 'customer':
                current_user = Customer.query.get(current_user_id)
            elif current_user_type == 'restaurant':
                current_user = Restaurant.query.get(current_user_id)
            elif current_user_type == 'delivery_agent':
                current_user = DeliveryAgent.query.get(current_user_id)
            elif current_user_type == 'admin':
                current_user = Admin.query.get(current_user_id)
            else:
                return jsonify({'success': False, 'message': 'Invalid user type'}), 401
            
            if not current_user:
                return jsonify({'success': False, 'message': 'User not found'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'phone', 'user_type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'{field} is required'
                }), 400
        
        name = data['name']
        email = data['email'].lower()
        password = data['password']
        phone = data['phone']
        user_type = data['user_type']
        
        # Validate user type
        valid_types = ['customer', 'restaurant', 'delivery_agent']
        if user_type not in valid_types:
            return jsonify({
                'success': False,
                'message': 'Invalid user type'
            }), 400
        
        # Check if user already exists
        existing_user = None
        if user_type == 'customer':
            existing_user = Customer.query.filter_by(email=email).first()
        elif user_type == 'restaurant':
            existing_user = Restaurant.query.filter_by(email=email).first()
        elif user_type == 'delivery_agent':
            existing_user = DeliveryAgent.query.filter_by(email=email).first()
        
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'User with this email already exists'
            }), 400
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Create user based on type
        if user_type == 'customer':
            new_user = Customer(
                name=name,
                email=email,
                password=hashed_password,
                phone=phone
            )
        elif user_type == 'restaurant':
            restaurant_name = data.get('restaurant_name', name)
            new_user = Restaurant(
                name=restaurant_name,
                email=email,
                password=hashed_password,
                phone=phone,
                address=data.get('address', ''),
                description=data.get('description', ''),
                category=data.get('category', 'general')
            )
        elif user_type == 'delivery_agent':
            new_user = DeliveryAgent(
                name=name,
                email=email,
                password=hashed_password,
                phone=phone,
                vehicle_type=data.get('vehicle_type', 'motorcycle'),
                license_number=data.get('license_number', '')
            )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generate token
        token = jwt.encode({
            'user_id': new_user.id,
            'user_type': user_type,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'phone': new_user.phone,
                'user_type': user_type
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Registration failed: {str(e)}'
        }), 500

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password') or not data.get('user_type'):
            return jsonify({
                'success': False,
                'message': 'Email, password, and user type are required'
            }), 400
        
        email = data['email'].lower()
        password = data['password']
        user_type = data['user_type']
        
        # Find user based on type
        user = None
        if user_type == 'customer':
            user = Customer.query.filter_by(email=email).first()
        elif user_type == 'restaurant':
            user = Restaurant.query.filter_by(email=email).first()
        elif user_type == 'delivery_agent':
            user = DeliveryAgent.query.filter_by(email=email).first()
        elif user_type == 'admin':
            user = Admin.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
        
        # Generate token
        token = jwt.encode({
            'user_id': user.id,
            'user_type': user_type,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
        }, JWT_SECRET, algorithm='HS256')
        
        # Prepare user data
        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'user_type': user_type
        }
        
        # Add type-specific data
        if user_type == 'restaurant':
            user_data['restaurant_name'] = user.name
            user_data['address'] = getattr(user, 'address', '')
            user_data['is_open'] = getattr(user, 'is_open', True)
        elif user_type == 'delivery_agent':
            user_data['vehicle_type'] = getattr(user, 'vehicle_type', 'motorcycle')
            user_data['is_available'] = getattr(user, 'is_available', False)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': user_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login failed: {str(e)}'
        }), 500

@auth_bp.route('/auth/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    try:
        user_type = request.headers.get('User-Type', 'customer')
        
        user_data = {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email,
            'phone': current_user.phone,
            'user_type': user_type
        }
        
        return jsonify({
            'success': True,
            'user': user_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Token verification failed: {str(e)}'
        }), 500

@auth_bp.route('/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    try:
        # In a real application, you might want to blacklist the token
        # For now, we'll just return a success message
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Logout failed: {str(e)}'
        }), 500

@auth_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400
        
        email = data['email'].lower()
        
        # In a real application, you would:
        # 1. Check if user exists
        # 2. Generate a reset token
        # 3. Send email with reset link
        # For now, we'll just return a success message
        
        return jsonify({
            'success': True,
            'message': 'Password reset instructions sent to your email'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Password reset failed: {str(e)}'
        }), 500

