"""
Sistema de notificaciones por WhatsApp usando Twilio
"""
from django.conf import settings
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)


class WhatsAppNotifier:
    """Clase para enviar notificaciones por WhatsApp"""
    
    def __init__(self):
        """Inicializa el cliente de Twilio"""
        try:
            self.account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
            self.auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
            self.whatsapp_from = getattr(settings, 'TWILIO_WHATSAPP_FROM', None)
            
            if self.account_sid and self.auth_token:
                self.client = Client(self.account_sid, self.auth_token)
                self.enabled = True
            else:
                self.enabled = False
                logger.warning("Twilio no está configurado. Las notificaciones por WhatsApp están deshabilitadas.")
        except Exception as e:
            self.enabled = False
            logger.error(f"Error al inicializar Twilio: {e}")
    
    def format_phone_number(self, phone):
        """
        Formatea el número de teléfono para WhatsApp
        Convierte 3001234567 a whatsapp:+573001234567
        """
        # Limpiar el número
        phone = ''.join(filter(str.isdigit, phone))
        
        # Si no empieza con código de país, agregar +57 (Colombia)
        if not phone.startswith('57'):
            phone = '57' + phone
        
        return f'whatsapp:+{phone}'
    
    def send_appointment_confirmation(self, appointment):
        """
        Envía confirmación de cita agendada
        
        Args:
            appointment: Objeto Appointment
        
        Returns:
            bool: True si se envió exitosamente
        """
        if not self.enabled:
            logger.info(f"WhatsApp deshabilitado. No se enviará notificación para cita #{appointment.id}")
            return False
        
        try:
            # Formatear fecha y hora
            fecha = appointment.appointment_date.strftime('%d/%m/%Y')
            hora = appointment.appointment_time.strftime('%I:%M %p')
            
            # Mensaje de confirmación
            message = f"""
🌊 *OCEANO OPTICO* 👓

¡Hola {appointment.full_name}!

✅ Tu cita ha sido agendada exitosamente:

📅 *Fecha:* {fecha}
🕐 *Hora:* {hora}
📍 *Lugar:* OCEANO OPTICO

💡 *Recomendaciones:*
• Llega 10 minutos antes
• Trae tu documento de identidad
• Si usas lentes, tráelos contigo

❓ *¿Necesitas cancelar o reagendar?*
Llámanos al: {getattr(settings, 'BUSINESS_PHONE', '300 123 4567')}

¡Te esperamos! 😊
            """.strip()
            
            # Enviar mensaje
            to_number = self.format_phone_number(appointment.phone_number)
            
            response = self.client.messages.create(
                from_=self.whatsapp_from,
                body=message,
                to=to_number
            )
            
            logger.info(f"WhatsApp enviado a {appointment.phone_number} - SID: {response.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar WhatsApp a {appointment.phone_number}: {e}")
            return False
    
    def send_appointment_reminder(self, appointment):
        """
        Envía recordatorio de cita (1 día antes)
        
        Args:
            appointment: Objeto Appointment
        
        Returns:
            bool: True si se envió exitosamente
        """
        if not self.enabled:
            return False
        
        try:
            fecha = appointment.appointment_date.strftime('%d/%m/%Y')
            hora = appointment.appointment_time.strftime('%I:%M %p')
            
            message = f"""
🌊 *OCEANO OPTICO* 👓

¡Hola {appointment.full_name}!

🔔 *Recordatorio de Cita*

Mañana tienes una cita agendada:

📅 *Fecha:* {fecha}
🕐 *Hora:* {hora}
📍 *Lugar:* OCEANO OPTICO

Nos vemos mañana 😊

*Si necesitas cancelar, llámanos:*
📞 {getattr(settings, 'BUSINESS_PHONE', '300 123 4567')}
            """.strip()
            
            to_number = self.format_phone_number(appointment.phone_number)
            
            response = self.client.messages.create(
                from_=self.whatsapp_from,
                body=message,
                to=to_number
            )
            
            logger.info(f"Recordatorio WhatsApp enviado a {appointment.phone_number} - SID: {response.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar recordatorio WhatsApp: {e}")
            return False
    
    def send_appointment_cancelled(self, appointment):
        """
        Notifica que una cita fue cancelada
        
        Args:
            appointment: Objeto Appointment
        
        Returns:
            bool: True si se envió exitosamente
        """
        if not self.enabled:
            return False
        
        try:
            fecha = appointment.appointment_date.strftime('%d/%m/%Y')
            hora = appointment.appointment_time.strftime('%I:%M %p')
            
            message = f"""
🌊 *OCEANO OPTICO* 👓

Hola {appointment.full_name},

Tu cita del día *{fecha}* a las *{hora}* ha sido cancelada.

Si deseas reagendar, contáctanos:
📞 {getattr(settings, 'BUSINESS_PHONE', '300 123 4567')}

O agenda en línea:
🌐 {getattr(settings, 'WEBSITE_URL', 'https://oceanooptico.com')}/agendar/

¡Gracias! 😊
            """.strip()
            
            to_number = self.format_phone_number(appointment.phone_number)
            
            response = self.client.messages.create(
                from_=self.whatsapp_from,
                body=message,
                to=to_number
            )
            
            logger.info(f"Notificación de cancelación enviada a {appointment.phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar notificación de cancelación: {e}")
            return False


# Instancia global
whatsapp_notifier = WhatsAppNotifier()


def notify_new_appointment(appointment):
    """
    Función auxiliar para enviar notificación de nueva cita
    """
    return whatsapp_notifier.send_appointment_confirmation(appointment)


def notify_appointment_reminder(appointment):
    """
    Función auxiliar para enviar recordatorio
    """
    return whatsapp_notifier.send_appointment_reminder(appointment)


def notify_appointment_cancelled(appointment):
    """
    Función auxiliar para notificar cancelación
    """
    return whatsapp_notifier.send_appointment_cancelled(appointment)
