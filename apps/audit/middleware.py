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


class ErrorCaptureMiddleware:
    """
    Middleware que captura todas las excepciones no manejadas
    y las registra en la base de datos.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        return self.get_response(request)
    
    def process_exception(self, request, exception):
        """
        Se ejecuta automáticamente cuando ocurre una excepción no manejada.
        """
        import sys
        import traceback
        from django.utils import timezone
        from .models import ErrorLog
        
        # Capturar información del error
        error_type = type(exception).__name__
        error_message = str(exception)
        stack_trace = ''.join(traceback.format_exception(*sys.exc_info()))
        
        # Determinar severidad automáticamente
        severity = self._determine_severity(exception)
        
        # Buscar si ya existe este error (mismo tipo y mensaje)
        existing_error = ErrorLog.objects.filter(
            error_type=error_type,
            error_message=error_message,
            is_resolved=False
        ).first()
        
        if existing_error:
            # Actualizar error existente
            existing_error.occurrence_count += 1
            existing_error.last_seen = timezone.now()
            existing_error.save()
            
            # Notificar cada 10 ocurrencias
            if existing_error.occurrence_count % 10 == 0:
                self._send_notification(existing_error, is_recurring=True)
        else:
            # Crear nuevo registro de error
            error_log = ErrorLog.objects.create(
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
                url=request.path,
                method=request.method,
                user=request.user if request.user.is_authenticated else None,
                organization=getattr(request, 'organization', None),
                request_data=self._get_request_data(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=get_client_ip() or self._get_client_ip(request),
                severity=severity,
                context=self._get_context(request)
            )
            
            # Enviar notificación para errores nuevos
            self._send_notification(error_log, is_recurring=False)
        
        # Retornar None para que Django maneje el error normalmente
        return None
    
    def _determine_severity(self, exception):
        """Determina la severidad del error basado en el tipo"""
        critical_errors = (
            'DatabaseError',
            'OperationalError',
            'IntegrityError',
            'PermissionDenied',
            'SecurityError',
        )
        
        high_errors = (
            'ValueError',
            'KeyError',
            'AttributeError',
            'ImportError',
            'TypeError',
        )
        
        error_name = type(exception).__name__
        
        if error_name in critical_errors:
            return 'critical'
        elif error_name in high_errors:
            return 'high'
        else:
            return 'medium'
    
    def _get_request_data(self, request):
        """Captura datos de la petición (GET, POST)"""
        try:
            data = {
                'GET': dict(request.GET),
                'POST': {}
            }
            
            # Solo capturar POST si no es multipart (archivos)
            if request.method == 'POST' and not request.FILES:
                # Filtrar datos sensibles
                post_data = dict(request.POST)
                sensitive_fields = ['password', 'password1', 'password2', 'token', 'secret']
                
                for key in post_data.keys():
                    if any(field in key.lower() for field in sensitive_fields):
                        post_data[key] = '***HIDDEN***'
                
                data['POST'] = post_data
            
            return data
        except:
            return {}
    
    def _get_client_ip(self, request):
        """Obtiene la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _get_context(self, request):
        """Captura contexto adicional útil para debugging"""
        try:
            context = {
                'session_key': request.session.session_key if hasattr(request, 'session') else None,
                'is_ajax': request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest',
                'referrer': request.META.get('HTTP_REFERER', ''),
                'language': request.LANGUAGE_CODE if hasattr(request, 'LANGUAGE_CODE') else None,
            }
            
            # Agregar info de usuario si está autenticado
            if request.user.is_authenticated:
                context['user_info'] = {
                    'username': request.user.username,
                    'email': request.user.email,
                    'is_staff': request.user.is_staff,
                    'is_superuser': request.user.is_superuser,
                }
            
            return context
        except:
            return {}
    
    def _send_notification(self, error_log, is_recurring=False):
        """Envía notificación de error a administradores"""
        try:
            from apps.notifications.services import send_notification
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            
            # Notificar solo a superusuarios
            superusers = User.objects.filter(is_superuser=True, is_active=True)
            
            if is_recurring:
                title = f'⚠️ Error Recurrente: {error_log.error_type}'
                message = f'{error_log.error_message}\n\nHa ocurrido {error_log.occurrence_count} veces\nURL: {error_log.url}'
            else:
                title = f'🔴 Nuevo Error: {error_log.error_type}'
                message = f'{error_log.error_message}\nURL: {error_log.url}\nSeveridad: {error_log.get_severity_display()}'
            
            for user in superusers:
                send_notification(
                    user=user,
                    title=title,
                    message=message,
                    notification_type='error',
                    channels=['email'],  # Email para errores
                    action_url=f'/admin/audit/errorlog/{error_log.id}/change/'
                )
            
            # Marcar como notificado
            error_log.notification_sent = True
            error_log.save(update_fields=['notification_sent'])
            
        except Exception as e:
            # Si falla la notificación, no queremos generar otro error
            print(f"Error enviando notificación: {e}")
