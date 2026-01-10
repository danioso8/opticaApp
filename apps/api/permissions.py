"""
Permisos personalizados para API
"""
from rest_framework import permissions


class HasAPIKeyPermission(permissions.BasePermission):
    """
    Permiso que requiere una API key válida
    """
    
    message = 'API key requerida'
    
    def has_permission(self, request, view):
        """Verifica si la petición tiene API key válida"""
        # Si la autenticación es APIKey, permitir
        from apps.api.models import APIKey
        return isinstance(request.auth, APIKey)


class HasReadScopePermission(permissions.BasePermission):
    """
    Permiso que requiere scope de lectura o superior
    """
    
    message = 'Permisos insuficientes: se requiere scope de lectura'
    
    def has_permission(self, request, view):
        """Verifica si tiene permiso de lectura"""
        from apps.api.models import APIKey
        
        if not isinstance(request.auth, APIKey):
            return False
        
        api_key = request.auth
        return api_key.scope in ['read', 'write', 'admin']


class HasWriteScopePermission(permissions.BasePermission):
    """
    Permiso que requiere scope de escritura o superior
    """
    
    message = 'Permisos insuficientes: se requiere scope de escritura'
    
    def has_permission(self, request, view):
        """Verifica si tiene permiso de escritura"""
        from apps.api.models import APIKey
        
        if not isinstance(request.auth, APIKey):
            return False
        
        # Solo requerir write para métodos que modifican
        if request.method in permissions.SAFE_METHODS:
            return True
        
        api_key = request.auth
        return api_key.scope in ['write', 'admin']


class HasAdminScopePermission(permissions.BasePermission):
    """
    Permiso que requiere scope de administrador
    """
    
    message = 'Permisos insuficientes: se requiere scope de administrador'
    
    def has_permission(self, request, view):
        """Verifica si tiene permiso de administrador"""
        from apps.api.models import APIKey
        
        if not isinstance(request.auth, APIKey):
            return False
        
        api_key = request.auth
        return api_key.scope == 'admin'


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso que permite solo al owner o admin
    """
    
    message = 'Solo el propietario o administrador puede realizar esta acción'
    
    def has_object_permission(self, request, view, obj):
        """Verifica si es el owner del objeto o admin"""
        # Permitir lectura a todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Verificar si es el owner
        if hasattr(obj, 'user'):
            if obj.user == request.user:
                return True
        
        if hasattr(obj, 'created_by'):
            if obj.created_by == request.user:
                return True
        
        # Verificar si es admin
        from apps.api.models import APIKey
        if isinstance(request.auth, APIKey):
            return request.auth.scope == 'admin'
        
        return request.user.is_staff or request.user.is_superuser


class RateLimitPermission(permissions.BasePermission):
    """
    Permiso que verifica rate limiting
    """
    
    message = 'Rate limit excedido. Intenta de nuevo más tarde.'
    
    def has_permission(self, request, view):
        """Verifica rate limit"""
        from apps.api.services import RateLimitService
        from apps.api.models import APIKey
        
        # Determinar identificador y límite
        if isinstance(request.auth, APIKey):
            identifier = str(request.auth.id)
            limit_type = 'api_key'
            limit = request.auth.rate_limit
        else:
            # Rate limit por IP para requests sin API key
            identifier = self.get_client_ip(request)
            limit_type = 'ip_address'
            limit = 100  # Límite más bajo para requests sin autenticación
        
        endpoint = request.path
        
        # Verificar rate limit
        can_proceed, remaining, retry_after = RateLimitService.check_rate_limit(
            identifier=identifier,
            limit_type=limit_type,
            endpoint=endpoint,
            limit=limit,
            window_minutes=60
        )
        
        # Agregar headers de rate limit a la respuesta
        request.rate_limit_remaining = remaining
        request.rate_limit_retry_after = retry_after
        
        return can_proceed
    
    @staticmethod
    def get_client_ip(request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
