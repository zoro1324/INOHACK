# Database Migration & Setup Guide

## Initial Setup

### 1. Create MySQL Database

```sql
-- Connect to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE animal_detection_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (optional, for production)
CREATE USER 'animal_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON animal_detection_db.* TO 'animal_user'@'localhost';
FLUSH PRIVILEGES;

-- Exit MySQL
EXIT;
```

### 2. Configure Django Database

Edit `.env`:
```bash
DB_NAME=animal_detection_db
DB_USER=root  # or 'animal_user' if created above
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

### 3. Install MySQL Client

**Windows:**
```bash
pip install mysqlclient

# If above fails, download wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient
# Then: pip install mysqlclient‑1.4.6‑cp310‑cp310‑win_amd64.whl
```

**Linux:**
```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient
```

**macOS:**
```bash
brew install mysql
pip install mysqlclient
```

### 4. Run Migrations

```bash
# Create migrations for api app
python manage.py makemigrations api

# Apply all migrations
python manage.py migrate

# Verify migrations
python manage.py showmigrations
```

Expected output:
```
api
 [X] 0001_initial
 [X] 0002_auto_...
auth
 [X] 0001_initial
 ...
```

---

## Database Schema Overview

### Tables Created

1. **users** - Custom user model with roles
2. **iot_devices** - IoT device registration
3. **image_captures** - Uploaded images
4. **animal_detections** - AI detection results
5. **alerts** - Alert records
6. **audit_logs** - System audit trail

### Indexes Created

```sql
-- User indexes
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_users_location ON users(last_known_lat, last_known_lon);

-- Device indexes
CREATE INDEX idx_devices_uid ON iot_devices(device_uid);
CREATE INDEX idx_devices_owner ON iot_devices(owner_id);
CREATE INDEX idx_devices_location ON iot_devices(latitude, longitude);
CREATE INDEX idx_devices_active ON iot_devices(is_active);

-- Image indexes
CREATE INDEX idx_images_device ON image_captures(device_id, captured_at);
CREATE INDEX idx_images_processed ON image_captures(ai_processed);
CREATE INDEX idx_images_date ON image_captures(captured_at DESC);

-- Detection indexes
CREATE INDEX idx_detections_image ON animal_detections(image_id);
CREATE INDEX idx_detections_animal ON animal_detections(animal_type);
CREATE INDEX idx_detections_risk ON animal_detections(risk_level);
CREATE INDEX idx_detections_date ON animal_detections(detected_at DESC);

-- Alert indexes
CREATE INDEX idx_alerts_detection ON alerts(detection_id);
CREATE INDEX idx_alerts_recipient ON alerts(recipient_id, status);
CREATE INDEX idx_alerts_date ON alerts(created_at DESC);
CREATE INDEX idx_alerts_status ON alerts(status);

-- Audit indexes
CREATE INDEX idx_audit_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_date ON audit_logs(created_at DESC);
```

---

## Sample Data Creation

### Create Superuser

```bash
python manage.py createsuperuser

# Enter details:
Username: admin
Email: admin@example.com
Password: SecureAdminPass123!
```

### Create Sample Users via Django Shell

```bash
python manage.py shell
```

```python
from api.models import User

# Create a farmer
farmer = User.objects.create_user(
    username='farmer1',
    email='farmer1@example.com',
    password='FarmerPass123!',
    phone_number='+1234567890',
    first_name='John',
    last_name='Doe',
    role='FARMER'
)

# Create a ranger
ranger = User.objects.create_user(
    username='ranger1',
    email='ranger1@example.com',
    password='RangerPass123!',
    phone_number='+1234567891',
    first_name='Jane',
    last_name='Smith',
    role='RANGER'
)

print(f"Created farmer: {farmer.username}")
print(f"Created ranger: {ranger.username}")

exit()
```

### Create Sample Device

```python
from api.models import User, IoTDevice
from api.utils import generate_device_api_key

farmer = User.objects.get(username='farmer1')

device = IoTDevice.objects.create(
    device_uid='ESP32_001',
    device_name='Farm Entrance Camera',
    owner=farmer,
    latitude=12.9716,
    longitude=77.5946,
    location_name='Main Farm Gate',
    api_key=generate_device_api_key(),
    is_active=True,
    firmware_version='1.0.0'
)

print(f"Device created: {device.device_uid}")
print(f"API Key: {device.api_key}")
```

---

## Database Maintenance

### Backup Database

```bash
# Full backup
mysqldump -u root -p animal_detection_db > backup_$(date +%Y%m%d).sql

# Backup with gzip compression
mysqldump -u root -p animal_detection_db | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore Database

```bash
# Restore from backup
mysql -u root -p animal_detection_db < backup_20240120.sql

# Restore from compressed backup
gunzip < backup_20240120.sql.gz | mysql -u root -p animal_detection_db
```

### Reset Database (Development Only)

```bash
# Drop all tables and recreate
python manage.py flush

# Or completely reset
mysql -u root -p
DROP DATABASE animal_detection_db;
CREATE DATABASE animal_detection_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

python manage.py migrate
python manage.py createsuperuser
```

---

## Common Migration Issues

### Issue 1: mysqlclient installation fails

**Solution:**
```bash
# Windows: Install Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/

# Or use PyMySQL as alternative:
pip install PyMySQL

# Add to settings.py __init__.py:
import pymysql
pymysql.install_as_MySQLdb()
```

### Issue 2: Migration conflicts

```bash
# Show current migrations
python manage.py showmigrations

# If conflicts, fake the migration
python manage.py migrate --fake api 0001

# Then run normally
python manage.py migrate
```

### Issue 3: Custom user model not recognized

```bash
# Ensure AUTH_USER_MODEL is set in settings.py
AUTH_USER_MODEL = 'api.User'

# Delete migrations and recreate
rm -rf api/migrations/
python manage.py makemigrations api
python manage.py migrate
```

### Issue 4: Foreign key constraints

```bash
# Disable foreign key checks (MySQL)
SET FOREIGN_KEY_CHECKS = 0;
# Run your operations
SET FOREIGN_KEY_CHECKS = 1;
```

---

## Database Optimization

### Add Indexes

```sql
-- If you need additional indexes:
CREATE INDEX idx_custom ON table_name(column_name);

-- Composite index
CREATE INDEX idx_composite ON table_name(col1, col2);

-- Check index usage
SHOW INDEX FROM users;
```

### Analyze Tables

```sql
-- Update table statistics
ANALYZE TABLE users;
ANALYZE TABLE iot_devices;
ANALYZE TABLE image_captures;
ANALYZE TABLE animal_detections;
ANALYZE TABLE alerts;
```

### Monitor Performance

```sql
-- Show slow queries
SHOW PROCESSLIST;

-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- Check table sizes
SELECT 
    table_name AS 'Table',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.TABLES
WHERE table_schema = 'animal_detection_db'
ORDER BY (data_length + index_length) DESC;
```

---

## Production Database Setup

### Security Hardening

```sql
-- Remove anonymous users
DELETE FROM mysql.user WHERE User='';

-- Remove test database
DROP DATABASE IF EXISTS test;

-- Restrict root access to localhost only
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');

-- Create application user with limited privileges
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT SELECT, INSERT, UPDATE, DELETE ON animal_detection_db.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
```

### Connection Pooling

In `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
            'use_unicode': True,
        },
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}
```

### Backup Strategy

```bash
# Automated daily backups (crontab)
0 2 * * * /usr/bin/mysqldump -u backup_user -p'password' animal_detection_db | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz

# Keep only last 30 days
0 3 * * * find /backups/ -name "db_*.sql.gz" -mtime +30 -delete
```

---

## Testing Database Setup

```bash
# Test connection
python manage.py dbshell

# Run checks
python manage.py check

# Test query
python manage.py shell
>>> from api.models import User
>>> User.objects.count()
0
>>> exit()
```

---

## Troubleshooting

### Check MySQL Status

```bash
# Linux
sudo systemctl status mysql

# Windows
# Check Services in Task Manager or:
net start MySQL
```

### Check Django Database Connection

```python
from django.db import connection
print(connection.settings_dict)
```

### View All Tables

```sql
USE animal_detection_db;
SHOW TABLES;
DESCRIBE users;
```

---

**Database setup complete! ✅**
