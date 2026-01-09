"""
Middleware para capturar información de la solicitud en auditorías.
"""
import threading

# Thread-local storage para información de la solicitud
_thread_locals = threading.local()


def get_current_request():
    """Obtiene la solicitud actual del thread."""
    return getattr(_thread_locals, 'request', None)


def get_current_user():
    """Obtiene el usuario actual del thread."""
    request = get_current_request()
    if request and hasattr(request, 'user'):
        return request.user if request.user.is_authenticated else None
    return None


def get_client_ip():
    """Obtiene la IP del cliente."""
    request = get_current_request()
    if not request:
        return None
    
    # Intentar obtener la IP real detrás de proxies
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    return ip


def get_user_agent():
    """Obtiene el user agent del navegador."""
    request = get_current_request()
    if not request:
        return ''
    
    return request.META.get('HTTP_USER_AGENT', '')


class AuditMiddleware:
    """
    Middleware que captura información de la solicitud para auditorías.
    Almacena request en thread-local para acceso desde signals.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Guardar request en thread-local
        _thread_locals.request = request
        
        # Procesar solicitud
        response = self.get_response(request)
        
        # Limpiar thread-local
        if hasattr(_thread_locals, 'request'):
            delattr(_thread_locals, 'request')
        
        return response
