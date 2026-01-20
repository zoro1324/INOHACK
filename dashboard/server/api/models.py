from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
import uuid


class User(AbstractUser):
    """
    Custom User model with role-based access control
    """
    ROLE_CHOICES = [
        ('FARMER', 'Farmer'),
        ('RANGER', 'Forest Officer / Ranger'),
        ('ADMIN', 'Administrator'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='FARMER')
    
    # Location tracking (with consent)
    last_known_lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Last known latitude for geo-based alerts"
    )
    last_known_lon = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Last known longitude for geo-based alerts"
    )
    location_consent = models.BooleanField(
        default=False,
        help_text="User consent for location tracking"
    )
    
    # FCM Token for push notifications
    fcm_token = models.CharField(max_length=255, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Override related_name to avoid conflicts
    groups = models.ManyToManyField(
        Group,
        related_name='api_users',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='api_users',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['last_known_lat', 'last_known_lon']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_farmer(self):
        return self.role == 'FARMER'
    
    def is_ranger(self):
        return self.role == 'RANGER'
    
    def is_admin_user(self):
        return self.role == 'ADMIN'


class IoTDevice(models.Model):
    """
    IoT Device (ESP32 with camera) Model
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_uid = models.CharField(
        max_length=50, unique=True,
        help_text="Unique device identifier printed on hardware"
    )
    device_name = models.CharField(max_length=100, blank=True)
    
    # Device ownership
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='devices',
        help_text="Farmer who owns this device"
    )
    
    # Location
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_name = models.CharField(max_length=255, blank=True)
    
    # Device status
    is_active = models.BooleanField(default=True)
    firmware_version = models.CharField(max_length=20, blank=True)
    
    # API Key for device authentication
    api_key = models.CharField(max_length=64, unique=True)
    
    # Buzzer status
    buzzer_active = models.BooleanField(default=False)
    
    # Timestamps
    last_seen_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'iot_devices'
        indexes = [
            models.Index(fields=['device_uid']),
            models.Index(fields=['owner']),
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.device_name or self.device_uid} ({self.location_name})"
    
    def is_claimed(self):
        return self.owner is not None


class ImageCapture(models.Model):
    """
    Images captured by IoT devices
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        IoTDevice, on_delete=models.CASCADE,
        related_name='images'
    )
    
    # Image file
    image = models.ImageField(upload_to='captures/%Y/%m/%d/')
    
    # Processing status
    ai_processed = models.BooleanField(default=False)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    file_size = models.IntegerField(help_text="File size in bytes")
    captured_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'image_captures'
        indexes = [
            models.Index(fields=['device', 'captured_at']),
            models.Index(fields=['ai_processed']),
            models.Index(fields=['-captured_at']),
        ]
        ordering = ['-captured_at']
    
    def __str__(self):
        return f"Image from {self.device.device_uid} at {self.captured_at}"


class AnimalDetection(models.Model):
    """
    AI-detected animals in images
    """
    ANIMAL_CHOICES = [
        ('tiger', 'Tiger'),
        ('lion', 'Lion'),
        ('leopard', 'Leopard'),
        ('elephant', 'Elephant'),
        ('bear', 'Bear'),
        ('bison', 'Bison'),
        ('boar', 'Boar'),
        ('deer', 'Deer'),
        ('human', 'Human'),
        ('other', 'Other'),
    ]
    
    RISK_LEVEL_CHOICES = [
        ('LOW', 'Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('HIGH', 'High Risk'),
        ('CRITICAL', 'Critical Risk'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ForeignKey(
        ImageCapture, on_delete=models.CASCADE,
        related_name='detections'
    )
    
    # Detection details
    animal_type = models.CharField(max_length=20, choices=ANIMAL_CHOICES)
    confidence_score = models.FloatField(
        help_text="AI confidence score (0.0 to 1.0)"
    )
    risk_level = models.CharField(
        max_length=10, choices=RISK_LEVEL_CHOICES
    )
    
    # Bounding box coordinates
    bounding_boxes = models.JSONField(
        help_text="List of bounding boxes: [{x, y, width, height, confidence}, ...]"
    )
    
    # Verification (for rangers)
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='verified_detections'
    )
    verification_notes = models.TextField(blank=True)
    
    # Timestamps
    detected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'animal_detections'
        indexes = [
            models.Index(fields=['image']),
            models.Index(fields=['animal_type']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['-detected_at']),
        ]
        ordering = ['-detected_at']
    
    def __str__(self):
        return f"{self.get_animal_type_display()} - {self.get_risk_level_display()} ({self.confidence_score:.2f})"


class Alert(models.Model):
    """
    Alerts sent to users based on detections
    """
    ALERT_TYPE_CHOICES = [
        ('PUSH', 'Push Notification'),
        ('SMS', 'SMS Message'),
        ('CALL', 'Phone Call'),
        ('BUZZER', 'Device Buzzer'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
        ('ACKNOWLEDGED', 'Acknowledged'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    detection = models.ForeignKey(
        AnimalDetection, on_delete=models.CASCADE,
        related_name='alerts'
    )
    
    # Alert details
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPE_CHOICES)
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='received_alerts'
    )
    
    # Message content
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Status tracking
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    sent_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # Retry logic
    retry_count = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)
    
    # Distance from user (for geo-based alerts)
    distance_km = models.FloatField(
        null=True, blank=True,
        help_text="Distance from user's last known location"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'alerts'
        indexes = [
            models.Index(fields=['detection']),
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_alert_type_display()} to {self.recipient.username} - {self.get_status_display()}"


class AuditLog(models.Model):
    """
    Audit log for ranger and admin actions
    """
    ACTION_CHOICES = [
        ('VIEW_DEVICE', 'Viewed Device'),
        ('VIEW_IMAGE', 'Viewed Image'),
        ('VIEW_DETECTION', 'Viewed Detection'),
        ('VERIFY_DETECTION', 'Verified Detection'),
        ('OVERRIDE_ALERT', 'Override Alert'),
        ('UPDATE_DEVICE', 'Updated Device'),
        ('DELETE_IMAGE', 'Deleted Image'),
        ('CHANGE_USER_ROLE', 'Changed User Role'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, related_name='audit_logs'
    )
    
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    target_model = models.CharField(max_length=50)
    target_id = models.CharField(max_length=100)
    
    # Additional context
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown'} - {self.get_action_display()} at {self.created_at}"
