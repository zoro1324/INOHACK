# API Testing Guide

## Using Postman/Thunder Client/HTTPie

### 1. Register a User

```bash
POST http://localhost:8000/api/auth/register/
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

### 2. Login

```bash
POST http://localhost:8000/api/auth/login/
Content-Type: application/json

{
    "username": "farmer1",
    "password": "SecurePass123!"
}

# Save the access token from response
```

### 3. Get User Profile

```bash
GET http://localhost:8000/api/auth/me/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### 4. Claim a Device

```bash
POST http://localhost:8000/api/devices/claim/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
    "device_uid": "ESP32_001",
    "device_name": "Farm Entrance Camera",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "location_name": "Main Farm Gate"
}

# Save the api_key from response for ESP32
```

### 5. List Devices

```bash
GET http://localhost:8000/api/devices/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### 6. Upload Image (ESP32 simulation)

```bash
POST http://localhost:8000/api/images/upload/
Content-Type: multipart/form-data

device_uid: ESP32_001
device_api_key: YOUR_DEVICE_API_KEY
image: @/path/to/test_image.jpg
captured_at: 2024-01-20T10:30:00Z
```

### 7. List Images

```bash
GET http://localhost:8000/api/images/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### 8. List Detections

```bash
GET http://localhost:8000/api/detections/
Authorization: Bearer YOUR_ACCESS_TOKEN

# With filters:
GET http://localhost:8000/api/detections/?animal_type=tiger
GET http://localhost:8000/api/detections/?risk_level=CRITICAL
```

### 9. Verify Detection (Ranger only)

```bash
POST http://localhost:8000/api/detections/DETECTION_ID/verify/
Authorization: Bearer RANGER_ACCESS_TOKEN
Content-Type: application/json

{
    "verified": true,
    "verification_notes": "Confirmed tiger sighting at location"
}
```

### 10. List Alerts

```bash
GET http://localhost:8000/api/alerts/
Authorization: Bearer YOUR_ACCESS_TOKEN

# With filters:
GET http://localhost:8000/api/alerts/?status=SENT
GET http://localhost:8000/api/alerts/?alert_type=PUSH
```

### 11. Acknowledge Alert

```bash
POST http://localhost:8000/api/alerts/ALERT_ID/acknowledge/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### 12. Dashboard Statistics

```bash
GET http://localhost:8000/api/dashboard/stats/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### 13. Device Heartbeat

```bash
POST http://localhost:8000/api/devices/DEVICE_ID/heartbeat/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
    "firmware_version": "1.0.5",
    "battery_level": 85.5,
    "signal_strength": -45
}
```

### 14. Audit Logs (Ranger/Admin only)

```bash
GET http://localhost:8000/api/audit-logs/
Authorization: Bearer RANGER_ACCESS_TOKEN
```

## Testing with Python

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Register
response = requests.post(f"{BASE_URL}/auth/register/", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "phone_number": "+1234567890",
    "first_name": "Test",
    "last_name": "User",
    "role": "FARMER"
})
print(response.json())

# Login
response = requests.post(f"{BASE_URL}/auth/login/", json={
    "username": "testuser",
    "password": "SecurePass123!"
})
tokens = response.json()['tokens']
access_token = tokens['access']

# Get profile
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/auth/me/", headers=headers)
print(response.json())

# Claim device
response = requests.post(f"{BASE_URL}/devices/claim/", 
    headers=headers,
    json={
        "device_uid": "ESP32_TEST",
        "device_name": "Test Camera",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "location_name": "Test Location"
    }
)
device = response.json()
print(f"Device claimed: {device['id']}")
print(f"API Key: {device['api_key']}")  # Note: api_key might not be in response for security

# Upload image
with open('test_image.jpg', 'rb') as f:
    files = {'image': f}
    data = {
        'device_uid': 'ESP32_TEST',
        'device_api_key': 'your-device-api-key',
        'captured_at': '2024-01-20T10:30:00Z'
    }
    response = requests.post(f"{BASE_URL}/images/upload/", 
        files=files, data=data)
    print(response.json())

# List detections
response = requests.get(f"{BASE_URL}/detections/", headers=headers)
print(response.json())

# Dashboard stats
response = requests.get(f"{BASE_URL}/dashboard/stats/", headers=headers)
stats = response.json()
print(f"Total devices: {stats['total_devices']}")
print(f"Total detections: {stats['total_detections']}")
```

## Testing with cURL

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "farmer1",
    "email": "farmer1@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "phone_number": "+1234567890",
    "first_name": "John",
    "last_name": "Doe",
    "role": "FARMER"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "farmer1",
    "password": "SecurePass123!"
  }'

# Get profile (use token from login response)
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Upload image
curl -X POST http://localhost:8000/api/images/upload/ \
  -F "device_uid=ESP32_001" \
  -F "device_api_key=your-api-key" \
  -F "image=@test_image.jpg" \
  -F "captured_at=2024-01-20T10:30:00Z"
```

## Common Testing Scenarios

### Scenario 1: Complete Farmer Workflow

1. Register as farmer
2. Login
3. Claim device
4. Device uploads image
5. View image
6. View detections
7. Receive and acknowledge alert

### Scenario 2: Ranger Workflow

1. Login as ranger (created via admin)
2. View all devices
3. View all detections
4. Verify detections
5. View audit logs

### Scenario 3: High-Risk Detection

1. Upload image with tiger
2. AI detects tiger with high confidence
3. System creates CRITICAL risk detection
4. Alerts sent to:
   - Device owner (PUSH, SMS, CALL, BUZZER)
   - Nearby users within 5km (PUSH, SMS)
   - All rangers (PUSH)
5. Device buzzer activated
6. Ranger verifies detection

## Expected HTTP Status Codes

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Error Response Format

```json
{
    "error": true,
    "message": "Error description",
    "details": {
        "field_name": ["Error message"]
    }
}
```
