from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.restaurant import db, Restaurant, MenuItem
from src.models.order import Order, OrderItem
import uuid
from datetime import datetime

restaurant_bp = Blueprint('restaurant', __name__)

# Restaurant Authentication
@restaurant_bp.route('/restaurants/register', methods=['POST'])
def register_restaurant():
    try:
        data = request.get_json()
        
        # Check if restaurant already exists
        existing_restaurant = Restaurant.query.filter_by(email=data['email']).first()
        if existing_restaurant:
            return jsonify({'error': 'Restaurant already exists'}), 400
        
        # Create new restaurant
        restaurant = Restaurant(
            name=data['name'],
            description=data.get('description', ''),
            address=data['address'],
            phone=data.get('phone', ''),
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            delivery_fee=data.get('delivery_fee', 0.0),
            minimum_order=data.get('minimum_order', 0.0)
        )
        
        db.session.add(restaurant)
        db.session.commit()
        
        return jsonify({
            'message': 'Restaurant registered successfully',
            'restaurant': restaurant.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@restaurant_bp.route('/restaurants/login', methods=['POST'])
def login_restaurant():
    try:
        data = request.get_json()
        restaurant = Restaurant.query.filter_by(email=data['email']).first()
        
        if restaurant and check_password_hash(restaurant.password_hash, data['password']):
            if not restaurant.is_active:
                return jsonify({'error': 'Restaurant account is deactivated'}), 403
            if not restaurant.is_approved:
                return jsonify({'error': 'Restaurant account is pending approval'}), 403
                
            return jsonify({
                'message': 'Login successful',
                'restaurant': restaurant.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Restaurant Profile Management
@restaurant_bp.route('/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    try:
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        return jsonify(restaurant.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@restaurant_bp.route('/restaurants/<int:restaurant_id>', methods=['PUT'])
def update_restaurant(restaurant_id):
    try:
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        data = request.get_json()
        
        # Update fields
        for field in ['name', 'description', 'address', 'phone', 'latitude', 'longitude', 'delivery_fee', 'minimum_order', 'estimated_delivery_time']:
            if field in data:
                setattr(restaurant, field, data[field])
        
        restaurant.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Restaurant updated successfully',
            'restaurant': restaurant.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Menu Management
@restaurant_bp.route('/restaurants/<int:restaurant_id>/menu', methods=['GET'])
def get_menu(restaurant_id):
    try:
        menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
        return jsonify([item.to_dict() for item in menu_items]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@restaurant_bp.route('/restaurants/<int:restaurant_id>/menu', methods=['POST'])
def add_menu_item(restaurant_id):
    try:
        data = request.get_json()
        
        menu_item = MenuItem(
            restaurant_id=restaurant_id,
            name=data['name'],
            description=data.get('description', ''),
            price=data['price'],
            image_url=data.get('image_url', ''),
            category=data.get('category', ''),
            preparation_time=data.get('preparation_time', 15)
        )
        
        db.session.add(menu_item)
        db.session.commit()
        
        return jsonify({
            'message': 'Menu item added successfully',
            'menu_item': menu_item.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@restaurant_bp.route('/menu-items/<int:item_id>', methods=['PUT'])
def update_menu_item(item_id):
    try:
        menu_item = MenuItem.query.get_or_404(item_id)
        data = request.get_json()
        
        # Update fields
        for field in ['name', 'description', 'price', 'image_url', 'category', 'is_available', 'preparation_time']:
            if field in data:
                setattr(menu_item, field, data[field])
        
        menu_item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Menu item updated successfully',
            'menu_item': menu_item.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@restaurant_bp.route('/menu-items/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    try:
        menu_item = MenuItem.query.get_or_404(item_id)
        db.session.delete(menu_item)
        db.session.commit()
        
        return jsonify({'message': 'Menu item deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Order Management for Restaurants
@restaurant_bp.route('/restaurants/<int:restaurant_id>/orders', methods=['GET'])
def get_restaurant_orders(restaurant_id):
    try:
        status = request.args.get('status')
        query = Order.query.filter_by(restaurant_id=restaurant_id)
        
        if status:
            query = query.filter_by(status=status)
        
        orders = query.order_by(Order.created_at.desc()).all()
        
        # Include order items and customer info
        orders_data = []
        for order in orders:
            order_dict = order.to_dict()
            order_dict['items'] = [item.to_dict() for item in order.order_items]
            order_dict['customer_name'] = order.customer.name if order.customer else None
            orders_data.append(order_dict)
        
        return jsonify(orders_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@restaurant_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        new_status = data['status']
        
        # Update status and timestamp
        order.status = new_status
        
        if new_status == 'confirmed':
            order.confirmed_at = datetime.utcnow()
        elif new_status == 'preparing':
            order.confirmed_at = order.confirmed_at or datetime.utcnow()
        elif new_status == 'ready':
            order.prepared_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order status updated successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

