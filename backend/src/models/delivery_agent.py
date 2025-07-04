from src.models.user import db
from datetime import datetime

class DeliveryAgent(db.Model):
    __tablename__ = 'delivery_agents'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)  # "motorcycle", "bicycle", "car"
    vehicle_number = db.Column(db.String(20))
    license_number = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=False)
    current_latitude = db.Column(db.Float)
    current_longitude = db.Column(db.Float)
    rating = db.Column(db.Float, default=0.0)
    total_deliveries = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='delivery_agent', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'vehicle_type': self.vehicle_type,
            'vehicle_number': self.vehicle_number,
            'license_number': self.license_number,
            'is_active': self.is_active,
            'is_approved': self.is_approved,
            'is_available': self.is_available,
            'current_latitude': self.current_latitude,
            'current_longitude': self.current_longitude,
            'rating': self.rating,
            'total_deliveries': self.total_deliveries,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

