from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.customer import db, Customer, CustomerAddress
from src.models.restaurant import Restaurant, MenuItem
from src.models.order import Order, OrderItem
from datetime import datetime, timedelta
import uuid

customer_bp = Blueprint('customer', __name__)

# Customer Authentication
@customer_bp.route('/customers/register', methods=['POST'])
def register_customer():
    try:
        data = request.get_json()
        
        # Check if customer already exists
        existing_customer = Customer.query.filter(
            (Customer.email == data['email']) | (Customer.phone == data['phone'])
        ).first()
        
        if existing_customer:
            return jsonify({'error': 'Customer already exists'}), 400
        
        # Create new customer
        customer = Customer(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            password_hash=generate_password_hash(data['password'])
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'message': 'Customer registered successfully',
            'customer': customer.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers/login', methods=['POST'])
def login_customer():
    try:
        data = request.get_json()
        customer = Customer.query.filter_by(email=data['email']).first()
        
        if customer and check_password_hash(customer.password_hash, data['password']):
            if not customer.is_active:
                return jsonify({'error': 'Customer account is deactivated'}), 403
                
            return jsonify({
                'message': 'Login successful',
                'customer': customer.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Customer Profile Management
@customer_bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        return jsonify(customer.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        # Update fields
        for field in ['name', 'email', 'phone']:
            if field in data:
                setattr(customer, field, data[field])
        
        customer.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Customer updated successfully',
            'customer': customer.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Address Management
@customer_bp.route('/customers/<int:customer_id>/addresses', methods=['GET'])
def get_customer_addresses(customer_id):
    try:
        addresses = CustomerAddress.query.filter_by(customer_id=customer_id).all()
        return jsonify([address.to_dict() for address in addresses]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers/<int:customer_id>/addresses', methods=['POST'])
def add_customer_address(customer_id):
    try:
        data = request.get_json()
        
        # If this is set as default, unset other defaults
        if data.get('is_default', False):
            CustomerAddress.query.filter_by(customer_id=customer_id, is_default=True).update({'is_default': False})
        
        address = CustomerAddress(
            customer_id=customer_id,
            title=data['title'],
            address=data['address'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            is_default=data.get('is_default', False)
        )
        
        db.session.add(address)
        db.session.commit()
        
        return jsonify({
            'message': 'Address added successfully',
            'address': address.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Restaurant Discovery
@customer_bp.route('/restaurants', methods=['GET'])
def get_restaurants():
    try:
        # Get query parameters
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        search = request.args.get('search', '')
        
        # Base query for active and approved restaurants
        query = Restaurant.query.filter_by(is_active=True, is_approved=True)
        
        # Add search filter
        if search:
            query = query.filter(Restaurant.name.contains(search))
        
        restaurants = query.all()
        
        # TODO: Add distance calculation if coordinates provided
        # For now, return all restaurants
        
        return jsonify([restaurant.to_dict() for restaurant in restaurants]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/restaurants/<int:restaurant_id>/menu', methods=['GET'])
def get_restaurant_menu(restaurant_id):
    try:
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id, is_available=True).all()
        
        return jsonify({
            'restaurant': restaurant.to_dict(),
            'menu_items': [item.to_dict() for item in menu_items]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Order Management
@customer_bp.route('/customers/<int:customer_id>/orders', methods=['POST'])
def create_order(customer_id):
    try:
        data = request.get_json()
        
        # Generate unique order number
        order_number = f"LVR{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        # Calculate estimated delivery time
        estimated_delivery = datetime.utcnow() + timedelta(minutes=data.get('estimated_delivery_time', 30))
        
        # Create order
        order = Order(
            customer_id=customer_id,
            restaurant_id=data['restaurant_id'],
            order_number=order_number,
            subtotal=data['subtotal'],
            delivery_fee=data['delivery_fee'],
            tax_amount=data.get('tax_amount', 0.0),
            total_amount=data['total_amount'],
            delivery_address=data['delivery_address'],
            delivery_latitude=data.get('delivery_latitude'),
            delivery_longitude=data.get('delivery_longitude'),
            delivery_notes=data.get('delivery_notes', ''),
            payment_method=data['payment_method'],
            estimated_delivery_time=estimated_delivery
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Add order items
        for item_data in data['items']:
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item_data['menu_item_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price'],
                special_instructions=item_data.get('special_instructions', '')
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers/<int:customer_id>/orders', methods=['GET'])
def get_customer_orders(customer_id):
    try:
        orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).all()
        
        # Include order items and restaurant info
        orders_data = []
        for order in orders:
            order_dict = order.to_dict()
            order_dict['items'] = [item.to_dict() for item in order.order_items]
            order_dict['restaurant_name'] = order.restaurant.name if order.restaurant else None
            orders_data.append(order_dict)
        
        return jsonify(orders_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order_details(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        
        order_dict = order.to_dict()
        order_dict['items'] = [item.to_dict() for item in order.order_items]
        order_dict['restaurant'] = order.restaurant.to_dict() if order.restaurant else None
        order_dict['delivery_agent'] = order.delivery_agent.to_dict() if order.delivery_agent else None
        
        return jsonify(order_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

