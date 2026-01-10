"""
Modelos para el sistema de configuraciones.
Permite gestionar configuraciones dinámicas por módulo y organización.
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import json
import re


class JSONFieldCompatible(models.TextField):
    """
    Campo compatible con SQLite que almacena JSON como texto.
    En PostgreSQL se comporta como JSONField nativo.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', dict)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}

    def to_python(self, value):
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_prep_value(self, value):
        if value is None:
            return '{}'
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)


class AppSetting(models.Model):
    """
    Configuración de aplicación (clave-valor).
    Permite configurar cualquier aspecto del sistema de forma dinámica.
    
    Campos:
        - key: Clave única de la configuración (ej: 'email.from_address')
        - value: Valor de la configuración (almacenado como texto)
        - value_type: Tipo de dato (string, int, bool, json, etc.)
        - organization: Organización (multi-tenant, None = global)
        - module: Módulo al que pertenece (appointments, billing, etc.)
        - description: Descripción de la configuración
        - is_sensitive: Si es dato sensible (API keys, passwords)
        - validation_rule: Regla de validación (regex, range, etc.)
    """
    
    VALUE_TYPE_CHOICES = [
        ('string', 'Texto'),
        ('int', 'Número entero'),
        ('float', 'Número decimal'),
        ('bool', 'Booleano'),
        ('json', 'JSON'),
        ('email', 'Email'),
        ('url', 'URL'),
        ('color', 'Color'),
        ('date', 'Fecha'),
        ('datetime', 'Fecha y hora'),
    ]
    
    # Clave única de la configuración
    key = models.CharField(
        'Clave',
        max_length=200,
        db_index=True,
        help_text='Identificador único (ej: email.smtp_host)'
    )
    
    # Valor de la configuración
    value = models.TextField(
        'Valor',
        blank=True,
        help_text='Valor de la configuración'
    )
    
    # Tipo de valor
    value_type = models.CharField(
        'Tipo de valor',
        max_length=20,
        choices=VALUE_TYPE_CHOICES,
        default='string'
    )
    
    # Organización (multi-tenant)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='app_settings',
        verbose_name='Organización',
        null=True,
        blank=True,
        help_text='Dejar vacío para configuración global'
    )
    
    # Módulo
    module = models.CharField(
        'Módulo',
        max_length=50,
        db_index=True,
        blank=True,
        help_text='Módulo al que pertenece (appointments, billing, etc.)'
    )
    
    # Descripción
    description = models.TextField(
        'Descripción',
        blank=True,
        help_text='Descripción de la configuración'
    )
    
    # Si es dato sensible
    is_sensitive = models.BooleanField(
        'Es sensible',
        default=False,
        help_text='Marcar si es API key, password, etc.'
    )
    
    # Regla de validación
    validation_rule = models.CharField(
        'Regla de validación',
        max_length=500,
        blank=True,
        help_text='Expresión regular, rango, etc.'
    )
    
    # Estado
    is_active = models.BooleanField(
        'Activo',
        default=True
    )
    
    # Valor por defecto
    default_value = models.TextField(
        'Valor por defecto',
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        'Fecha de creación',
        default=timezone.now
    )
    
    updated_at = models.DateTimeField(
        'Fecha de actualización',
        auto_now=True
    )
    
    class Meta:
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuraciones'
        unique_together = [['key', 'organization']]
        ordering = ['module', 'key']
        indexes = [
            models.Index(fields=['key', 'organization']),
            models.Index(fields=['module', 'is_active']),
        ]
    
    def __str__(self):
        org_name = self.organization.name if self.organization else 'Global'
        return f"{self.key} ({org_name})"
    
    def clean(self):
        """Validar el valor según el tipo y reglas."""
        super().clean()
        
        # Validar según tipo
        if self.value:
            try:
                if self.value_type == 'int':
                    int(self.value)
                elif self.value_type == 'float':
                    float(self.value)
                elif self.value_type == 'bool':
                    if self.value.lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
                        raise ValidationError('Valor booleano inválido')
                elif self.value_type == 'json':
                    json.loads(self.value)
                elif self.value_type == 'email':
                    from django.core.validators import validate_email
                    validate_email(self.value)
                elif self.value_type == 'url':
                    from django.core.validators import URLValidator
                    URLValidator()(self.value)
            except (ValueError, ValidationError) as e:
                raise ValidationError(f'Valor inválido para tipo {self.value_type}: {e}')
        
        # Validar regla personalizada (regex)
        if self.validation_rule and self.value:
            if not re.match(self.validation_rule, self.value):
                raise ValidationError('El valor no cumple con la regla de validación')
    
    def get_value(self):
        """Retorna el valor convertido al tipo correcto."""
        if not self.value:
            return self.get_default_value()
        
        if self.value_type == 'int':
            return int(self.value)
        elif self.value_type == 'float':
            return float(self.value)
        elif self.value_type == 'bool':
            return self.value.lower() in ['true', '1', 'yes']
        elif self.value_type == 'json':
            return json.loads(self.value)
        else:
            return self.value
    
    def get_default_value(self):
        """Retorna el valor por defecto convertido."""
        if not self.default_value:
            return None
        
        if self.value_type == 'int':
            return int(self.default_value)
        elif self.value_type == 'float':
            return float(self.default_value)
        elif self.value_type == 'bool':
            return self.default_value.lower() in ['true', '1', 'yes']
        elif self.value_type == 'json':
            return json.loads(self.default_value)
        else:
            return self.default_value


class IntegrationConfig(models.Model):
    """
    Configuración de integraciones externas.
    Agrupa configuraciones relacionadas con servicios externos.
    
    Tipos de integración:
        - email: SMTP, SendGrid, etc.
        - whatsapp: Baileys, Twilio, etc.
        - sms: Twilio, Nexmo, etc.
        - payment: Wompi, PayU, Stripe, etc.
        - dian: Facturación electrónica DIAN
        - crm: HubSpot, Salesforce, etc.
    """
    
    INTEGRATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('payment', 'Pagos'),
        ('dian', 'DIAN (Facturación electrónica)'),
        ('erp', 'ERP'),
        ('crm', 'CRM'),
        ('analytics', 'Analytics'),
        ('storage', 'Almacenamiento'),
        ('other', 'Otro'),
    ]
    
    # Tipo de integración
    integration_type = models.CharField(
        'Tipo de integración',
        max_length=50,
        choices=INTEGRATION_TYPE_CHOICES,
        db_index=True
    )
    
    # Nombre de la integración
    name = models.CharField(
        'Nombre',
        max_length=100,
        help_text='Nombre del servicio (ej: Wompi, Twilio, SMTP)'
    )
    
    # Organización (multi-tenant)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='integration_configs',
        verbose_name='Organización'
    )
    
    # Configuración (JSON)
    config = JSONFieldCompatible(
        'Configuración',
        help_text='Configuración en formato JSON'
    )
    
    # Credenciales (JSON encriptado)
    credentials = JSONFieldCompatible(
        'Credenciales',
        help_text='API keys, tokens, passwords (se deben encriptar)'
    )
    
    # Estado
    is_active = models.BooleanField(
        'Activo',
        default=True
    )
    
    is_test_mode = models.BooleanField(
        'Modo de prueba',
        default=True,
        help_text='Si está en modo sandbox/test'
    )
    
    # Última verificación
    last_verified_at = models.DateTimeField(
        'Última verificación',
        null=True,
        blank=True,
        help_text='Última vez que se verificó la conexión'
    )
    
    is_verified = models.BooleanField(
        'Verificado',
        default=False,
        help_text='Si la conexión fue verificada exitosamente'
    )
    
    verification_error = models.TextField(
        'Error de verificación',
        blank=True
    )
    
    # Metadatos
    metadata = JSONFieldCompatible(
        'Metadatos',
        help_text='Información adicional'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        'Fecha de creación',
        default=timezone.now
    )
    
    updated_at = models.DateTimeField(
        'Fecha de actualización',
        auto_now=True
    )
    
    class Meta:
        verbose_name = 'Configuración de integración'
        verbose_name_plural = 'Configuraciones de integración'
        unique_together = [['integration_type', 'name', 'organization']]
        ordering = ['integration_type', 'name']
        indexes = [
            models.Index(fields=['integration_type', 'is_active']),
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_integration_type_display()} - {self.name} ({self.organization.name})"
    
    def verify_connection(self):
        """
        Verifica la conexión con el servicio externo.
        Debe ser implementado según el tipo de integración.
        """
        # TODO: Implementar verificación según tipo
        self.last_verified_at = timezone.now()
        self.save()
        return True


class SettingCategory(models.Model):
    """
    Categoría para agrupar configuraciones en la UI.
    Facilita la organización visual de las configuraciones.
    """
    
    name = models.CharField(
        'Nombre',
        max_length=100
    )
    
    slug = models.SlugField(
        'Slug',
        max_length=100,
        unique=True
    )
    
    description = models.TextField(
        'Descripción',
        blank=True
    )
    
    icon = models.CharField(
        'Ícono',
        max_length=50,
        blank=True,
        help_text='Clase de ícono (ej: fas fa-cog)'
    )
    
    order = models.IntegerField(
        'Orden',
        default=0,
        help_text='Orden de visualización'
    )
    
    # Relación con configuraciones
    settings = models.ManyToManyField(
        AppSetting,
        related_name='categories',
        blank=True,
        verbose_name='Configuraciones'
    )
    
    class Meta:
        verbose_name = 'Categoría de configuración'
        verbose_name_plural = 'Categorías de configuración'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
