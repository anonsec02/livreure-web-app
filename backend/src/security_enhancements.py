"""
Security Enhancements for Livreure Backend
تحسينات الأمان للواجهة الخلفية لمنصة Livreure
"""

import hashlib
import secrets
import re
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
import time

# Rate limiting storage (in production, use Redis)
rate_limit_storage = {}

def generate_secure_password_hash(password):
    """
    Generate a more secure password hash using salt
    إنشاء تشفير آمن لكلمة المرور باستخدام الملح
    """
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', 
                                       password.encode('utf-8'), 
                                       salt.encode('utf-8'), 
                                       100000)
    return salt + password_hash.hex()

def verify_password(password, stored_hash):
    """
    Verify password against stored hash
    التحقق من كلمة المرور مقابل التشفير المحفوظ
    """
    salt = stored_hash[:32]
    stored_password_hash = stored_hash[32:]
    password_hash = hashlib.pbkdf2_hmac('sha256',
                                       password.encode('utf-8'),
                                       salt.encode('utf-8'),
                                       100000)
    return password_hash.hex() == stored_password_hash

def validate_password_strength(password):
    """
    Validate password strength
    التحقق من قوة كلمة المرور
    """
    if len(password) < 8:
        return False, "كلمة المرور يجب أن تكون 8 أحرف على الأقل"
    
    if not re.search(r"[A-Z]", password):
        return False, "كلمة المرور يجب أن تحتوي على حرف كبير واحد على الأقل"
    
    if not re.search(r"[a-z]", password):
        return False, "كلمة المرور يجب أن تحتوي على حرف صغير واحد على الأقل"
    
    if not re.search(r"\d", password):
        return False, "كلمة المرور يجب أن تحتوي على رقم واحد على الأقل"
    
    return True, "كلمة المرور قوية"

def validate_email(email):
    """
    Validate email format
    التحقق من صيغة البريد الإلكتروني
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """
    Validate Mauritanian phone number
    التحقق من رقم الهاتف الموريتاني
    """
    # Mauritanian phone numbers: +222 followed by 8 digits
    pattern = r'^(\+222|222)?[0-9]{8}$'
    return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None

def rate_limit(max_requests=60, window_minutes=1):
    """
    Rate limiting decorator
    محدد معدل الطلبات
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            
            # Create key for this IP and endpoint
            key = f"{client_ip}:{request.endpoint}"
            
            # Get current time
            now = time.time()
            window_start = now - (window_minutes * 60)
            
            # Initialize or clean old requests
            if key not in rate_limit_storage:
                rate_limit_storage[key] = []
            
            # Remove old requests outside the window
            rate_limit_storage[key] = [req_time for req_time in rate_limit_storage[key] 
                                     if req_time > window_start]
            
            # Check if limit exceeded
            if len(rate_limit_storage[key]) >= max_requests:
                return jsonify({
                    'success': False,
                    'message': 'تم تجاوز الحد المسموح من الطلبات. يرجى المحاولة لاحقاً',
                    'retry_after': window_minutes * 60
                }), 429
            
            # Add current request
            rate_limit_storage[key].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_input(data):
    """
    Sanitize user input to prevent XSS
    تنظيف مدخلات المستخدم لمنع XSS
    """
    if isinstance(data, str):
        # Remove potentially dangerous characters
        data = re.sub(r'[<>"\']', '', data)
        # Remove script tags
        data = re.sub(r'<script.*?</script>', '', data, flags=re.IGNORECASE | re.DOTALL)
        return data.strip()
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    else:
        return data

def generate_order_number():
    """
    Generate secure order number
    إنشاء رقم طلب آمن
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = secrets.token_hex(4).upper()
    return f"LVR{timestamp}{random_part}"

def log_security_event(event_type, user_id=None, ip_address=None, details=None):
    """
    Log security events for monitoring
    تسجيل الأحداث الأمنية للمراقبة
    """
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user_id': user_id,
        'ip_address': ip_address or request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
        'details': details
    }
    
    # In production, send to logging service
    print(f"SECURITY EVENT: {log_entry}")

def validate_mauritanian_data(data):
    """
    Validate data specific to Mauritanian context
    التحقق من البيانات الخاصة بالسياق الموريتاني
    """
    errors = []
    
    if 'phone' in data:
        if not validate_phone(data['phone']):
            errors.append("رقم الهاتف غير صحيح. يجب أن يكون رقم موريتاني صحيح")
    
    if 'email' in data:
        if not validate_email(data['email']):
            errors.append("البريد الإلكتروني غير صحيح")
    
    if 'password' in data:
        is_valid, message = validate_password_strength(data['password'])
        if not is_valid:
            errors.append(message)
    
    return len(errors) == 0, errors

