"""
Notification System for Livreure Platform
نظام الإشعارات لمنصة Livreure
"""

from datetime import datetime
from src.models.user import db
from flask import jsonify
import json

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # customer, restaurant, delivery_agent, admin
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # order, payment, system, promotion
    data = db.Column(db.Text)  # JSON data for additional info
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_type': self.user_type,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'data': json.loads(self.data) if self.data else None,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class NotificationService:
    """
    Service class for handling notifications
    فئة الخدمة للتعامل مع الإشعارات
    """
    
    @staticmethod
    def create_notification(user_id, user_type, title, message, notification_type, data=None):
        """
        Create a new notification
        إنشاء إشعار جديد
        """
        try:
            notification = Notification(
                user_id=user_id,
                user_type=user_type,
                title=title,
                message=message,
                type=notification_type,
                data=json.dumps(data) if data else None
            )
            
            db.session.add(notification)
            db.session.commit()
            
            return notification
        except Exception as e:
            db.session.rollback()
            print(f"Error creating notification: {e}")
            return None
    
    @staticmethod
    def get_user_notifications(user_id, user_type, limit=50, unread_only=False):
        """
        Get notifications for a user
        الحصول على إشعارات المستخدم
        """
        query = Notification.query.filter_by(user_id=user_id, user_type=user_type)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
        return [notification.to_dict() for notification in notifications]
    
    @staticmethod
    def mark_as_read(notification_id, user_id):
        """
        Mark notification as read
        تحديد الإشعار كمقروء
        """
        try:
            notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
            if notification:
                notification.is_read = True
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"Error marking notification as read: {e}")
            return False
    
    @staticmethod
    def mark_all_as_read(user_id, user_type):
        """
        Mark all notifications as read for a user
        تحديد جميع الإشعارات كمقروءة للمستخدم
        """
        try:
            Notification.query.filter_by(user_id=user_id, user_type=user_type).update({'is_read': True})
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error marking all notifications as read: {e}")
            return False
    
    @staticmethod
    def get_unread_count(user_id, user_type):
        """
        Get count of unread notifications
        الحصول على عدد الإشعارات غير المقروءة
        """
        return Notification.query.filter_by(user_id=user_id, user_type=user_type, is_read=False).count()

# Notification templates for different events
# قوالب الإشعارات للأحداث المختلفة

class NotificationTemplates:
    """
    Templates for different types of notifications
    قوالب لأنواع مختلفة من الإشعارات
    """
    
    # Order notifications for customers
    ORDER_CONFIRMED = {
        'title': 'تم تأكيد طلبك',
        'message': 'تم تأكيد طلبك رقم {order_number} وسيتم تحضيره قريباً',
        'type': 'order'
    }
    
    ORDER_PREPARING = {
        'title': 'يتم تحضير طلبك',
        'message': 'المطعم يقوم بتحضير طلبك رقم {order_number} الآن',
        'type': 'order'
    }
    
    ORDER_READY = {
        'title': 'طلبك جاهز للاستلام',
        'message': 'طلبك رقم {order_number} جاهز وسيتم توصيله قريباً',
        'type': 'order'
    }
    
    ORDER_PICKED_UP = {
        'title': 'تم استلام طلبك',
        'message': 'وكيل التوصيل استلم طلبك رقم {order_number} وهو في الطريق إليك',
        'type': 'order'
    }
    
    ORDER_DELIVERED = {
        'title': 'تم توصيل طلبك',
        'message': 'تم توصيل طلبك رقم {order_number} بنجاح. نتمنى أن تكون قد استمتعت بوجبتك!',
        'type': 'order'
    }
    
    ORDER_CANCELLED = {
        'title': 'تم إلغاء طلبك',
        'message': 'تم إلغاء طلبك رقم {order_number}. سيتم استرداد المبلغ خلال 3-5 أيام عمل',
        'type': 'order'
    }
    
    # Restaurant notifications
    NEW_ORDER = {
        'title': 'طلب جديد',
        'message': 'لديك طلب جديد رقم {order_number} بقيمة {total_amount} أوقية',
        'type': 'order'
    }
    
    # Delivery agent notifications
    DELIVERY_ASSIGNED = {
        'title': 'مهمة توصيل جديدة',
        'message': 'تم تعيين طلب رقم {order_number} لك للتوصيل',
        'type': 'order'
    }
    
    # Payment notifications
    PAYMENT_SUCCESS = {
        'title': 'تم الدفع بنجاح',
        'message': 'تم دفع مبلغ {amount} أوقية بنجاح لطلب رقم {order_number}',
        'type': 'payment'
    }
    
    PAYMENT_FAILED = {
        'title': 'فشل في الدفع',
        'message': 'فشل في دفع مبلغ {amount} أوقية لطلب رقم {order_number}. يرجى المحاولة مرة أخرى',
        'type': 'payment'
    }
    
    # Promotional notifications
    WELCOME_BONUS = {
        'title': 'مرحباً بك في Livreure!',
        'message': 'احصل على خصم 20% على طلبك الأول باستخدام الكود: WELCOME20',
        'type': 'promotion'
    }
    
    SPECIAL_OFFER = {
        'title': 'عرض خاص لك!',
        'message': 'احصل على خصم {discount}% على طلبك التالي. العرض ساري حتى {expiry_date}',
        'type': 'promotion'
    }

def send_order_notification(order, status, user_type='customer'):
    """
    Send notification based on order status
    إرسال إشعار بناءً على حالة الطلب
    """
    templates = {
        'confirmed': NotificationTemplates.ORDER_CONFIRMED,
        'preparing': NotificationTemplates.ORDER_PREPARING,
        'ready': NotificationTemplates.ORDER_READY,
        'picked_up': NotificationTemplates.ORDER_PICKED_UP,
        'delivered': NotificationTemplates.ORDER_DELIVERED,
        'cancelled': NotificationTemplates.ORDER_CANCELLED
    }
    
    if status not in templates:
        return False
    
    template = templates[status]
    
    # Determine recipient based on status and user type
    if user_type == 'customer':
        user_id = order.customer_id
    elif user_type == 'restaurant':
        user_id = order.restaurant_id
        template = NotificationTemplates.NEW_ORDER
    elif user_type == 'delivery_agent' and order.delivery_agent_id:
        user_id = order.delivery_agent_id
        template = NotificationTemplates.DELIVERY_ASSIGNED
    else:
        return False
    
    # Format message with order data
    title = template['title']
    message = template['message'].format(
        order_number=order.order_number,
        total_amount=order.total_amount
    )
    
    # Create notification
    return NotificationService.create_notification(
        user_id=user_id,
        user_type=user_type,
        title=title,
        message=message,
        notification_type=template['type'],
        data={'order_id': order.id, 'order_number': order.order_number}
    )

def send_welcome_notification(user_id, user_type):
    """
    Send welcome notification to new users
    إرسال إشعار ترحيب للمستخدمين الجدد
    """
    template = NotificationTemplates.WELCOME_BONUS
    
    return NotificationService.create_notification(
        user_id=user_id,
        user_type=user_type,
        title=template['title'],
        message=template['message'],
        notification_type=template['type'],
        data={'promo_code': 'WELCOME20', 'discount': 20}
    )

