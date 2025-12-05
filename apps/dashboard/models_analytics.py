"""
Modelos para Analytics y Métricas del Dashboard
"""
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from apps.organizations.base_models import TenantModel


class DashboardMetric(TenantModel):
    """Métricas diarias del dashboard"""
    
    METRIC_TYPES = [
        ('revenue', 'Ingresos'),
        ('appointments', 'Citas'),
        ('patients', 'Pacientes'),
        ('sales', 'Ventas'),
        ('conversion', 'Conversión'),
    ]
    
    date = models.DateField(verbose_name='Fecha', db_index=True)
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES, verbose_name='Tipo de Métrica')
    
    # Valores
    value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Valor', default=0)
    count = models.IntegerField(verbose_name='Cantidad', default=0)
    
    # Comparativas
    previous_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Valor Anterior', null=True, blank=True)
    percentage_change = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='% Cambio', null=True, blank=True)
    
    # Metadata (usando TextField para compatibilidad SQLite)
    details = models.TextField(verbose_name='Detalles JSON', blank=True, default='{}')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Métrica del Dashboard'
        verbose_name_plural = 'Métricas del Dashboard'
        ordering = ['-date', 'metric_type']
        unique_together = ['organization', 'date', 'metric_type']
        indexes = [
            models.Index(fields=['organization', 'date', 'metric_type']),
            models.Index(fields=['organization', 'metric_type', '-date']),
        ]
    
    def __str__(self):
        return f"{self.get_metric_type_display()} - {self.date} - {self.organization.name}"


class RealtimeMetric(models.Model):
    """Métricas en tiempo real (últimas 24 horas)"""
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='realtime_metrics'
    )
    
    # Métricas actuales
    active_users = models.IntegerField(default=0, verbose_name='Usuarios Activos')
    appointments_today = models.IntegerField(default=0, verbose_name='Citas Hoy')
    revenue_today = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Ingresos Hoy')
    pending_appointments = models.IntegerField(default=0, verbose_name='Citas Pendientes')
    
    # Tendencias
    appointments_trend = models.CharField(max_length=10, default='stable', verbose_name='Tendencia Citas')  # up, down, stable
    revenue_trend = models.CharField(max_length=10, default='stable', verbose_name='Tendencia Ingresos')
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Métrica en Tiempo Real'
        verbose_name_plural = 'Métricas en Tiempo Real'
    
    def __str__(self):
        return f"Métricas RT - {self.organization.name}"


class KPITarget(TenantModel):
    """Objetivos/Metas de KPIs"""
    
    name = models.CharField(max_length=200, verbose_name='Nombre del KPI')
    metric_type = models.CharField(max_length=50, verbose_name='Tipo de Métrica')
    
    # Objetivo
    target_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Meta')
    current_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Valor Actual', default=0)
    
    # Período
    period_start = models.DateField(verbose_name='Inicio del Período')
    period_end = models.DateField(verbose_name='Fin del Período')
    
    # Estado
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    achieved = models.BooleanField(default=False, verbose_name='Alcanzado')
    achievement_date = models.DateField(null=True, blank=True, verbose_name='Fecha de Logro')
    
    # Metadata
    description = models.TextField(blank=True, verbose_name='Descripción')
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Objetivo KPI'
        verbose_name_plural = 'Objetivos KPI'
        ordering = ['-period_start']
    
    def __str__(self):
        return f"{self.name} - {self.organization.name}"
    
    @property
    def progress_percentage(self):
        """Calcula el porcentaje de progreso"""
        if self.target_value > 0:
            return min(100, (float(self.current_value) / float(self.target_value)) * 100)
        return 0


class HeatmapData(TenantModel):
    """Datos para heatmaps de horarios populares"""
    
    DAYS_OF_WEEK = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, verbose_name='Día de la Semana')
    hour = models.IntegerField(verbose_name='Hora (0-23)')
    
    # Contadores
    appointment_count = models.IntegerField(default=0, verbose_name='Total de Citas')
    revenue_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Ingresos Totales')
    
    # Período de análisis
    period_start = models.DateField(verbose_name='Inicio del Período')
    period_end = models.DateField(verbose_name='Fin del Período')
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Dato de Heatmap'
        verbose_name_plural = 'Datos de Heatmap'
        unique_together = ['organization', 'day_of_week', 'hour', 'period_start', 'period_end']
        indexes = [
            models.Index(fields=['organization', 'period_start', 'period_end']),
        ]
    
    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.hour}:00 - {self.organization.name}"


class CustomerSatisfaction(TenantModel):
    """Encuestas de satisfacción del cliente"""
    
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='satisfaction_surveys'
    )
    
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='satisfaction_survey'
    )
    
    # Ratings (1-5)
    overall_rating = models.IntegerField(verbose_name='Calificación General', default=5)
    service_rating = models.IntegerField(verbose_name='Calificación de Servicio', default=5)
    quality_rating = models.IntegerField(verbose_name='Calificación de Calidad', default=5)
    speed_rating = models.IntegerField(verbose_name='Calificación de Rapidez', default=5)
    
    # NPS (Net Promoter Score)
    nps_score = models.IntegerField(
        verbose_name='Puntuación NPS (0-10)',
        help_text='¿Qué tan probable es que nos recomiende?',
        null=True,
        blank=True
    )
    
    # Feedback
    comments = models.TextField(verbose_name='Comentarios', blank=True)
    
    # Metadata
    survey_date = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Encuesta')
    responded_via = models.CharField(
        max_length=50,
        choices=[
            ('email', 'Email'),
            ('whatsapp', 'WhatsApp'),
            ('sms', 'SMS'),
            ('in_person', 'En Persona'),
            ('web', 'Página Web'),
        ],
        default='web',
        verbose_name='Respondió Vía'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Encuesta de Satisfacción'
        verbose_name_plural = 'Encuestas de Satisfacción'
        ordering = ['-survey_date']
    
    def __str__(self):
        return f"Encuesta - {self.patient.full_name} - {self.survey_date.date()}"
    
    @property
    def average_rating(self):
        """Calcula el promedio de todas las calificaciones"""
        ratings = [
            self.overall_rating,
            self.service_rating,
            self.quality_rating,
            self.speed_rating
        ]
        return sum(ratings) / len(ratings)
    
    @property
    def nps_category(self):
        """Categoriza según NPS: Promotor, Pasivo, Detractor"""
        if self.nps_score is None:
            return None
        if self.nps_score >= 9:
            return 'promoter'
        elif self.nps_score >= 7:
            return 'passive'
        else:
            return 'detractor'
