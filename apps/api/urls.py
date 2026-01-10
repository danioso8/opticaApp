"""
URLs para API REST
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.api import viewsets

# Router para ViewSets
router = DefaultRouter()
router.register(r'keys', viewsets.APIKeyViewSet, basename='apikey')
router.register(r'logs', viewsets.APILogViewSet, basename='apilog')
router.register(r'rate-limits', viewsets.RateLimitRecordViewSet, basename='ratelimit')
router.register(r'webhooks', viewsets.APIWebhookViewSet, basename='webhook')

app_name = 'api'

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Documentación y info
    path('', include('rest_framework.urls', namespace='rest_framework')),
]
