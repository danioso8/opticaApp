"""
Notificador de WhatsApp usando Baileys
Envía notificaciones a través del servidor Node.js con Baileys
"""
from apps.appointments.whatsapp_baileys_client import whatsapp_baileys_client
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def format_time(time_value):
    """Convierte appointment_time a string formateado (maneja str o time object)"""
    if isinstance(time_value, str):
        time_obj = datetime.strptime(time_value, '%H:%M:%S').time()
        return time_obj.strftime('%I:%M %p')
    else:
        return time_value.strftime('%I:%M %p')


class WhatsAppBaileysNotifier:
    """Notificador que usa WhatsApp Baileys (servidor Node.js)"""
    
    def __init__(self, organization=None):
        self.organization = organization
        self.client = whatsapp_baileys_client
    
    def send_appointment_confirmation(self, appointment):
        """
        Envía confirmación de nueva cita por WhatsApp
        """
        try:
            logger.info(f"=== BAILEYS: Iniciando envío de confirmación para cita #{appointment.id} ===")
            
            if not hasattr(appointment, 'phone_number') or not appointment.phone_number:
                logger.warning(f"Cita #{appointment.id} no tiene teléfono")
                return False
            
            logger.info(f"BAILEYS: Teléfono: {appointment.phone_number}")
            
            org_id = appointment.organization.id if appointment.organization else None
            if not org_id:
                logger.error("BAILEYS: No hay organización para enviar WhatsApp")
                return False
            
            # Verificar que WhatsApp esté conectado
            status = self.client.get_status(org_id)
            if not status or status.get('status') != 'connected':
                logger.warning(f"WhatsApp no conectado para org {org_id}. Estado: {status.get('status') if status else 'unknown'}")
                return False
            
            # Obtener configuración de notificaciones para plantillas personalizadas
            from apps.appointments.models_notifications import NotificationSettings
            settings = NotificationSettings.get_settings(appointment.organization)
            
            # Preparar variables para la plantilla
            org_name = appointment.organization.name if appointment.organization else 'OCEANO OPTICO'
            
            # Convertir fecha a objeto date si es string
            from datetime import datetime
            if isinstance(appointment.appointment_date, str):
                date_obj = datetime.strptime(appointment.appointment_date, '%Y-%m-%d').date()
                date_str = date_obj.strftime('%d/%m/%Y')
            else:
                date_str = appointment.appointment_date.strftime('%d/%m/%Y')
            
            time_str = format_time(appointment.appointment_time)
            
            doctor_name = 'Por asignar'
            if hasattr(appointment, 'doctor') and appointment.doctor:
                doctor_name = appointment.doctor.full_name
            
            arrival_minutes = settings.arrival_minutes_before if settings else 10
            
            # Usar plantilla personalizada o mensaje por defecto
            if settings and settings.confirmation_message_template:
                message = settings.confirmation_message_template.format(
                    organization=org_name,
                    patient_name=appointment.full_name,
                    date=date_str,
                    time=time_str,
                    doctor=doctor_name,
                    arrival_minutes=arrival_minutes
                )
            else:
                # Mensaje por defecto si no hay plantilla
                message = f"""
✅ CITA CONFIRMADA - {org_name}

Hola {appointment.full_name},

Tu cita ha sido agendada exitosamente:

📅 Fecha: {date_str}
🕒 Hora: {time_str}
👤 Doctor: {doctor_name}

Llega {arrival_minutes} minutos antes de tu cita.

Si necesitas cancelar o reagendar, contáctanos con anticipación.

¡Te esperamos! 👓
                """.strip()
            
            logger.info(f"BAILEYS: Enviando mensaje a {appointment.phone_number}")
            
            # Enviar mensaje
            result = self.client.send_message(org_id, appointment.phone_number, message)
            
            logger.info(f"BAILEYS: Resultado del envío: {result}")
            
            if result and result.get('success'):
                logger.info(f"✅ BAILEYS: WhatsApp enviado a {appointment.phone_number} para cita #{appointment.id}")
                
                # Incrementar contador de uso de WhatsApp
                self._increment_whatsapp_usage()
                
                return True
            else:
                logger.error(f"❌ BAILEYS: Error enviando WhatsApp: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando confirmación WhatsApp: {e}", exc_info=True)
            return False
    
    def send_appointment_reminder(self, appointment):
        """
        Envía recordatorio de cita (1 día antes)
        """
        try:
            if not hasattr(appointment, 'phone_number') or not appointment.phone_number:
                return False
            
            org_id = appointment.organization.id if appointment.organization else None
            if not org_id:
                return False
            
            # Verificar conexión
            status = self.client.get_status(org_id)
            if not status or status.get('status') != 'connected':
                logger.warning(f"WhatsApp no conectado para recordatorio")
                return False
            
            org_name = appointment.organization.name if appointment.organization else 'OCEANO OPTICO'
            date_str = appointment.appointment_date.strftime('%d/%m/%Y')
            time_str = format_time(appointment.appointment_time)
            
            message = f"""
🔔 RECORDATORIO DE CITA - {org_name}

Hola {appointment.full_name},

Te recordamos tu cita programada para MAÑANA:

📅 Fecha: {date_str}
🕒 Hora: {time_str}
👤 Doctor: {appointment.doctor.full_name if appointment.doctor else 'Por asignar'}

Por favor, confirma tu asistencia.

¡Te esperamos! 👓
            """.strip()
            
            result = self.client.send_message(org_id, appointment.phone_number, message)
            
            if result and result.get('success'):
                self._increment_whatsapp_usage()
                
            return result and result.get('success')
            
        except Exception as e:
            logger.error(f"Error enviando recordatorio WhatsApp: {e}")
            return False
    
    def send_appointment_cancelled(self, appointment):
        """
        Notifica cancelación de cita
        """
        try:
            if not hasattr(appointment, 'phone_number') or not appointment.phone_number:
                return False
            
            org_id = appointment.organization.id if appointment.organization else None
            if not org_id:
                return False
            
            status = self.client.get_status(org_id)
            if not status or status.get('status') != 'connected':
                return False
            
            # Obtener configuración
            from apps.appointments.models_notifications import NotificationSettings
            settings = NotificationSettings.get_settings(appointment.organization)
            
            org_name = appointment.organization.name if appointment.organization else 'OCEANO OPTICO'
            date_str = appointment.appointment_date.strftime('%d/%m/%Y')
            time_str = format_time(appointment.appointment_time)
            
            # Usar plantilla personalizada
            if settings and settings.cancellation_message_template:
                message = settings.cancellation_message_template.format(
                    organization=org_name,
                    patient_name=appointment.full_name,
                    date=date_str,
                    time=time_str
                )
            else:
                message = f"""
❌ CITA CANCELADA - {org_name}

Hola {appointment.full_name},

Tu cita ha sido cancelada:

📅 Fecha: {date_str}
🕒 Hora: {time_str}

Si deseas reagendar, contáctanos.

Gracias por tu comprensión. 👓
                """.strip()
            
            result = self.client.send_message(org_id, appointment.phone_number, message)
            
            if result and result.get('success'):
                self._increment_whatsapp_usage()
                
            return result and result.get('success')
            
        except Exception as e:
            logger.error(f"Error enviando cancelación WhatsApp: {e}")
            return False
    
    def send_appointment_rescheduled(self, appointment, old_date, old_time):
        """
        Notifica reagendamiento de cita
        """
        try:
            if not hasattr(appointment, 'phone_number') or not appointment.phone_number:
                return False
            
            org_id = appointment.organization.id if appointment.organization else None
            if not org_id:
                return False
            
            status = self.client.get_status(org_id)
            if not status or status.get('status') != 'connected':
                return False
            
            # Obtener configuración
            from apps.appointments.models_notifications import NotificationSettings
            settings = NotificationSettings.get_settings(appointment.organization)
            
            org_name = appointment.organization.name if appointment.organization else 'OCEANO OPTICO'
            new_date_str = appointment.appointment_date.strftime('%d/%m/%Y')
            new_time_str = format_time(appointment.appointment_time)
            
            doctor_name = 'Por asignar'
            if hasattr(appointment, 'doctor') and appointment.doctor:
                doctor_name = appointment.doctor.full_name
            
            arrival_minutes = settings.arrival_minutes_before if settings else 10
            
            # Usar plantilla personalizada
            if settings and settings.rescheduled_message_template:
                message = settings.rescheduled_message_template.format(
                    organization=org_name,
                    patient_name=appointment.full_name,
                    date=new_date_str,
                    time=new_time_str,
                    doctor=doctor_name,
                    arrival_minutes=arrival_minutes
                )
            else:
                message = f"""
🔄 CITA REAGENDADA - {org_name}

Hola {appointment.full_name},

Tu cita ha sido reagendada:

📅 Nueva Fecha: {new_date_str}
🕒 Nueva Hora: {new_time_str}
👤 Doctor: {doctor_name}

Llega {arrival_minutes} minutos antes de tu cita.

¡Te esperamos! 👓
                """.strip()
            
            result = self.client.send_message(org_id, appointment.phone_number, message)
            
            if result and result.get('success'):
                self._increment_whatsapp_usage()
                
            return result and result.get('success')
            
        except Exception as e:
            logger.error(f"Error enviando reagendamiento WhatsApp: {e}")
            return False
    
    def _increment_whatsapp_usage(self):
        """
        Incrementa el contador de mensajes WhatsApp para la organización
        """
        try:
            if not self.organization:
                return
            
            from apps.appointments.models_whatsapp_usage import WhatsAppUsage
            usage = WhatsAppUsage.get_current_usage(self.organization)
            usage.increment_message()
            
            logger.info(f"📊 WhatsApp usage: {usage.messages_sent}/{usage.messages_included} para {self.organization.name}")
            
        except Exception as e:
            logger.error(f"Error incrementando uso WhatsApp: {e}")



# Instancia global
whatsapp_baileys_notifier = WhatsAppBaileysNotifier()
