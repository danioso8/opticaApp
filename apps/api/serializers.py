"""
Serializers para API REST
Define cómo se serializan los modelos a JSON
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.api.models import APIKey, APILog, RateLimitRecord, APIWebhook

User = get_user_model()


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer para API Keys"""
    
    key = serializers.CharField(read_only=True, help_text='La API key generada (solo visible al crear)')
    is_valid = serializers.BooleanField(read_only=True, source='is_valid')
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'key', 'key_prefix', 'scope', 'status',
            'allowed_ips', 'allowed_endpoints', 'rate_limit',
            'expires_at', 'last_used_at', 'last_used_ip',
            'total_requests', 'notes', 'is_valid',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['key_prefix', 'last_used_at', 'last_used_ip', 'total_requests']
    
    def create(self, validated_data):
        """Override create to show full key only once"""
        instance = super().create(validated_data)
        # Return the full key only on creation
        return instance


class APIKeyListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de API Keys"""
    
    is_valid = serializers.BooleanField(read_only=True, source='is_valid')
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'key_prefix', 'scope', 'status',
            'last_used_at', 'total_requests', 'is_valid', 'created_at'
        ]


class APILogSerializer(serializers.ModelSerializer):
    """Serializer para logs de API"""
    
    api_key_name = serializers.CharField(source='api_key.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    is_error = serializers.BooleanField(read_only=True, source='is_error')
    is_success = serializers.BooleanField(read_only=True, source='is_success')
    
    class Meta:
        model = APILog
        fields = [
            'id', 'api_key', 'api_key_name', 'user', 'user_email',
            'method', 'endpoint', 'full_path',
            'request_params', 'response_status', 'response_time',
            'ip_address', 'user_agent', 'error_message',
            'is_error', 'is_success', 'created_at'
        ]
        read_only_fields = ['created_at']


class RateLimitRecordSerializer(serializers.ModelSerializer):
    """Serializer para registros de rate limit"""
    
    can_make_request = serializers.BooleanField(read_only=True, source='can_make_request')
    is_limit_exceeded = serializers.BooleanField(read_only=True, source='is_limit_exceeded')
    
    class Meta:
        model = RateLimitRecord
        fields = [
            'id', 'limit_type', 'identifier', 'endpoint',
            'request_count', 'window_start', 'window_end', 'limit',
            'is_blocked', 'blocked_until',
            'can_make_request', 'is_limit_exceeded',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class APIWebhookSerializer(serializers.ModelSerializer):
    """Serializer para webhooks"""
    
    api_key_name = serializers.CharField(source='api_key.name', read_only=True)
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = APIWebhook
        fields = [
            'id', 'name', 'url', 'api_key', 'api_key_name',
            'events', 'status', 'headers', 'secret',
            'retry_on_failure', 'max_retries',
            'last_triggered_at', 'last_success_at', 'last_failure_at',
            'total_triggers', 'total_successes', 'total_failures',
            'success_rate', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'last_triggered_at', 'last_success_at', 'last_failure_at',
            'total_triggers', 'total_successes', 'total_failures',
            'created_at', 'updated_at'
        ]
    
    def get_success_rate(self, obj):
        """Calcula el porcentaje de éxito"""
        if obj.total_triggers == 0:
            return 100.0
        return round((obj.total_successes / obj.total_triggers) * 100, 2)


class APIWebhookListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de webhooks"""
    
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = APIWebhook
        fields = [
            'id', 'name', 'url', 'status', 'is_active',
            'total_triggers', 'success_rate', 'last_triggered_at'
        ]
    
    def get_success_rate(self, obj):
        if obj.total_triggers == 0:
            return 100.0
        return round((obj.total_successes / obj.total_triggers) * 100, 2)
