"""
Modelo para gestionar las conexiones de WhatsApp por organización
Mantiene el estado y metadata de las sesiones persistentes
"""
from django.db import models
from django.utils import timezone
from apps.organizations.models import Organization


class WhatsAppConnection(models.Model):
    """
    Registra y gestiona las conexiones de WhatsApp por organización.
    
    Este modelo complementa los archivos de sesión de Baileys guardados en
    /var/www/whatsapp-server/auth_sessions/{organization_id}/
    
    Propósito:
    - Rastrear qué organizaciones tienen WhatsApp conectado
    - Almacenar el número de teléfono vinculado
    - Registrar cuándo se conectó/desconectó
    - Prevenir pérdidas de sesión innecesarias
    - Facilitar la reconexión automática
    """
    
    STATUS_CHOICES = [
        ('connected', 'Conectado'),
        ('disconnected', 'Desconectado'),
        ('connecting', 'Conectando'),
        ('qr_ready', 'QR Listo para escanear'),
        ('error', 'Error'),
    ]
    
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='whatsapp_connection',
        verbose_name='Organización'
    )
    
    # Información de la conexión
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Número de WhatsApp',
        help_text='Número de teléfono vinculado (formato: 573001234567)'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='disconnected',
        verbose_name='Estado'
    )
    
    # Metadata de la sesión
    session_exists = models.BooleanField(
        default=False,
        verbose_name='Sesión existe',
        help_text='Indica si hay archivos de sesión guardados en el servidor'
    )
    
    last_connected_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última conexión',
        help_text='Última vez que WhatsApp se conectó exitosamente'
    )
    
    last_disconnected_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última desconexión'
    )
    
    disconnection_reason = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Razón de desconexión',
        help_text='Última razón de desconexión (para diagnóstico)'
    )
    
    # Control de reconexión
    reconnect_attempts = models.IntegerField(
        default=0,
        verbose_name='Intentos de reconexión',
        help_text='Contador de intentos de reconexión automática'
    )
    
    last_reconnect_attempt = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Último intento de reconexión'
    )
    
    # Gestión manual
    manually_disconnected = models.BooleanField(
        default=False,
        verbose_name='Desconectado manualmente',
        help_text='True si el usuario cerró sesión intencionalmente. Previene reconexión automática.'
    )
    
    disconnected_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whatsapp_disconnections',
        verbose_name='Desconectado por'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Conexión de WhatsApp'
        verbose_name_plural = 'Conexiones de WhatsApp'
        ordering = ['-last_connected_at']
    
    def __str__(self):
        status_display = self.get_status_display()
        if self.phone_number:
            return f"{self.organization.name} - {self.phone_number} ({status_display})"
        return f"{self.organization.name} ({status_display})"
    
    def mark_connected(self, phone_number):
        """Marcar como conectado exitosamente"""
        self.status = 'connected'
        self.phone_number = phone_number
        self.session_exists = True
        self.last_connected_at = timezone.now()
        self.reconnect_attempts = 0
        self.manually_disconnected = False
        self.disconnected_by = None
        self.save()
    
    def mark_disconnected(self, reason=None, manual=False, user=None):
        """Marcar como desconectado"""
        self.status = 'disconnected'
        self.last_disconnected_at = timezone.now()
        if reason:
            self.disconnection_reason = reason
        if manual:
            self.manually_disconnected = True
            self.disconnected_by = user
            self.session_exists = False  # Sesión se eliminará
        self.save()
    
    def increment_reconnect_attempt(self):
        """Incrementar contador de intentos de reconexión"""
        self.reconnect_attempts += 1
        self.last_reconnect_attempt = timezone.now()
        self.save()
    
    def should_auto_reconnect(self):
        """Determina si se debe intentar reconexión automática"""
        # No reconectar si fue desconexión manual
        if self.manually_disconnected:
            return False
        
        # No reconectar si no hay sesión guardada
        if not self.session_exists:
            return False
        
        # Limitar a 3 intentos de reconexión
        if self.reconnect_attempts >= 3:
            return False
        
        return True
    
    @classmethod
    def sync_from_server(cls, organization_id, server_status):
        """
        Sincroniza el estado desde el servidor WhatsApp
        
        Args:
            organization_id: ID de la organización
            server_status: dict con status del servidor WhatsApp
                {
                    'status': 'connected',
                    'phone_number': '573001234567',
                    'connected': True
                }
        """
        from apps.organizations.models import Organization
        
        org = Organization.objects.get(id=organization_id)
        connection, created = cls.objects.get_or_create(organization=org)
        
        if server_status.get('connected'):
            connection.mark_connected(server_status.get('phone_number'))
        else:
            status = server_status.get('status', 'disconnected')
            connection.status = status
            connection.save()
        
        return connection
    
    @classmethod
    def get_active_connections(cls):
        """Obtiene todas las conexiones activas"""
        return cls.objects.filter(status='connected')
    
    @classmethod
    def get_or_create_for_org(cls, organization):
        """Obtiene o crea la conexión para una organización"""
        connection, created = cls.objects.get_or_create(
            organization=organization,
            defaults={'status': 'disconnected'}
        )
        return connection
