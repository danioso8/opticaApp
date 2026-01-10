"""
Middleware para logging automático de peticiones API
"""
import time
import json
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from apps.api.models import APILog, APIKey


class APILoggingMiddleware(MiddlewareMixin):
    """
    Middleware que registra automáticamente todas las peticiones API
    """
    
    def process_request(self, request):
        """Registra el inicio de la petición"""
        # Solo loggear rutas /api/
        if not request.path.startswith('/api/'):
            return None
        
        # Guardar timestamp de inicio
        request._api_log_start_time = time.time()
        
        return None
    
    def process_response(self, request, response):
        """Registra la respuesta de la petición"""
        # Solo loggear rutas /api/
        if not request.path.startswith('/api/'):
            return response
        
        # Solo loggear si tenemos tiempo de inicio
        if not hasattr(request, '_api_log_start_time'):
            return response
        
        # Calcular tiempo de respuesta
        response_time = (time.time() - request._api_log_start_time) * 1000  # en ms
        
        # Obtener datos de la petición
        api_key = None
        user = None
        organization = None
        
        if hasattr(request, 'auth') and isinstance(request.auth, APIKey):
            api_key = request.auth
            user = request.user if request.user.is_authenticated else None
            organization = api_key.organization
        elif hasattr(request.user, 'userprofile'):
            user = request.user if request.user.is_authenticated else None
            if user and hasattr(user, 'userprofile'):
                organization = user.userprofile.organization
        
        # Si no hay organización, no loggear
        if not organization:
            return response
        
        # Obtener IP
        ip_address = self.get_client_ip(request)
        
        # Obtener user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Obtener request body (limitado)
        request_body = {}
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if hasattr(request, 'body'):
                    request_body = json.loads(request.body.decode('utf-8'))
                elif hasattr(request, 'data'):
                    request_body = request.data
            except (json.JSONDecodeError, UnicodeDecodeError):
                request_body = {'error': 'Could not decode body'}
        
        # Obtener query params
        request_params = dict(request.GET)
        
        # Obtener response body (limitado)
        response_body = {}
        try:
            if hasattr(response, 'data'):
                response_body = response.data
            elif hasattr(response, 'content'):
                content = response.content.decode('utf-8')
                if len(content) < 10000:  # Solo si es pequeño
                    response_body = json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            pass
        
        # Crear log asíncrono (no bloquear la respuesta)
        try:
            APILog.objects.create(
                api_key=api_key,
                user=user,
                organization=organization,
                method=request.method,
                endpoint=request.path,
                full_path=request.get_full_path(),
                request_headers=self.get_headers(request),
                request_body=request_body,
                request_params=request_params,
                response_status=response.status_code,
                response_body=response_body,
                response_time=response_time,
                ip_address=ip_address,
                user_agent=user_agent[:500] if user_agent else ''
            )
        except Exception as e:
            # No fallar si hay error en el logging
            print(f"Error logging API request: {e}")
        
        # Agregar headers de rate limit si existen
        if hasattr(request, 'rate_limit_remaining'):
            response['X-RateLimit-Remaining'] = str(request.rate_limit_remaining)
        
        if hasattr(request, 'rate_limit_retry_after'):
            response['X-RateLimit-Retry-After'] = str(request.rate_limit_retry_after)
        
        # Agregar tiempo de respuesta
        response['X-Response-Time'] = f"{response_time:.2f}ms"
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_headers(request):
        """Obtiene los headers de la petición"""
        headers = {}
        for key, value in request.META.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-').title()
                headers[header_name] = value
        return headers
