from django.db import models
from apps.organizations.base_models import TenantModel


class NotificationSettings(TenantModel):
    """Configuración de notificaciones por organización"""
    
    # WhatsApp (Twilio)
    twilio_enabled = models.BooleanField(
        default=False,
        verbose_name="Habilitar WhatsApp (Twilio)"
    )
    twilio_account_sid = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Twilio Account SID"
    )
    twilio_auth_token = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Twilio Auth Token"
    )
    twilio_whatsapp_from = models.CharField(
        max_length=50,
        default='whatsapp:+14155238886',
        verbose_name="Número WhatsApp (Twilio)"
    )
    
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
    
    # Local WhatsApp Bot
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
        if self.twilio_enabled and self.twilio_account_sid and self.twilio_auth_token:
            return 'twilio'
        elif self.local_whatsapp_enabled:
            return 'local_whatsapp'
        elif self.email_enabled:
            return 'email'
        return None
