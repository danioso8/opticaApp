from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.organizations.base_models import TenantModel
import json


class JSONFieldCompatible(models.TextField):
    """Campo compatible con SQLite y PostgreSQL para datos JSON"""
    def __init__(self, *args, **kwargs):
        kwargs.pop('default', None)
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
        return json.dumps(value)
    
    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)


class Notification(TenantModel):
    """
    Notificación para un usuario
    Puede ser enviada por múltiples canales: sistema, email, WhatsApp, SMS
    """
    TYPE_CHOICES = [
        ('info', 'Información'),
        ('success', 'Éxito'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('reminder', 'Recordatorio'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Usuario'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    message = models.TextField(
        verbose_name='Mensaje'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='info',
        verbose_name='Tipo'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal',
        verbose_name='Prioridad'
    )
    
    # Estado de lectura
    is_read = models.BooleanField(
        default=False,
        verbose_name='Leída'
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Leída el'
    )
    
    # Acción relacionada (opcional)
    action_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='URL de Acción',
        help_text='URL a la que redirige al hacer clic'
    )
    action_label = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Etiqueta del Botón',
        help_text='Texto del botón de acción'
    )
    
    # Metadatos adicionales (JSON)
    # Ejemplo: {"module": "appointments", "object_id": 123, "icon": "calendar"}
    metadata = JSONFieldCompatible(
        verbose_name='Metadatos',
        blank=True
    )
    
    # Origen de la notificación
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
        verbose_name='Enviada por'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Creada el'
    )
    
    # Expiración (opcional)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Expira el'
    )
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['user', 'organization']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        """Marca la notificación como leída"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def is_expired(self):
        """Verifica si la notificación ha expirado"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    def get_icon(self):
        """Obtiene el icono según el tipo"""
        icons = {
            'info': '📋',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'reminder': '⏰',
        }
        return self.metadata.get('icon', icons.get(self.notification_type, '📌'))


class NotificationChannel(TenantModel):
    """
    Canal de envío de notificaciones
    """
    CHANNEL_CHOICES = [
        ('system', 'Sistema (Dashboard)'),
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('sending', 'Enviando'),
        ('sent', 'Enviado'),
        ('failed', 'Fallido'),
        ('delivered', 'Entregado'),
        ('read', 'Leído'),
    ]
    
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='channels',
        verbose_name='Notificación'
    )
    channel = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,
        verbose_name='Canal'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    
    # Datos específicos del canal
    recipient = models.CharField(
        max_length=255,
        verbose_name='Destinatario',
        help_text='Email, número de teléfono, etc.'
    )
    
    # Respuesta del servicio de envío
    response_data = JSONFieldCompatible(
        verbose_name='Respuesta del Servicio',
        blank=True
    )
    error_message = models.TextField(
        blank=True,
        verbose_name='Mensaje de Error'
    )
    
    # Timestamps
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Enviado el'
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Entregado el'
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Leído el'
    )
    
    # Reintentos
    retry_count = models.IntegerField(
        default=0,
        verbose_name='Intentos de Reenvío'
    )
    max_retries = models.IntegerField(
        default=3,
        verbose_name='Máximo de Reintentos'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Canal de Notificación'
        verbose_name_plural = 'Canales de Notificación'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['notification', 'channel']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification.title} - {self.get_channel_display()}"
    
    def can_retry(self):
        """Verifica si se puede reintentar el envío"""
        return self.status == 'failed' and self.retry_count < self.max_retries


class NotificationPreference(TenantModel):
    """
    Preferencias de notificación por usuario
    Controla qué tipos de notificaciones recibe en qué canales
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name='Usuario'
    )
    
    # Tipo de notificación (ej: 'appointment_reminder', 'payment_received', etc.)
    notification_type = models.CharField(
        max_length=100,
        verbose_name='Tipo de Notificación',
        help_text='Código del tipo de notificación'
    )
    
    # Canales habilitados para este tipo (JSON array)
    # Ejemplo: ["system", "email", "whatsapp"]
    enabled_channels = JSONFieldCompatible(
        verbose_name='Canales Habilitados',
        blank=True,
        help_text='Lista de canales habilitados para este tipo'
    )
    
    # Configuración específica por canal
    channel_config = JSONFieldCompatible(
        verbose_name='Configuración de Canales',
        blank=True,
        help_text='Configuración específica por canal'
    )
    
    is_enabled = models.BooleanField(
        default=True,
        verbose_name='Habilitado'
    )
    
    class Meta:
        verbose_name = 'Preferencia de Notificación'
        verbose_name_plural = 'Preferencias de Notificación'
        unique_together = [['user', 'organization', 'notification_type']]
        indexes = [
            models.Index(fields=['user', 'organization']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.notification_type}"
    
    def is_channel_enabled(self, channel):
        """Verifica si un canal está habilitado"""
        if not self.is_enabled:
            return False
        channels = self.enabled_channels if isinstance(self.enabled_channels, list) else []
        return channel in channels


class NotificationTemplate(TenantModel):
    """
    Plantillas de notificaciones reutilizables
    """
    code = models.CharField(
        max_length=100,
        verbose_name='Código',
        help_text='Código único para la plantilla'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    # Plantilla del título (puede incluir variables: {variable})
    title_template = models.CharField(
        max_length=200,
        verbose_name='Plantilla del Título'
    )
    
    # Plantilla del mensaje
    message_template = models.TextField(
        verbose_name='Plantilla del Mensaje'
    )
    
    # Tipo por defecto
    default_type = models.CharField(
        max_length=20,
        choices=Notification.TYPE_CHOICES,
        default='info',
        verbose_name='Tipo por Defecto'
    )
    
    # Canales por defecto
    default_channels = JSONFieldCompatible(
        verbose_name='Canales por Defecto',
        blank=True,
        help_text='Lista de canales a usar por defecto'
    )
    
    # Variables esperadas (documentación)
    expected_variables = JSONFieldCompatible(
        verbose_name='Variables Esperadas',
        blank=True,
        help_text='Lista de variables que acepta la plantilla'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Plantilla de Notificación'
        verbose_name_plural = 'Plantillas de Notificación'
        unique_together = [['organization', 'code']]
        indexes = [
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def render(self, variables=None):
        """
        Renderiza la plantilla con las variables proporcionadas
        """
        if variables is None:
            variables = {}
        
        title = self.title_template
        message = self.message_template
        
        # Reemplazar variables
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            title = title.replace(placeholder, str(value))
            message = message.replace(placeholder, str(value))
        
        return {
            'title': title,
            'message': message,
            'type': self.default_type
        }


class NotificationBatch(TenantModel):
    """
    Lote de notificaciones enviadas masivamente
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre del Lote'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    # Plantilla utilizada (opcional)
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Plantilla'
    )
    
    # Estado del envío
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('scheduled', 'Programado'),
        ('sending', 'Enviando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )
    
    # Estadísticas
    total_recipients = models.IntegerField(
        default=0,
        verbose_name='Total de Destinatarios'
    )
    sent_count = models.IntegerField(
        default=0,
        verbose_name='Enviados'
    )
    failed_count = models.IntegerField(
        default=0,
        verbose_name='Fallidos'
    )
    
    # Programación
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Programado para'
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Iniciado el'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Completado el'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='notification_batches',
        verbose_name='Creado por'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Lote de Notificaciones'
        verbose_name_plural = 'Lotes de Notificaciones'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def success_rate(self):
        """Tasa de éxito del envío"""
        if self.total_recipients == 0:
            return 0
        return (self.sent_count / self.total_recipients) * 100
