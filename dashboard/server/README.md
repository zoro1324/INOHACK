# Animal Detection & Alert System - Backend API

## ✅ **DOCUMENTATION FIXED - All Errors Corrected!**

> **Quick Fix:** Had server startup issues? The logs directory is now **auto-created**. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for all fixes.

## 🎯 Project Overview

A comprehensive Django REST Framework backend for real-time animal movement detection and alert system using IoT devices (ESP32 cameras) with AI-powered detection and role-based access control.

## ✨ Key Features

- ✅ **JWT Authentication** with role-based access control
- ✅ **Role Management**: Farmer, Forest Officer/Ranger, Admin
- ✅ **IoT Device Management**: Register, claim, and monitor ESP32 devices
- ✅ **AI-Powered Detection**: Automatic animal detection with confidence scoring
- ✅ **Geo-Based Alerts**: Location-aware notifications within configurable radius
- ✅ **Multi-Channel Notifications**: Push, SMS, Call, Device Buzzer
- ✅ **Risk Level System**: LOW, MEDIUM, HIGH, CRITICAL classifications
- ✅ **Background Processing**: Celery + Redis for async tasks
- ✅ **Audit Logging**: Track all ranger/admin actions
- ✅ **API Documentation**: Swagger/OpenAPI auto-generated docs
- ✅ **Production-Ready**: Scalable, secure, well-documented

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   ESP32     │─────▶│  Django API  │─────▶│  AI Service │
│   Camera    │      │  (REST)      │      │  (ML Model) │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ├──▶ MySQL Database
                            │
                            ├──▶ Redis (Celery)
                            │
                            └──▶ Notification Services
                                 (FCM, SMS, Call)
```

## 📦 Tech Stack

- **Backend**: Django 5.2 + Django REST Framework
- **Database**: MySQL 8.0
- **Cache/Queue**: Redis
- **Task Queue**: Celery
- **Authentication**: JWT (SimpleJWT)
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Image Processing**: Pillow
- **Deployment**: Gunicorn + Nginx

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.10+
MySQL 8.0+
Redis 6.0+ (optional, for Celery)
```

### Installation

```bash
# 1. Navigate to server directory
cd INOHACK/dashboard/server

# 2. Create virtual environment
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows CMD:
venv\Scripts\activate.bat

# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env  # Linux/Mac
Copy-Item .env.example .env  # Windows PowerShell

# ⚠️ IMPORTANT: Edit .env and set your MySQL password!
# DB_PASSWORD=your-actual-mysql-password

# 5. Setup database
mysql -u root -p
CREATE DATABASE animal_detection_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 6. Run migrations
python manage.py makemigrations
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Create media directory (logs is auto-created now!)
mkdir media

# 9. Run development server
python manage.py runserver
```

**✅ Server should now be running at http://localhost:8000/**

### Start Background Workers

```bash
# Terminal 1: Celery Worker
celery -A server worker -l info

# Terminal 2: Celery Beat (Scheduler)
celery -A server beat -l info
```

### Access Points

- **API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
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

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "farmer1",
    "password": "SecurePass123!"
}

Response:
{
    "user": {
        "id": "uuid",
        "username": "farmer1",
        "email": "farmer1@example.com",
        "role": "FARMER"
    },
    "tokens": {
        "refresh": "refresh_token_here",
        "access": "access_token_here"
    }
}
```

#### Get Profile
```http
GET /api/auth/me/
Authorization: Bearer <access_token>
```

### Device Management

#### Claim Device (Farmers)
```http
POST /api/devices/claim/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "device_uid": "ESP32_001",
    "device_name": "Farm Entrance Camera",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "location_name": "Main Farm Gate"
}
```

#### List Devices
```http
GET /api/devices/
Authorization: Bearer <access_token>

# Farmers see only their devices
# Rangers see all devices
```

#### Device Heartbeat
```http
POST /api/devices/{device_id}/heartbeat/
Authorization: Bearer <access_token>

{
    "firmware_version": "1.0.5",
    "battery_level": 85.5,
    "signal_strength": -45
}

Response:
{
    "status": "ok",
    "buzzer_command": "OFF"
}
```

### Image Upload (ESP32)

```http
POST /api/images/upload/
Content-Type: multipart/form-data

device_uid: ESP32_001
device_api_key: <64-character-hex-api-key>
image: <binary-image-file>
captured_at: 2024-01-20T10:30:00Z

Response:
{
    "status": "success",
    "image_id": "uuid",
    "message": "Image received and queued for processing"
}
```

### Detection Endpoints

#### List Detections
```http
GET /api/detections/
Authorization: Bearer <access_token>

# Query parameters:
?animal_type=tiger
?risk_level=CRITICAL
?device=device_uuid
```

#### Verify Detection (Rangers Only)
```http
POST /api/detections/{detection_id}/verify/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "verified": true,
    "verification_notes": "Confirmed tiger sighting"
}
```

### Alert Endpoints

#### List Alerts
```http
GET /api/alerts/
Authorization: Bearer <access_token>

# Query parameters:
?status=SENT
?alert_type=PUSH
```

#### Acknowledge Alert
```http
POST /api/alerts/{alert_id}/acknowledge/
Authorization: Bearer <access_token>
```

### Dashboard Statistics
```http
GET /api/dashboard/stats/
Authorization: Bearer <access_token>

Response:
{
    "total_devices": 5,
    "active_devices": 4,
    "total_images": 1234,
    "total_detections": 89,
    "critical_alerts": 3,
    "recent_detections": [...],
    "detection_by_animal": {...},
    "detection_by_risk": {...}
}
```

## 🔐 Role-Based Permissions

### Farmer
- Register and manage own devices
- View images from own devices
- View detections from own devices
- Receive alerts for own devices and nearby threats
- Acknowledge own alerts

### Forest Officer / Ranger
- View **all** devices, images, detections
- Verify detections
- Receive critical alerts region-wide
- Access audit logs

### Admin
- Full system access
- User management
- System configuration
- All ranger permissions

## 🤖 AI Detection Workflow

1. **ESP32 captures image** → Uploads to `/api/images/upload/`
2. **API validates device** → Saves image to storage
3. **Celery task triggered** → Sends image to AI service
4. **AI returns detections** → Creates `AnimalDetection` records
5. **Risk level determined** → Based on animal type + confidence
6. **Alerts created** → For device owner + nearby users
7. **Notifications dispatched** → Push, SMS, Call, Buzzer
8. **Rangers notified** → For critical detections

## 🌍 Geo-Based Alert System

### How It Works

1. Users opt-in for location tracking (`location_consent=true`)
2. App updates `last_known_lat` and `last_known_lon` periodically
3. When detection occurs, system:
   - Calculates distance to all consented users
   - Alerts users within `ALERT_RADIUS_KM` (default: 5km)
   - Includes distance in alert message

### Privacy

- Location tracking requires explicit consent
- Only last known location stored (not continuous tracking)
- No location history maintained
- Users can disable anytime

## 🎚️ Risk Level Configuration

```python
RISK_LEVELS = {
    "LOW": {
        "animals": ["boar", "deer", "bison"],
        "confidence_threshold": 0.5,
        "alert_types": ["PUSH"]
    },
    "MEDIUM": {
        "animals": ["bear", "elephant"],
        "confidence_threshold": 0.6,
        "alert_types": ["PUSH", "SMS"]
    },
    "HIGH": {
        "animals": ["leopard"],
        "confidence_threshold": 0.7,
        "alert_types": ["PUSH", "SMS", "BUZZER"]
    },
    "CRITICAL": {
        "animals": ["tiger", "lion"],
        "confidence_threshold": 0.7,
        "alert_types": ["PUSH", "SMS", "CALL", "BUZZER"]
    }
}
```

## 🔧 Environment Configuration

Key `.env` variables:

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=animal_detection_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306

# Redis & Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# AI Service
AI_INFERENCE_URL=http://localhost:8001/predict
AI_INFERENCE_TIMEOUT=30

# Notifications
FCM_SERVER_KEY=your-fcm-key
SMS_API_KEY=your-sms-key
CALL_API_KEY=your-call-key

# Alerts
ALERT_RADIUS_KM=5.0
```

## 📱 ESP32 Integration Guide

### Device Registration Flow

1. **Admin pre-registers device** in Django admin with unique `device_uid`
2. **System generates** 64-char API key automatically
3. **Farmer claims device** via mobile app using device UID
4. **ESP32 receives credentials** and stores in EEPROM
5. **Device authenticates** for all subsequent requests

### Sample ESP32 Code

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"

const char* deviceUID = "ESP32_001";
const char* apiKey = "your-64-char-api-key";
const char* serverURL = "http://api.yourdomain.com/api/images/upload/";

void uploadImage() {
    camera_fb_t *fb = esp_camera_fb_get();
    
    HTTPClient http;
    http.begin(serverURL);
    
    String boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW";
    http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
    
    // Build multipart form data
    String postData = "--" + boundary + "\r\n";
    postData += "Content-Disposition: form-data; name=\"device_uid\"\r\n\r\n";
    postData += deviceUID + "\r\n";
    // ... add other fields
    
    int httpResponseCode = http.POST(postData);
    
    esp_camera_fb_return(fb);
    http.end();
}
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test api

# With coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

## 📊 Monitoring & Logs

### Check System Status

```bash
# Django logs
tail -f logs/django.log

# Celery worker status
celery -A server inspect active
celery -A server inspect stats

# Database connections
python manage.py dbshell
```

### Key Metrics to Monitor

- API response times
- Celery queue lengths
- Database query performance
- Failed notification retries
- Image processing times
- Alert delivery rates

## 🚀 Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guide including:

- AWS EC2 setup
- Nginx configuration
- SSL/TLS setup
- Systemd service files
- Database optimization
- Security hardening

## 🔒 Security Features

- JWT token authentication
- Password hashing (Django's PBKDF2)
- CORS configuration
- Rate limiting
- SQL injection protection (Django ORM)
- XSS protection
- CSRF protection
- Audit logging for sensitive actions
- API key encryption
- Secure file upload validation

## 📈 Scalability

### Horizontal Scaling

- Stateless API (can run multiple instances)
- Celery workers can be distributed
- Database read replicas supported
- Redis cluster for high availability

### Performance Optimization

- Database indexing on frequent queries
- Celery for async processing
- Image compression
- Query optimization with `select_related` and `prefetch_related`
- Redis caching for frequent reads

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check MySQL service
sudo systemctl status mysql
# Verify credentials in .env
```

**Celery Tasks Not Running**
```bash
# Check Redis
redis-cli ping
# Restart worker
celery -A server worker --purge -l info
```

**Image Upload Fails**
```bash
# Check media folder permissions
chmod 755 media/
# Check file size limits in settings.py
```

## 📖 Additional Documentation

- [Full API Reference](http://localhost:8000/api/docs/)
- [Deployment Guide](DEPLOYMENT.md)
- [Django Documentation](https://docs.djangoproject.com/)
- [DRF Documentation](https://www.django-rest-framework.org/)

## 🐛 Troubleshooting

### Common Issues

**Server won't start - "logs directory not found"**
- ✅ **FIXED!** - Logs directory is now auto-created by Django

**MySQL connection error**
```bash
# Check if MySQL is running
Get-Service MySQL*  # Windows
sudo systemctl status mysql  # Linux

# Verify credentials in .env file
DB_PASSWORD=your-actual-password  # Must match your MySQL password
```

**mysqlclient installation fails (Windows)**
```bash
# Install Visual C++ Build Tools first
# Or use PyMySQL as alternative - see TROUBLESHOOTING.md
```

**"No module named 'corsheaders'"**
```bash
pip install -r requirements.txt
```

**For more issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)** ⭐

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

[Your License Here]

## 👥 Team

- [Your Team Members]

## 📧 Support

For issues and questions:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) first
- Review logs: `logs/django.log`
- GitHub Issues: [Create Issue]

---

**Built with ❤️ for wildlife conservation and farmer safety**
