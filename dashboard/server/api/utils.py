from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from math import radians, sin, cos, sqrt, atan2
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response = {
            'error': True,
            'message': str(exc),
            'details': response.data
        }
        response.data = custom_response
    
    return response


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in kilometers
    """
    # Earth radius in kilometers
    R = 6371.0
    
    # Convert to radians
    lat1_rad = radians(float(lat1))
    lon1_rad = radians(float(lon1))
    lat2_rad = radians(float(lat2))
    lon2_rad = radians(float(lon2))
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return distance


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """
    Get user agent from request
    """
    return request.META.get('HTTP_USER_AGENT', '')


def determine_risk_level(animal_type, confidence_score):
    """
    Determine risk level based on animal type and confidence score
    """
    from django.conf import settings
    
    risk_config = settings.RISK_LEVELS
    
    for risk_level, config in risk_config.items():
        if animal_type.lower() in config['animals']:
            if confidence_score >= config['confidence_threshold']:
                return risk_level
    
    # Default to LOW if no match
    return 'LOW'


def get_alert_types_for_risk(risk_level):
    """
    Get alert types based on risk level
    """
    from django.conf import settings
    
    risk_config = settings.RISK_LEVELS.get(risk_level, {})
    return risk_config.get('alert_types', ['PUSH'])


def create_audit_log(user, action, target_model, target_id, request, details=None):
    """
    Create an audit log entry
    """
    from .models import AuditLog
    
    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            target_model=target_model,
            target_id=str(target_id),
            details=details or {},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")


def generate_alert_message(detection, distance_km=None):
    """
    Generate alert message based on detection
    """
    animal_name = detection.get_animal_type_display()
    risk_level = detection.get_risk_level_display()
    confidence = int(detection.confidence_score * 100)
    
    device = detection.image.device
    location = device.location_name or f"({device.latitude}, {device.longitude})"
    
    title = f"{risk_level} Alert: {animal_name} Detected"
    
    message = f"A {animal_name} has been detected near {location} "
    message += f"with {confidence}% confidence. "
    message += f"Risk level: {risk_level}. "
    
    if distance_km:
        message += f"Distance from your location: {distance_km:.2f} km. "
    
    message += "Please take necessary precautions."
    
    return title, message


import secrets
import hashlib


def generate_device_api_key():
    """
    Generate a secure API key for IoT device
    """
    return secrets.token_hex(32)


def validate_image_file(file):
    """
    Validate uploaded image file
    """
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024
    if file.size > max_size:
        return False, "Image file too large. Maximum size is 10MB."
    
    # Check file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
    if file.content_type not in allowed_types:
        return False, "Invalid file type. Only JPEG and PNG are allowed."
    
    return True, None
