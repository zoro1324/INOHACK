from django.shortcuts import render
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.db.models import Count, Q
from django.conf import settings

from .models import (
    User, IoTDevice, ImageCapture, AnimalDetection,
    Alert, AuditLog
)
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserProfileUpdateSerializer, IoTDeviceSerializer, DeviceClaimSerializer,
    DeviceHeartbeatSerializer, ImageCaptureSerializer, ImageUploadSerializer,
    AnimalDetectionSerializer, DetectionVerificationSerializer,
    AlertSerializer, AlertAcknowledgeSerializer, AuditLogSerializer,
    DashboardStatsSerializer
)
from .permissions import (
    IsFarmer, IsRanger, IsAdmin, IsFarmerOrRanger,
    IsRangerOrAdmin, IsOwnerOrRanger, IsDeviceOwner,
    CanVerifyDetection
)
from .utils import (
    calculate_distance, create_audit_log, generate_device_api_key,
    validate_image_file
)
from .tasks import process_image_with_ai

import logging

logger = logging.getLogger(__name__)


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration
    POST /api/auth/register
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    """
    API endpoint for user login
    POST /api/auth/login
    """
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to get and update current user profile
    GET /api/auth/me
    PATCH /api/auth/me
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UserProfileUpdateSerializer
        return UserSerializer


# ============================================================================
# DEVICE MANAGEMENT VIEWS
# ============================================================================

class IoTDeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for IoT Device management
    
    Farmers can only see their own devices
    Rangers can see all devices
    """
    serializer_class = IoTDeviceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'RANGER' or user.role == 'ADMIN':
            # Rangers and Admins can see all devices
            queryset = IoTDevice.objects.all()
            create_audit_log(
                user, 'VIEW_DEVICE', 'IoTDevice', 'all',
                self.request, {'action': 'list_all'}
            )
        else:
            # Farmers can only see their own devices
            queryset = IoTDevice.objects.filter(owner=user)
        
        # Filters
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.select_related('owner').order_by('-created_at')
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Audit log
        create_audit_log(
            request.user, 'VIEW_DEVICE', 'IoTDevice', instance.id,
            request
        )
        
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'], permission_classes=[IsFarmer])
    def claim(self, request):
        """
        Claim an unclaimed device
        POST /api/devices/claim
        """
        serializer = DeviceClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        device_uid = serializer.validated_data['device_uid']
        
        try:
            # Try to get existing device
            device = IoTDevice.objects.get(device_uid=device_uid)
            if device.is_claimed():
                return Response(
                    {'error': 'Device already claimed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            device.owner = request.user
        except IoTDevice.DoesNotExist:
            # Create new device
            device = IoTDevice(
                device_uid=device_uid,
                owner=request.user,
                api_key=generate_device_api_key()
            )
        
        # Update device details
        device.device_name = serializer.validated_data.get(
            'device_name', f"Device {device_uid}"
        )
        device.latitude = serializer.validated_data['latitude']
        device.longitude = serializer.validated_data['longitude']
        device.location_name = serializer.validated_data.get('location_name', '')
        device.save()
        
        logger.info(f"Device {device_uid} claimed by user {request.user.username}")
        
        return Response(
            IoTDeviceSerializer(device).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def heartbeat(self, request, pk=None):
        """
        Device heartbeat endpoint
        POST /api/devices/{id}/heartbeat
        """
        device = self.get_object()
        
        # Check ownership or ranger permission
        if device.owner != request.user and request.user.role != 'RANGER':
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DeviceHeartbeatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Update last seen
        device.last_seen_at = timezone.now()
        
        # Update firmware if provided
        if 'firmware_version' in serializer.validated_data:
            device.firmware_version = serializer.validated_data['firmware_version']
        
        device.save()
        
        return Response({
            'status': 'ok',
            'buzzer_command': 'ON' if device.buzzer_active else 'OFF'
        })


# ============================================================================
# IMAGE AND DETECTION VIEWS
# ============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def image_upload_view(request):
    """
    ESP32 image upload endpoint
    POST /api/images/upload
    
    No JWT required - uses device_uid + api_key authentication
    """
    serializer = ImageUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    device = serializer.validated_data['device']
    image_file = serializer.validated_data['image']
    
    # Validate image
    is_valid, error_msg = validate_image_file(image_file)
    if not is_valid:
        return Response(
            {'error': error_msg},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create image capture
    image_capture = ImageCapture.objects.create(
        device=device,
        image=image_file,
        captured_at=serializer.validated_data['captured_at'],
        file_size=image_file.size
    )
    
    # Update device last seen
    device.last_seen_at = timezone.now()
    device.save(update_fields=['last_seen_at'])
    
    # Trigger async AI processing
    process_image_with_ai.delay(str(image_capture.id))
    
    logger.info(f"Image uploaded from device {device.device_uid}")
    
    return Response({
        'status': 'success',
        'image_id': str(image_capture.id),
        'message': 'Image received and queued for processing'
    }, status=status.HTTP_201_CREATED)


class ImageCaptureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing image captures
    
    Farmers can only see images from their devices
    Rangers can see all images
    """
    serializer_class = ImageCaptureSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'RANGER' or user.role == 'ADMIN':
            queryset = ImageCapture.objects.all()
        else:
            queryset = ImageCapture.objects.filter(device__owner=user)
        
        # Filters
        device_id = self.request.query_params.get('device', None)
        if device_id:
            queryset = queryset.filter(device__id=device_id)
        
        ai_processed = self.request.query_params.get('ai_processed', None)
        if ai_processed is not None:
            queryset = queryset.filter(
                ai_processed=ai_processed.lower() == 'true'
            )
        
        return queryset.select_related('device', 'device__owner').prefetch_related('detections')


class AnimalDetectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for animal detections
    """
    serializer_class = AnimalDetectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'RANGER' or user.role == 'ADMIN':
            queryset = AnimalDetection.objects.all()
        else:
            queryset = AnimalDetection.objects.filter(
                image__device__owner=user
            )
        
        # Filters
        animal_type = self.request.query_params.get('animal_type', None)
        if animal_type:
            queryset = queryset.filter(animal_type=animal_type)
        
        risk_level = self.request.query_params.get('risk_level', None)
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        
        device_id = self.request.query_params.get('device', None)
        if device_id:
            queryset = queryset.filter(image__device__id=device_id)
        
        return queryset.select_related(
            'image', 'image__device', 'verified_by'
        ).order_by('-detected_at')
    
    @action(detail=True, methods=['post'], permission_classes=[CanVerifyDetection])
    def verify(self, request, pk=None):
        """
        Verify a detection (Rangers only)
        POST /api/detections/{id}/verify
        """
        detection = self.get_object()
        
        serializer = DetectionVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        detection.verified = serializer.validated_data['verified']
        detection.verified_by = request.user
        detection.verification_notes = serializer.validated_data.get(
            'verification_notes', ''
        )
        detection.save()
        
        # Audit log
        create_audit_log(
            request.user, 'VERIFY_DETECTION', 'AnimalDetection',
            detection.id, request,
            {'verified': detection.verified}
        )
        
        return Response(AnimalDetectionSerializer(detection).data)


# ============================================================================
# ALERT VIEWS
# ============================================================================

class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing alerts
    """
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'RANGER' or user.role == 'ADMIN':
            # Rangers see all alerts
            queryset = Alert.objects.all()
        else:
            # Users see only their alerts
            queryset = Alert.objects.filter(recipient=user)
        
        # Filters
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        alert_type = self.request.query_params.get('alert_type', None)
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        
        return queryset.select_related(
            'detection', 'detection__image', 'detection__image__device',
            'recipient'
        ).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """
        Acknowledge an alert
        POST /api/alerts/{id}/acknowledge
        """
        alert = self.get_object()
        
        # Only recipient can acknowledge
        if alert.recipient != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        alert.status = 'ACKNOWLEDGED'
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        return Response(AlertSerializer(alert).data)


# ============================================================================
# DASHBOARD AND STATISTICS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats_view(request):
    """
    Get dashboard statistics
    GET /api/dashboard/stats
    """
    user = request.user
    
    if user.role == 'RANGER' or user.role == 'ADMIN':
        # Rangers see all stats
        devices = IoTDevice.objects.all()
        images = ImageCapture.objects.all()
        detections = AnimalDetection.objects.all()
        alerts = Alert.objects.all()
    else:
        # Farmers see only their stats
        devices = IoTDevice.objects.filter(owner=user)
        images = ImageCapture.objects.filter(device__owner=user)
        detections = AnimalDetection.objects.filter(image__device__owner=user)
        alerts = Alert.objects.filter(recipient=user)
    
    # Aggregate statistics
    stats = {
        'total_devices': devices.count(),
        'active_devices': devices.filter(is_active=True).count(),
        'total_images': images.count(),
        'total_detections': detections.count(),
        'critical_alerts': alerts.filter(
            detection__risk_level='CRITICAL',
            status='SENT'
        ).count(),
        'recent_detections': AnimalDetectionSerializer(
            detections.order_by('-detected_at')[:10],
            many=True
        ).data,
        'detection_by_animal': dict(
            detections.values('animal_type').annotate(
                count=Count('id')
            ).values_list('animal_type', 'count')
        ),
        'detection_by_risk': dict(
            detections.values('risk_level').annotate(
                count=Count('id')
            ).values_list('risk_level', 'count')
        )
    }
    
    return Response(stats)


# ============================================================================
# AUDIT LOG VIEWS (Admin/Ranger only)
# ============================================================================

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing audit logs (Rangers and Admins only)
    """
    serializer_class = AuditLogSerializer
    permission_classes = [IsRangerOrAdmin]
    queryset = AuditLog.objects.all().select_related('user').order_by('-created_at')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filters
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(user__id=user_id)
        
        action = self.request.query_params.get('action', None)
        if action:
            queryset = queryset.filter(action=action)
        
        return queryset
