from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, IoTDevice, ImageCapture, AnimalDetection, Alert, AuditLog
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'phone_number', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'phone_number']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': (
                'role', 'phone_number', 'last_known_lat', 'last_known_lon',
                'location_consent', 'fcm_token'
            )
        }),
    )


@admin.register(IoTDevice)
class IoTDeviceAdmin(admin.ModelAdmin):
    list_display = [
        'device_uid', 'device_name', 'owner', 'location_name',
        'is_active', 'last_seen_at', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['device_uid', 'device_name', 'location_name', 'owner__username']
    readonly_fields = ['api_key', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('device_uid', 'device_name', 'owner', 'api_key')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'location_name')
        }),
        ('Status', {
            'fields': ('is_active', 'firmware_version', 'buzzer_active', 'last_seen_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ImageCapture)
class ImageCaptureAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'device', 'captured_at', 'ai_processed',
        'file_size', 'created_at'
    ]
    list_filter = ['ai_processed', 'captured_at', 'created_at']
    search_fields = ['device__device_uid', 'device__device_name']
    readonly_fields = ['created_at', 'file_size']
    date_hierarchy = 'captured_at'


@admin.register(AnimalDetection)
class AnimalDetectionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'animal_type', 'risk_level', 'confidence_score',
        'verified', 'detected_at'
    ]
    list_filter = ['animal_type', 'risk_level', 'verified', 'detected_at']
    search_fields = ['animal_type', 'image__device__device_uid']
    readonly_fields = ['detected_at']
    date_hierarchy = 'detected_at'
    
    fieldsets = (
        ('Detection Info', {
            'fields': ('image', 'animal_type', 'confidence_score', 'risk_level')
        }),
        ('Bounding Boxes', {
            'fields': ('bounding_boxes',)
        }),
        ('Verification', {
            'fields': ('verified', 'verified_by', 'verification_notes')
        }),
        ('Timestamp', {
            'fields': ('detected_at',)
        }),
    )


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'alert_type', 'recipient', 'status',
        'distance_km', 'created_at'
    ]
    list_filter = ['alert_type', 'status', 'created_at']
    search_fields = ['recipient__username', 'title', 'message']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Alert Info', {
            'fields': ('detection', 'alert_type', 'recipient')
        }),
        ('Content', {
            'fields': ('title', 'message', 'distance_km')
        }),
        ('Status', {
            'fields': ('status', 'sent_at', 'acknowledged_at')
        }),
        ('Retry Info', {
            'fields': ('retry_count', 'last_error'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'action', 'target_model',
        'target_id', 'created_at'
    ]
    list_filter = ['action', 'target_model', 'created_at']
    search_fields = ['user__username', 'target_id']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
