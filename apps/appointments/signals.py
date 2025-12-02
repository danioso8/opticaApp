from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)


def notify_new_appointment(appointment):
    """
    Envía notificación de nueva cita a todos los clientes conectados
    Y envía notificación al paciente (WhatsApp/Email según entorno)
    """
    # Notificación WebSocket
    channel_layer = get_channel_layer()
    
    appointment_data = {
        'id': appointment.id,
        'full_name': appointment.full_name,
        'phone_number': appointment.phone_number,
        'appointment_date': str(appointment.appointment_date),
        'appointment_time': str(appointment.appointment_time),
        'status': appointment.status,
    }
    
    async_to_sync(channel_layer.group_send)(
        'appointments',
        {
            'type': 'new_appointment',
            'appointment': appointment_data,
            'message': f'Nueva cita agendada: {appointment.full_name}'
        }
    )
    
    # Envío de notificación automático según configuración de la organización
    try:
        from apps.appointments.models_notifications import NotificationSettings
        from apps.appointments.notifications import get_notifier
        
        # Obtener configuración de notificaciones
        notification_settings = NotificationSettings.get_settings(appointment.organization)
        
        # Verificar si las notificaciones de confirmación están habilitadas
        if notification_settings and notification_settings.send_confirmation:
            notifier = get_notifier(appointment.organization)
            
            # Enviar notificación según el método activo
            if notification_settings.get_active_method() in ['twilio', 'local_whatsapp']:
                notifier.send_appointment_confirmation(appointment)
            elif notification_settings.get_active_method() == 'email' and appointment.email:
                notifier.send_appointment_confirmation(appointment)
            
            logger.info(f"Notificación de confirmación enviada para cita #{appointment.id}")
        else:
            logger.info(f"Notificaciones de confirmación deshabilitadas para cita #{appointment.id}")
    except Exception as e:
        logger.error(f"Error al enviar notificación: {e}")


def notify_appointment_updated(appointment):
    """
    Envía notificación de cita actualizada
    """
    channel_layer = get_channel_layer()
    
    appointment_data = {
        'id': appointment.id,
        'full_name': appointment.full_name,
        'status': appointment.status,
        'status_display': appointment.get_status_display(),
    }
    
    async_to_sync(channel_layer.group_send)(
        'appointments',
        {
            'type': 'appointment_updated',
            'appointment': appointment_data,
            'message': f'Cita actualizada: {appointment.full_name} - {appointment.get_status_display()}'
        }
    )


def notify_system_toggled(is_open):
    """
    Envía notificación de cambio en estado del sistema
    """
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        'appointments',
        {
            'type': 'system_toggled',
            'is_open': is_open,
            'message': f'Sistema {"abierto" if is_open else "cerrado"}'
        }
    )
