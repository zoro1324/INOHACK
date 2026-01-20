# Animal Detection Backend - Setup & Deployment Guide

## 📋 Overview

This is a production-grade Django REST API backend for a Real-Time Animal Movement Detection & Alert System. It supports:

- **Role-Based Access Control** (Farmer, Ranger, Admin)
- **IoT Device Management** (ESP32 with cameras)
- **AI-Powered Animal Detection**
- **Geo-Based Alert System**
- **Real-Time Notifications** (Push, SMS, Call, Buzzer)
- **Background Processing** with Celery

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- MySQL 8.0+
- Redis 6.0+
- pip & virtualenv

### 2. Installation

```bash
# Navigate to server directory
cd dashboard/server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE animal_detection_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Configure environment variables
cp .env.example .env
# Edit .env with your database credentials
```

### 4. Django Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create logs directory
mkdir logs
```

### 5. Running the Server

#### Development Mode

```bash
# Terminal 1: Django Server
python manage.py runserver

# Terminal 2: Celery Worker
celery -A server worker -l info

# Terminal 3: Celery Beat (Scheduler)
celery -A server beat -l info
```

#### Production Mode

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn server.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 🔐 Authentication

### Register a New User

```bash
POST /api/auth/register/
Content-Type: application/json

{
    "username": "farmer1",
    "email": "farmer1@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "phone_number": "+1234567890",
    "first_name": "John",
    "last_name": "Doe",
    "role": "FARMER"
}
```

### Login

```bash
POST /api/auth/login/
Content-Type: application/json

{
    "username": "farmer1",
    "password": "SecurePass123!"
}

# Response includes JWT tokens
{
    "user": {...},
    "tokens": {
        "refresh": "...",
        "access": "..."
    }
}
```

### Use JWT Token

```bash
GET /api/auth/me/
Authorization: Bearer <access_token>
```

---

## 📱 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/refresh/` - Refresh JWT token
- `GET /api/auth/me/` - Get current user profile
- `PATCH /api/auth/me/` - Update user profile

### Device Management
- `GET /api/devices/` - List devices (filtered by role)
- `POST /api/devices/claim/` - Claim a new device
- `GET /api/devices/{id}/` - Get device details
- `PATCH /api/devices/{id}/` - Update device
- `POST /api/devices/{id}/heartbeat/` - Device heartbeat

### Image & Detection
- `POST /api/images/upload/` - ESP32 image upload (no JWT)
- `GET /api/images/` - List image captures
- `GET /api/images/{id}/` - Get image details
- `GET /api/detections/` - List detections
- `GET /api/detections/{id}/` - Get detection details
- `POST /api/detections/{id}/verify/` - Verify detection (Rangers only)

### Alerts
- `GET /api/alerts/` - List alerts
- `GET /api/alerts/{id}/` - Get alert details
- `POST /api/alerts/{id}/acknowledge/` - Acknowledge alert

### Dashboard
- `GET /api/dashboard/stats/` - Get dashboard statistics

### Audit Logs (Rangers/Admins only)
- `GET /api/audit-logs/` - List audit logs

### API Documentation
- `GET /api/docs/` - Swagger UI
- `GET /api/redoc/` - ReDoc UI

---

## 🤖 ESP32 Integration

### Device Authentication

ESP32 devices authenticate using `device_uid` + `api_key`:

```bash
POST /api/images/upload/
Content-Type: multipart/form-data

device_uid: ESP32_001
device_api_key: <64-char-hex-key>
image: <binary-image-data>
captured_at: 2024-01-20T10:30:00Z
```

### Device API Key Generation

API keys are automatically generated when a device is claimed. You can find them in:
- Django Admin: `/admin/api/iotdevice/`
- Or programmatically via the claim endpoint

### Buzzer Control

The device receives buzzer commands in the heartbeat response:

```json
{
    "status": "ok",
    "buzzer_command": "ON"  // or "OFF"
}
```

---

## 🔧 Configuration

### Environment Variables

Key settings in `.env`:

```bash
# Security
DJANGO_SECRET_KEY=<generate-strong-key>
DEBUG=False  # Set to False in production
ALLOWED_HOSTS=your-domain.com,api.your-domain.com

# Database
DB_NAME=animal_detection_db
DB_USER=db_user
DB_PASSWORD=<strong-password>
DB_HOST=localhost
DB_PORT=3306

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# AI Service
AI_INFERENCE_URL=http://ml-service:8001/predict
AI_INFERENCE_TIMEOUT=30

# Notifications
FCM_SERVER_KEY=<firebase-server-key>
SMS_API_KEY=<sms-provider-key>
CALL_API_KEY=<call-provider-key>

# Alerts
ALERT_RADIUS_KM=5.0
```

### Risk Level Configuration

Risk levels are configured in `settings.py`:

```python
RISK_LEVELS = {
    "LOW": {
        "animals": ["boar", "deer", "bison"],
        "confidence_threshold": 0.5,
        "alert_types": ["PUSH"],
    },
    "MEDIUM": {
        "animals": ["bear", "elephant"],
        "confidence_threshold": 0.6,
        "alert_types": ["PUSH", "SMS"],
    },
    "HIGH": {
        "animals": ["leopard"],
        "confidence_threshold": 0.7,
        "alert_types": ["PUSH", "SMS", "BUZZER"],
    },
    "CRITICAL": {
        "animals": ["tiger", "lion"],
        "confidence_threshold": 0.7,
        "alert_types": ["PUSH", "SMS", "CALL", "BUZZER"],
    },
}
```

---

## 🌐 Deployment

### AWS EC2 Deployment

```bash
# Install system dependencies
sudo apt update
sudo apt install python3-pip python3-venv mysql-server redis-server nginx

# Setup MySQL
sudo mysql_secure_installation
sudo mysql
CREATE DATABASE animal_detection_db;
CREATE USER 'dbuser'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON animal_detection_db.* TO 'dbuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Clone repository & setup
git clone <your-repo>
cd dashboard/server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with production values

# Run migrations
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser

# Setup Gunicorn service
sudo nano /etc/systemd/system/animal-api.service
```

**Gunicorn Service File:**

```ini
[Unit]
Description=Animal Detection API
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/INOHACK/dashboard/server
Environment="PATH=/home/ubuntu/INOHACK/dashboard/server/venv/bin"
ExecStart=/home/ubuntu/INOHACK/dashboard/server/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/home/ubuntu/INOHACK/dashboard/server/server.sock \
    server.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl start animal-api
sudo systemctl enable animal-api
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location /static/ {
        alias /home/ubuntu/INOHACK/dashboard/server/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/INOHACK/dashboard/server/media/;
    }

    location / {
        proxy_pass http://unix:/home/ubuntu/INOHACK/dashboard/server/server.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Celery Worker & Beat (Systemd)

```bash
# Celery Worker Service
sudo nano /etc/systemd/system/celery-worker.service
```

```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/INOHACK/dashboard/server
Environment="PATH=/home/ubuntu/INOHACK/dashboard/server/venv/bin"
ExecStart=/home/ubuntu/INOHACK/dashboard/server/venv/bin/celery -A server worker -l info

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start celery-worker
sudo systemctl enable celery-worker
```

---

## 🧪 Testing

```bash
# Run tests
python manage.py test

# With coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 📊 Monitoring

### Check Celery Tasks

```bash
# Monitor Celery worker
celery -A server inspect active

# Monitor Celery stats
celery -A server inspect stats
```

### Check Logs

```bash
# Django logs
tail -f logs/django.log

# Celery logs
journalctl -u celery-worker -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 🔒 Security Checklist

- [ ] Change `DJANGO_SECRET_KEY` in production
- [ ] Set `DEBUG=False` in production
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Use strong database passwords
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Configure firewall rules
- [ ] Set up regular database backups
- [ ] Rotate API keys regularly
- [ ] Monitor logs for suspicious activity
- [ ] Keep dependencies updated

---

## 📖 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/documentation)

---

## 🆘 Troubleshooting

### Database Connection Issues

```bash
# Check MySQL status
sudo systemctl status mysql

# Test connection
mysql -u root -p -e "SHOW DATABASES;"
```

### Celery Not Processing Tasks

```bash
# Check Redis
redis-cli ping

# Restart Celery
sudo systemctl restart celery-worker
sudo systemctl restart celery-beat
```

### Permission Errors

```bash
# Fix media folder permissions
sudo chown -R ubuntu:www-data media/
sudo chmod -R 755 media/
```

---

## 📝 License

[Your License Here]

## 👥 Contributors

[Your Team]

---

**For support, contact: contact@example.com**
