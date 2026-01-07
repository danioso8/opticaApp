from django.db import models
from apps.organizations.base_models import TenantModel


class NotificationSettings(TenantModel):
    """Configuración de notificaciones por organización"""
    
    # Email
    email_enabled = models.BooleanField(
        default=True,
        verbose_name="Habilitar Email"
    )
    email_from = models.EmailField(
        blank=True,
        verbose_name="Email remitente",
        help_text="Deja vacío para usar el email por defecto del sistema"
    )
    
    # Local WhatsApp Bot (Baileys)
    local_whatsapp_enabled = models.BooleanField(
        default=False,
        verbose_name="Habilitar WhatsApp Local (Baileys)"
    )
    local_whatsapp_url = models.URLField(
        default='http://localhost:3000',
        verbose_name="URL del bot local"
    )
    
    # Notificaciones automáticas
    send_confirmation = models.BooleanField(
        default=True,
        verbose_name="Enviar confirmación al agendar"
    )
    send_reminder = models.BooleanField(
        default=True,
        verbose_name="Enviar recordatorio (1 día antes)"
    )
    send_cancellation = models.BooleanField(
        default=True,
        verbose_name="Enviar notificación de cancelación"
    )
    
    # Configuración de tiempos
    reminder_hours_before = models.IntegerField(
        default=24,
        verbose_name="Horas antes del recordatorio",
        help_text="Cuántas horas antes de la cita enviar recordatorio"
    )
    arrival_minutes_before = models.IntegerField(
        default=10,
        verbose_name="Minutos de anticipación",
        help_text="Cuántos minutos antes debe llegar el paciente"
    )
    
    # Plantillas de mensajes
    confirmation_message_template = models.TextField(
        default='✅ CITA CONFIRMADA - {organization}\n\nHola {patient_name},\n\nTu cita ha sido agendada exitosamente:\n\n📅 Fecha: {date}\n🕒 Hora: {time}\n👤 Doctor: {doctor}\n\nLlega {arrival_minutes} minutos antes de tu cita.\n\nSi necesitas cancelar o reagendar, contáctanos con anticipación.\n\n¡Te esperamos! 👓',
        verbose_name="Plantilla de confirmación",
        help_text="Variables: {organization}, {patient_name}, {date}, {time}, {doctor}, {arrival_minutes}"
    )
    reminder_message_template = models.TextField(
        default='⏰ RECORDATORIO DE CITA - {organization}\n\nHola {patient_name},\n\nTe recordamos tu cita:\n\n📅 Fecha: {date}\n🕒 Hora: {time}\n👤 Doctor: {doctor}\n\nLlega {arrival_minutes} minutos antes de tu cita.\n\nSi no puedes asistir, contáctanos lo antes posible.\n\n¡Nos vemos pronto! 👓',
        verbose_name="Plantilla de recordatorio",
        help_text="Variables: {organization}, {patient_name}, {date}, {time}, {doctor}, {arrival_minutes}"
    )
    cancellation_message_template = models.TextField(
        default='❌ CITA CANCELADA - {organization}\n\nHola {patient_name},\n\nTu cita ha sido cancelada:\n\n📅 Fecha: {date}\n🕒 Hora: {time}\n\nSi deseas reagendar, contáctanos.\n\nGracias por tu comprensión. 👓',
        verbose_name="Plantilla de cancelación",
        help_text="Variables: {organization}, {patient_name}, {date}, {time}"
    )
    rescheduled_message_template = models.TextField(
        default='🔄 CITA REAGENDADA - {organization}\n\nHola {patient_name},\n\nTu cita ha sido reagendada:\n\n📅 Nueva Fecha: {date}\n🕒 Nueva Hora: {time}\n👤 Doctor: {doctor}\n\nLlega {arrival_minutes} minutos antes de tu cita.\n\n¡Te esperamos! 👓',
        verbose_name="Plantilla de reagendamiento",
        help_text="Variables: {organization}, {patient_name}, {date}, {time}, {doctor}, {arrival_minutes}"
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración de Notificaciones"
        verbose_name_plural = "Configuraciones de Notificaciones"
        unique_together = [['organization']]
    
    def __str__(self):
        return f"Notificaciones - {self.organization.name}"
    
    @classmethod
    def get_settings(cls, organization=None):
        """Obtiene o crea la configuración para una organización"""
        if organization:
            settings, created = cls.objects.get_or_create(organization=organization)
            return settings
        return cls.objects.first()
    
    def get_active_method(self):
        """Retorna el método de notificación activo"""
        if self.local_whatsapp_enabled:
            return 'local_whatsapp'
        elif self.email_enabled:
            return 'email'
        return None


class AppointmentNotification(TenantModel):
    """Modelo para rastrear notificaciones de citas nuevas en dashboard"""
    
    appointment = models.OneToOneField(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        related_name='push_notification',
        verbose_name="Cita"
    )
    
    is_notified = models.BooleanField(
        default=False,
        verbose_name="Notificación push enviada"
    )
    
    notified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de notificación"
    )
    
    created_from_landing = models.BooleanField(
        default=False,
        verbose_name="Creada desde landing page"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    class Meta:
        verbose_name = "Notificación Push de Cita"
        verbose_name_plural = "Notificaciones Push de Citas"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'is_notified', 'created_from_landing']),
        ]
    
    def __str__(self):
        return f"Notificación Push - {self.appointment}"
