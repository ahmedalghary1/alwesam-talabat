# Deployment & Production Guide

## Overview

This guide covers deploying the Alwesam-Talabat platform to a production environment with best practices for security, performance, and reliability.

---

## Pre-Deployment Checklist

### Code Preparation

- [ ] All features tested locally
- [ ] Database migrations up to date
- [ ] Static files collected
- [ ] Dependencies listed in requirements.txt
- [ ] Environment variables documented
- [ ] Debug mode disabled
- [ ] Secret key secured

---

## Environment Configuration

### 1. Create Production Environment File

Create `.env` in project root:

```bash
# Security
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL example)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=alwesam_db
DB_USER=alwesam_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Media and Static
MEDIA_ROOT=/var/www/alwesam-talabat/media
STATIC_ROOT=/var/www/alwesam-talabat/staticfiles

# Email (Optional)
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password
```

### 2. Update settings.py

```python
# project/settings.py
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=BASE_DIR / 'db.sqlite3'),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

---

## Database Setup

### PostgreSQL Installation (Ubuntu/Debian)

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql

postgres=# CREATE DATABASE alwesam_db;
postgres=# CREATE USER alwesam_user WITH PASSWORD 'secure_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE alwesam_db TO alwesam_user;
postgres=# \q
```

### Migrate from SQLite to PostgreSQL

```bash
# 1. Backup SQLite data
python manage.py dumpdata > backup.json

# 2. Update .env with PostgreSQL credentials

# 3. Install psycopg2
pip install psycopg2-binary

# 4. Run migrations
python manage.py migrate

# 5. Load data
python manage.py loaddata backup.json

# 6. Create superuser if needed
python manage.py createsuperuser
```

---

## Static Files Setup

### 1. Update settings.py

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 2. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

This copies all static files to `STATIC_ROOT` for serving by web server.

---

## Application Server (Gunicorn)

### Installation

```bash
pip install gunicorn
```

### Create Gunicorn Configuration

**File**: `gunicorn_config.py`

```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
```

### Create Systemd Service

**File**: `/etc/systemd/system/alwesam.service`

```ini
[Unit]
Description=Alwesam-Talabat Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/alwesam-talabat
Environment="PATH=/var/www/alwesam-talabat/venv/bin"
ExecStart=/var/www/alwesam-talabat/venv/bin/gunicorn \
          --config gunicorn_config.py \
          project.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl start alwesam
sudo systemctl enable alwesam
sudo systemctl status alwesam
```

---

## Web Server (Nginx)

### Installation

```bash
sudo apt install nginx
```

### Nginx Configuration

**File**: `/etc/nginx/sites-available/alwesam`

```nginx
upstream alwesam {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security Headers
    add_header X-Frame-Options "DENY";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Client Max Body Size (for image uploads)
    client_max_body_size 20M;
    
    # Static files
    location /static/ {
        alias /var/www/alwesam-talabat/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/alwesam-talabat/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # Proxy to Gunicorn
    location / {
        proxy_pass http://alwesam;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/alwesam /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## SSL/TLS Setup (Let's Encrypt)

### Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx
```

### Obtain Certificate

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Auto-Renewal

Certbot automatically sets up renewal. Verify:

```bash
sudo certbot renew --dry-run
```

---

## Security Hardening

### 1. Firewall Configuration (UFW)

```bash
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

### 2. Disable Debug Mode

Ensure `.env` has:

```
DEBUG=False
```

### 3. Secure Secret Key

Generate new secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Update `.env`:

```
SECRET_KEY=your-new-secret-key-here
```

### 4. Configure ALLOWED_HOSTS

```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

---

## Performance Optimization

### 1. Database Connection Pooling

Install pgbouncer:

```bash
sudo apt install pgbouncer
```

### 2. Redis Caching

```bash
# Install Redis
sudo apt install redis-server

# Update settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3. Enable Gzip Compression (Nginx)

Add to nginx config:

```nginx
gzip on;
gzip_vary on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;
```

### 4. Database Query Optimization

```python
# Use select_related and prefetch_related
products = Product.objects.select_related('category').prefetch_related('variants')
```

---

## Monitoring & Logging

### 1. Application Logging

**settings.py**:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/alwesam/django.log',
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### 2. Server Monitoring

Install monitoring tools:

```bash
# System monitoring
sudo apt install htop

# Web monitoring (optional)
# - New Relic
# - Datadog
# - Prometheus + Grafana
```

---

## Backup Strategy

### 1. Database Backup Script

**File**: `backup.sh`

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/alwesam"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U alwesam_user alwesam_db > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/alwesam-talabat/media/

# Remove backups older than 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

### 2. Automate Backups (Cron)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup.sh >> /var/log/alwesam/backup.log 2>&1
```

---

## Updates & Maintenance

### Application Update Procedure

```bash
# 1. Pull latest code
cd /var/www/alwesam-talabat
git pull origin main

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install/update dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Restart services
sudo systemctl restart alwesam
sudo systemctl reload nginx
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Review migration files
# Apply migrations
python manage.py migrate

# If issues occur, rollback
python manage.py migrate app_name previous_migration_name
```

---

## Troubleshooting

### Common Production Issues

**Issue**: 502 Bad Gateway
**Solutions**:

- Check Gunicorn is running: `sudo systemctl status alwesam`
- Check Gunicorn logs: `sudo journalctl -u alwesam`
- Verify socket connection between Nginx and Gunicorn

**Issue**: Static files not loading
**Solutions**:

- Run `python manage.py collectstatic`
- Check Nginx static file path
- Verify file permissions

**Issue**: Database connection errors
**Solutions**:

- Verify PostgreSQL is running
- Check database credentials in `.env`
- Test connection: `psql -U alwesam_user -d alwesam_db`

**Issue**: High memory usage
**Solutions**:

- Reduce Gunicorn workers
- Enable database connection pooling
- Implement Redis caching

---

## Production Environment Variables Summary

```bash
# Required
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=domain.com,www.domain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_HOST=localhost
DB_PORT=5432

# Optional
EMAIL_HOST=...
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
```

---

## Quick Reference Commands

```bash
# Restart application
sudo systemctl restart alwesam

# View application logs
sudo journalctl -u alwesam -f

# Restart Nginx
sudo systemctl restart nginx

# Check Nginx configuration
sudo nginx -t

# Django management commands
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser

# Database backup
pg_dump dbname > backup.sql

# Database restore
psql dbname < backup.sql
```
