"""
Sistema Unificado de Notificaciones
Detecta automáticamente el entorno y usa el método apropiado:
- Local: WhatsApp (Baileys - Gratis)
- Producción: Email (SMTP - Gratis)
"""
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_notifier(organization=None):
    """
    Obtiene el notificador apropiado según la configuración de la organización
    
    Returns:
        Notificador (Twilio, WhatsApp local o Email)
    """
    from apps.appointments.models_notifications import NotificationSettings
    
    # Obtener configuración de la organización
    notification_settings = NotificationSettings.get_settings(organization)
    
    if not notification_settings:
        # Fallback al comportamiento anterior
        is_production = getattr(settings, 'DEBUG', True) == False
        use_email = getattr(settings, 'USE_EMAIL_NOTIFICATIONS', is_production)
        
        if use_email:
            logger.info("Usando notificaciones por Email (Fallback)")
            from apps.appointments.email_notifier import email_notifier
            return email_notifier
        else:
            logger.info("Usando notificaciones por WhatsApp Local (Fallback)")
            try:
                from apps.appointments.whatsapp_local import whatsapp_notifier
                return whatsapp_notifier
            except ImportError:
                from apps.appointments.email_notifier import email_notifier
                return email_notifier
    
    # Usar configuración de la base de datos
    active_method = notification_settings.get_active_method()
    
    if active_method == 'twilio':
        logger.info("Usando notificaciones por Twilio WhatsApp")
        from apps.appointments.whatsapp import WhatsAppNotifier
        # Crear instancia con credenciales de la BD
        notifier = WhatsAppNotifier()
        notifier.account_sid = notification_settings.twilio_account_sid
        notifier.auth_token = notification_settings.twilio_auth_token
        notifier.whatsapp_from = notification_settings.twilio_whatsapp_from
        from twilio.rest import Client
        notifier.client = Client(notifier.account_sid, notifier.auth_token)
        notifier.enabled = True
        return notifier
    elif active_method == 'local_whatsapp':
        logger.info("Usando notificaciones por WhatsApp Local")
        try:
            from apps.appointments.whatsapp_local import whatsapp_notifier
            return whatsapp_notifier
        except ImportError:
            logger.warning("WhatsApp local no disponible, usando Email")
            from apps.appointments.email_notifier import email_notifier
            return email_notifier
    elif active_method == 'email':
        logger.info("Usando notificaciones por Email")
        from apps.appointments.email_notifier import email_notifier
        return email_notifier
    else:
        logger.warning("Ningún método de notificación configurado, usando Email por defecto")
        from apps.appointments.email_notifier import email_notifier
        return email_notifier


# Instancia global del notificador
notifier = get_notifier()


def notify_new_appointment(appointment):
    """
    Envía notificación de nueva cita
    Usa WhatsApp en local, Email en producción
    """
    try:
        return notifier.send_appointment_confirmation(appointment)
    except Exception as e:
        logger.error(f"Error al enviar notificación de nueva cita: {e}")
        return False


def notify_appointment_reminder(appointment):
    """
    Envía recordatorio de cita (1 día antes)
    Usa WhatsApp en local, Email en producción
    """
    try:
        return notifier.send_appointment_reminder(appointment)
    except Exception as e:
        logger.error(f"Error al enviar recordatorio: {e}")
        return False


def notify_appointment_cancelled(appointment):
    """
    Notifica que una cita fue cancelada
    Usa WhatsApp en local, Email en producción
    """
    try:
        return notifier.send_appointment_cancelled(appointment)
    except Exception as e:
        logger.error(f"Error al enviar notificación de cancelación: {e}")
        return False


def notify_appointment_rescheduled(appointment, old_date, old_time):
    """
    Notifica que una cita fue reagendada
    Usa WhatsApp en local, Email en producción
    
    Args:
        appointment: Objeto Appointment con los nuevos datos
        old_date: Fecha anterior de la cita
        old_time: Hora anterior de la cita
    """
    try:
        # Obtener el notificador apropiado
        notifier_instance = get_notifier(appointment.organization)
        
        # Formatear fechas y horas
        old_date_str = old_date.strftime('%d/%m/%Y')
        old_time_str = old_time.strftime('%H:%M')
        new_date_str = appointment.appointment_date.strftime('%d/%m/%Y')
        new_time_str = appointment.appointment_time.strftime('%H:%M')
        
        # Preparar mensaje
        message = f"""
📅 CITA REAGENDADA - {appointment.organization.name if appointment.organization else 'OCEANO OPTICO'}

Hola {appointment.full_name},

Su cita ha sido REAGENDADA:

❌ Cita Anterior:
   📆 {old_date_str}
   🕒 {old_time_str}

✅ Nueva Cita:
   📆 {new_date_str}
   🕒 {new_time_str}

Por favor, confirme su asistencia en el nuevo horario.

Si tiene alguna duda, contáctenos.
        """.strip()
        
        # Intentar enviar por WhatsApp o Email según configuración
        if hasattr(notifier_instance, 'send_message'):
            # Es un notificador de WhatsApp
            phone = appointment.phone_number
            if not phone.startswith('+'):
                phone = '+' + phone
            return notifier_instance.send_message(phone, message)
        elif hasattr(notifier_instance, 'send_email'):
            # Es un notificador de Email
            if appointment.email:
                subject = 'Cita Reagendada - ' + (appointment.organization.name if appointment.organization else 'OCEANO OPTICO')
                return notifier_instance.send_email(
                    appointment.email,
                    subject,
                    message
                )
        
        logger.warning(f"No se pudo enviar notificación de reagendamiento para cita {appointment.id}")
        return False
        
    except Exception as e:
        logger.error(f"Error al enviar notificación de reagendamiento: {e}")
        return False


def send_test_notification(phone_or_email, method='auto'):
    """
    Envía una notificación de prueba
    
    Args:
        phone_or_email: Teléfono o email del destinatario
        method: 'whatsapp', 'email' o 'auto'
    
    Returns:
        dict: Resultado del envío
    """
    if method == 'auto':
        method = 'email' if '@' in phone_or_email else 'whatsapp'
    
    try:
        if method == 'whatsapp':
            from apps.appointments.whatsapp_local import whatsapp_notifier
            message = """
👓 OCEANO OPTICO - PRUEBA

¡Hola! 👋

Este es un mensaje de prueba del sistema de notificaciones.

Si recibes este mensaje, significa que el bot está funcionando correctamente. ✅

🔧 Sistema de citas automatizado
            """.strip()
            success = whatsapp_notifier.send_message(phone_or_email, message)
            return {
                'success': success,
                'method': 'whatsapp',
                'message': 'Mensaje enviado por WhatsApp' if success else 'Error al enviar por WhatsApp'
            }
        
        elif method == 'email':
            from django.core.mail import send_mail
            subject = 'Prueba de Notificaciones - OCEANO OPTICO'
            message = """
Hola,

Este es un correo de prueba del sistema de notificaciones de OCEANO OPTICO.

Si recibes este mensaje, significa que el sistema de email está funcionando correctamente. ✅

--
OCEANO OPTICO
Sistema de Citas Automatizado
            """.strip()
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [phone_or_email],
                fail_silently=False,
            )
            return {
                'success': True,
                'method': 'email',
                'message': 'Email enviado correctamente'
            }
    
    except Exception as e:
        logger.error(f"Error en send_test_notification: {e}")
        return {
            'success': False,
            'method': method,
            'message': str(e)
        }
