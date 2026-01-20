# Quick Fix Guide - Common Issues

## Issue: Server Won't Start - "logs directory not found"

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'D:\\INOHACK\\dashboard\\server\\logs\\django.log'
```

**Fix:** ✅ **FIXED** - The logs directory is now auto-created by Django settings.

---

## Issue: mysqlclient Installation Fails (Windows)

**Error:**
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**Fix:**
```powershell
# Option 1: Install Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Option 2: Use PyMySQL instead
pip uninstall mysqlclient
pip install PyMySQL
```

Then add to `server/__init__.py` (before celery import):
```python
import pymysql
pymysql.install_as_MySQLdb()
```

---

## Issue: Module 'api' has no attribute 'apps'

**Error:**
```
django.core.exceptions.ImproperlyConfigured: 'api' must supply a default AppConfig subclass
```

**Fix:** Ensure `api/apps.py` exists with:
```python
from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
```

---

## Issue: No module named 'corsheaders'

**Error:**
```
ModuleNotFoundError: No module named 'corsheaders'
```

**Fix:**
```powershell
pip install -r requirements.txt
```

---

## Issue: Can't connect to MySQL

**Error:**
```
django.db.utils.OperationalError: (2003, "Can't connect to MySQL server on 'localhost'")
```

**Fix:**
```powershell
# 1. Check MySQL is running
# Windows:
Get-Service MySQL*
# Start if stopped:
Start-Service MySQL80  # or your MySQL service name

# 2. Test connection
mysql -u root -p

# 3. Create database
CREATE DATABASE animal_detection_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 4. Update .env with correct credentials
DB_NAME=animal_detection_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

---

## Issue: No such table: api_user

**Error:**
```
django.db.utils.OperationalError: no such table: api_user
```

**Fix:**
```powershell
# Run migrations
python manage.py makemigrations
python manage.py migrate
```

---

## Issue: Redis Connection Error

**Error:**
```
redis.exceptions.ConnectionError: Error 10061 connecting to localhost:6379
```

**Fix:**
```powershell
# Install Redis for Windows
# Download from: https://github.com/microsoftarchive/redis/releases

# Or use Docker
docker run -d -p 6379:6379 redis

# Or disable Celery temporarily:
# Comment out Celery import in server/__init__.py
```

---

## Issue: SECRET_KEY not found

**Error:**
```
django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty
```

**Fix:**
```powershell
# Create .env file
Copy-Item .env.example .env

# Edit .env and set:
DJANGO_SECRET_KEY=your-secret-key-here-change-this
```

Generate a secure key:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Complete Fresh Setup (Clean Slate)

```powershell
# 1. Navigate to project
cd D:\INOHACK\dashboard\server

# 2. Create and activate virtual environment
python -m venv venv
.\\venv\\Scripts\\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
Copy-Item .env.example .env
# Edit .env with your MySQL credentials

# 5. Create MySQL database
mysql -u root -p
CREATE DATABASE animal_detection_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 6. Create media directory (logs is auto-created)
mkdir media -ErrorAction SilentlyContinue

# 7. Run migrations
python manage.py makemigrations
python manage.py migrate

# 8. Create superuser
python manage.py createsuperuser

# 9. Start server
python manage.py runserver

# 10. In new terminal: Start Celery (if needed)
celery -A server worker -l info
```

---

## Verification Checklist

- [ ] Python 3.10+ installed: `python --version`
- [ ] MySQL running: `mysql -u root -p`
- [ ] Database created: `SHOW DATABASES;`
- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip list`
- [ ] `.env` file exists with correct values
- [ ] `media` directory exists
- [ ] Migrations applied: `python manage.py showmigrations`
- [ ] Server starts: `python manage.py runserver`
- [ ] Can access admin: http://localhost:8000/admin/
- [ ] Can access API docs: http://localhost:8000/api/docs/

---

## Quick Test

```powershell
# Test database connection
python manage.py dbshell

# Test migrations
python manage.py check

# Test admin access
# Navigate to: http://localhost:8000/admin/
```

---

## Still Having Issues?

1. Check logs: `Get-Content logs\django.log -Tail 50`
2. Run with verbose output: `python manage.py runserver --verbosity 3`
3. Check Django version: `pip show django`
4. Verify all apps installed: `python manage.py check --deploy`

---

## Windows-Specific Tips

```powershell
# Use PowerShell (not CMD) for better compatibility
# Activate virtual environment in PowerShell:
.\\venv\\Scripts\\Activate.ps1

# If script execution is disabled:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Check Python path:
Get-Command python | Select-Object -ExpandProperty Source
```

---

✅ **Your server should now be running on http://localhost:8000/**
