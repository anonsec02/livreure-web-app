# Livreure Deployment Guide

## Quick Start Deployment

### 1. Repository Setup
```bash
# Clone the repository
git clone https://github.com/anonsec02/livreure-web-app.git
cd livreure-web-app

# Install backend dependencies
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the backend directory:
```env
DATABASE_URL="mysql+pymysql://sql8788256:cixscfQvUs@sql8.freesqldatabase.com:3306/sql8788256"
SECRET_KEY="livreure-mauritania-secret-2024"
JWT_SECRET="livreure-mauritania-secret-key-2024-production"
FLASK_ENV="production"
```

### 3. Database Setup
```bash
# Run the application to create tables
cd backend
python src/main.py

# Seed initial data (optional)
python seed_data.py
```

### 4. Start the Application
```bash
# Development mode
python src/main.py

# Production mode (recommended)
gunicorn --bind 0.0.0.0:5000 src.main:app
```

### 5. Access the Application
- **Frontend**: http://localhost:5000/enhanced-index.html
- **API**: http://localhost:5000/api/
- **Authentication**: http://localhost:5000/auth/

## Production Deployment

### Using PythonAnywhere (Recommended for quick deployment)

1. **Upload files** to PythonAnywhere
2. **Install dependencies** in a virtual environment
3. **Configure WSGI** file:
```python
import sys
import os

# Add your project directory to sys.path
mysite = os.path.expanduser('~/livreure-web-app')
sys.path.insert(0, mysite)

from backend.src.main import app as application
```

4. **Set environment variables** in the web app configuration
5. **Configure static files** mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/livreure-web-app/`

### Using Traditional VPS/Server

#### 1. Server Setup (Ubuntu/Debian)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3.11-venv python3-pip nginx mysql-client -y

# Create application user
sudo useradd -m -s /bin/bash livreure
sudo su - livreure
```

#### 2. Application Setup
```bash
# Clone repository
git clone https://github.com/anonsec02/livreure-web-app.git
cd livreure-web-app

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
pip install gunicorn
```

#### 3. Systemd Service
Create `/etc/systemd/system/livreure.service`:
```ini
[Unit]
Description=Livreure Web Application
After=network.target

[Service]
User=livreure
Group=livreure
WorkingDirectory=/home/livreure/livreure-web-app
Environment=PATH=/home/livreure/livreure-web-app/venv/bin
ExecStart=/home/livreure/livreure-web-app/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 backend.src.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 4. Nginx Configuration
Create `/etc/nginx/sites-available/livreure`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/livreure/livreure-web-app/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 5. Enable and Start Services
```bash
# Enable and start application
sudo systemctl enable livreure
sudo systemctl start livreure

# Enable and configure Nginx
sudo ln -s /etc/nginx/sites-available/livreure /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Database Configuration

### Current Setup (FreeSQLDatabase)
- **Host**: sql8.freesqldatabase.com
- **Database**: sql8788256
- **User**: sql8788256
- **Password**: cixscfQvUs
- **Port**: 3306

### Production Database Recommendations

#### 1. Managed Database Services
- **DigitalOcean Managed Databases**
- **AWS RDS**
- **Google Cloud SQL**
- **Azure Database for MySQL**

#### 2. Self-Hosted MySQL
```bash
# Install MySQL
sudo apt install mysql-server -y

# Secure installation
sudo mysql_secure_installation

# Create database and user
mysql -u root -p
CREATE DATABASE livreure_production;
CREATE USER 'livreure'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON livreure_production.* TO 'livreure'@'localhost';
FLUSH PRIVILEGES;
```

## Security Considerations

### 1. Environment Variables
Never commit sensitive data to version control:
```bash
# Use environment variables for:
- DATABASE_URL
- SECRET_KEY
- JWT_SECRET
- API_KEYS
```

### 2. SSL/HTTPS Setup
```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 3. Firewall Configuration
```bash
# Configure UFW
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## Monitoring and Maintenance

### 1. Application Monitoring
```bash
# Check application status
sudo systemctl status livreure

# View logs
sudo journalctl -u livreure -f

# Monitor resource usage
htop
```

### 2. Database Backup
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -h sql8.freesqldatabase.com -u sql8788256 -p sql8788256 > backup_$DATE.sql
```

### 3. Log Rotation
Configure log rotation in `/etc/logrotate.d/livreure`:
```
/var/log/livreure/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 livreure livreure
}
```

## Performance Optimization

### 1. Application Level
- Use connection pooling for database
- Implement caching (Redis/Memcached)
- Optimize database queries
- Use CDN for static assets

### 2. Server Level
- Configure Nginx caching
- Enable gzip compression
- Optimize MySQL configuration
- Monitor resource usage

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check database connectivity
mysql -h sql8.freesqldatabase.com -u sql8788256 -p

# Verify environment variables
echo $DATABASE_URL
```

#### 2. Permission Issues
```bash
# Fix file permissions
sudo chown -R livreure:livreure /home/livreure/livreure-web-app
sudo chmod -R 755 /home/livreure/livreure-web-app
```

#### 3. Service Not Starting
```bash
# Check service status
sudo systemctl status livreure

# View detailed logs
sudo journalctl -u livreure --no-pager
```

## Scaling Considerations

### Horizontal Scaling
- Load balancer (Nginx/HAProxy)
- Multiple application instances
- Database read replicas
- CDN for static content

### Vertical Scaling
- Increase server resources
- Optimize application code
- Database performance tuning
- Caching implementation

## Backup and Recovery

### 1. Database Backup
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/home/livreure/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -h sql8.freesqldatabase.com -u sql8788256 -p sql8788256 | gzip > $BACKUP_DIR/livreure_$DATE.sql.gz
```

### 2. Application Backup
```bash
# Backup application files
tar -czf livreure_app_backup_$(date +%Y%m%d).tar.gz /home/livreure/livreure-web-app
```

### 3. Recovery Procedures
```bash
# Restore database
gunzip < backup_file.sql.gz | mysql -h host -u user -p database

# Restore application
tar -xzf livreure_app_backup.tar.gz -C /
```

## Support and Maintenance

### Regular Maintenance Tasks
1. **Weekly**: Check logs and system resources
2. **Monthly**: Update dependencies and security patches
3. **Quarterly**: Performance review and optimization
4. **Annually**: Security audit and infrastructure review

### Contact Information
- **Developer**: Available for manual intervention as needed
- **Repository**: https://github.com/anonsec02/livreure-web-app
- **Documentation**: This deployment guide and development summary

---

**Last Updated**: July 4, 2025  
**Version**: 1.0.0  
**Status**: Production Ready

