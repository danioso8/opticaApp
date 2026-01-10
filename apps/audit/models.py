"""
Modelos para el sistema de auditoría.
Registra automáticamente todas las acciones críticas del sistema.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import json

User = get_user_model()


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


class AuditLog(models.Model):
    """
    Registro de auditoría que captura todas las acciones del sistema.
    
    Campos:
        - action: Tipo de acción (CREATE, UPDATE, DELETE, VIEW, LOGIN, etc.)
        - user: Usuario que realizó la acción
        - organization: Organización (multi-tenant)
        - content_type: Tipo de modelo afectado
        - object_id: ID del objeto afectado
        - object_repr: Representación del objeto
        - changes: JSON con cambios (before/after)
        - ip_address: IP del usuario
        - user_agent: Navegador/dispositivo
        - created_at: Timestamp
        - metadata: Datos adicionales
    """
    
    ACTION_CHOICES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('VIEW', 'Ver'),
        ('LOGIN', 'Iniciar sesión'),
        ('LOGOUT', 'Cerrar sesión'),
        ('LOGIN_FAILED', 'Intento de login fallido'),
        ('EXPORT', 'Exportar'),
        ('IMPORT', 'Importar'),
        ('PRINT', 'Imprimir'),
        ('EMAIL', 'Enviar email'),
        ('SMS', 'Enviar SMS'),
        ('WHATSAPP', 'Enviar WhatsApp'),
        ('PAYMENT', 'Pago'),
        ('REFUND', 'Reembolso'),
        ('OTHER', 'Otra acción'),
    ]
    
    # Acción realizada
    action = models.CharField(
        'Acción',
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True
    )
    
    # Usuario que realizó la acción
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='Usuario'
    )
    
    # Organización (multi-tenant)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='audit_logs',
        verbose_name='Organización',
        null=True,
        blank=True
    )
    
    # Objeto afectado (GenericForeignKey)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Tipo de objeto'
    )
    object_id = models.CharField(
        'ID del objeto',
        max_length=255,
        null=True,
        blank=True,
        db_index=True
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Representación del objeto
    object_repr = models.CharField(
        'Representación del objeto',
        max_length=500,
        blank=True
    )
    
    # Cambios realizados (before/after)
    changes = JSONFieldCompatible(
        'Cambios',
        help_text='JSON con cambios antes/después'
    )
    
    # Información de la solicitud
    ip_address = models.GenericIPAddressField(
        'Dirección IP',
        null=True,
        blank=True
    )
    
    user_agent = models.TextField(
        'User Agent',
        blank=True,
        help_text='Navegador y sistema operativo'
    )
    
    # Timestamp
    created_at = models.DateTimeField(
        'Fecha de creación',
        default=timezone.now,
        db_index=True
    )
    
    # Metadatos adicionales
    metadata = JSONFieldCompatible(
        'Metadatos',
        help_text='Información adicional en formato JSON'
    )
    
    # Descripción opcional
    description = models.TextField(
        'Descripción',
        blank=True,
        help_text='Descripción detallada de la acción'
    )
    
    class Meta:
        verbose_name = 'Registro de auditoría'
        verbose_name_plural = 'Registros de auditoría'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action', '-created_at']),
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),
        ]
    
    def __str__(self):
        user_name = self.user.get_full_name() if self.user else 'Sistema'
        action_name = self.get_action_display()
        if self.object_repr:
            return f"{user_name} - {action_name}: {self.object_repr}"
        return f"{user_name} - {action_name}"
    
    def get_changes_display(self):
        """Retorna los cambios en formato legible."""
        if not self.changes:
            return "Sin cambios"
        
        lines = []
        for field, values in self.changes.items():
            if isinstance(values, dict) and 'old' in values and 'new' in values:
                lines.append(f"{field}: {values['old']} → {values['new']}")
            else:
                lines.append(f"{field}: {values}")
        
        return "\n".join(lines)


class AuditConfig(models.Model):
    """
    Configuración de auditoría por modelo y organización.
    Define qué acciones se auditan para cada modelo.
    """
    
    # Modelo a auditar
    model_name = models.CharField(
        'Modelo',
        max_length=100,
        help_text='Nombre del modelo (app.Model)'
    )
    
    # Organización (multi-tenant)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='audit_configs',
        verbose_name='Organización',
        null=True,
        blank=True,
        help_text='Dejar vacío para configuración global'
    )
    
    # Qué acciones auditar
    track_creates = models.BooleanField(
        'Auditar creaciones',
        default=True
    )
    
    track_updates = models.BooleanField(
        'Auditar actualizaciones',
        default=True
    )
    
    track_deletes = models.BooleanField(
        'Auditar eliminaciones',
        default=True
    )
    
    track_reads = models.BooleanField(
        'Auditar lecturas',
        default=False,
        help_text='Puede generar muchos registros'
    )
    
    # Retención de datos
    retention_days = models.IntegerField(
        'Días de retención',
        default=365,
        help_text='Días para mantener los logs antes de eliminarlos'
    )
    
    # Estado
    is_active = models.BooleanField(
        'Activo',
        default=True
    )
    
    # Campos a excluir del tracking
    excluded_fields = JSONFieldCompatible(
        'Campos excluidos',
        help_text='Lista de campos que no se auditarán'
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
        verbose_name = 'Configuración de auditoría'
        verbose_name_plural = 'Configuraciones de auditoría'
        unique_together = [['model_name', 'organization']]
        indexes = [
            models.Index(fields=['model_name', 'is_active']),
        ]
    
    def __str__(self):
        org_name = self.organization.name if self.organization else 'Global'
        return f"{self.model_name} - {org_name}"
    
    def should_track_action(self, action):
        """Verifica si una acción debe ser auditada."""
        if not self.is_active:
            return False
        
        action_map = {
            'CREATE': self.track_creates,
            'UPDATE': self.track_updates,
            'DELETE': self.track_deletes,
            'VIEW': self.track_reads,
        }
        
        return action_map.get(action, False)


class AuditRetentionLog(models.Model):
    """
    Registro de ejecuciones de limpieza de auditorías antiguas.
    """
    
    # Ejecución
    executed_at = models.DateTimeField(
        'Fecha de ejecución',
        default=timezone.now
    )
    
    # Resultados
    logs_deleted = models.IntegerField(
        'Logs eliminados',
        default=0
    )
    
    oldest_date_deleted = models.DateTimeField(
        'Fecha más antigua eliminada',
        null=True,
        blank=True
    )
    
    # Duración
    duration_seconds = models.FloatField(
        'Duración (segundos)',
        default=0
    )
    
    # Detalles
    details = JSONFieldCompatible(
        'Detalles',
        help_text='Detalles de la ejecución'
    )
    
    class Meta:
        verbose_name = 'Registro de limpieza'
        verbose_name_plural = 'Registros de limpieza'
        ordering = ['-executed_at']
    
    def __str__(self):
        return f"Limpieza {self.executed_at.strftime('%d/%m/%Y %H:%M')} - {self.logs_deleted} logs"


class ErrorLog(models.Model):
    """
    Registro de errores de la aplicación para monitoreo en tiempo real.
    Similar a Sentry pero propio.
    """
    
    # Timestamp
    timestamp = models.DateTimeField(
        'Fecha y hora',
        default=timezone.now,
        db_index=True
    )
    
    # Error information
    error_type = models.CharField(
        'Tipo de error',
        max_length=200,
        help_text='ValueError, AttributeError, KeyError, etc.'
    )
    
    error_message = models.TextField(
        'Mensaje de error'
    )
    
    stack_trace = models.TextField(
        'Stack trace completo'
    )
    
    # Request information
    url = models.CharField(
        'URL',
        max_length=500,
        blank=True
    )
    
    method = models.CharField(
        'Método HTTP',
        max_length=10,
        blank=True,
        help_text='GET, POST, PUT, DELETE, etc.'
    )
    
    # User context
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuario',
        related_name='error_logs'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Organización',
        related_name='error_logs'
    )
    
    # Request data
    request_data = JSONFieldCompatible(
        'Datos de petición',
        help_text='GET params, POST data, etc.'
    )
    
    user_agent = models.TextField(
        'User Agent',
        blank=True
    )
    
    ip_address = models.GenericIPAddressField(
        'Dirección IP',
        null=True,
        blank=True
    )
    
    # Additional context
    context = JSONFieldCompatible(
        'Contexto adicional',
        help_text='Variables locales, estado de la sesión, etc.'
    )
    
    # Resolution tracking
    is_resolved = models.BooleanField(
        'Resuelto',
        default=False,
        db_index=True
    )
    
    resolved_at = models.DateTimeField(
        'Resuelto en',
        null=True,
        blank=True
    )
    
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Resuelto por',
        related_name='resolved_errors'
    )
    
    resolution_notes = models.TextField(
        'Notas de resolución',
        blank=True
    )
    
    # Occurrence tracking
    occurrence_count = models.IntegerField(
        'Veces que ocurrió',
        default=1
    )
    
    first_seen = models.DateTimeField(
        'Primera vez visto',
        default=timezone.now
    )
    
    last_seen = models.DateTimeField(
        'Última vez visto',
        auto_now=True
    )
    
    # Severity
    SEVERITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]
    
    severity = models.CharField(
        'Severidad',
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='medium'
    )
    
    # Notification
    notification_sent = models.BooleanField(
        'Notificación enviada',
        default=False
    )
    
    class Meta:
        verbose_name = 'Error de sistema'
        verbose_name_plural = 'Errores de sistema'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['error_type', 'is_resolved']),
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['severity', 'is_resolved']),
        ]
    
    def __str__(self):
        return f"{self.error_type} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
    
    def mark_resolved(self, user, notes=''):
        """Marca el error como resuelto"""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.resolution_notes = notes
        self.save()
    
    def get_similar_errors(self, limit=5):
        """Encuentra errores similares (mismo tipo y mensaje)"""
        return ErrorLog.objects.filter(
            error_type=self.error_type,
            error_message=self.error_message,
            is_resolved=False
        ).exclude(id=self.id).order_by('-timestamp')[:limit]
    
    @classmethod
    def get_unresolved_count(cls):
        """Cuenta de errores sin resolver"""
        return cls.objects.filter(is_resolved=False).count()
    
    @classmethod
    def get_critical_errors(cls):
        """Errores críticos sin resolver"""
        return cls.objects.filter(
            is_resolved=False,
            severity='critical'
        ).order_by('-timestamp')
    
    @classmethod
    def get_error_stats(cls, days=7):
        """Estadísticas de errores de los últimos N días"""
        from django.db.models import Count, Sum
        from django.utils import timezone
        from datetime import timedelta
        
        start_date = timezone.now() - timedelta(days=days)
        
        stats = cls.objects.filter(timestamp__gte=start_date).aggregate(
            total_errors=Count('id'),
            unique_errors=Count('id', distinct=True),
            total_occurrences=Sum('occurrence_count'),
            unresolved=Count('id', filter=models.Q(is_resolved=False))
        )
        
        return stats
