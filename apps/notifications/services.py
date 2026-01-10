"""
Servicio para gestión de notificaciones
Centraliza la lógica de creación y envío de notificaciones
"""
from django.contrib.auth.models import User
from django.utils import timezone
from apps.notifications.models import (
    Notification, NotificationChannel, NotificationPreference,
    NotificationTemplate, NotificationBatch
)


class NotificationService:
    """Servicio centralizado para gestión de notificaciones"""
    
    def __init__(self, organization):
        self.organization = organization
    
    def send_notification(
        self,
        user,
        title,
        message,
        notification_type='info',
        priority='normal',
        channels=None,
        action_url='',
        action_label='',
        metadata=None,
        created_by=None,
        expires_at=None
    ):
        """
        Envía una notificación a un usuario por los canales especificados
        
        Args:
            user: Usuario destinatario
            title: Título de la notificación
            message: Mensaje de la notificación
            notification_type: Tipo (info, success, warning, error, reminder)
            priority: Prioridad (low, normal, high, urgent)
            channels: Lista de canales ['system', 'email', 'whatsapp']
                      Si es None, usa los canales habilitados en preferencias
            action_url: URL de acción (opcional)
            action_label: Etiqueta del botón (opcional)
            metadata: Dict con datos adicionales
            created_by: Usuario que crea la notificación
            expires_at: Fecha de expiración
        
        Returns:
            Notification object
        """
        # Crear notificación en sistema
        notification = Notification.objects.create(
            organization=self.organization,
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            action_url=action_url,
            action_label=action_label,
            metadata=metadata or {},
            created_by=created_by,
            expires_at=expires_at
        )
        
        # Determinar canales a usar
        if channels is None:
            channels = self._get_user_enabled_channels(user, notification_type)
        
        # Siempre incluir 'system' si no está
        if 'system' not in channels:
            channels.insert(0, 'system')
        
        # Crear canales de envío
        for channel in channels:
            recipient = self._get_recipient_for_channel(user, channel)
            if recipient:
                channel_obj = NotificationChannel.objects.create(
                    organization=self.organization,
                    notification=notification,
                    channel=channel,
                    recipient=recipient
                )
                
                # Enviar por el canal
                self._send_via_channel(channel_obj)
        
        return notification
    
    def send_from_template(
        self,
        user,
        template_code,
        variables=None,
        channels=None,
        created_by=None
    ):
        """
        Envía una notificación usando una plantilla
        
        Args:
            user: Usuario destinatario
            template_code: Código de la plantilla
            variables: Dict con variables para la plantilla
            channels: Canales a usar (None = canales por defecto)
            created_by: Usuario que envía
        
        Returns:
            Notification object
        """
        try:
            template = NotificationTemplate.objects.get(
                organization=self.organization,
                code=template_code,
                is_active=True
            )
        except NotificationTemplate.DoesNotExist:
            raise ValueError(f"Plantilla '{template_code}' no encontrada")
        
        # Renderizar plantilla
        rendered = template.render(variables or {})
        
        # Usar canales de la plantilla si no se especifican
        if channels is None:
            channels = template.default_channels if isinstance(template.default_channels, list) else ['system']
        
        # Enviar notificación
        return self.send_notification(
            user=user,
            title=rendered['title'],
            message=rendered['message'],
            notification_type=rendered['type'],
            channels=channels,
            created_by=created_by
        )
    
    def send_bulk(
        self,
        users,
        title,
        message,
        notification_type='info',
        channels=None,
        created_by=None,
        batch_name='Envío Masivo'
    ):
        """
        Envía notificaciones masivas a múltiples usuarios
        
        Args:
            users: Lista o QuerySet de usuarios
            title, message, notification_type, channels: Igual que send_notification
            created_by: Usuario que envía
            batch_name: Nombre del lote
        
        Returns:
            NotificationBatch object
        """
        # Crear lote
        batch = NotificationBatch.objects.create(
            organization=self.organization,
            name=batch_name,
            status='sending',
            total_recipients=len(users),
            created_by=created_by,
            started_at=timezone.now()
        )
        
        sent_count = 0
        failed_count = 0
        
        # Enviar a cada usuario
        for user in users:
            try:
                self.send_notification(
                    user=user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    channels=channels,
                    created_by=created_by
                )
                sent_count += 1
            except Exception as e:
                failed_count += 1
                # Log error (opcional)
                print(f"Error enviando a {user.username}: {e}")
        
        # Actualizar lote
        batch.sent_count = sent_count
        batch.failed_count = failed_count
        batch.status = 'completed'
        batch.completed_at = timezone.now()
        batch.save()
        
        return batch
    
    def _get_user_enabled_channels(self, user, notification_type):
        """Obtiene los canales habilitados para el usuario y tipo"""
        try:
            pref = NotificationPreference.objects.get(
                organization=self.organization,
                user=user,
                notification_type=notification_type,
                is_enabled=True
            )
            channels = pref.enabled_channels if isinstance(pref.enabled_channels, list) else []
            return channels
        except NotificationPreference.DoesNotExist:
            # Por defecto: solo sistema
            return ['system']
    
    def _get_recipient_for_channel(self, user, channel):
        """Obtiene el destinatario según el canal"""
        if channel == 'system':
            return user.username
        elif channel == 'email':
            return user.email
        elif channel == 'whatsapp':
            # Obtener número de WhatsApp del perfil
            return getattr(user, 'phone_number', '')
        elif channel == 'sms':
            return getattr(user, 'phone_number', '')
        return ''
    
    def _send_via_channel(self, channel_obj):
        """Envía la notificación por el canal específico"""
        channel = channel_obj.channel
        
        if channel == 'system':
            # Sistema: ya está guardado en BD
            channel_obj.status = 'sent'
            channel_obj.sent_at = timezone.now()
            channel_obj.save()
        
        elif channel == 'email':
            # Email: usar servicio de email
            try:
                from apps.notifications.email_service import send_email_notification
                send_email_notification(channel_obj)
                channel_obj.status = 'sent'
                channel_obj.sent_at = timezone.now()
            except Exception as e:
                channel_obj.status = 'failed'
                channel_obj.error_message = str(e)
            channel_obj.save()
        
        elif channel == 'whatsapp':
            # WhatsApp: usar servicio de WhatsApp
            try:
                from apps.notifications.whatsapp_service import send_whatsapp_notification
                send_whatsapp_notification(channel_obj)
                channel_obj.status = 'sent'
                channel_obj.sent_at = timezone.now()
            except Exception as e:
                channel_obj.status = 'failed'
                channel_obj.error_message = str(e)
            channel_obj.save()
        
        # Otros canales...
    
    def mark_all_as_read(self, user):
        """Marca todas las notificaciones del usuario como leídas"""
        count = Notification.objects.filter(
            organization=self.organization,
            user=user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        return count
    
    def get_unread_count(self, user):
        """Obtiene el contador de notificaciones no leídas"""
        return Notification.objects.filter(
            organization=self.organization,
            user=user,
            is_read=False
        ).count()
    
    def get_recent_notifications(self, user, limit=10):
        """Obtiene las notificaciones recientes del usuario"""
        return Notification.objects.filter(
            organization=self.organization,
            user=user
        ).order_by('-created_at')[:limit]
    
    def delete_old_notifications(self, days=30):
        """Elimina notificaciones antiguas leídas"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        count = Notification.objects.filter(
            organization=self.organization,
            is_read=True,
            read_at__lt=cutoff_date
        ).delete()[0]
        return count


def create_default_preferences(user, organization):
    """
    Crea preferencias por defecto para un nuevo usuario
    """
    default_types = [
        ('appointment_reminder', ['system', 'email', 'whatsapp']),
        ('payment_received', ['system', 'email']),
        ('invoice_created', ['system', 'email']),
        ('low_stock', ['system', 'email']),
        ('new_message', ['system']),
        ('system_update', ['system']),
    ]
    
    for notif_type, channels in default_types:
        NotificationPreference.objects.get_or_create(
            organization=organization,
            user=user,
            notification_type=notif_type,
            defaults={
                'enabled_channels': channels,
                'is_enabled': True
            }
        )


def create_default_templates(organization):
    """
    Crea plantillas de notificaciones por defecto
    """
    templates = [
        {
            'code': 'appointment_reminder',
            'name': 'Recordatorio de Cita',
            'title_template': 'Recordatorio: Cita programada',
            'message_template': 'Tienes una cita programada para el {date} a las {time} con {doctor}.',
            'default_type': 'reminder',
            'default_channels': ['system', 'email', 'whatsapp'],
            'expected_variables': ['date', 'time', 'doctor']
        },
        {
            'code': 'payment_received',
            'name': 'Pago Recibido',
            'title_template': 'Pago recibido',
            'message_template': 'Se ha registrado un pago de {amount} por {concept}. Gracias.',
            'default_type': 'success',
            'default_channels': ['system', 'email'],
            'expected_variables': ['amount', 'concept']
        },
        {
            'code': 'low_stock',
            'name': 'Stock Bajo',
            'title_template': 'Alerta: Stock bajo',
            'message_template': 'El producto {product} tiene stock bajo ({quantity} unidades). Considera reabastecer.',
            'default_type': 'warning',
            'default_channels': ['system', 'email'],
            'expected_variables': ['product', 'quantity']
        },
    ]
    
    for template_data in templates:
        NotificationTemplate.objects.get_or_create(
            organization=organization,
            code=template_data['code'],
            defaults=template_data
        )
