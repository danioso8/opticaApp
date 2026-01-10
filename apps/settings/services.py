"""
Servicios para el sistema de configuraciones.
Proporciona funciones para obtener, establecer y gestionar configuraciones.
"""
from django.core.cache import cache
from django.db.models import Q
import json

from .models import AppSetting, IntegrationConfig, SettingCategory


class SettingsService:
    """
    Servicio para gestionar configuraciones de la aplicación.
    Incluye cache para mejorar el rendimiento.
    """
    
    CACHE_TIMEOUT = 3600  # 1 hora
    
    @staticmethod
    def get(key, organization=None, default=None, use_cache=True):
        """
        Obtiene el valor de una configuración.
        Busca primero en la org específica, luego global.
        
        Args:
            key: Clave de la configuración
            organization: Organización (None = global)
            default: Valor por defecto si no existe
            use_cache: Si debe usar cache
        
        Returns:
            Valor de la configuración o default
        """
        # Intentar obtener de cache
        if use_cache:
            cache_key = f"setting_{key}_{organization.id if organization else 'global'}"
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
        
        # Buscar configuración específica de la organización
        if organization:
            setting = AppSetting.objects.filter(
                key=key,
                organization=organization,
                is_active=True
            ).first()
            
            if setting:
                value = setting.get_value()
                if use_cache:
                    cache.set(cache_key, value, SettingsService.CACHE_TIMEOUT)
                return value
        
        # Buscar configuración global
        setting = AppSetting.objects.filter(
            key=key,
            organization__isnull=True,
            is_active=True
        ).first()
        
        if setting:
            value = setting.get_value()
            if use_cache:
                cache.set(cache_key, value, SettingsService.CACHE_TIMEOUT)
            return value
        
        # Retornar valor por defecto
        return default
    
    @staticmethod
    def set(key, value, organization=None, value_type='string', 
            description='', module='', is_sensitive=False):
        """
        Establece el valor de una configuración.
        Crea la configuración si no existe.
        
        Args:
            key: Clave de la configuración
            value: Valor a establecer
            organization: Organización
            value_type: Tipo de valor
            description: Descripción
            module: Módulo
            is_sensitive: Si es dato sensible
        
        Returns:
            AppSetting creado o actualizado
        """
        # Convertir valor a string según tipo
        if value_type == 'json':
            value_str = json.dumps(value, ensure_ascii=False)
        elif value_type == 'bool':
            value_str = 'true' if value else 'false'
        else:
            value_str = str(value)
        
        # Crear o actualizar
        setting, created = AppSetting.objects.update_or_create(
            key=key,
            organization=organization,
            defaults={
                'value': value_str,
                'value_type': value_type,
                'description': description,
                'module': module,
                'is_sensitive': is_sensitive,
                'is_active': True
            }
        )
        
        # Invalidar cache
        cache_key = f"setting_{key}_{organization.id if organization else 'global'}"
        cache.delete(cache_key)
        
        return setting
    
    @staticmethod
    def get_module_settings(module, organization=None):
        """
        Obtiene todas las configuraciones de un módulo.
        
        Args:
            module: Nombre del módulo
            organization: Organización
        
        Returns:
            Dict con configuraciones {key: value}
        """
        filters = Q(module=module, is_active=True)
        
        if organization:
            filters &= Q(organization=organization) | Q(organization__isnull=True)
        else:
            filters &= Q(organization__isnull=True)
        
        settings = AppSetting.objects.filter(filters)
        
        result = {}
        for setting in settings:
            # Si hay org específica y global, preferir org específica
            if setting.key not in result or setting.organization == organization:
                result[setting.key] = setting.get_value()
        
        return result
    
    @staticmethod
    def delete(key, organization=None):
        """
        Elimina una configuración.
        
        Args:
            key: Clave de la configuración
            organization: Organización
        
        Returns:
            Número de configuraciones eliminadas
        """
        count = AppSetting.objects.filter(
            key=key,
            organization=organization
        ).delete()[0]
        
        # Invalidar cache
        cache_key = f"setting_{key}_{organization.id if organization else 'global'}"
        cache.delete(cache_key)
        
        return count
    
    @staticmethod
    def clear_cache(organization=None):
        """
        Limpia el cache de configuraciones.
        
        Args:
            organization: Organización (None = limpiar todo)
        """
        if organization:
            # Limpiar cache de la organización
            settings = AppSetting.objects.filter(organization=organization)
            for setting in settings:
                cache_key = f"setting_{setting.key}_{organization.id}"
                cache.delete(cache_key)
        else:
            # Limpiar todo el cache de settings
            # (en producción se debería usar un prefijo para los keys)
            cache.clear()


class IntegrationService:
    """
    Servicio para gestionar configuraciones de integraciones.
    """
    
    @staticmethod
    def get_integration(integration_type, organization, name=None):
        """
        Obtiene la configuración de una integración.
        
        Args:
            integration_type: Tipo de integración
            organization: Organización
            name: Nombre específico (opcional)
        
        Returns:
            IntegrationConfig o None
        """
        filters = {
            'integration_type': integration_type,
            'organization': organization,
            'is_active': True
        }
        
        if name:
            filters['name'] = name
        
        return IntegrationConfig.objects.filter(**filters).first()
    
    @staticmethod
    def create_integration(integration_type, name, organization, 
                          config=None, credentials=None, is_test_mode=True):
        """
        Crea una configuración de integración.
        
        Args:
            integration_type: Tipo de integración
            name: Nombre
            organization: Organización
            config: Configuración (dict)
            credentials: Credenciales (dict)
            is_test_mode: Si está en modo test
        
        Returns:
            IntegrationConfig creado
        """
        integration = IntegrationConfig.objects.create(
            integration_type=integration_type,
            name=name,
            organization=organization,
            config=config or {},
            credentials=credentials or {},
            is_test_mode=is_test_mode,
            is_active=True
        )
        
        return integration
    
    @staticmethod
    def update_integration(integration_id, **kwargs):
        """
        Actualiza una configuración de integración.
        
        Args:
            integration_id: ID de la integración
            **kwargs: Campos a actualizar
        
        Returns:
            IntegrationConfig actualizado
        """
        integration = IntegrationConfig.objects.get(id=integration_id)
        
        for key, value in kwargs.items():
            setattr(integration, key, value)
        
        integration.save()
        return integration
    
    @staticmethod
    def verify_integration(integration_id):
        """
        Verifica la conexión de una integración.
        
        Args:
            integration_id: ID de la integración
        
        Returns:
            Bool indicando si la verificación fue exitosa
        """
        integration = IntegrationConfig.objects.get(id=integration_id)
        
        try:
            result = integration.verify_connection()
            integration.is_verified = result
            integration.verification_error = ''
            integration.save()
            return result
        except Exception as e:
            integration.is_verified = False
            integration.verification_error = str(e)
            integration.save()
            return False
    
    @staticmethod
    def get_active_integrations(organization, integration_type=None):
        """
        Obtiene todas las integraciones activas de una organización.
        
        Args:
            organization: Organización
            integration_type: Tipo de integración (opcional)
        
        Returns:
            QuerySet de IntegrationConfig
        """
        filters = {
            'organization': organization,
            'is_active': True
        }
        
        if integration_type:
            filters['integration_type'] = integration_type
        
        return IntegrationConfig.objects.filter(**filters)


def create_default_settings():
    """
    Crea configuraciones por defecto del sistema.
    """
    default_settings = [
        # Email
        {
            'key': 'email.from_name',
            'value': 'OpticaApp',
            'value_type': 'string',
            'module': 'email',
            'description': 'Nombre del remitente de emails'
        },
        {
            'key': 'email.from_address',
            'value': 'noreply@opticaapp.com',
            'value_type': 'email',
            'module': 'email',
            'description': 'Dirección de email del remitente'
        },
        
        # Appointments
        {
            'key': 'appointments.duration_default',
            'value': '30',
            'value_type': 'int',
            'module': 'appointments',
            'description': 'Duración por defecto de citas (minutos)'
        },
        {
            'key': 'appointments.reminder_hours',
            'value': '24',
            'value_type': 'int',
            'module': 'appointments',
            'description': 'Horas antes para recordatorio de cita'
        },
        {
            'key': 'appointments.allow_overlap',
            'value': 'false',
            'value_type': 'bool',
            'module': 'appointments',
            'description': 'Permitir citas superpuestas'
        },
        
        # Billing
        {
            'key': 'billing.currency',
            'value': 'COP',
            'value_type': 'string',
            'module': 'billing',
            'description': 'Moneda para facturación'
        },
        {
            'key': 'billing.tax_rate',
            'value': '19',
            'value_type': 'int',
            'module': 'billing',
            'description': 'Tasa de IVA (%)'
        },
        
        # Notifications
        {
            'key': 'notifications.channels',
            'value': '["email", "whatsapp", "system"]',
            'value_type': 'json',
            'module': 'notifications',
            'description': 'Canales de notificación habilitados'
        },
        
        # Security
        {
            'key': 'security.session_timeout',
            'value': '3600',
            'value_type': 'int',
            'module': 'security',
            'description': 'Tiempo de sesión en segundos'
        },
        {
            'key': 'security.password_min_length',
            'value': '8',
            'value_type': 'int',
            'module': 'security',
            'description': 'Longitud mínima de contraseña'
        },
    ]
    
    created_count = 0
    for setting_data in default_settings:
        _, created = AppSetting.objects.get_or_create(
            key=setting_data['key'],
            organization=None,
            defaults=setting_data
        )
        if created:
            created_count += 1
    
    return created_count


def create_default_categories():
    """
    Crea categorías por defecto para organizar configuraciones.
    """
    categories = [
        {
            'name': 'General',
            'slug': 'general',
            'description': 'Configuraciones generales de la aplicación',
            'icon': 'fas fa-cog',
            'order': 1
        },
        {
            'name': 'Email',
            'slug': 'email',
            'description': 'Configuración de correo electrónico',
            'icon': 'fas fa-envelope',
            'order': 2
        },
        {
            'name': 'Notificaciones',
            'slug': 'notifications',
            'description': 'Configuración de notificaciones',
            'icon': 'fas fa-bell',
            'order': 3
        },
        {
            'name': 'Citas',
            'slug': 'appointments',
            'description': 'Configuración de sistema de citas',
            'icon': 'fas fa-calendar',
            'order': 4
        },
        {
            'name': 'Facturación',
            'slug': 'billing',
            'description': 'Configuración de facturación y pagos',
            'icon': 'fas fa-file-invoice-dollar',
            'order': 5
        },
        {
            'name': 'Seguridad',
            'slug': 'security',
            'description': 'Configuración de seguridad',
            'icon': 'fas fa-shield-alt',
            'order': 6
        },
        {
            'name': 'Integraciones',
            'slug': 'integrations',
            'description': 'Integraciones con servicios externos',
            'icon': 'fas fa-plug',
            'order': 7
        },
    ]
    
    created_count = 0
    for cat_data in categories:
        _, created = SettingCategory.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        if created:
            created_count += 1
    
    return created_count
