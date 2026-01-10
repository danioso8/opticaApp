"""
ViewSets para API REST
Define los endpoints CRUD para cada modelo
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

from apps.api.models import APIKey, APILog, RateLimitRecord, APIWebhook
from apps.api.serializers import (
    APIKeySerializer, APIKeyListSerializer,
    APILogSerializer,
    RateLimitRecordSerializer,
    APIWebhookSerializer, APIWebhookListSerializer
)
from apps.api.services import APIService, RateLimitService, WebhookService


class APIKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de API Keys
    
    list: Listar todas las API keys del usuario
    create: Crear nueva API key
    retrieve: Ver detalles de una API key
    update: Actualizar API key
    destroy: Eliminar API key
    revoke: Revocar una API key
    regenerate: Regenerar una API key
    """
    
    queryset = APIKey.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'scope']
    search_fields = ['name', 'key_prefix']
    ordering_fields = ['created_at', 'last_used_at', 'total_requests']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for list and detail"""
        if self.action == 'list':
            return APIKeyListSerializer
        return APIKeySerializer
    
    def get_queryset(self):
        """Filter by current user's organization"""
        user = self.request.user
        if hasattr(user, 'userprofile') and user.userprofile.organization:
            return APIKey.objects.filter(
                organization=user.userprofile.organization
            )
        return APIKey.objects.none()
    
    def perform_create(self, serializer):
        """Set user and organization on create"""
        user = self.request.user
        organization = user.userprofile.organization if hasattr(user, 'userprofile') else None
        serializer.save(user=user, organization=organization)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoca una API key"""
        api_key = self.get_object()
        api_key.status = 'revoked'
        api_key.save()
        return Response({'message': 'API Key revocada exitosamente'})
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenera una API key (crea una nueva y revoca la anterior)"""
        old_key = self.get_object()
        
        # Crear nueva key con los mismos parámetros
        new_key = APIKey.objects.create(
            name=f"{old_key.name} (Regenerada)",
            user=old_key.user,
            organization=old_key.organization,
            scope=old_key.scope,
            allowed_ips=old_key.allowed_ips,
            allowed_endpoints=old_key.allowed_endpoints,
            rate_limit=old_key.rate_limit,
            expires_at=old_key.expires_at
        )
        
        # Revocar la anterior
        old_key.status = 'revoked'
        old_key.save()
        
        serializer = self.get_serializer(new_key)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Obtiene estadísticas de uso de una API key"""
        api_key = self.get_object()
        
        # Últimos 30 días de logs
        thirty_days_ago = timezone.now() - timedelta(days=30)
        logs = APILog.objects.filter(
            api_key=api_key,
            created_at__gte=thirty_days_ago
        )
        
        stats = {
            'total_requests': api_key.total_requests,
            'last_used_at': api_key.last_used_at,
            'last_30_days': {
                'total': logs.count(),
                'success': logs.filter(response_status__lt=400).count(),
                'errors': logs.filter(response_status__gte=400).count(),
                'avg_response_time': logs.aggregate(
                    avg=models.Avg('response_time')
                )['avg'] or 0,
            },
            'top_endpoints': list(
                logs.values('endpoint')
                .annotate(count=models.Count('id'))
                .order_by('-count')[:10]
            ),
            'status_distribution': list(
                logs.values('response_status')
                .annotate(count=models.Count('id'))
                .order_by('-count')
            )
        }
        
        return Response(stats)


class APILogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para logs de API (solo lectura)
    
    list: Listar logs de API
    retrieve: Ver detalles de un log
    """
    
    queryset = APILog.objects.all()
    serializer_class = APILogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['method', 'response_status', 'api_key', 'user']
    search_fields = ['endpoint', 'ip_address']
    ordering_fields = ['created_at', 'response_time', 'response_status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter by current user's organization"""
        user = self.request.user
        if hasattr(user, 'userprofile') and user.userprofile.organization:
            return APILog.objects.filter(
                organization=user.userprofile.organization
            )
        return APILog.objects.none()
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas generales de logs"""
        queryset = self.get_queryset()
        
        # Últimos 7 días
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_logs = queryset.filter(created_at__gte=seven_days_ago)
        
        stats = {
            'total_requests': queryset.count(),
            'last_7_days': {
                'total': recent_logs.count(),
                'success': recent_logs.filter(response_status__lt=400).count(),
                'errors': recent_logs.filter(response_status__gte=400).count(),
                'avg_response_time': recent_logs.aggregate(
                    avg=models.Avg('response_time')
                )['avg'] or 0,
            },
            'by_method': list(
                recent_logs.values('method')
                .annotate(count=models.Count('id'))
                .order_by('-count')
            ),
            'error_distribution': list(
                recent_logs.filter(response_status__gte=400)
                .values('response_status')
                .annotate(count=models.Count('id'))
                .order_by('-count')[:10]
            )
        }
        
        return Response(stats)


class RateLimitRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para registros de rate limiting (solo lectura)
    
    list: Listar registros de rate limit
    retrieve: Ver detalles de un registro
    """
    
    queryset = RateLimitRecord.objects.all()
    serializer_class = RateLimitRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['limit_type', 'is_blocked', 'api_key']
    ordering_fields = ['created_at', 'request_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter by current user's organization"""
        user = self.request.user
        if hasattr(user, 'userprofile') and user.userprofile.organization:
            return RateLimitRecord.objects.filter(
                organization=user.userprofile.organization
            )
        return RateLimitRecord.objects.none()


class APIWebhookViewSet(viewsets.ModelViewSet):
    """
    ViewSet para webhooks
    
    list: Listar webhooks
    create: Crear webhook
    retrieve: Ver detalles de webhook
    update: Actualizar webhook
    destroy: Eliminar webhook
    test: Probar webhook
    """
    
    queryset = APIWebhook.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_active']
    search_fields = ['name', 'url']
    ordering_fields = ['created_at', 'last_triggered_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for list and detail"""
        if self.action == 'list':
            return APIWebhookListSerializer
        return APIWebhookSerializer
    
    def get_queryset(self):
        """Filter by current user's organization"""
        user = self.request.user
        if hasattr(user, 'userprofile') and user.userprofile.organization:
            return APIWebhook.objects.filter(
                organization=user.userprofile.organization
            )
        return APIWebhook.objects.none()
    
    def perform_create(self, serializer):
        """Set organization on create"""
        user = self.request.user
        organization = user.userprofile.organization if hasattr(user, 'userprofile') else None
        serializer.save(organization=organization)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Prueba un webhook enviando un payload de ejemplo"""
        webhook = self.get_object()
        
        test_payload = {
            'event': 'test',
            'data': {'message': 'This is a test webhook'},
            'timestamp': timezone.now().isoformat()
        }
        
        success, response = WebhookService.trigger_webhook(webhook, test_payload)
        
        return Response({
            'success': success,
            'response': response,
            'message': 'Webhook probado exitosamente' if success else 'Error al probar webhook'
        })
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Obtiene el historial de triggers de un webhook"""
        webhook = self.get_object()
        
        # Buscar logs relacionados con este webhook
        # (esto requeriría un modelo adicional WebhookLog, por ahora retornamos stats)
        
        return Response({
            'total_triggers': webhook.total_triggers,
            'total_successes': webhook.total_successes,
            'total_failures': webhook.total_failures,
            'success_rate': (webhook.total_successes / webhook.total_triggers * 100) 
                           if webhook.total_triggers > 0 else 100,
            'last_triggered_at': webhook.last_triggered_at,
            'last_success_at': webhook.last_success_at,
            'last_failure_at': webhook.last_failure_at
        })


# Import models for statistics
from django.db import models
