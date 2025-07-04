# 🚀 دليل النشر - منصة Livreure

## 📋 نظرة عامة

هذا الدليل يوضح كيفية نشر منصة Livreure في بيئة الإنتاج للعمل الميداني في موريتانيا.

## 🔧 المتطلبات الأساسية

### الخادم
- **نظام التشغيل**: Ubuntu 20.04+ أو CentOS 8+
- **الذاكرة**: 2GB RAM كحد أدنى (4GB مُوصى به)
- **التخزين**: 20GB مساحة حرة كحد أدنى
- **المعالج**: 2 CPU cores كحد أدنى

### البرمجيات المطلوبة
- Python 3.8+
- pip
- Git
- Nginx (للإنتاج)
- Supervisor (لإدارة العمليات)
- SSL Certificate (للأمان)

## 🛠️ خطوات النشر

### 1. إعداد الخادم

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Python و pip
sudo apt install python3 python3-pip python3-venv git nginx supervisor -y

# إنشاء مستخدم للتطبيق
sudo adduser livreure
sudo usermod -aG sudo livreure
```

### 2. استنساخ المشروع

```bash
# التبديل للمستخدم الجديد
sudo su - livreure

# استنساخ المستودع
git clone https://github.com/anonsec02/livreure-web-app.git
cd livreure-web-app
```

### 3. إعداد البيئة الافتراضية

```bash
# إنشاء البيئة الافتراضية
python3 -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
cd backend
pip install -r requirements.txt
pip install gunicorn  # خادم WSGI للإنتاج
```

### 4. إعداد قاعدة البيانات

```bash
# إنشاء قاعدة البيانات والبيانات التجريبية
python seed_data.py

# للإنتاج، يُنصح بالترقية إلى PostgreSQL
# pip install psycopg2-binary
```

### 5. إعداد متغيرات البيئة

```bash
# إنشاء ملف البيئة
cat > /home/livreure/livreure-web-app/backend/.env << EOF
# Production Environment Variables
DATABASE_URL=sqlite:///livreure_production.db
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
JWT_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')
PORT=5000
DEBUG=False
FLASK_ENV=production

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Mauritanian Settings
DEFAULT_TIMEZONE=Africa/Nouakchott
DEFAULT_CURRENCY=MRU
DEFAULT_LANGUAGE=ar
EOF
```

### 6. إعداد Gunicorn

```bash
# إنشاء ملف تكوين Gunicorn
cat > /home/livreure/livreure-web-app/backend/gunicorn.conf.py << EOF
# Gunicorn Configuration for Livreure
bind = "127.0.0.1:5000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "livreure"
group = "livreure"
tmp_upload_dir = None
errorlog = "/var/log/livreure/error.log"
accesslog = "/var/log/livreure/access.log"
loglevel = "info"
EOF

# إنشاء مجلد السجلات
sudo mkdir -p /var/log/livreure
sudo chown livreure:livreure /var/log/livreure
```

### 7. إعداد Supervisor

```bash
# إنشاء ملف تكوين Supervisor
sudo cat > /etc/supervisor/conf.d/livreure.conf << EOF
[program:livreure]
command=/home/livreure/livreure-web-app/venv/bin/gunicorn -c gunicorn.conf.py src.main:app
directory=/home/livreure/livreure-web-app/backend
user=livreure
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/livreure/supervisor.log
environment=PATH="/home/livreure/livreure-web-app/venv/bin"
EOF

# إعادة تحميل Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start livreure
```

### 8. إعداد Nginx

```bash
# إنشاء ملف تكوين Nginx
sudo cat > /etc/nginx/sites-available/livreure << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Static Files
    location /static/ {
        alias /home/livreure/livreure-web-app/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API Routes
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Auth Routes
    location /auth/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Main Application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Admin Dashboard
    location /admin-dashboard/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# تفعيل الموقع
sudo ln -s /etc/nginx/sites-available/livreure /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 9. إعداد SSL Certificate

```bash
# باستخدام Let's Encrypt (مجاني)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# إعداد التجديد التلقائي
sudo crontab -e
# إضافة السطر التالي:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 10. إعداد Firewall

```bash
# تفعيل UFW
sudo ufw enable

# السماح بالمنافذ المطلوبة
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443

# عرض الحالة
sudo ufw status
```

## 🔄 التحديثات والصيانة

### تحديث التطبيق

```bash
# التبديل للمستخدم
sudo su - livreure
cd livreure-web-app

# سحب التحديثات
git pull origin master

# تفعيل البيئة الافتراضية
source venv/bin/activate

# تحديث المتطلبات
cd backend
pip install -r requirements.txt

# إعادة تشغيل التطبيق
sudo supervisorctl restart livreure
```

### النسخ الاحتياطي

```bash
# إنشاء سكريبت النسخ الاحتياطي
cat > /home/livreure/backup.sh << EOF
#!/bin/bash
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/livreure/backups"
mkdir -p \$BACKUP_DIR

# نسخ احتياطي لقاعدة البيانات
cp /home/livreure/livreure-web-app/backend/livreure_production.db \$BACKUP_DIR/db_backup_\$DATE.db

# نسخ احتياطي للملفات
tar -czf \$BACKUP_DIR/files_backup_\$DATE.tar.gz /home/livreure/livreure-web-app

# حذف النسخ القديمة (أكثر من 30 يوم)
find \$BACKUP_DIR -name "*.db" -mtime +30 -delete
find \$BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: \$DATE"
EOF

chmod +x /home/livreure/backup.sh

# إضافة إلى crontab للتشغيل اليومي
crontab -e
# إضافة السطر التالي:
# 0 2 * * * /home/livreure/backup.sh
```

## 📊 المراقبة والسجلات

### عرض السجلات

```bash
# سجلات التطبيق
sudo tail -f /var/log/livreure/error.log
sudo tail -f /var/log/livreure/access.log

# سجلات Supervisor
sudo tail -f /var/log/livreure/supervisor.log

# سجلات Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### مراقبة الأداء

```bash
# حالة التطبيق
sudo supervisorctl status livreure

# استخدام الموارد
htop
df -h
free -h

# اتصالات الشبكة
sudo netstat -tulpn | grep :5000
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443
```

## 🔒 الأمان

### إعدادات الأمان الإضافية

```bash
# تحديث النظام بانتظام
sudo apt update && sudo apt upgrade -y

# تثبيت fail2ban لحماية SSH
sudo apt install fail2ban -y

# إعداد fail2ban
sudo cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### مراقبة الأمان

```bash
# فحص محاولات الدخول المشبوهة
sudo grep "Failed password" /var/log/auth.log

# فحص حالة fail2ban
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

## 🌍 إعدادات موريتانيا المحددة

### المنطقة الزمنية

```bash
# تعيين المنطقة الزمنية لموريتانيا
sudo timedatectl set-timezone Africa/Nouakchott
```

### اللغة والترميز

```bash
# إعداد اللغة العربية
sudo apt install language-pack-ar -y
sudo locale-gen ar_MR.UTF-8
```

## 📞 الدعم والمساعدة

### معلومات الاتصال
- **المطور**: ra-one02
- **Telegram**: [@raone_002](https://t.me/raone_002)
- **GitHub**: [anonsec02](https://github.com/anonsec02)

### الأخطاء الشائعة وحلولها

#### خطأ في الاتصال بقاعدة البيانات
```bash
# التحقق من صلاحيات الملفات
sudo chown -R livreure:livreure /home/livreure/livreure-web-app
chmod 644 /home/livreure/livreure-web-app/backend/livreure_production.db
```

#### خطأ في تشغيل Gunicorn
```bash
# التحقق من السجلات
sudo supervisorctl tail livreure stderr

# إعادة تشغيل الخدمة
sudo supervisorctl restart livreure
```

#### مشاكل SSL
```bash
# تجديد الشهادة
sudo certbot renew --dry-run

# التحقق من تاريخ انتهاء الصلاحية
sudo certbot certificates
```

---

**ملاحظة**: هذا الدليل مُعد خصيصاً للنشر في البيئة الموريتانية. تأكد من تخصيص الإعدادات حسب احتياجاتك المحددة.

🇲🇷 **Livreure** - منصة التوصيل الأولى في موريتانيا

