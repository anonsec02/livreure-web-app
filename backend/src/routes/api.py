from flask import Blueprint, request, jsonify
from src.routes.auth import token_required
from src.models.user import db
from src.models.customer import Customer
from src.models.restaurant import Restaurant, MenuItem
from src.models.delivery_agent import DeliveryAgent
from src.models.order import Order, OrderItem
from sqlalchemy import func, desc
import datetime

api_bp = Blueprint('api', __name__)

# Restaurant endpoints
@api_bp.route('/restaurants', methods=['GET'])
def get_restaurants():
    try:
        # Get query parameters
        category = request.args.get('category')
        search = request.args.get('search')
        is_open = request.args.get('is_open')
        
        # Build query
        query = Restaurant.query
        
        if category and category != 'all':
            query = query.filter(Restaurant.category.ilike(f'%{category}%'))
        
        if search:
            query = query.filter(
                Restaurant.name.ilike(f'%{search}%') |
                Restaurant.description.ilike(f'%{search}%')
            )
        
        if is_open == 'true':
            query = query.filter(Restaurant.is_open == True)
        
        restaurants = query.all()
        
        restaurants_data = []
        for restaurant in restaurants:
            # Calculate average rating (mock data for now)
            avg_rating = 4.5  # In real app, calculate from reviews
            
            restaurants_data.append({
                'id': restaurant.id,
                'name': restaurant.name,
                'description': restaurant.description,
                'category': restaurant.category,
                'address': restaurant.address,
                'phone': restaurant.phone,
                'is_open': restaurant.is_open,
                'rating': avg_rating,
                'delivery_time': '30-45',  # Mock data
                'delivery_fee': 100,  # Mock data
                'image': f'/static/images/restaurants/{restaurant.id}.jpg'
            })
        
        return jsonify({
            'success': True,
            'restaurants': restaurants_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch restaurants: {str(e)}'
        }), 500

@api_bp.route('/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant_details(restaurant_id):
    try:
        restaurant = Restaurant.query.get(restaurant_id)
        
        if not restaurant:
            return jsonify({
                'success': False,
                'message': 'Restaurant not found'
            }), 404
        
        # Get menu items
        menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
        
        menu_data = []
        for item in menu_items:
            menu_data.append({
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': float(item.price),
                'category': item.category,
                'is_available': item.is_available,
                'image': f'/static/images/menu/{item.id}.jpg'
            })
        
        restaurant_data = {
            'id': restaurant.id,
            'name': restaurant.name,
            'description': restaurant.description,
            'category': restaurant.category,
            'address': restaurant.address,
            'phone': restaurant.phone,
            'is_open': restaurant.is_open,
            'rating': 4.5,  # Mock data
            'delivery_time': '30-45',
            'delivery_fee': 100,
            'image': f'/static/images/restaurants/{restaurant.id}.jpg',
            'menu_items': menu_data
        }
        
        return jsonify({
            'success': True,
            'restaurant': restaurant_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch restaurant details: {str(e)}'
        }), 500

# Order endpoints
@api_bp.route('/orders', methods=['POST'])
@token_required
def create_order(current_user):
    try:
        data = request.get_json()
        
        if not data.get('items') or not data.get('total'):
            return jsonify({
                'success': False,
                'message': 'Items and total are required'
            }), 400
        
        # Create order
        new_order = Order(
            customer_id=current_user.id,
            restaurant_id=data.get('restaurant_id', 1),  # Default restaurant
            total_amount=float(data['total']),
            delivery_address=data.get('delivery_address', current_user.address if hasattr(current_user, 'address') else ''),
            status='pending',
            created_at=datetime.datetime.utcnow()
        )
        
        db.session.add(new_order)
        db.session.flush()  # Get the order ID
        
        # Add order items
        for item in data['items']:
            order_item = OrderItem(
                order_id=new_order.id,
                menu_item_id=item['id'],
                quantity=item['quantity'],
                price=float(item['price'])
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order_id': new_order.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to create order: {str(e)}'
        }), 500

@api_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@token_required
def update_order_status(current_user, order_id):
    try:
        data = request.get_json()
        
        if not data.get('status'):
            return jsonify({
                'success': False,
                'message': 'Status is required'
            }), 400
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        # Update order status
        order.status = data['status']
        order.updated_at = datetime.datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order status updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update order status: {str(e)}'
        }), 500

# Restaurant management endpoints
@api_bp.route('/restaurant/stats', methods=['GET'])
@token_required
def get_restaurant_stats(current_user):
    try:
        today = datetime.date.today()
        
        # Get today's orders
        today_orders = Order.query.filter(
            Order.restaurant_id == current_user.id,
            func.date(Order.created_at) == today
        ).count()
        
        # Get pending orders
        pending_orders = Order.query.filter(
            Order.restaurant_id == current_user.id,
            Order.status == 'pending'
        ).count()
        
        # Get today's revenue
        today_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            Order.restaurant_id == current_user.id,
            func.date(Order.created_at) == today,
            Order.status.in_(['completed', 'delivered'])
        ).scalar() or 0
        
        stats = {
            'today_orders': today_orders,
            'pending_orders': pending_orders,
            'today_revenue': float(today_revenue),
            'rating': 4.8  # Mock data
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch restaurant stats: {str(e)}'
        }), 500

@api_bp.route('/restaurant/orders', methods=['GET'])
@token_required
def get_restaurant_orders(current_user):
    try:
        status_filter = request.args.get('status')
        
        query = Order.query.filter(Order.restaurant_id == current_user.id)
        
        if status_filter and status_filter != 'all':
            query = query.filter(Order.status == status_filter)
        
        orders = query.order_by(desc(Order.created_at)).limit(50).all()
        
        orders_data = []
        for order in orders:
            # Get customer info
            customer = Customer.query.get(order.customer_id)
            
            # Get order items
            order_items = OrderItem.query.filter_by(order_id=order.id).all()
            items_data = []
            
            for item in order_items:
                menu_item = MenuItem.query.get(item.menu_item_id)
                items_data.append({
                    'name': menu_item.name if menu_item else 'Unknown Item',
                    'quantity': item.quantity,
                    'price': float(item.price)
                })
            
            orders_data.append({
                'id': order.id,
                'customer_name': customer.name if customer else 'Unknown Customer',
                'total': float(order.total_amount),
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'delivery_address': order.delivery_address,
                'items': items_data
            })
        
        return jsonify({
            'success': True,
            'orders': orders_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch restaurant orders: {str(e)}'
        }), 500

@api_bp.route('/restaurant/status', methods=['PUT'])
@token_required
def update_restaurant_status(current_user):
    try:
        data = request.get_json()
        
        if 'is_open' not in data:
            return jsonify({
                'success': False,
                'message': 'is_open status is required'
            }), 400
        
        current_user.is_open = data['is_open']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Restaurant status updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update restaurant status: {str(e)}'
        }), 500

# Delivery agent endpoints
@api_bp.route('/delivery/stats', methods=['GET'])
@token_required
def get_delivery_stats(current_user):
    try:
        today = datetime.date.today()
        
        # Get completed deliveries today
        completed_deliveries = Order.query.filter(
            Order.delivery_agent_id == current_user.id,
            func.date(Order.updated_at) == today,
            Order.status == 'delivered'
        ).count()
        
        # Calculate today's earnings (mock calculation)
        today_earnings = completed_deliveries * 150  # 150 ouguiya per delivery
        
        stats = {
            'completed_deliveries': completed_deliveries,
            'today_earnings': today_earnings,
            'rating': 4.9,  # Mock data
            'avg_delivery_time': 18  # Mock data
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch delivery stats: {str(e)}'
        }), 500

@api_bp.route('/delivery/available-orders', methods=['GET'])
@token_required
def get_available_orders(current_user):
    try:
        # Get orders that are ready for delivery
        orders = Order.query.filter(
            Order.status == 'ready',
            Order.delivery_agent_id.is_(None)
        ).order_by(Order.created_at).limit(20).all()
        
        orders_data = []
        for order in orders:
            # Get restaurant and customer info
            restaurant = Restaurant.query.get(order.restaurant_id)
            customer = Customer.query.get(order.customer_id)
            
            orders_data.append({
                'id': order.id,
                'restaurant_name': restaurant.name if restaurant else 'Unknown Restaurant',
                'customer_name': customer.name if customer else 'Unknown Customer',
                'delivery_address': order.delivery_address,
                'total': float(order.total_amount),
                'delivery_fee': 150,  # Mock data
                'distance': 2.5,  # Mock data
                'created_at': order.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'orders': orders_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch available orders: {str(e)}'
        }), 500

@api_bp.route('/delivery/accept-order/<int:order_id>', methods=['POST'])
@token_required
def accept_delivery_order(current_user, order_id):
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        if order.delivery_agent_id:
            return jsonify({
                'success': False,
                'message': 'Order already assigned to another delivery agent'
            }), 400
        
        # Assign order to delivery agent
        order.delivery_agent_id = current_user.id
        order.status = 'out_for_delivery'
        order.updated_at = datetime.datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order accepted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to accept order: {str(e)}'
        }), 500

@api_bp.route('/delivery/status', methods=['PUT'])
@token_required
def update_delivery_status(current_user):
    try:
        data = request.get_json()
        
        if 'is_available' not in data:
            return jsonify({
                'success': False,
                'message': 'is_available status is required'
            }), 400
        
        current_user.is_available = data['is_available']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Delivery status updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update delivery status: {str(e)}'
        }), 500

# Customer endpoints
@api_bp.route('/customer/orders', methods=['GET'])
@token_required
def get_customer_orders(current_user):
    try:
        orders = Order.query.filter(
            Order.customer_id == current_user.id
        ).order_by(desc(Order.created_at)).limit(50).all()
        
        orders_data = []
        for order in orders:
            # Get restaurant info
            restaurant = Restaurant.query.get(order.restaurant_id)
            
            # Get order items
            order_items = OrderItem.query.filter_by(order_id=order.id).all()
            items_data = []
            
            for item in order_items:
                menu_item = MenuItem.query.get(item.menu_item_id)
                items_data.append({
                    'name': menu_item.name if menu_item else 'Unknown Item',
                    'quantity': item.quantity,
                    'price': float(item.price)
                })
            
            orders_data.append({
                'id': order.id,
                'restaurant_name': restaurant.name if restaurant else 'Unknown Restaurant',
                'total': float(order.total_amount),
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'delivery_address': order.delivery_address,
                'items': items_data
            })
        
        return jsonify({
            'success': True,
            'orders': orders_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch customer orders: {str(e)}'
        }), 500

