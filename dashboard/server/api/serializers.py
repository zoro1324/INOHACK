from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User, IoTDevice, ImageCapture, AnimalDetection, Alert, AuditLog
import secrets


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(
        write_only=True, required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2',
            'phone_number', 'role', 'first_name', 'last_name'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def validate_role(self, value):
        # Only allow FARMER registration through API
        # RANGER and ADMIN should be set by admins
        if value not in ['FARMER']:
            raise serializers.ValidationError(
                "Only FARMER role can be registered through API"
            )
        return value
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.',
                    code='authorization'
                )
        else:
            raise serializers.ValidationError(
                'Must include "username" and "password".',
                code='authorization'
            )
        
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone_number', 'role',
            'first_name', 'last_name', 'last_known_lat', 'last_known_lon',
            'location_consent', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'last_known_lat', 'last_known_lon', 'location_consent',
            'fcm_token'
        ]


class IoTDeviceSerializer(serializers.ModelSerializer):
    """
    Serializer for IoT Device
    """
    owner_details = UserSerializer(source='owner', read_only=True)
    is_claimed = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = IoTDevice
        fields = [
            'id', 'device_uid', 'device_name', 'owner', 'owner_details',
            'latitude', 'longitude', 'location_name', 'is_active',
            'firmware_version', 'buzzer_active', 'is_claimed',
            'last_seen_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'api_key', 'created_at', 'updated_at',
            'last_seen_at'
        ]


class DeviceClaimSerializer(serializers.Serializer):
    """
    Serializer for claiming a device
    """
    device_uid = serializers.CharField(max_length=50)
    device_name = serializers.CharField(max_length=100, required=False)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    location_name = serializers.CharField(max_length=255, required=False)
    
    def validate_device_uid(self, value):
        try:
            device = IoTDevice.objects.get(device_uid=value)
            if device.is_claimed():
                raise serializers.ValidationError(
                    "This device is already claimed by another user."
                )
        except IoTDevice.DoesNotExist:
            # Device doesn't exist, will be created
            pass
        return value


class DeviceHeartbeatSerializer(serializers.Serializer):
    """
    Serializer for device heartbeat
    """
    firmware_version = serializers.CharField(max_length=20, required=False)
    battery_level = serializers.FloatField(required=False)
    signal_strength = serializers.FloatField(required=False)


class ImageCaptureSerializer(serializers.ModelSerializer):
    """
    Serializer for Image Capture
    """
    device_details = IoTDeviceSerializer(source='device', read_only=True)
    detection_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ImageCapture
        fields = [
            'id', 'device', 'device_details', 'image',
            'ai_processed', 'processing_started_at', 'processing_completed_at',
            'file_size', 'captured_at', 'created_at', 'detection_count'
        ]
        read_only_fields = [
            'id', 'ai_processed', 'processing_started_at',
            'processing_completed_at', 'created_at'
        ]
    
    def get_detection_count(self, obj):
        return obj.detections.count()


class ImageUploadSerializer(serializers.Serializer):
    """
    Serializer for ESP32 image upload
    """
    device_uid = serializers.CharField(max_length=50)
    device_api_key = serializers.CharField(max_length=64)
    image = serializers.ImageField()
    captured_at = serializers.DateTimeField()
    
    def validate(self, attrs):
        device_uid = attrs.get('device_uid')
        device_api_key = attrs.get('device_api_key')
        
        try:
            device = IoTDevice.objects.get(
                device_uid=device_uid,
                api_key=device_api_key
            )
            if not device.is_active:
                raise serializers.ValidationError(
                    "Device is not active."
                )
            attrs['device'] = device
        except IoTDevice.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid device credentials."
            )
        
        return attrs


class AnimalDetectionSerializer(serializers.ModelSerializer):
    """
    Serializer for Animal Detection
    """
    image_details = ImageCaptureSerializer(source='image', read_only=True)
    verified_by_details = UserSerializer(source='verified_by', read_only=True)
    
    class Meta:
        model = AnimalDetection
        fields = [
            'id', 'image', 'image_details', 'animal_type',
            'confidence_score', 'risk_level', 'bounding_boxes',
            'verified', 'verified_by', 'verified_by_details',
            'verification_notes', 'detected_at'
        ]
        read_only_fields = [
            'id', 'detected_at', 'image', 'animal_type',
            'confidence_score', 'risk_level', 'bounding_boxes'
        ]


class DetectionVerificationSerializer(serializers.Serializer):
    """
    Serializer for verifying detections (Rangers only)
    """
    verified = serializers.BooleanField()
    verification_notes = serializers.CharField(
        required=False, allow_blank=True
    )


class AlertSerializer(serializers.ModelSerializer):
    """
    Serializer for Alert
    """
    detection_details = AnimalDetectionSerializer(source='detection', read_only=True)
    recipient_details = UserSerializer(source='recipient', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'detection', 'detection_details', 'alert_type',
            'recipient', 'recipient_details', 'title', 'message',
            'status', 'sent_at', 'acknowledged_at', 'distance_km',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'sent_at', 'created_at', 'updated_at'
        ]


class AlertAcknowledgeSerializer(serializers.Serializer):
    """
    Serializer for acknowledging alerts
    """
    alert_id = serializers.UUIDField()


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for Audit Log
    """
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_details', 'action',
            'target_model', 'target_id', 'details',
            'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DashboardStatsSerializer(serializers.Serializer):
    """
    Serializer for dashboard statistics
    """
    total_devices = serializers.IntegerField()
    active_devices = serializers.IntegerField()
    total_images = serializers.IntegerField()
    total_detections = serializers.IntegerField()
    critical_alerts = serializers.IntegerField()
    recent_detections = AnimalDetectionSerializer(many=True)
    detection_by_animal = serializers.DictField()
    detection_by_risk = serializers.DictField()
