"""
Order Tracking API Routes
مسارات API لتتبع الطلبات
"""

from flask import Blueprint, request, jsonify
from src.routes.auth import token_required
from src.order_tracking import OrderTrackingService
from src.models.order import Order
from src.security_enhancements import rate_limit, sanitize_input

tracking_bp = Blueprint('tracking', __name__)

@tracking_bp.route('/orders/<int:order_id>/status', methods=['GET'])
@token_required
@rate_limit(max_requests=60, window_minutes=1)
def get_order_status(current_user, current_user_type, order_id):
    """
    Get current order status and tracking information
    الحصول على حالة الطلب الحالية ومعلومات التتبع
    """
    try:
        # Verify user has access to this order
        order = Order.query.get(order_id)
        if not order:
            return jsonify({
                'success': False,
                'message': 'الطلب غير موجود'
            }), 404
        
        # Check permissions
        has_access = False
        if current_user_type == 'customer' and order.customer_id == current_user.id:
            has_access = True
        elif current_user_type == 'restaurant' and order.restaurant_id == current_user.id:
            has_access = True
        elif current_user_type == 'delivery_agent' and order.delivery_agent_id == current_user.id:
            has_access = True
        elif current_user_type == 'admin':
            has_access = True
        
        if not has_access:
            return jsonify({
                'success': False,
                'message': 'غير مصرح لك بالوصول لهذا الطلب'
            }), 403
        
        # Get status information
        status_info = OrderTrackingService.get_current_order_status(order_id)
        
        if status_info:
            return jsonify({
                'success': True,
                'status_info': status_info
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'لا توجد معلومات تتبع لهذا الطلب'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في جلب معلومات التتبع'
        }), 500

@tracking_bp.route('/orders/<int:order_id>/history', methods=['GET'])
@token_required
@rate_limit(max_requests=30, window_minutes=1)
def get_order_tracking_history(current_user, current_user_type, order_id):
    """
    Get complete tracking history for an order
    الحصول على تاريخ التتبع الكامل للطلب
    """
    try:
        # Verify user has access to this order
        order = Order.query.get(order_id)
        if not order:
            return jsonify({
                'success': False,
                'message': 'الطلب غير موجود'
            }), 404
        
        # Check permissions
        has_access = False
        if current_user_type == 'customer' and order.customer_id == current_user.id:
            has_access = True
        elif current_user_type == 'restaurant' and order.restaurant_id == current_user.id:
            has_access = True
        elif current_user_type == 'delivery_agent' and order.delivery_agent_id == current_user.id:
            has_access = True
        elif current_user_type == 'admin':
            has_access = True
        
        if not has_access:
            return jsonify({
                'success': False,
                'message': 'غير مصرح لك بالوصول لهذا الطلب'
            }), 403
        
        # Get tracking history
        tracking_history = OrderTrackingService.get_order_tracking_history(order_id)
        
        return jsonify({
            'success': True,
            'tracking_history': tracking_history
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في جلب تاريخ التتبع'
        }), 500

@tracking_bp.route('/orders/<int:order_id>/update-status', methods=['POST'])
@token_required
@rate_limit(max_requests=20, window_minutes=1)
def update_order_status(current_user, current_user_type, order_id):
    """
    Update order status
    تحديث حالة الطلب
    """
    try:
        data = sanitize_input(request.get_json())
        
        # Validate required fields
        if 'status' not in data:
            return jsonify({
                'success': False,
                'message': 'حالة الطلب مطلوبة'
            }), 400
        
        new_status = data['status']
        location_lat = data.get('location_latitude')
        location_lng = data.get('location_longitude')
        notes = data.get('notes')
        
        # Verify user has permission to update this order
        order = Order.query.get(order_id)
        if not order:
            return jsonify({
                'success': False,
                'message': 'الطلب غير موجود'
            }), 404
        
        # Check permissions based on user type and status
        can_update = False
        
        if current_user_type == 'restaurant' and order.restaurant_id == current_user.id:
            # Restaurant can update: confirmed, preparing, ready, cancelled
            if new_status in ['confirmed', 'preparing', 'ready', 'cancelled']:
                can_update = True
        
        elif current_user_type == 'delivery_agent' and order.delivery_agent_id == current_user.id:
            # Delivery agent can update: picked_up, delivered
            if new_status in ['picked_up', 'delivered']:
                can_update = True
        
        elif current_user_type == 'admin':
            # Admin can update any status
            can_update = True
        
        elif current_user_type == 'customer' and order.customer_id == current_user.id:
            # Customer can only cancel pending orders
            if new_status == 'cancelled' and order.status == 'pending':
                can_update = True
        
        if not can_update:
            return jsonify({
                'success': False,
                'message': 'غير مصرح لك بتحديث حالة هذا الطلب'
            }), 403
        
        # Update order status
        success, message = OrderTrackingService.update_order_status(
            order_id=order_id,
            new_status=new_status,
            updated_by=current_user.id,
            updated_by_type=current_user_type,
            location_lat=location_lat,
            location_lng=location_lng,
            notes=notes
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في تحديث حالة الطلب'
        }), 500

@tracking_bp.route('/delivery-agent/current-orders', methods=['GET'])
@token_required
@rate_limit(max_requests=30, window_minutes=1)
def get_delivery_agent_orders(current_user, current_user_type):
    """
    Get current orders for delivery agent
    الحصول على الطلبات الحالية لوكيل التوصيل
    """
    try:
        if current_user_type != 'delivery_agent':
            return jsonify({
                'success': False,
                'message': 'هذا الإجراء مخصص لوكلاء التوصيل فقط'
            }), 403
        
        orders = OrderTrackingService.get_delivery_agent_current_orders(current_user.id)
        
        return jsonify({
            'success': True,
            'orders': orders,
            'count': len(orders)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في جلب الطلبات'
        }), 500

@tracking_bp.route('/restaurant/<int:restaurant_id>/orders-summary', methods=['GET'])
@token_required
@rate_limit(max_requests=30, window_minutes=1)
def get_restaurant_orders_summary(current_user, current_user_type, restaurant_id):
    """
    Get orders summary for restaurant
    الحصول على ملخص الطلبات للمطعم
    """
    try:
        # Check permissions
        if current_user_type == 'restaurant' and current_user.id != restaurant_id:
            return jsonify({
                'success': False,
                'message': 'غير مصرح لك بالوصول لبيانات هذا المطعم'
            }), 403
        elif current_user_type not in ['restaurant', 'admin']:
            return jsonify({
                'success': False,
                'message': 'غير مصرح لك بهذا الإجراء'
            }), 403
        
        # Get date parameter
        date_str = request.args.get('date')
        date = None
        if date_str:
            from datetime import datetime
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'تاريخ غير صحيح. استخدم صيغة YYYY-MM-DD'
                }), 400
        
        summary = OrderTrackingService.get_restaurant_orders_summary(restaurant_id, date)
        
        return jsonify({
            'success': True,
            'summary': summary,
            'date': date.isoformat() if date else None
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في جلب ملخص الطلبات'
        }), 500

@tracking_bp.route('/orders/<int:order_id>/metrics', methods=['GET'])
@token_required
@rate_limit(max_requests=30, window_minutes=1)
def get_order_metrics(current_user, current_user_type, order_id):
    """
    Get delivery performance metrics for an order
    الحصول على مقاييس أداء التوصيل للطلب
    """
    try:
        # Verify user has access to this order
        order = Order.query.get(order_id)
        if not order:
            return jsonify({
                'success': False,
                'message': 'الطلب غير موجود'
            }), 404
        
        # Check permissions (admin or involved parties)
        has_access = False
        if current_user_type == 'admin':
            has_access = True
        elif current_user_type == 'restaurant' and order.restaurant_id == current_user.id:
            has_access = True
        elif current_user_type == 'delivery_agent' and order.delivery_agent_id == current_user.id:
            has_access = True
        
        if not has_access:
            return jsonify({
                'success': False,
                'message': 'غير مصرح لك بالوصول لهذه البيانات'
            }), 403
        
        # Get metrics
        metrics = OrderTrackingService.calculate_delivery_metrics(order_id)
        
        if metrics:
            return jsonify({
                'success': True,
                'metrics': metrics
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'لا توجد بيانات كافية لحساب المقاييس'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في جلب مقاييس الأداء'
        }), 500

