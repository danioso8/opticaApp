"""
Modelos para el sistema de promociones y campañas de marketing
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.organizations.models import Organization
from apps.patients.models import Patient
import uuid


class Promotion(models.Model):
    """Modelo para promociones y descuentos"""
    
    CATEGORY_CHOICES = [
        ('frames', 'Monturas'),
        ('lenses', 'Lentes'),
        ('sunglasses', 'Gafas de Sol'),
        ('contacts', 'Lentes de Contacto'),
        ('exam', 'Examen Visual'),
        ('all', 'Todos los Productos'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activa'),
        ('inactive', 'Inactiva'),
        ('expired', 'Expirada'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='promotions')
    code = models.CharField(max_length=50, unique=True, help_text='Código único de promoción (ej: NAVIDAD2026)')
    name = models.CharField(max_length=200, help_text='Nombre descriptivo de la promoción')
    description = models.TextField(help_text='Descripción detallada de la promoción')
    
    # Descuento
    discount_percentage = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text='Porcentaje de descuento (1-100)'
    )
    
    # Categoría
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='all')
    
    # Fechas
    start_date = models.DateField(help_text='Fecha de inicio de la promoción')
    end_date = models.DateField(help_text='Fecha de fin de la promoción')
    
    # Estado
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Uso
    max_uses = models.IntegerField(null=True, blank=True, help_text='Máximo de veces que se puede usar (dejar vacío para ilimitado)')
    current_uses = models.IntegerField(default=0, help_text='Veces que se ha usado')
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='promotions_created')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'
    
    def __str__(self):
        return f"{self.code} - {self.discount_percentage}% OFF en {self.get_category_display()}"
    
    def is_valid(self):
        """Verifica si la promoción está activa y vigente"""
        from django.utils import timezone
        now = timezone.now().date()
        return (
            self.status == 'active' and
            self.start_date <= now <= self.end_date and
            (self.max_uses is None or self.current_uses < self.max_uses)
        )
    
    def get_category_display_emoji(self):
        """Retorna emoji según la categoría"""
        emojis = {
            'frames': '👓',
            'lenses': '🔍',
            'sunglasses': '🕶️',
            'contacts': '👁️',
            'exam': '📋',
            'all': '🎁',
        }
        return emojis.get(self.category, '🎁')


class PromotionCampaign(models.Model):
    """Modelo para campañas de envío de promociones"""
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('scheduled', 'Programada'),
        ('in_progress', 'En Progreso'),
        ('paused', 'Pausada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]
    
    FILTER_CHOICES = [
        ('all', 'Todos los Clientes'),
        ('last_visit_30', 'Última visita hace 30 días'),
        ('last_visit_60', 'Última visita hace 60 días'),
        ('last_visit_90', 'Última visita hace 90 días'),
        ('last_visit_180', 'Última visita hace 6 meses'),
        ('never_visited', 'Nunca han visitado'),
        ('has_phone', 'Solo con teléfono registrado'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='promotion_campaigns')
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='campaigns')
    
    # Configuración de la campaña
    name = models.CharField(max_length=200, help_text='Nombre de la campaña')
    message_template = models.TextField(
        help_text='Plantilla del mensaje. Variables: {name}, {code}, {discount}, {category}, {end_date}'
    )
    
    # Filtros de destinatarios
    recipient_filter = models.CharField(max_length=30, choices=FILTER_CHOICES, default='all')
    
    # Configuración de envío
    daily_limit = models.IntegerField(
        default=20,
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        help_text='Máximo de mensajes por día (recomendado: 20-30)'
    )
    delay_seconds = models.IntegerField(
        default=10,
        validators=[MinValueValidator(5), MaxValueValidator(60)],
        help_text='Segundos de espera entre mensajes (recomendado: 8-15)'
    )
    
    # Horario de envío
    send_hour_start = models.IntegerField(
        default=9,
        validators=[MinValueValidator(0), MaxValueValidator(23)],
        help_text='Hora de inicio de envíos (formato 24h)'
    )
    send_hour_end = models.IntegerField(
        default=19,
        validators=[MinValueValidator(0), MaxValueValidator(23)],
        help_text='Hora de fin de envíos (formato 24h)'
    )
    
    # Estado
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Fechas
    scheduled_date = models.DateField(null=True, blank=True, help_text='Fecha programada de inicio')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Estadísticas
    total_recipients = models.IntegerField(default=0)
    messages_sent = models.IntegerField(default=0)
    messages_failed = models.IntegerField(default=0)
    messages_pending = models.IntegerField(default=0)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Campaña de Promoción'
        verbose_name_plural = 'Campañas de Promoción'
    
    def __str__(self):
        return f"{self.name} - {self.promotion.code}"
    
    def get_recipients(self):
        """Obtiene la lista de pacientes según el filtro configurado"""
        from datetime import timedelta
        from django.utils import timezone
        
        queryset = Patient.objects.filter(organization=self.organization)
        
        # Filtrar solo pacientes con teléfono
        queryset = queryset.exclude(phone_number__isnull=True).exclude(phone_number='')
        
        if self.recipient_filter == 'all':
            return queryset
        elif self.recipient_filter == 'last_visit_30':
            date_limit = timezone.now().date() - timedelta(days=30)
            return queryset.filter(last_appointment_date__gte=date_limit)
        elif self.recipient_filter == 'last_visit_60':
            date_limit = timezone.now().date() - timedelta(days=60)
            return queryset.filter(last_appointment_date__gte=date_limit)
        elif self.recipient_filter == 'last_visit_90':
            date_limit = timezone.now().date() - timedelta(days=90)
            return queryset.filter(last_appointment_date__gte=date_limit)
        elif self.recipient_filter == 'last_visit_180':
            date_limit = timezone.now().date() - timedelta(days=180)
            return queryset.filter(last_appointment_date__gte=date_limit)
        elif self.recipient_filter == 'never_visited':
            return queryset.filter(last_appointment_date__isnull=True)
        elif self.recipient_filter == 'has_phone':
            return queryset
        
        return queryset
    
    def update_stats(self):
        """Actualiza las estadísticas de la campaña"""
        messages = self.messages.all()
        self.total_recipients = messages.count()
        self.messages_sent = messages.filter(status='sent').count()
        self.messages_failed = messages.filter(status='failed').count()
        self.messages_pending = messages.filter(status='pending').count()
        self.save()


class PromotionMessage(models.Model):
    """Modelo para mensajes individuales de una campaña"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('sent', 'Enviado'),
        ('failed', 'Fallido'),
        ('skipped', 'Omitido'),
    ]
    
    campaign = models.ForeignKey(PromotionCampaign, on_delete=models.CASCADE, related_name='messages')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='promotion_messages')
    
    # Mensaje
    message_text = models.TextField(help_text='Texto del mensaje personalizado')
    phone_number = models.CharField(max_length=20)
    
    # Estado
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Intentos
    send_attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    
    # Fechas
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Mensaje de Promoción'
        verbose_name_plural = 'Mensajes de Promoción'
        indexes = [
            models.Index(fields=['campaign', 'status']),
            models.Index(fields=['status', 'scheduled_for']),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.get_status_display()}"
    
    def can_retry(self):
        """Verifica si se puede reintentar el envío"""
        return self.status == 'failed' and self.send_attempts < self.max_attempts


class PromotionUsage(models.Model):
    """Modelo para rastrear el uso de códigos promocionales"""
    
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='usages')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='promotion_usages')
    
    # Detalles del uso
    used_at = models.DateTimeField(auto_now_add=True)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Referencia
    reference = models.CharField(max_length=100, blank=True, help_text='Número de factura o referencia')
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-used_at']
        verbose_name = 'Uso de Promoción'
        verbose_name_plural = 'Usos de Promociones'
    
    def __str__(self):
        return f"{self.promotion.code} - {self.patient.full_name}"
