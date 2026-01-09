"""
Signals para auditoría automática de modelos.
Captura cambios en modelos y los registra automáticamente.
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.core.exceptions import ObjectDoesNotExist

from .services import AuditService
from .middleware import get_current_user, get_client_ip, get_user_agent


# Diccionario para almacenar el estado anterior de los objetos
_pre_save_instances = {}


@receiver(pre_save)
def capture_pre_save_state(sender, instance, **kwargs):
    """
    Captura el estado del objeto antes de guardarlo.
    Se usa para detectar cambios en UPDATE.
    """
    # Solo para objetos existentes (UPDATE)
    if instance.pk:
        try:
            # Guardar estado anterior
            old_instance = sender.objects.get(pk=instance.pk)
            key = f"{sender.__name__}_{instance.pk}"
            _pre_save_instances[key] = old_instance
        except ObjectDoesNotExist:
            pass


@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    """
    Registra creación o actualización de modelos.
    """
    # Ignorar modelos del sistema de auditoría
    if sender.__module__.startswith('apps.audit'):
        return
    
    # Ignorar sesiones y otros modelos de sistema
    ignored_models = ['Session', 'ContentType', 'Permission', 'LogEntry', 'MigrationRecorder']
    if sender.__name__ in ignored_models:
        return
    
    # Ignorar durante migraciones
    if sender._meta.app_label == 'migrations':
        return
    
    # Determinar acción
    action = 'CREATE' if created else 'UPDATE'
    
    # Obtener información del usuario y request
    user = get_current_user()
    ip_address = get_client_ip()
    user_agent = get_user_agent()
    
    # Obtener organización si el modelo tiene ese campo
    organization = None
    if hasattr(instance, 'organization'):
        organization = instance.organization
    elif hasattr(instance, 'get_organization'):
        organization = instance.get_organization()
    
    # Detectar cambios en UPDATE
    changes = {}
    if not created:
        key = f"{sender.__name__}_{instance.pk}"
        old_instance = _pre_save_instances.get(key)
        
        if old_instance:
            # Comparar campos
            for field in instance._meta.fields:
                field_name = field.name
                
                # Ignorar campos automáticos
                if field_name in ['id', 'created_at', 'updated_at']:
                    continue
                
                old_value = getattr(old_instance, field_name, None)
                new_value = getattr(instance, field_name, None)
                
                # Detectar cambio
                if old_value != new_value:
                    changes[field_name] = {
                        'old': str(old_value) if old_value is not None else None,
                        'new': str(new_value) if new_value is not None else None
                    }
            
            # Limpiar de caché
            del _pre_save_instances[key]
    
    # Registrar en auditoría
    AuditService.log_action(
        action=action,
        user=user,
        organization=organization,
        instance=instance,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent
    )


@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    """
    Registra eliminación de modelos.
    """
    # Ignorar modelos del sistema de auditoría
    if sender.__module__.startswith('apps.audit'):
        return
    
    # Ignorar modelos de sistema
    ignored_models = ['Session', 'ContentType', 'Permission', 'LogEntry']
    if sender.__name__ in ignored_models:
        return
    
    # Obtener información del usuario y request
    user = get_current_user()
    ip_address = get_client_ip()
    user_agent = get_user_agent()
    
    # Obtener organización
    organization = None
    if hasattr(instance, 'organization'):
        organization = instance.organization
    elif hasattr(instance, 'get_organization'):
        organization = instance.get_organization()
    
    # Capturar datos del objeto eliminado
    changes = {}
    for field in instance._meta.fields:
        field_name = field.name
        if field_name not in ['id', 'created_at', 'updated_at']:
            value = getattr(instance, field_name, None)
            changes[field_name] = str(value) if value is not None else None
    
    # Registrar en auditoría
    AuditService.log_action(
        action='DELETE',
        user=user,
        organization=organization,
        instance=instance,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent
    )


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Registra inicio de sesión exitoso.
    """
    organization = None
    if hasattr(user, 'get_active_organization'):
        organization = user.get_active_organization()
    
    AuditService.log_action(
        action='LOGIN',
        user=user,
        organization=organization,
        ip_address=get_client_ip(),
        user_agent=get_user_agent(),
        description=f"Inicio de sesión exitoso: {user.email}"
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Registra cierre de sesión.
    """
    if user:
        organization = None
        if hasattr(user, 'get_active_organization'):
            organization = user.get_active_organization()
        
        AuditService.log_action(
            action='LOGOUT',
            user=user,
            organization=organization,
            ip_address=get_client_ip(),
            user_agent=get_user_agent(),
            description=f"Cierre de sesión: {user.email}"
        )


@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    """
    Registra intentos de inicio de sesión fallidos.
    """
    email = credentials.get('username', 'Unknown')
    
    AuditService.log_action(
        action='LOGIN_FAILED',
        user=None,
        organization=None,
        ip_address=get_client_ip(),
        user_agent=get_user_agent(),
        description=f"Intento de login fallido: {email}",
        metadata={'email': email}
    )
