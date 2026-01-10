"""
Servicios de lógica de negocio para API
"""
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import requests
import hmac
import hashlib
import json

from apps.api.models import APIKey, APILog, RateLimitRecord, APIWebhook


class APIService:
    """Servicio para gestión de API Keys y autenticación"""
    
    @staticmethod
    def validate_api_key(key, endpoint=None, ip_address=None):
        """
        Valida una API key
        
        Args:
            key: La API key a validar
            endpoint: Endpoint opcional para verificar permisos
            ip_address: IP opcional para verificar restricciones
        
        Returns:
            tuple: (is_valid, api_key_instance, error_message)
        """
        try:
            # Extraer prefix (primeros 8 caracteres)
            if len(key) < 8:
                return False, None, "API key inválida"
            
            key_prefix = key[:8]
            key_hash = APIKey.hash_key(key)
            
            # Buscar la key
            api_key = APIKey.objects.filter(
                key_prefix=key_prefix,
                key_hash=key_hash
            ).first()
            
            if not api_key:
                return False, None, "API key no encontrada"
            
            # Validar estado
            if not api_key.is_valid():
                return False, api_key, f"API key {api_key.status}"
            
            # Validar IP si está configurada
            if ip_address and not api_key.can_access_from_ip(ip_address):
                return False, api_key, "IP no autorizada"
            
            # Validar endpoint si está configurado
            if endpoint and not api_key.can_access_endpoint(endpoint):
                return False, api_key, "Endpoint no autorizado"
            
            # Registrar uso
            api_key.record_usage(ip_address)
            
            return True, api_key, None
            
        except Exception as e:
            return False, None, str(e)
    
    @staticmethod
    def create_api_key(user, organization, name, scope='read', **kwargs):
        """
        Crea una nueva API key
        
        Args:
            user: Usuario propietario
            organization: Organización
            name: Nombre descriptivo
            scope: Alcance (read, write, admin)
            **kwargs: Otros parámetros opcionales
        
        Returns:
            APIKey: La API key creada
        """
        api_key = APIKey.objects.create(
            user=user,
            organization=organization,
            name=name,
            scope=scope,
            **kwargs
        )
        
        return api_key
    
    @staticmethod
    def log_request(api_key, user, organization, method, endpoint, **kwargs):
        """
        Registra una petición API en el log
        
        Args:
            api_key: API Key usada (puede ser None)
            user: Usuario que hizo la petición (puede ser None)
            organization: Organización
            method: Método HTTP
            endpoint: Endpoint accedido
            **kwargs: Otros parámetros del log
        
        Returns:
            APILog: El log creado
        """
        log = APILog.objects.create(
            api_key=api_key,
            user=user,
            organization=organization,
            method=method,
            endpoint=endpoint,
            **kwargs
        )
        
        return log


class RateLimitService:
    """Servicio para gestión de rate limiting"""
    
    @staticmethod
    def check_rate_limit(identifier, limit_type, endpoint, limit, window_minutes=60):
        """
        Verifica si se excedió el rate limit
        
        Args:
            identifier: Identificador único (API key, IP, user ID)
            limit_type: Tipo de límite (api_key, ip_address, user)
            endpoint: Endpoint específico o '*' para todos
            limit: Número máximo de requests permitidos
            window_minutes: Tamaño de la ventana en minutos
        
        Returns:
            tuple: (can_proceed, remaining_requests, retry_after_seconds)
        """
        now = timezone.now()
        window_start = now - timedelta(minutes=window_minutes)
        window_end = now
        
        # Buscar o crear registro
        record, created = RateLimitRecord.objects.get_or_create(
            limit_type=limit_type,
            identifier=identifier,
            endpoint=endpoint,
            window_start__gte=window_start,
            window_end__lte=window_end,
            defaults={
                'window_start': window_start,
                'window_end': window_end,
                'limit': limit,
                'request_count': 0,
                'organization_id': 1  # TODO: Get from context
            }
        )
        
        # Si la ventana expiró, crear nueva
        if now > record.window_end:
            record = RateLimitRecord.objects.create(
                limit_type=limit_type,
                identifier=identifier,
                endpoint=endpoint,
                window_start=now,
                window_end=now + timedelta(minutes=window_minutes),
                limit=limit,
                request_count=0,
                organization_id=1  # TODO: Get from context
            )
        
        # Verificar si puede hacer la petición
        can_proceed = record.can_make_request()
        
        if can_proceed:
            record.increment()
            remaining = limit - record.request_count
            retry_after = 0
        else:
            remaining = 0
            retry_after = int((record.window_end - now).total_seconds())
        
        return can_proceed, remaining, retry_after
    
    @staticmethod
    def cleanup_old_records(days=7):
        """
        Limpia registros antiguos de rate limiting
        
        Args:
            days: Días de antigüedad para eliminar
        
        Returns:
            int: Número de registros eliminados
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted, _ = RateLimitRecord.objects.filter(
            window_end__lt=cutoff_date
        ).delete()
        
        return deleted


class WebhookService:
    """Servicio para gestión de webhooks"""
    
    @staticmethod
    def trigger_webhook(webhook, payload):
        """
        Dispara un webhook enviando el payload a la URL
        
        Args:
            webhook: Instancia de APIWebhook
            payload: Datos a enviar (dict)
        
        Returns:
            tuple: (success, response_data)
        """
        if not webhook.is_active or webhook.status != 'active':
            return False, {'error': 'Webhook no activo'}
        
        try:
            # Preparar headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'OpticaApp-Webhook/1.0',
                **webhook.headers
            }
            
            # Firmar payload si hay secret
            if webhook.secret:
                payload_json = json.dumps(payload, sort_keys=True)
                signature = hmac.new(
                    webhook.secret.encode(),
                    payload_json.encode(),
                    hashlib.sha256
                ).hexdigest()
                headers['X-Webhook-Signature'] = f'sha256={signature}'
            
            # Enviar request
            response = requests.post(
                webhook.url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            # Verificar respuesta
            success = 200 <= response.status_code < 300
            
            # Registrar trigger
            webhook.record_trigger(success=success)
            
            return success, {
                'status_code': response.status_code,
                'response': response.text[:500]  # Limitar tamaño
            }
            
        except requests.exceptions.Timeout:
            webhook.record_trigger(success=False)
            return False, {'error': 'Timeout al conectar con webhook'}
        
        except requests.exceptions.RequestException as e:
            webhook.record_trigger(success=False)
            return False, {'error': str(e)}
    
    @staticmethod
    def trigger_event(organization, event, data):
        """
        Dispara todos los webhooks suscritos a un evento
        
        Args:
            organization: Organización
            event: Nombre del evento (ej: 'patient.created')
            data: Datos del evento
        
        Returns:
            list: Lista de resultados para cada webhook
        """
        webhooks = APIWebhook.objects.filter(
            organization=organization,
            is_active=True,
            status='active'
        )
        
        results = []
        
        for webhook in webhooks:
            if webhook.is_subscribed_to(event):
                payload = {
                    'event': event,
                    'data': data,
                    'timestamp': timezone.now().isoformat(),
                    'organization_id': organization.id
                }
                
                success, response = WebhookService.trigger_webhook(webhook, payload)
                
                results.append({
                    'webhook_id': webhook.id,
                    'webhook_name': webhook.name,
                    'success': success,
                    'response': response
                })
        
        return results


class APIDocumentationService:
    """Servicio para generar documentación de API"""
    
    @staticmethod
    def get_api_info():
        """Retorna información general de la API"""
        return {
            'name': 'OpticaApp API',
            'version': '1.0',
            'description': 'API REST para OpticaApp - Sistema multi-tenant para gestión óptica',
            'base_url': '/api/v1/',
            'authentication': {
                'type': 'API Key',
                'header': 'Authorization',
                'format': 'Bearer {api_key}'
            },
            'rate_limiting': {
                'default': '1000 requests/hour',
                'authenticated': '5000 requests/hour'
            },
            'pagination': {
                'page_size': 50,
                'max_page_size': 500
            },
            'formats': ['json'],
            'documentation': '/api/docs/'
        }
    
    @staticmethod
    def get_endpoints_list():
        """Retorna lista de endpoints disponibles"""
        return [
            {
                'path': '/api/v1/keys/',
                'methods': ['GET', 'POST'],
                'description': 'Gestión de API Keys'
            },
            {
                'path': '/api/v1/logs/',
                'methods': ['GET'],
                'description': 'Logs de peticiones API'
            },
            {
                'path': '/api/v1/webhooks/',
                'methods': ['GET', 'POST', 'PUT', 'DELETE'],
                'description': 'Gestión de webhooks'
            },
            # Aquí se agregarían más endpoints de otros módulos
        ]
