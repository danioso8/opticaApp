"""
Modelos para el sistema de reportes.
Permite crear, programar y exportar reportes personalizados.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
import json

User = get_user_model()


class JSONFieldCompatible(models.TextField):
    """Campo compatible con SQLite que almacena JSON como texto."""
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


class ReportTemplate(models.Model):
    """
    Plantilla de reporte reutilizable.
    Define qué datos mostrar y cómo formatearlos.
    """
    
    REPORT_TYPE_CHOICES = [
        ('sales', 'Ventas'),
        ('patients', 'Pacientes'),
        ('appointments', 'Citas'),
        ('inventory', 'Inventario'),
        ('financial', 'Financiero'),
        ('clinical', 'Clínico'),
        ('hr', 'Recursos Humanos'),
        ('analytics', 'Analytics'),
        ('custom', 'Personalizado'),
    ]
    
    # Nombre del reporte
    name = models.CharField(
        'Nombre',
        max_length=200
    )
    
    # Tipo de reporte
    report_type = models.CharField(
        'Tipo de reporte',
        max_length=50,
        choices=REPORT_TYPE_CHOICES,
        db_index=True
    )
    
    # Descripción
    description = models.TextField(
        'Descripción',
        blank=True
    )
    
    # Organización (multi-tenant)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='report_templates',
        verbose_name='Organización',
        null=True,
        blank=True,
        help_text='Dejar vacío para plantilla global'
    )
    
    # Creador
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_reports',
        verbose_name='Creado por'
    )
    
    # Configuración del reporte (JSON)
    config = JSONFieldCompatible(
        'Configuración',
        help_text='Configuración en formato JSON (filtros, campos, agrupaciones)'
    )
    
    # Query SQL personalizado (opcional)
    custom_query = models.TextField(
        'Query personalizado',
        blank=True,
        help_text='Query SQL para reportes avanzados'
    )
    
    # Columnas a mostrar
    columns = JSONFieldCompatible(
        'Columnas',
        help_text='Lista de columnas a mostrar'
    )
    
    # Filtros por defecto
    default_filters = JSONFieldCompatible(
        'Filtros por defecto',
        help_text='Filtros que se aplican por defecto'
    )
    
    # Agrupaciones
    grouping = JSONFieldCompatible(
        'Agrupaciones',
        help_text='Campos por los que agrupar'
    )
    
    # Ordenamiento
    ordering = JSONFieldCompatible(
        'Ordenamiento',
        help_text='Orden de los resultados'
    )
    
    # Si es reporte del sistema (no editable)
    is_system = models.BooleanField(
        'Es del sistema',
        default=False
    )
    
    # Si es público
    is_public = models.BooleanField(
        'Es público',
        default=False,
        help_text='Visible para todos los usuarios de la org'
    )
    
    # Estado
    is_active = models.BooleanField(
        'Activo',
        default=True
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
        verbose_name = 'Plantilla de reporte'
        verbose_name_plural = 'Plantillas de reporte'
        ordering = ['report_type', 'name']
        indexes = [
            models.Index(fields=['report_type', 'is_active']),
            models.Index(fields=['organization', 'is_public']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class Report(models.Model):
    """
    Reporte generado.
    Instancia de una plantilla con datos específicos.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('html', 'HTML'),
    ]
    
    # Plantilla utilizada
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='generated_reports',
        verbose_name='Plantilla'
    )
    
    # Organización
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name='Organización'
    )
    
    # Usuario que generó el reporte
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_reports',
        verbose_name='Generado por'
    )
    
    # Nombre del reporte generado
    name = models.CharField(
        'Nombre',
        max_length=200
    )
    
    # Parámetros aplicados
    parameters = JSONFieldCompatible(
        'Parámetros',
        help_text='Filtros y parámetros aplicados al generar'
    )
    
    # Rango de fechas
    date_from = models.DateField(
        'Fecha desde',
        null=True,
        blank=True
    )
    
    date_to = models.DateField(
        'Fecha hasta',
        null=True,
        blank=True
    )
    
    # Formato de salida
    output_format = models.CharField(
        'Formato',
        max_length=20,
        choices=FORMAT_CHOICES,
        default='pdf'
    )
    
    # Estado
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    
    # Archivo generado
    file = models.FileField(
        'Archivo',
        upload_to='reports/%Y/%m/',
        null=True,
        blank=True
    )
    
    # Resultados (JSON para visualización)
    results = JSONFieldCompatible(
        'Resultados',
        help_text='Datos del reporte en formato JSON'
    )
    
    # Estadísticas
    total_records = models.IntegerField(
        'Total de registros',
        default=0
    )
    
    # Tiempo de generación
    generation_time = models.FloatField(
        'Tiempo de generación (s)',
        null=True,
        blank=True
    )
    
    # Error (si falló)
    error_message = models.TextField(
        'Mensaje de error',
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        'Fecha de creación',
        default=timezone.now,
        db_index=True
    )
    
    completed_at = models.DateTimeField(
        'Fecha de completado',
        null=True,
        blank=True
    )
    
    # Expiración
    expires_at = models.DateTimeField(
        'Expira el',
        null=True,
        blank=True,
        help_text='Fecha en que se elimina automáticamente'
    )
    
    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status', '-created_at']),
            models.Index(fields=['generated_by', '-created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d/%m/%Y')}"
    
    def is_expired(self):
        """Verifica si el reporte ha expirado."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class ScheduledReport(models.Model):
    """
    Reporte programado para generación automática.
    """
    
    FREQUENCY_CHOICES = [
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
    ]
    
    # Plantilla a ejecutar
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name='scheduled_reports',
        verbose_name='Plantilla'
    )
    
    # Organización
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='scheduled_reports',
        verbose_name='Organización'
    )
    
    # Nombre
    name = models.CharField(
        'Nombre',
        max_length=200
    )
    
    # Descripción
    description = models.TextField(
        'Descripción',
        blank=True
    )
    
    # Frecuencia
    frequency = models.CharField(
        'Frecuencia',
        max_length=20,
        choices=FREQUENCY_CHOICES
    )
    
    # Día de ejecución (para semanal/mensual)
    day_of_week = models.IntegerField(
        'Día de la semana',
        null=True,
        blank=True,
        help_text='0=Lunes, 6=Domingo'
    )
    
    day_of_month = models.IntegerField(
        'Día del mes',
        null=True,
        blank=True,
        help_text='1-31'
    )
    
    # Hora de ejecución
    time = models.TimeField(
        'Hora',
        default='09:00:00'
    )
    
    # Parámetros
    parameters = JSONFieldCompatible(
        'Parámetros',
        help_text='Parámetros para la generación'
    )
    
    # Formato de salida
    output_format = models.CharField(
        'Formato',
        max_length=20,
        choices=Report.FORMAT_CHOICES,
        default='pdf'
    )
    
    # Destinatarios (emails)
    recipients = JSONFieldCompatible(
        'Destinatarios',
        help_text='Lista de emails para enviar el reporte'
    )
    
    # Estado
    is_active = models.BooleanField(
        'Activo',
        default=True
    )
    
    # Última ejecución
    last_run_at = models.DateTimeField(
        'Última ejecución',
        null=True,
        blank=True
    )
    
    last_run_status = models.CharField(
        'Estado última ejecución',
        max_length=20,
        blank=True
    )
    
    # Próxima ejecución
    next_run_at = models.DateTimeField(
        'Próxima ejecución',
        null=True,
        blank=True
    )
    
    # Creador
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_scheduled_reports',
        verbose_name='Creado por'
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
        verbose_name = 'Reporte programado'
        verbose_name_plural = 'Reportes programados'
        ordering = ['next_run_at']
        indexes = [
            models.Index(fields=['is_active', 'next_run_at']),
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"
    
    def calculate_next_run(self):
        """Calcula la próxima fecha de ejecución."""
        from datetime import timedelta, datetime
        
        now = timezone.now()
        
        if self.frequency == 'daily':
            next_run = now + timedelta(days=1)
        elif self.frequency == 'weekly':
            next_run = now + timedelta(days=7)
        elif self.frequency == 'monthly':
            next_run = now + timedelta(days=30)
        elif self.frequency == 'quarterly':
            next_run = now + timedelta(days=90)
        elif self.frequency == 'yearly':
            next_run = now + timedelta(days=365)
        else:
            next_run = now + timedelta(days=1)
        
        # Ajustar hora
        next_run = next_run.replace(
            hour=self.time.hour,
            minute=self.time.minute,
            second=0,
            microsecond=0
        )
        
        self.next_run_at = next_run
        self.save()
        
        return next_run


class ReportShare(models.Model):
    """
    Compartir reporte con otros usuarios.
    """
    
    # Reporte compartido
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='shares',
        verbose_name='Reporte'
    )
    
    # Compartido por
    shared_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports_shared',
        verbose_name='Compartido por'
    )
    
    # Compartido con
    shared_with = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports_received',
        verbose_name='Compartido con',
        null=True,
        blank=True
    )
    
    # O compartido con email externo
    shared_with_email = models.EmailField(
        'Email destinatario',
        blank=True
    )
    
    # Mensaje
    message = models.TextField(
        'Mensaje',
        blank=True
    )
    
    # Permisos
    can_download = models.BooleanField(
        'Puede descargar',
        default=True
    )
    
    # Expiración
    expires_at = models.DateTimeField(
        'Expira el',
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        'Fecha de creación',
        default=timezone.now
    )
    
    viewed_at = models.DateTimeField(
        'Visto el',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Compartir reporte'
        verbose_name_plural = 'Reportes compartidos'
        ordering = ['-created_at']
    
    def __str__(self):
        recipient = self.shared_with.email if self.shared_with else self.shared_with_email
        return f"{self.report.name} → {recipient}"
    
    def is_expired(self):
        """Verifica si el compartido ha expirado."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
