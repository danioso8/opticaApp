"""
Autenticación personalizada para API
"""
from rest_framework import authentication, exceptions
from apps.api.services import APIService


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Autenticación mediante API Key en el header Authorization
    
    Format: Authorization: Bearer {api_key}
    """
    
    def authenticate(self, request):
        """
        Autentica la petición usando API Key
        
        Returns:
            tuple: (user, auth) o None si no hay API key
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        # Verificar formato "Bearer {key}"
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise exceptions.AuthenticationFailed('Formato de Authorization inválido')
        
        api_key = parts[1]
        
        # Obtener endpoint y IP
        endpoint = request.path
        ip_address = self.get_client_ip(request)
        
        # Validar API key
        is_valid, api_key_obj, error_msg = APIService.validate_api_key(
            api_key,
            endpoint=endpoint,
            ip_address=ip_address
        )
        
        if not is_valid:
            raise exceptions.AuthenticationFailed(error_msg or 'API Key inválida')
        
        # Retornar usuario y objeto API key
        return (api_key_obj.user, api_key_obj)
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response.
        """
        return 'Bearer'
    
    @staticmethod
    def get_client_ip(request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class APIKeyOrSessionAuthentication(authentication.BaseAuthentication):
    """
    Autenticación que acepta API Key o Session
    Útil para endpoints que pueden ser accedidos desde el frontend o API
    """
    
    def authenticate(self, request):
        """Try API key first, then session"""
        # Try API key
        api_auth = APIKeyAuthentication()
        try:
            result = api_auth.authenticate(request)
            if result is not None:
                return result
        except exceptions.AuthenticationFailed:
            pass
        
        # Try session authentication
        session_auth = authentication.SessionAuthentication()
        try:
            result = session_auth.authenticate(request)
            if result is not None:
                return result
        except exceptions.AuthenticationFailed:
            pass
        
        return None
