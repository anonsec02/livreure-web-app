"""
Notifications API Routes
مسارات API للإشعارات
"""

from flask import Blueprint, request, jsonify
from src.routes.auth import token_required
from src.notifications import NotificationService, send_welcome_notification
from src.security_enhancements import rate_limit, sanitize_input

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications', methods=['GET'])
@token_required
@rate_limit(max_requests=30, window_minutes=1)
def get_notifications(current_user, current_user_type):
    """
    Get user notifications
    الحصول على إشعارات المستخدم
    """
    try:
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        # Validate limit
        if limit > 100:
            limit = 100
        
        # Get notifications
        notifications = NotificationService.get_user_notifications(
            user_id=current_user.id,
            user_type=current_user_type,
            limit=limit,
            unread_only=unread_only
        )
        
        # Get unread count
        unread_count = NotificationService.get_unread_count(
            user_id=current_user.id,
            user_type=current_user_type
        )
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'unread_count': unread_count,
            'total_count': len(notifications)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في جلب الإشعارات'
        }), 500

@notifications_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@token_required
@rate_limit(max_requests=60, window_minutes=1)
def mark_notification_read(current_user, current_user_type, notification_id):
    """
    Mark a notification as read
    تحديد إشعار كمقروء
    """
    try:
        success = NotificationService.mark_as_read(notification_id, current_user.id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'تم تحديد الإشعار كمقروء'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'الإشعار غير موجود'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في تحديث الإشعار'
        }), 500

@notifications_bp.route('/notifications/read-all', methods=['POST'])
@token_required
@rate_limit(max_requests=10, window_minutes=1)
def mark_all_notifications_read(current_user, current_user_type):
    """
    Mark all notifications as read
    تحديد جميع الإشعارات كمقروءة
    """
    try:
        success = NotificationService.mark_all_as_read(
            user_id=current_user.id,
            user_type=current_user_type
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'تم تحديد جميع الإشعارات كمقروءة'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'حدث خطأ في تحديث الإشعارات'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في تحديث الإشعارات'
        }), 500

@notifications_bp.route('/notifications/unread-count', methods=['GET'])
@token_required
@rate_limit(max_requests=60, window_minutes=1)
def get_unread_count(current_user, current_user_type):
    """
    Get count of unread notifications
    الحصول على عدد الإشعارات غير المقروءة
    """
    try:
        unread_count = NotificationService.get_unread_count(
            user_id=current_user.id,
            user_type=current_user_type
        )
        
        return jsonify({
            'success': True,
            'unread_count': unread_count
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في جلب عدد الإشعارات'
        }), 500

# Admin endpoint to send custom notifications
@notifications_bp.route('/admin/notifications/send', methods=['POST'])
@token_required
@rate_limit(max_requests=10, window_minutes=1)
def send_custom_notification(current_user, current_user_type):
    """
    Send custom notification (Admin only)
    إرسال إشعار مخصص (للمديرين فقط)
    """
    try:
        # Check if user is admin
        if current_user_type != 'admin':
            return jsonify({
                'success': False,
                'message': 'غير مصرح لك بهذا الإجراء'
            }), 403
        
        data = sanitize_input(request.get_json())
        
        # Validate required fields
        required_fields = ['user_id', 'user_type', 'title', 'message', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'الحقل {field} مطلوب'
                }), 400
        
        # Create notification
        notification = NotificationService.create_notification(
            user_id=data['user_id'],
            user_type=data['user_type'],
            title=data['title'],
            message=data['message'],
            notification_type=data['type'],
            data=data.get('data')
        )
        
        if notification:
            return jsonify({
                'success': True,
                'message': 'تم إرسال الإشعار بنجاح',
                'notification': notification.to_dict()
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'حدث خطأ في إرسال الإشعار'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في إرسال الإشعار'
        }), 500

# Endpoint to send welcome notification to new users
@notifications_bp.route('/notifications/welcome', methods=['POST'])
@token_required
@rate_limit(max_requests=5, window_minutes=1)
def send_welcome(current_user, current_user_type):
    """
    Send welcome notification to current user
    إرسال إشعار ترحيب للمستخدم الحالي
    """
    try:
        notification = send_welcome_notification(current_user.id, current_user_type)
        
        if notification:
            return jsonify({
                'success': True,
                'message': 'تم إرسال إشعار الترحيب',
                'notification': notification.to_dict()
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'حدث خطأ في إرسال إشعار الترحيب'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في إرسال إشعار الترحيب'
        }), 500

