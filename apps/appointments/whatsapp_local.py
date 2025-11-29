"""
Sistema de notificaciones WhatsApp usando API REST local (Baileys)
Sin costos - Solo necesitas un número de WhatsApp
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class WhatsAppNotifierLocal:
    """
    Clase para enviar notificaciones por WhatsApp usando servidor local
    Baileys/WPPConnect en Node.js
    """
    
    def __init__(self):
        """Inicializa el cliente local"""
        self.api_url = getattr(settings, 'WHATSAPP_API_URL', 'http://localhost:3000')
        self.enabled = True  # Siempre habilitado si el servidor está corriendo
    
    def format_phone_number(self, phone):
        """
        Formatea el número de teléfono para WhatsApp
        3001234567 -> 573001234567@c.us
        """
        # Limpiar el número
        phone = ''.join(filter(str.isdigit, phone))
        
        # Si no empieza con código de país, agregar 57 (Colombia)
        if not phone.startswith('57'):
            phone = '57' + phone
        
        return f'{phone}@c.us'
    
    def send_message(self, phone, message):
        """
        Envía un mensaje por WhatsApp
        
        Args:
            phone: Número de teléfono
            message: Texto del mensaje
        
        Returns:
            bool: True si se envió exitosamente
        """
        try:
            to_number = self.format_phone_number(phone)
            
            # Llamada a la API local
            response = requests.post(
                f'{self.api_url}/send-message',
                json={
                    'chatId': to_number,
                    'message': message
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"WhatsApp enviado a {phone}")
                return True
            else:
                logger.error(f"Error al enviar WhatsApp: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.warning("Servidor WhatsApp no está corriendo. Ejecuta: npm start en whatsapp-bot/")
            return False
        except Exception as e:
            logger.error(f"Error al enviar WhatsApp: {e}")
            return False
    
    def send_appointment_confirmation(self, appointment):
        """Envía confirmación de cita agendada"""
        fecha = appointment.appointment_date.strftime('%d/%m/%Y')
        hora = appointment.appointment_time.strftime('%I:%M %p')
        
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
        
        return self.send_message(appointment.phone_number, message)
    
    def send_appointment_reminder(self, appointment):
        """Envía recordatorio de cita (1 día antes)"""
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
        
        return self.send_message(appointment.phone_number, message)
    
    def send_appointment_cancelled(self, appointment):
        """Notifica que una cita fue cancelada"""
        fecha = appointment.appointment_date.strftime('%d/%m/%Y')
        hora = appointment.appointment_time.strftime('%I:%M %p')
        
        message = f"""
🌊 *OCEANO OPTICO* 👓

Hola {appointment.full_name},

Tu cita del día *{fecha}* a las *{hora}* ha sido cancelada.

Si deseas reagendar, contáctanos:
📞 {getattr(settings, 'BUSINESS_PHONE', '300 123 4567')}

O agenda en línea:
🌐 {getattr(settings, 'WEBSITE_URL', 'http://127.0.0.1:8000')}/agendar/

¡Gracias! 😊
        """.strip()
        
        return self.send_message(appointment.phone_number, message)


# Instancia global
whatsapp_notifier = WhatsAppNotifierLocal()


def notify_new_appointment(appointment):
    """Función auxiliar para enviar notificación de nueva cita"""
    return whatsapp_notifier.send_appointment_confirmation(appointment)


def notify_appointment_reminder(appointment):
    """Función auxiliar para enviar recordatorio"""
    return whatsapp_notifier.send_appointment_reminder(appointment)


def notify_appointment_cancelled(appointment):
    """Función auxiliar para notificar cancelación"""
    return whatsapp_notifier.send_appointment_cancelled(appointment)
