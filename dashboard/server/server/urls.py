"""
URL configuration for server project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from api import views

# API Router
router = DefaultRouter()
router.register(r'devices', views.IoTDeviceViewSet, basename='device')
router.register(r'images', views.ImageCaptureViewSet, basename='image')
router.register(r'detections', views.AnimalDetectionViewSet, basename='detection')
router.register(r'alerts', views.AlertViewSet, basename='alert')
router.register(r'audit-logs', views.AuditLogViewSet, basename='auditlog')

# Swagger/OpenAPI documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Animal Detection API",
        default_version='v1',
        description="Real-Time Animal Movement Detection & Alert System API",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Authentication
    path('api/auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('api/auth/login/', views.UserLoginView.as_view(), name='login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/me/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Image Upload (ESP32)
    path('api/images/upload/', views.image_upload_view, name='image-upload'),
    
    # Dashboard
    path('api/dashboard/stats/', views.dashboard_stats_view, name='dashboard-stats'),
    
    # Router URLs
    path('api/', include(router.urls)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
