"""
Throttling personalizado para API
"""
from rest_framework.throttling import BaseThrottle
from apps.api.services import RateLimitService
from apps.api.models import APIKey


class APIKeyRateThrottle(BaseThrottle):
    """
    Throttle basado en el rate limit de la API Key
    """
    
    def allow_request(self, request, view):
        """
        Verifica si la petición está permitida según el rate limit
        """
        # Solo aplicar si hay API key
        if not isinstance(request.auth, APIKey):
            return True
        
        api_key = request.auth
        identifier = str(api_key.id)
        endpoint = request.path
        
        # Verificar rate limit
        can_proceed, remaining, retry_after = RateLimitService.check_rate_limit(
            identifier=identifier,
            limit_type='api_key',
            endpoint=endpoint,
            limit=api_key.rate_limit,
            window_minutes=60
        )
        
        # Guardar para usar en headers
        self.wait_time = retry_after
        
        return can_proceed
    
    def wait(self):
        """
        Retorna el tiempo que debe esperar antes de reintentar
        """
        return self.wait_time if hasattr(self, 'wait_time') else None


class IPRateThrottle(BaseThrottle):
    """
    Throttle basado en IP para requests sin autenticación
    """
    
    def allow_request(self, request, view):
        """
        Verifica si la petición está permitida según el rate limit de IP
        """
        # Solo aplicar si NO hay API key
        if isinstance(request.auth, APIKey):
            return True
        
        ip_address = self.get_client_ip(request)
        endpoint = request.path
        
        # Límite más restrictivo para IPs no autenticadas
        can_proceed, remaining, retry_after = RateLimitService.check_rate_limit(
            identifier=ip_address,
            limit_type='ip_address',
            endpoint=endpoint,
            limit=100,  # 100 requests por hora sin autenticación
            window_minutes=60
        )
        
        self.wait_time = retry_after
        
        return can_proceed
    
    def wait(self):
        """Retorna el tiempo que debe esperar"""
        return self.wait_time if hasattr(self, 'wait_time') else None
    
    @staticmethod
    def get_client_ip(request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class GlobalRateThrottle(BaseThrottle):
    """
    Throttle global para toda la organización
    """
    
    def allow_request(self, request, view):
        """
        Verifica el rate limit global de la organización
        """
        # Obtener organización del usuario
        organization = None
        if hasattr(request.user, 'userprofile'):
            organization = request.user.userprofile.organization
        
        if not organization:
            return True
        
        identifier = f"org_{organization.id}"
        endpoint = '*'  # Global para todos los endpoints
        
        # Límite global alto por organización
        can_proceed, remaining, retry_after = RateLimitService.check_rate_limit(
            identifier=identifier,
            limit_type='organization',
            endpoint=endpoint,
            limit=10000,  # 10,000 requests por hora por organización
            window_minutes=60
        )
        
        self.wait_time = retry_after
        
        return can_proceed
    
    def wait(self):
        """Retorna el tiempo que debe esperar"""
        return self.wait_time if hasattr(self, 'wait_time') else None
