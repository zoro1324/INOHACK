from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.db import transaction
import requests
import logging
from datetime import timedelta

from .models import ImageCapture, AnimalDetection, Alert, User, IoTDevice
from .utils import (
    calculate_distance, determine_risk_level,
    get_alert_types_for_risk, generate_alert_message
)

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_image_with_ai(self, image_id):
    """
    Process image with AI model and create detections
    """
    try:
        image = ImageCapture.objects.get(id=image_id)
    except ImageCapture.DoesNotExist:
        logger.error(f"Image {image_id} not found")
        return
    
    # Mark as processing started
    image.processing_started_at = timezone.now()
    image.save(update_fields=['processing_started_at'])
    
    try:
        # Send image to AI inference service
        with image.image.open('rb') as img_file:
            files = {'image': img_file}
            response = requests.post(
                settings.AI_INFERENCE_URL,
                files=files,
                timeout=settings.AI_INFERENCE_TIMEOUT
            )
        
        if response.status_code != 200:
            raise Exception(f"AI service returned status {response.status_code}")
        
        ai_results = response.json()
        
        # Process detections
        with transaction.atomic():
            for detection_data in ai_results.get('detections', []):
                animal_type = detection_data.get('class', 'other')
                confidence = detection_data.get('confidence', 0.0)
                
                # Determine risk level
                risk_level = determine_risk_level(animal_type, confidence)
                
                # Create detection
                detection = AnimalDetection.objects.create(
                    image=image,
                    animal_type=animal_type,
                    confidence_score=confidence,
                    risk_level=risk_level,
                    bounding_boxes=detection_data.get('bounding_boxes', [])
                )
                
                logger.info(
                    f"Detection created: {animal_type} "
                    f"with confidence {confidence} and risk {risk_level}"
                )
                
                # Trigger alerts based on risk level
                trigger_alerts_for_detection.delay(str(detection.id))
        
        # Mark as processed
        image.ai_processed = True
        image.processing_completed_at = timezone.now()
        image.save(update_fields=['ai_processed', 'processing_completed_at'])
        
        logger.info(f"Image {image_id} processed successfully")
        
    except Exception as e:
        logger.error(f"Error processing image {image_id}: {str(e)}")
        image.ai_processed = False
        image.save(update_fields=['ai_processed'])
        
        # Retry the task
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))


@shared_task
def trigger_alerts_for_detection(detection_id):
    """
    Create and send alerts for a detection
    """
    try:
        detection = AnimalDetection.objects.select_related(
            'image', 'image__device', 'image__device__owner'
        ).get(id=detection_id)
    except AnimalDetection.DoesNotExist:
        logger.error(f"Detection {detection_id} not found")
        return
    
    device = detection.image.device
    risk_level = detection.risk_level
    
    # Get alert types for this risk level
    alert_types = get_alert_types_for_risk(risk_level)
    
    # Alert device owner
    if device.owner:
        create_alerts_for_user(
            device.owner, detection, alert_types, distance_km=0
        )
    
    # Alert nearby users (geo-based alerts)
    if risk_level in ['HIGH', 'CRITICAL']:
        alert_nearby_users(detection, alert_types)
    
    # Activate device buzzer for certain risk levels
    if 'BUZZER' in alert_types:
        device.buzzer_active = True
        device.save(update_fields=['buzzer_active'])
    
    # Alert all rangers for critical risks
    if risk_level == 'CRITICAL':
        rangers = User.objects.filter(role='RANGER')
        for ranger in rangers:
            create_alerts_for_user(
                ranger, detection, ['PUSH'], distance_km=None
            )


def alert_nearby_users(detection, alert_types):
    """
    Alert users within configured radius
    """
    device = detection.image.device
    radius_km = settings.ALERT_RADIUS_KM
    
    # Get users with location consent
    users_with_location = User.objects.filter(
        location_consent=True,
        last_known_lat__isnull=False,
        last_known_lon__isnull=False
    ).exclude(id=device.owner.id if device.owner else None)
    
    for user in users_with_location:
        distance = calculate_distance(
            device.latitude, device.longitude,
            user.last_known_lat, user.last_known_lon
        )
        
        if distance <= radius_km:
            create_alerts_for_user(user, detection, alert_types, distance)


def create_alerts_for_user(user, detection, alert_types, distance_km):
    """
    Create alerts for a specific user
    """
    title, message = generate_alert_message(detection, distance_km)
    
    for alert_type in alert_types:
        alert = Alert.objects.create(
            detection=detection,
            alert_type=alert_type,
            recipient=user,
            title=title,
            message=message,
            distance_km=distance_km
        )
        
        # Send alert based on type
        if alert_type == 'PUSH':
            send_push_notification.delay(str(alert.id))
        elif alert_type == 'SMS':
            send_sms_notification.delay(str(alert.id))
        elif alert_type == 'CALL':
            initiate_phone_call.delay(str(alert.id))


@shared_task(bind=True, max_retries=3)
def send_push_notification(self, alert_id):
    """
    Send push notification via FCM
    """
    try:
        alert = Alert.objects.select_related('recipient').get(id=alert_id)
    except Alert.DoesNotExist:
        logger.error(f"Alert {alert_id} not found")
        return
    
    recipient = alert.recipient
    
    if not recipient.fcm_token:
        logger.warning(f"User {recipient.username} has no FCM token")
        alert.status = 'FAILED'
        alert.last_error = "No FCM token available"
        alert.save()
        return
    
    try:
        # Send FCM notification
        fcm_url = "https://fcm.googleapis.com/fcm/send"
        headers = {
            "Authorization": f"key={settings.FCM_SERVER_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "to": recipient.fcm_token,
            "notification": {
                "title": alert.title,
                "body": alert.message,
                "priority": "high"
            },
            "data": {
                "alert_id": str(alert.id),
                "detection_id": str(alert.detection.id),
                "risk_level": alert.detection.risk_level
            }
        }
        
        response = requests.post(fcm_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            alert.status = 'SENT'
            alert.sent_at = timezone.now()
            logger.info(f"Push notification sent for alert {alert_id}")
        else:
            raise Exception(f"FCM returned status {response.status_code}")
        
    except Exception as e:
        alert.status = 'FAILED'
        alert.last_error = str(e)
        alert.retry_count += 1
        logger.error(f"Failed to send push notification: {str(e)}")
        
        if alert.retry_count < 3:
            self.retry(exc=e, countdown=60 * alert.retry_count)
    
    finally:
        alert.save()


@shared_task(bind=True, max_retries=3)
def send_sms_notification(self, alert_id):
    """
    Send SMS notification
    """
    try:
        alert = Alert.objects.select_related('recipient').get(id=alert_id)
    except Alert.DoesNotExist:
        logger.error(f"Alert {alert_id} not found")
        return
    
    recipient = alert.recipient
    
    try:
        # Send SMS via provider API (example with Twilio-like interface)
        sms_api_url = "https://api.sms-provider.com/send"
        headers = {
            "Authorization": f"Bearer {settings.SMS_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "to": recipient.phone_number,
            "message": f"{alert.title}\n\n{alert.message}"
        }
        
        response = requests.post(sms_api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            alert.status = 'SENT'
            alert.sent_at = timezone.now()
            logger.info(f"SMS sent for alert {alert_id}")
        else:
            raise Exception(f"SMS API returned status {response.status_code}")
        
    except Exception as e:
        alert.status = 'FAILED'
        alert.last_error = str(e)
        alert.retry_count += 1
        logger.error(f"Failed to send SMS: {str(e)}")
        
        if alert.retry_count < 3:
            self.retry(exc=e, countdown=60 * alert.retry_count)
    
    finally:
        alert.save()


@shared_task(bind=True, max_retries=2)
def initiate_phone_call(self, alert_id):
    """
    Initiate automated phone call
    """
    try:
        alert = Alert.objects.select_related('recipient').get(id=alert_id)
    except Alert.DoesNotExist:
        logger.error(f"Alert {alert_id} not found")
        return
    
    recipient = alert.recipient
    
    try:
        # Initiate call via provider API
        call_api_url = "https://api.call-provider.com/call"
        headers = {
            "Authorization": f"Bearer {settings.CALL_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "to": recipient.phone_number,
            "message": alert.message,
            "voice": "en-US"
        }
        
        response = requests.post(call_api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            alert.status = 'SENT'
            alert.sent_at = timezone.now()
            logger.info(f"Phone call initiated for alert {alert_id}")
        else:
            raise Exception(f"Call API returned status {response.status_code}")
        
    except Exception as e:
        alert.status = 'FAILED'
        alert.last_error = str(e)
        alert.retry_count += 1
        logger.error(f"Failed to initiate call: {str(e)}")
        
        if alert.retry_count < 2:
            self.retry(exc=e, countdown=120 * alert.retry_count)
    
    finally:
        alert.save()


@shared_task
def cleanup_old_images():
    """
    Cleanup old images (older than 90 days)
    Runs daily via Celery Beat
    """
    cutoff_date = timezone.now() - timedelta(days=90)
    
    old_images = ImageCapture.objects.filter(
        captured_at__lt=cutoff_date
    )
    
    count = old_images.count()
    
    # Delete images and associated files
    for image in old_images:
        try:
            # Delete file from storage
            if image.image:
                image.image.delete()
            # Delete record
            image.delete()
        except Exception as e:
            logger.error(f"Failed to delete image {image.id}: {str(e)}")
    
    logger.info(f"Cleaned up {count} old images")
    
    return f"Deleted {count} images"


@shared_task
def deactivate_old_buzzers():
    """
    Deactivate buzzers that have been active for more than 30 minutes
    """
    devices = IoTDevice.objects.filter(buzzer_active=True)
    
    count = 0
    for device in devices:
        # Check last detection time
        last_detection = AnimalDetection.objects.filter(
            image__device=device
        ).order_by('-detected_at').first()
        
        if last_detection:
            time_since_detection = timezone.now() - last_detection.detected_at
            if time_since_detection > timedelta(minutes=30):
                device.buzzer_active = False
                device.save(update_fields=['buzzer_active'])
                count += 1
    
    logger.info(f"Deactivated {count} buzzers")
    return f"Deactivated {count} buzzers"
