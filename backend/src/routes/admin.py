from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.admin import db, Admin
from src.models.customer import Customer
from src.models.restaurant import Restaurant
from src.models.delivery_agent import DeliveryAgent
from src.models.order import Order
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

# Admin Authentication
@admin_bp.route('/admin/login', methods=['POST'])
def login_admin():
    try:
        data = request.get_json()
        admin = Admin.query.filter_by(username=data['username']).first()
        
        if admin and check_password_hash(admin.password_hash, data['password']):
            if not admin.is_active:
                return jsonify({'error': 'Admin account is deactivated'}), 403
                
            # Update last login
            admin.last_login = datetime.utcnow()
            db.session.commit()
                
            return jsonify({
                'message': 'Login successful',
                'admin': admin.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Dashboard Statistics
@admin_bp.route('/admin/dashboard', methods=['GET'])
def get_dashboard_stats():
    try:
        today = datetime.utcnow().date()
        
        # Daily orders
        daily_orders = Order.query.filter(
            func.date(Order.created_at) == today
        ).count()
        
        # Active restaurants
        active_restaurants = Restaurant.query.filter_by(
            is_active=True, 
            is_approved=True
        ).count()
        
        # Available delivery agents
        available_agents = DeliveryAgent.query.filter_by(
            is_active=True,
            is_approved=True,
            is_available=True
        ).count()
        
        # Total revenue (today)
        daily_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            func.date(Order.created_at) == today,
            Order.payment_status == 'paid'
        ).scalar() or 0
        
        # Recent orders
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
        recent_orders_data = []
        for order in recent_orders:
            order_dict = order.to_dict()
            order_dict['customer_name'] = order.customer.name if order.customer else None
            order_dict['restaurant_name'] = order.restaurant.name if order.restaurant else None
            recent_orders_data.append(order_dict)
        
        # Weekly statistics for charts
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_orders = []
        weekly_revenue = []
        
        for i in range(7):
            date = (datetime.utcnow() - timedelta(days=6-i)).date()
            
            orders_count = Order.query.filter(
                func.date(Order.created_at) == date
            ).count()
            
            revenue = db.session.query(func.sum(Order.total_amount)).filter(
                func.date(Order.created_at) == date,
                Order.payment_status == 'paid'
            ).scalar() or 0
            
            weekly_orders.append({
                'date': date.strftime('%Y-%m-%d'),
                'orders': orders_count
            })
            
            weekly_revenue.append({
                'date': date.strftime('%Y-%m-%d'),
                'revenue': float(revenue)
            })
        
        return jsonify({
            'daily_orders': daily_orders,
            'active_restaurants': active_restaurants,
            'available_agents': available_agents,
            'daily_revenue': float(daily_revenue),
            'recent_orders': recent_orders_data,
            'weekly_orders': weekly_orders,
            'weekly_revenue': weekly_revenue
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Restaurant Management
@admin_bp.route('/admin/restaurants', methods=['GET'])
def get_all_restaurants():
    try:
        status = request.args.get('status')  # pending, approved, rejected
        
        query = Restaurant.query
        if status == 'pending':
            query = query.filter_by(is_approved=False, is_active=True)
        elif status == 'approved':
            query = query.filter_by(is_approved=True)
        elif status == 'rejected':
            query = query.filter_by(is_active=False)
        
        restaurants = query.order_by(Restaurant.created_at.desc()).all()
        return jsonify([restaurant.to_dict() for restaurant in restaurants]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/restaurants/<int:restaurant_id>/approve', methods=['POST'])
def approve_restaurant(restaurant_id):
    try:
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        restaurant.is_approved = True
        restaurant.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Restaurant approved successfully',
            'restaurant': restaurant.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/restaurants/<int:restaurant_id>/reject', methods=['POST'])
def reject_restaurant(restaurant_id):
    try:
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        restaurant.is_active = False
        restaurant.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Restaurant rejected successfully',
            'restaurant': restaurant.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delivery Agent Management
@admin_bp.route('/admin/delivery-agents', methods=['GET'])
def get_all_delivery_agents():
    try:
        status = request.args.get('status')  # pending, approved, rejected
        
        query = DeliveryAgent.query
        if status == 'pending':
            query = query.filter_by(is_approved=False, is_active=True)
        elif status == 'approved':
            query = query.filter_by(is_approved=True)
        elif status == 'rejected':
            query = query.filter_by(is_active=False)
        
        agents = query.order_by(DeliveryAgent.created_at.desc()).all()
        return jsonify([agent.to_dict() for agent in agents]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/delivery-agents/<int:agent_id>/approve', methods=['POST'])
def approve_delivery_agent(agent_id):
    try:
        agent = DeliveryAgent.query.get_or_404(agent_id)
        agent.is_approved = True
        agent.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Delivery agent approved successfully',
            'agent': agent.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/delivery-agents/<int:agent_id>/reject', methods=['POST'])
def reject_delivery_agent(agent_id):
    try:
        agent = DeliveryAgent.query.get_or_404(agent_id)
        agent.is_active = False
        agent.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Delivery agent rejected successfully',
            'agent': agent.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Customer Management
@admin_bp.route('/admin/customers', methods=['GET'])
def get_all_customers():
    try:
        customers = Customer.query.order_by(Customer.created_at.desc()).all()
        return jsonify([customer.to_dict() for customer in customers]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Order Management
@admin_bp.route('/admin/orders', methods=['GET'])
def get_all_orders():
    try:
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = Order.query
        
        if status:
            query = query.filter_by(status=status)
        
        if date_from:
            query = query.filter(Order.created_at >= datetime.fromisoformat(date_from))
        
        if date_to:
            query = query.filter(Order.created_at <= datetime.fromisoformat(date_to))
        
        orders = query.order_by(Order.created_at.desc()).all()
        
        # Include related data
        orders_data = []
        for order in orders:
            order_dict = order.to_dict()
            order_dict['customer_name'] = order.customer.name if order.customer else None
            order_dict['restaurant_name'] = order.restaurant.name if order.restaurant else None
            order_dict['delivery_agent_name'] = order.delivery_agent.name if order.delivery_agent else None
            orders_data.append(order_dict)
        
        return jsonify(orders_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Reports
@admin_bp.route('/admin/reports/revenue', methods=['GET'])
def get_revenue_report():
    try:
        period = request.args.get('period', 'week')  # week, month, year
        
        if period == 'week':
            start_date = datetime.utcnow() - timedelta(days=7)
        elif period == 'month':
            start_date = datetime.utcnow() - timedelta(days=30)
        elif period == 'year':
            start_date = datetime.utcnow() - timedelta(days=365)
        else:
            start_date = datetime.utcnow() - timedelta(days=7)
        
        # Total revenue
        total_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= start_date,
            Order.payment_status == 'paid'
        ).scalar() or 0
        
        # Orders count
        total_orders = Order.query.filter(
            Order.created_at >= start_date
        ).count()
        
        # Average order value
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        return jsonify({
            'period': period,
            'total_revenue': float(total_revenue),
            'total_orders': total_orders,
            'average_order_value': float(avg_order_value),
            'start_date': start_date.isoformat(),
            'end_date': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

