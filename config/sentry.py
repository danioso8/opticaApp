"""
Configuración de Sentry para OpticaApp
Monitoreo de errores en producción
"""
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging
from decouple import config


def init_sentry():
    """
    Inicializa Sentry solo en producción
    """
    SENTRY_DSN = config('SENTRY_DSN', default='')
    ENVIRONMENT = config('ENVIRONMENT', default='development')
    DEBUG = config('DEBUG', default=True, cast=bool)
    
    # Solo inicializar en producción y si hay DSN configurado
    if SENTRY_DSN and not DEBUG:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                DjangoIntegration(
                    transaction_style='url',
                    middleware_spans=True,
                    signals_spans=True,
                    cache_spans=True,
                ),
                LoggingIntegration(
                    level=logging.INFO,        # Captura logs de nivel INFO+
                    event_level=logging.ERROR  # Envía a Sentry solo ERROR+
                ),
            ],
            
            # Configuración de trazas de rendimiento
            traces_sample_rate=0.1,  # 10% de transacciones para performance monitoring
            
            # Configuración de muestreo de errores
            sample_rate=1.0,  # 100% de errores
            
            # Configuración del entorno
            environment=ENVIRONMENT,
            
            # Configuración de releases (para tracking de versiones)
            release=f"opticaapp@{config('APP_VERSION', default='1.0.0')}",
            
            # Configuración de datos sensibles
            send_default_pii=False,  # No enviar información personal identificable
            
            # Configuración de captura de contexto
            request_bodies='small',  # Capturar cuerpos de request pequeños
            max_request_body_size='medium',  # Tamaño máximo: medium
            
            # Filtrar datos sensibles adicionales
            before_send=filter_sensitive_data,
            
            # Configuración de breadcrumbs
            max_breadcrumbs=50,
            
            # Tags personalizados
            default_integrations=True,
            
            # Configuración de performance
            profiles_sample_rate=0.1,  # 10% de profiles para performance profiling
        )
        
        # Log de inicialización exitosa
        logging.info(f"✅ Sentry inicializado correctamente - Environment: {ENVIRONMENT}")
    else:
        if DEBUG:
            logging.info("🔧 Sentry deshabilitado en modo DEBUG")
        else:
            logging.warning("⚠️ SENTRY_DSN no configurado - Monitoreo deshabilitado")


def filter_sensitive_data(event, hint):
    """
    Filtra datos sensibles antes de enviar a Sentry
    """
    # Filtrar cookies sensibles
    if 'request' in event:
        if 'cookies' in event['request']:
            sensitive_cookies = ['sessionid', 'csrftoken', 'auth_token']
            for cookie in sensitive_cookies:
                if cookie in event['request']['cookies']:
                    event['request']['cookies'][cookie] = '[Filtered]'
        
        # Filtrar headers sensibles
        if 'headers' in event['request']:
            sensitive_headers = ['Authorization', 'Cookie', 'X-Api-Key']
            for header in sensitive_headers:
                if header in event['request']['headers']:
                    event['request']['headers'][header] = '[Filtered]'
        
        # Filtrar datos sensibles de POST
        if 'data' in event['request'] and isinstance(event['request']['data'], dict):
            sensitive_fields = ['password', 'token', 'secret', 'api_key', 'private_key', 
                              'credit_card', 'cvv', 'ssn', 'pin']
            for field in sensitive_fields:
                if field in event['request']['data']:
                    event['request']['data'][field] = '[Filtered]'
    
    # Agregar contexto personalizado
    if 'user' in event:
        # Mantener solo ID de usuario, no información personal
        if 'email' in event['user']:
            event['user']['email'] = '[Filtered]'
        if 'username' in event['user']:
            # Mantener solo primeros 3 caracteres
            event['user']['username'] = event['user']['username'][:3] + '***'
    
    # Agregar tags personalizados
    if 'tags' not in event:
        event['tags'] = {}
    
    event['tags']['app'] = 'opticaapp'
    
    # Agregar contexto de organización si existe
    if 'request' in event and hasattr(event.get('request'), 'organization'):
        event['tags']['organization_id'] = str(event['request'].organization.id)
        event['tags']['organization_name'] = event['request'].organization.name
    
    return event


def capture_message(message, level='info', **kwargs):
    """
    Wrapper para capturar mensajes personalizados en Sentry
    """
    try:
        sentry_sdk.capture_message(message, level=level, **kwargs)
    except Exception as e:
        logging.error(f"Error al enviar mensaje a Sentry: {e}")


def capture_exception(exception, **kwargs):
    """
    Wrapper para capturar excepciones en Sentry
    """
    try:
        sentry_sdk.capture_exception(exception, **kwargs)
    except Exception as e:
        logging.error(f"Error al enviar excepción a Sentry: {e}")


def set_user(user_id, email=None, username=None):
    """
    Configura el usuario actual en el contexto de Sentry
    """
    try:
        sentry_sdk.set_user({
            "id": user_id,
            "email": email,
            "username": username
        })
    except Exception as e:
        logging.error(f"Error al configurar usuario en Sentry: {e}")


def set_context(key, data):
    """
    Agrega contexto personalizado a Sentry
    """
    try:
        sentry_sdk.set_context(key, data)
    except Exception as e:
        logging.error(f"Error al configurar contexto en Sentry: {e}")


def add_breadcrumb(message, category='info', level='info', data=None):
    """
    Agrega un breadcrumb al contexto de Sentry
    """
    try:
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data or {}
        )
    except Exception as e:
        logging.error(f"Error al agregar breadcrumb a Sentry: {e}")
