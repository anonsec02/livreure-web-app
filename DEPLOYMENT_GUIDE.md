# دليل النشر والتشغيل - منصة Livreure

## نظرة عامة
هذا الدليل يوضح كيفية نشر وتشغيل منصة Livreure على خوادم الإنتاج.

## متطلبات النظام

### الحد الأدنى للمتطلبات
- **المعالج:** 1 CPU Core
- **الذاكرة:** 512 MB RAM
- **التخزين:** 1 GB مساحة حرة
- **نظام التشغيل:** Ubuntu 18.04+ أو CentOS 7+
- **Python:** 3.8 أو أحدث

### المتطلبات الموصى بها
- **المعالج:** 2+ CPU Cores
- **الذاكرة:** 2+ GB RAM
- **التخزين:** 10+ GB مساحة حرة
- **الشبكة:** اتصال إنترنت مستقر

## خطوات النشر

### 1. تحضير الخادم

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Python و pip
sudo apt install python3 python3-pip python3-venv git -y

# تثبيت nginx (اختياري للإنتاج)
sudo apt install nginx -y
```

### 2. استنساخ المشروع

```bash
# استنساخ المستودع
git clone https://github.com/anonsec02/livreure-web-app.git
cd livreure-web-app

# إنشاء بيئة افتراضية
python3 -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
pip install -r backend/requirements.txt
```

### 3. إعداد قاعدة البيانات

```bash
# الانتقال إلى مجلد الواجهة الخلفية
cd backend

# تشغيل البيانات التجريبية
python3 seed_data.py
```

### 4. تشغيل الخادم

#### للتطوير والاختبار:
```bash
# تشغيل خادم التطوير
python3 src/main.py
```

#### للإنتاج:
```bash
# تثبيت gunicorn
pip install gunicorn

# تشغيل خادم الإنتاج
gunicorn --bind 0.0.0.0:5000 --workers 4 src.main:app
```

### 5. إعداد Nginx (للإنتاج)

إنشاء ملف التكوين:
```bash
sudo nano /etc/nginx/sites-available/livreure
```

محتوى الملف:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # الواجهة الأمامية
    location / {
        root /path/to/livreure-web-app;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # لوحة تحكم الإدارة
    location /admin-dashboard/ {
        root /path/to/livreure-web-app;
        index index.html;
        try_files $uri $uri/ /admin-dashboard/index.html;
    }

    # API الواجهة الخلفية
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

تفعيل الموقع:
```bash
sudo ln -s /etc/nginx/sites-available/livreure /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## النشر على PythonAnywhere

### 1. رفع الملفات
```bash
# ضغط المشروع
tar -czf livreure.tar.gz livreure-web-app/

# رفع الملف عبر واجهة PythonAnywhere
```

### 2. إعداد التطبيق
```python
# في ملف wsgi.py
import sys
import os

# إضافة مسار المشروع
path = '/home/yourusername/livreure-web-app/backend'
if path not in sys.path:
    sys.path.append(path)

from src.main import app as application
```

### 3. إعداد الملفات الثابتة
```python
# في إعدادات PythonAnywhere
# Static files:
# URL: /
# Directory: /home/yourusername/livreure-web-app/

# URL: /admin-dashboard/
# Directory: /home/yourusername/livreure-web-app/admin-dashboard/
```

## النشر على Render

### 1. إعداد ملف render.yaml
```yaml
services:
  - type: web
    name: livreure-backend
    env: python
    buildCommand: "pip install -r backend/requirements.txt"
    startCommand: "cd backend && python src/main.py"
    envVars:
      - key: PORT
        value: 5000

  - type: static
    name: livreure-frontend
    buildCommand: "echo 'No build needed'"
    staticPublishPath: .
    routes:
      - type: rewrite
        source: /admin-dashboard/*
        destination: /admin-dashboard/index.html
      - type: rewrite
        source: /*
        destination: /index.html
```

### 2. متغيرات البيئة
```bash
# في إعدادات Render
PORT=5000
FLASK_ENV=production
```

## إعداد قاعدة البيانات الخارجية

### استخدام FreeSQLDatabase
```python
# في ملف src/main.py
import os

# إعداد قاعدة البيانات
if os.environ.get('DATABASE_URL'):
    # استخدام قاعدة البيانات الخارجية
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # استخدام SQLite المحلية
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/app.db'
```

## مراقبة الأداء

### 1. مراقبة الخادم
```bash
# مراقبة استخدام الموارد
htop

# مراقبة سجلات الخادم
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 2. مراقبة التطبيق
```python
# إضافة سجلات في التطبيق
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# في الدوال
logger.info(f"User {user_id} logged in")
logger.error(f"Database error: {str(e)}")
```

## النسخ الاحتياطي

### 1. نسخ احتياطي لقاعدة البيانات
```bash
# SQLite
cp backend/src/database/app.db backup/app_$(date +%Y%m%d_%H%M%S).db

# MySQL/PostgreSQL
mysqldump -u username -p database_name > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. نسخ احتياطي للملفات
```bash
# ضغط المشروع
tar -czf livreure_backup_$(date +%Y%m%d_%H%M%S).tar.gz livreure-web-app/
```

## استكشاف الأخطاء

### مشاكل شائعة وحلولها

#### 1. خطأ في الاتصال بقاعدة البيانات
```bash
# التحقق من وجود قاعدة البيانات
ls -la backend/src/database/

# إعادة إنشاء قاعدة البيانات
cd backend && python3 seed_data.py
```

#### 2. خطأ في تحميل الملفات الثابتة
```bash
# التحقق من أذونات الملفات
chmod -R 755 livreure-web-app/
```

#### 3. خطأ في CORS
```python
# في src/main.py
from flask_cors import CORS
CORS(app, origins=['*'])
```

## الأمان

### 1. إعدادات الأمان الأساسية
```python
# في src/main.py
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['WTF_CSRF_ENABLED'] = True
```

### 2. تشفير HTTPS
```bash
# تثبيت Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. جدار الحماية
```bash
# إعداد UFW
sudo ufw enable
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
```

## التحديثات

### تحديث المشروع
```bash
# سحب آخر التحديثات
git pull origin master

# إعادة تشغيل الخدمات
sudo systemctl restart nginx
sudo systemctl restart your-app-service
```

## الدعم الفني

للحصول على الدعم الفني:
- **المطور:** ra-one02
- **التليجرام:** [@raone_002](https://t.me/raone_002)
- **GitHub Issues:** [رابط المستودع](https://github.com/anonsec02/livreure-web-app/issues)

---

**© 2024 Livreure Platform - تم التطوير بواسطة ra-one02**

