"""
Enhanced Order Tracking System for Livreure
نظام تتبع الطلبات المحسن لمنصة Livreure
"""

from datetime import datetime, timedelta
from src.models.user import db
from src.models.order import Order
from src.notifications import send_order_notification
import json

class OrderTracking(db.Model):
    __tablename__ = 'order_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    location_latitude = db.Column(db.Float)
    location_longitude = db.Column(db.Float)
    notes = db.Column(db.Text)
    estimated_arrival = db.Column(db.DateTime)
    actual_time = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.Integer)  # User ID who updated the status
    updated_by_type = db.Column(db.String(20))  # User type who updated
    
    # Relationship
    order = db.relationship('Order', backref='tracking_history')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'status': self.status,
            'location_latitude': self.location_latitude,
            'location_longitude': self.location_longitude,
            'notes': self.notes,
            'estimated_arrival': self.estimated_arrival.isoformat() if self.estimated_arrival else None,
            'actual_time': self.actual_time.isoformat() if self.actual_time else None,
            'updated_by': self.updated_by,
            'updated_by_type': self.updated_by_type
        }

class OrderTrackingService:
    """
    Service for managing order tracking
    خدمة إدارة تتبع الطلبات
    """
    
    # Order status flow
    STATUS_FLOW = {
        'pending': ['confirmed', 'cancelled'],
        'confirmed': ['preparing', 'cancelled'],
        'preparing': ['ready', 'cancelled'],
        'ready': ['picked_up', 'cancelled'],
        'picked_up': ['delivered', 'cancelled'],
        'delivered': [],
        'cancelled': []
    }
    
    # Status descriptions in Arabic
    STATUS_DESCRIPTIONS = {
        'pending': 'في انتظار التأكيد',
        'confirmed': 'تم تأكيد الطلب',
        'preparing': 'يتم تحضير الطلب',
        'ready': 'الطلب جاهز للاستلام',
        'picked_up': 'تم استلام الطلب',
        'delivered': 'تم توصيل الطلب',
        'cancelled': 'تم إلغاء الطلب'
    }
    
    # Estimated time for each status (in minutes)
    ESTIMATED_TIMES = {
        'confirmed': 5,
        'preparing': 25,
        'ready': 5,
        'picked_up': 20,
        'delivered': 0
    }
    
    @staticmethod
    def update_order_status(order_id, new_status, updated_by=None, updated_by_type=None, 
                          location_lat=None, location_lng=None, notes=None):
        """
        Update order status with tracking
        تحديث حالة الطلب مع التتبع
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return False, "الطلب غير موجود"
            
            # Check if status transition is valid
            current_status = order.status
            if new_status not in OrderTrackingService.STATUS_FLOW.get(current_status, []):
                return False, f"لا يمكن تغيير الحالة من {current_status} إلى {new_status}"
            
            # Calculate estimated arrival time
            estimated_arrival = None
            if new_status in OrderTrackingService.ESTIMATED_TIMES:
                estimated_minutes = OrderTrackingService.ESTIMATED_TIMES[new_status]
                if estimated_minutes > 0:
                    estimated_arrival = datetime.utcnow() + timedelta(minutes=estimated_minutes)
            
            # Create tracking record
            tracking = OrderTracking(
                order_id=order_id,
                status=new_status,
                location_latitude=location_lat,
                location_longitude=location_lng,
                notes=notes,
                estimated_arrival=estimated_arrival,
                updated_by=updated_by,
                updated_by_type=updated_by_type
            )
            
            # Update order status and timestamps
            order.status = new_status
            
            if new_status == 'confirmed':
                order.confirmed_at = datetime.utcnow()
            elif new_status == 'ready':
                order.prepared_at = datetime.utcnow()
            elif new_status == 'picked_up':
                order.picked_up_at = datetime.utcnow()
            elif new_status == 'delivered':
                order.delivered_at = datetime.utcnow()
            
            # Update estimated delivery time
            if estimated_arrival:
                order.estimated_delivery_time = estimated_arrival
            
            db.session.add(tracking)
            db.session.commit()
            
            # Send notifications
            OrderTrackingService._send_status_notifications(order, new_status)
            
            return True, "تم تحديث حالة الطلب بنجاح"
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating order status: {e}")
            return False, "حدث خطأ في تحديث حالة الطلب"
    
    @staticmethod
    def get_order_tracking_history(order_id):
        """
        Get complete tracking history for an order
        الحصول على تاريخ التتبع الكامل للطلب
        """
        tracking_records = OrderTracking.query.filter_by(order_id=order_id)\
                                             .order_by(OrderTracking.actual_time.asc()).all()
        
        return [record.to_dict() for record in tracking_records]
    
    @staticmethod
    def get_current_order_status(order_id):
        """
        Get current status with detailed information
        الحصول على الحالة الحالية مع معلومات مفصلة
        """
        order = Order.query.get(order_id)
        if not order:
            return None
        
        latest_tracking = OrderTracking.query.filter_by(order_id=order_id)\
                                           .order_by(OrderTracking.actual_time.desc()).first()
        
        status_info = {
            'order_id': order_id,
            'order_number': order.order_number,
            'current_status': order.status,
            'status_description': OrderTrackingService.STATUS_DESCRIPTIONS.get(order.status, order.status),
            'estimated_delivery_time': order.estimated_delivery_time.isoformat() if order.estimated_delivery_time else None,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'confirmed_at': order.confirmed_at.isoformat() if order.confirmed_at else None,
            'prepared_at': order.prepared_at.isoformat() if order.prepared_at else None,
            'picked_up_at': order.picked_up_at.isoformat() if order.picked_up_at else None,
            'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None
        }
        
        if latest_tracking:
            status_info.update({
                'last_location_latitude': latest_tracking.location_latitude,
                'last_location_longitude': latest_tracking.location_longitude,
                'last_update_time': latest_tracking.actual_time.isoformat(),
                'last_notes': latest_tracking.notes
            })
        
        return status_info
    
    @staticmethod
    def get_delivery_agent_current_orders(agent_id):
        """
        Get current orders assigned to a delivery agent
        الحصول على الطلبات الحالية المعينة لوكيل التوصيل
        """
        orders = Order.query.filter_by(delivery_agent_id=agent_id)\
                           .filter(Order.status.in_(['picked_up', 'ready']))\
                           .order_by(Order.created_at.desc()).all()
        
        result = []
        for order in orders:
            order_info = order.to_dict()
            order_info['tracking_info'] = OrderTrackingService.get_current_order_status(order.id)
            result.append(order_info)
        
        return result
    
    @staticmethod
    def calculate_delivery_metrics(order_id):
        """
        Calculate delivery performance metrics
        حساب مقاييس أداء التوصيل
        """
        tracking_history = OrderTrackingService.get_order_tracking_history(order_id)
        
        if not tracking_history:
            return None
        
        metrics = {
            'total_time': None,
            'preparation_time': None,
            'delivery_time': None,
            'on_time_delivery': False
        }
        
        # Create status timeline
        status_times = {}
        for record in tracking_history:
            status_times[record['status']] = datetime.fromisoformat(record['actual_time'])
        
        # Calculate preparation time (confirmed to ready)
        if 'confirmed' in status_times and 'ready' in status_times:
            prep_time = status_times['ready'] - status_times['confirmed']
            metrics['preparation_time'] = prep_time.total_seconds() / 60  # in minutes
        
        # Calculate delivery time (picked_up to delivered)
        if 'picked_up' in status_times and 'delivered' in status_times:
            delivery_time = status_times['delivered'] - status_times['picked_up']
            metrics['delivery_time'] = delivery_time.total_seconds() / 60  # in minutes
        
        # Calculate total time (confirmed to delivered)
        if 'confirmed' in status_times and 'delivered' in status_times:
            total_time = status_times['delivered'] - status_times['confirmed']
            metrics['total_time'] = total_time.total_seconds() / 60  # in minutes
            
            # Check if delivered on time (within estimated time + 10 minutes buffer)
            order = Order.query.get(order_id)
            if order and order.estimated_delivery_time:
                buffer_time = order.estimated_delivery_time + timedelta(minutes=10)
                metrics['on_time_delivery'] = status_times['delivered'] <= buffer_time
        
        return metrics
    
    @staticmethod
    def _send_status_notifications(order, new_status):
        """
        Send notifications for status updates
        إرسال إشعارات لتحديثات الحالة
        """
        # Send to customer
        send_order_notification(order, new_status, 'customer')
        
        # Send to restaurant for new orders
        if new_status == 'confirmed':
            send_order_notification(order, new_status, 'restaurant')
        
        # Send to delivery agent when order is ready
        if new_status == 'ready' and order.delivery_agent_id:
            send_order_notification(order, new_status, 'delivery_agent')
    
    @staticmethod
    def get_restaurant_orders_summary(restaurant_id, date=None):
        """
        Get orders summary for a restaurant
        الحصول على ملخص الطلبات للمطعم
        """
        if not date:
            date = datetime.utcnow().date()
        
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        
        orders = Order.query.filter_by(restaurant_id=restaurant_id)\
                           .filter(Order.created_at.between(start_date, end_date))\
                           .all()
        
        summary = {
            'total_orders': len(orders),
            'pending_orders': len([o for o in orders if o.status == 'pending']),
            'confirmed_orders': len([o for o in orders if o.status == 'confirmed']),
            'preparing_orders': len([o for o in orders if o.status == 'preparing']),
            'ready_orders': len([o for o in orders if o.status == 'ready']),
            'completed_orders': len([o for o in orders if o.status == 'delivered']),
            'cancelled_orders': len([o for o in orders if o.status == 'cancelled']),
            'total_revenue': sum([o.total_amount for o in orders if o.status == 'delivered'])
        }
        
        return summary

