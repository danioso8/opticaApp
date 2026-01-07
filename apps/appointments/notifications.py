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
    
    if active_method in ['whatsapp', 'twilio']:
        logger.info("Usando notificaciones por Twilio WhatsApp")
        from apps.appointments.whatsapp import WhatsAppNotifier
        # Usar configuración centralizada de settings
        notifier = WhatsAppNotifier(organization)
        return notifier
    elif active_method == 'local_whatsapp':
        logger.info("Usando notificaciones por WhatsApp Baileys (Local)")
        try:
            from apps.appointments.whatsapp_baileys_notifier import WhatsAppBaileysNotifier
            return WhatsAppBaileysNotifier(organization)
        except ImportError as e:
            logger.warning(f"WhatsApp Baileys no disponible: {e}, usando Email")
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
# notifier = get_notifier()  # Comentado para evitar import circular


def notify_new_appointment(appointment):
    """
    Envía notificación de nueva cita por TODOS los métodos habilitados
    (WhatsApp Y Email si ambos están activos)
    """
    from apps.appointments.models_notifications import NotificationSettings
    
    settings = NotificationSettings.get_settings(appointment.organization)
    if not settings:
        logger.warning("No hay configuración de notificaciones")
        return False
    
    results = []
    
    # Enviar por WhatsApp Local si está habilitado
    if settings.local_whatsapp_enabled:
        try:
            from apps.appointments.whatsapp_baileys_notifier import WhatsAppBaileysNotifier
            notifier = WhatsAppBaileysNotifier(appointment.organization)
            success = notifier.send_appointment_confirmation(appointment)
            results.append(('WhatsApp', success))
            logger.info(f"WhatsApp notificación: {'✓' if success else '✗'}")
        except Exception as e:
            logger.error(f"Error enviando WhatsApp: {e}")
            results.append(('WhatsApp', False))
    
    # Enviar por Email si está habilitado
    if settings.email_enabled and appointment.email:
        try:
            from apps.appointments.email_notifier import email_notifier
            success = email_notifier.send_appointment_confirmation(appointment)
            results.append(('Email', success))
            logger.info(f"Email notificación: {'✓' if success else '✗'}")
        except Exception as e:
            logger.error(f"Error enviando Email: {e}")
            results.append(('Email', False))
    
    # Retornar True si al menos uno fue exitoso
    return any(success for _, success in results) if results else False


def notify_appointment_reminder(appointment):
    """
    Envía recordatorio de cita por TODOS los métodos habilitados
    """
    from apps.appointments.models_notifications import NotificationSettings
    
    settings = NotificationSettings.get_settings(appointment.organization)
    if not settings:
        return False
    
    results = []
    
    # WhatsApp Local
    if settings.local_whatsapp_enabled:
        try:
            from apps.appointments.whatsapp_baileys_notifier import WhatsAppBaileysNotifier
            notifier = WhatsAppBaileysNotifier(appointment.organization)
            success = notifier.send_appointment_reminder(appointment)
            results.append(('WhatsApp', success))
        except Exception as e:
            logger.error(f"Error enviando recordatorio WhatsApp: {e}")
            results.append(('WhatsApp', False))
    
    # Email
    if settings.email_enabled and appointment.email:
        try:
            from apps.appointments.email_notifier import email_notifier
            success = email_notifier.send_appointment_reminder(appointment)
            results.append(('Email', success))
        except Exception as e:
            logger.error(f"Error enviando recordatorio Email: {e}")
            results.append(('Email', False))
    
    return any(success for _, success in results) if results else False


def notify_appointment_cancelled(appointment):
    """
    Notifica cancelación de cita por TODOS los métodos habilitados
    """
    from apps.appointments.models_notifications import NotificationSettings
    
    settings = NotificationSettings.get_settings(appointment.organization)
    if not settings:
        return False
    
    results = []
    
    # WhatsApp Local
    if settings.local_whatsapp_enabled:
        try:
            from apps.appointments.whatsapp_baileys_notifier import WhatsAppBaileysNotifier
            notifier = WhatsAppBaileysNotifier(appointment.organization)
            success = notifier.send_appointment_cancelled(appointment)
            results.append(('WhatsApp', success))
        except Exception as e:
            logger.error(f"Error enviando cancelación WhatsApp: {e}")
            results.append(('WhatsApp', False))
    
    # Email
    if settings.email_enabled and appointment.email:
        try:
            from apps.appointments.email_notifier import email_notifier
            success = email_notifier.send_appointment_cancelled(appointment)
            results.append(('Email', success))
        except Exception as e:
            logger.error(f"Error enviando cancelación Email: {e}")
            results.append(('Email', False))
    
    return any(success for _, success in results) if results else False


def notify_appointment_rescheduled(appointment, old_date, old_time):
    """
    Notifica reagendamiento de cita por TODOS los métodos habilitados
    
    Args:
        appointment: Objeto Appointment con los nuevos datos
        old_date: Fecha anterior de la cita
        old_time: Hora anterior de la cita
    """
    from apps.appointments.models_notifications import NotificationSettings
    
    settings = NotificationSettings.get_settings(appointment.organization)
    if not settings:
        return False
    
    results = []
    
    # WhatsApp Local
    if settings.local_whatsapp_enabled:
        try:
            from apps.appointments.whatsapp_baileys_notifier import WhatsAppBaileysNotifier
            notifier = WhatsAppBaileysNotifier(appointment.organization)
            success = notifier.send_appointment_rescheduled(appointment, old_date, old_time)
            results.append(('WhatsApp', success))
        except Exception as e:
            logger.error(f"Error enviando reagendamiento WhatsApp: {e}")
            results.append(('WhatsApp', False))
    
    # Email
    if settings.email_enabled and appointment.email:
        try:
            from apps.appointments.email_notifier import email_notifier
            success = email_notifier.send_appointment_rescheduled(appointment, old_date, old_time)
            results.append(('Email', success))
        except Exception as e:
            logger.error(f"Error enviando reagendamiento Email: {e}")
            results.append(('Email', False))
    
    return any(success for _, success in results) if results else False


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
