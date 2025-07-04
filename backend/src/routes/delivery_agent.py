from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.delivery_agent import db, DeliveryAgent
from src.models.order import Order
from datetime import datetime

delivery_agent_bp = Blueprint('delivery_agent', __name__)

# Delivery Agent Authentication
@delivery_agent_bp.route('/delivery-agents/register', methods=['POST'])
def register_delivery_agent():
    try:
        data = request.get_json()
        
        # Check if delivery agent already exists
        existing_agent = DeliveryAgent.query.filter(
            (DeliveryAgent.email == data['email']) | (DeliveryAgent.phone == data['phone'])
        ).first()
        
        if existing_agent:
            return jsonify({'error': 'Delivery agent already exists'}), 400
        
        # Create new delivery agent
        agent = DeliveryAgent(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            password_hash=generate_password_hash(data['password']),
            vehicle_type=data['vehicle_type'],
            vehicle_number=data.get('vehicle_number', ''),
            license_number=data.get('license_number', '')
        )
        
        db.session.add(agent)
        db.session.commit()
        
        return jsonify({
            'message': 'Delivery agent registered successfully',
            'agent': agent.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@delivery_agent_bp.route('/delivery-agents/login', methods=['POST'])
def login_delivery_agent():
    try:
        data = request.get_json()
        agent = DeliveryAgent.query.filter_by(email=data['email']).first()
        
        if agent and check_password_hash(agent.password_hash, data['password']):
            if not agent.is_active:
                return jsonify({'error': 'Delivery agent account is deactivated'}), 403
            if not agent.is_approved:
                return jsonify({'error': 'Delivery agent account is pending approval'}), 403
                
            return jsonify({
                'message': 'Login successful',
                'agent': agent.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delivery Agent Profile Management
@delivery_agent_bp.route('/delivery-agents/<int:agent_id>', methods=['GET'])
def get_delivery_agent(agent_id):
    try:
        agent = DeliveryAgent.query.get_or_404(agent_id)
        return jsonify(agent.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@delivery_agent_bp.route('/delivery-agents/<int:agent_id>', methods=['PUT'])
def update_delivery_agent(agent_id):
    try:
        agent = DeliveryAgent.query.get_or_404(agent_id)
        data = request.get_json()
        
        # Update fields
        for field in ['name', 'phone', 'vehicle_type', 'vehicle_number', 'license_number']:
            if field in data:
                setattr(agent, field, data[field])
        
        agent.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Delivery agent updated successfully',
            'agent': agent.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Availability Management
@delivery_agent_bp.route('/delivery-agents/<int:agent_id>/availability', methods=['PUT'])
def update_availability(agent_id):
    try:
        agent = DeliveryAgent.query.get_or_404(agent_id)
        data = request.get_json()
        
        agent.is_available = data['is_available']
        
        # Update location if provided
        if 'latitude' in data and 'longitude' in data:
            agent.current_latitude = data['latitude']
            agent.current_longitude = data['longitude']
        
        agent.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Availability updated successfully',
            'agent': agent.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@delivery_agent_bp.route('/delivery-agents/<int:agent_id>/location', methods=['PUT'])
def update_location(agent_id):
    try:
        agent = DeliveryAgent.query.get_or_404(agent_id)
        data = request.get_json()
        
        agent.current_latitude = data['latitude']
        agent.current_longitude = data['longitude']
        agent.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Location updated successfully',
            'agent': agent.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Order Management for Delivery Agents
@delivery_agent_bp.route('/delivery-agents/<int:agent_id>/available-orders', methods=['GET'])
def get_available_orders(agent_id):
    try:
        # Get orders that are ready for pickup and don't have a delivery agent assigned
        orders = Order.query.filter_by(
            status='ready',
            delivery_agent_id=None
        ).order_by(Order.created_at.asc()).all()
        
        # Include restaurant and customer info
        orders_data = []
        for order in orders:
            order_dict = order.to_dict()
            order_dict['restaurant'] = order.restaurant.to_dict() if order.restaurant else None
            order_dict['customer_name'] = order.customer.name if order.customer else None
            orders_data.append(order_dict)
        
        return jsonify(orders_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@delivery_agent_bp.route('/delivery-agents/<int:agent_id>/orders', methods=['GET'])
def get_agent_orders(agent_id):
    try:
        status = request.args.get('status')
        query = Order.query.filter_by(delivery_agent_id=agent_id)
        
        if status:
            query = query.filter_by(status=status)
        
        orders = query.order_by(Order.created_at.desc()).all()
        
        # Include restaurant and customer info
        orders_data = []
        for order in orders:
            order_dict = order.to_dict()
            order_dict['restaurant'] = order.restaurant.to_dict() if order.restaurant else None
            order_dict['customer_name'] = order.customer.name if order.customer else None
            orders_data.append(order_dict)
        
        return jsonify(orders_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@delivery_agent_bp.route('/orders/<int:order_id>/accept', methods=['POST'])
def accept_order(order_id):
    try:
        data = request.get_json()
        agent_id = data['agent_id']
        
        order = Order.query.get_or_404(order_id)
        agent = DeliveryAgent.query.get_or_404(agent_id)
        
        # Check if order is still available
        if order.delivery_agent_id is not None:
            return jsonify({'error': 'Order already assigned to another agent'}), 400
        
        if order.status != 'ready':
            return jsonify({'error': 'Order is not ready for pickup'}), 400
        
        # Assign order to agent
        order.delivery_agent_id = agent_id
        order.status = 'picked_up'
        order.picked_up_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order accepted successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@delivery_agent_bp.route('/orders/<int:order_id>/deliver', methods=['POST'])
def deliver_order(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        
        # Update order status
        order.status = 'delivered'
        order.delivered_at = datetime.utcnow()
        order.payment_status = 'paid'  # Assuming cash payment is completed
        
        # Update agent stats
        if order.delivery_agent:
            order.delivery_agent.total_deliveries += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order delivered successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

