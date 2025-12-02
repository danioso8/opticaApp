"""
Sistema de notificaciones por Email (100% GRATIS)
Funciona en local y en Render/producción
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Clase para enviar notificaciones por Email"""
    
    def __init__(self):
        """Inicializa el notificador de email"""
        self.enabled = True
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@oceanooptico.com')
    
    def send_appointment_confirmation(self, appointment):
        """
        Envía confirmación de cita agendada por email
        
        Args:
            appointment: Objeto Appointment
        
        Returns:
            bool: True si se envió exitosamente
        """
        if not self.enabled:
            logger.info(f"Email deshabilitado. No se enviará notificación para cita #{appointment.id}")
            return False
        
        # Verificar que el appointment tenga email (si no, usar el phone como fallback)
        to_email = getattr(appointment, 'email', None)
        if not to_email:
            logger.warning(f"Cita #{appointment.id} no tiene email. No se puede enviar notificación.")
            return False
        
        try:
            # Formatear fecha y hora
            fecha = appointment.appointment_date.strftime('%d/%m/%Y')
            hora = appointment.appointment_time.strftime('%I:%M %p')
            
            # Obtener datos de la organización
            org_name = "OCEANO OPTICO"
            org_phone = getattr(settings, 'BUSINESS_PHONE', '300 123 4567')
            org_address = ""
            
            if hasattr(appointment, 'organization') and appointment.organization:
                org = appointment.organization
                org_name = org.name.upper()
                org_phone = org.phone or org_phone
                
                # Construir dirección completa
                address_parts = []
                if org.address:
                    address_parts.append(org.address)
                if org.neighborhood:
                    address_parts.append(org.neighborhood)
                if org.city:
                    address_parts.append(org.city)
                
                if address_parts:
                    org_address = ', '.join(address_parts)
            
            # Asunto del email
            subject = f'Confirmación de Cita - {org_name}'
            
            # Mensaje en texto plano
            text_content = f"""
Hola {appointment.full_name},

¡Tu cita ha sido agendada exitosamente!

DETALLES DE TU CITA:
━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Fecha: {fecha}
🕐 Hora: {hora}
{'📍 Dirección: ' + org_address if org_address else ''}

RECOMENDACIONES:
• Llega 10 minutos antes
• Trae tu documento de identidad
• Si usas lentes, tráelos contigo

¿NECESITAS CANCELAR O REAGENDAR?
Llámanos al: {org_phone}

¡Te esperamos!

--
{org_name}
{org_phone}
            """.strip()
            
            # Mensaje HTML (más bonito)
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background: #f9f9f9;
            padding: 30px;
            border: 1px solid #ddd;
        }}
        .details {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }}
        .detail-item {{
            margin: 10px 0;
            font-size: 16px;
        }}
        .icon {{
            display: inline-block;
            width: 24px;
        }}
        .recommendations {{
            background: #fff8e1;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 14px;
            border-top: 1px solid #ddd;
        }}
        .button {{
            display: inline-block;
            padding: 12px 30px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌊 {org_name} 👓</h1>
        <p>Confirmación de Cita</p>
    </div>
    
    <div class="content">
        <h2>¡Hola {appointment.full_name}!</h2>
        <p>Tu cita ha sido agendada exitosamente.</p>
        
        <div class="details">
            <h3>📋 Detalles de tu Cita</h3>
            <div class="detail-item">
                <span class="icon">📅</span> <strong>Fecha:</strong> {fecha}
            </div>
            <div class="detail-item">
                <span class="icon">🕐</span> <strong>Hora:</strong> {hora}
            </div>
            {f'<div class="detail-item"><span class="icon">📍</span> <strong>Dirección:</strong> {org_address}</div>' if org_address else ''}
        </div>
        
        <div class="recommendations">
            <h3>💡 Recomendaciones</h3>
            <ul>
                <li>Llega 10 minutos antes de tu cita</li>
                <li>Trae tu documento de identidad</li>
                <li>Si usas lentes, tráelos contigo</li>
            </ul>
        </div>
        
        <p><strong>¿Necesitas cancelar o reagendar?</strong></p>
        <p>Llámanos al: <strong>{org_phone}</strong></p>
    </div>
    
    <div class="footer">
        <p>{org_name}</p>
        <p>📞 {org_phone}</p>
        <p style="font-size: 12px; color: #999;">
            Este es un correo automático, por favor no respondas a este mensaje.
        </p>
    </div>
</body>
</html>
            """
            
            # Crear email con HTML
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[to_email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Email de confirmación enviado a {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar email a {to_email}: {e}")
            return False
    
    def send_appointment_reminder(self, appointment):
        """
        Envía recordatorio de cita (1 día antes)
        
        Args:
            appointment: Objeto Appointment
        
        Returns:
            bool: True si se envió exitosamente
        """
        to_email = getattr(appointment, 'email', None)
        if not to_email:
            return False
        
        try:
            fecha = appointment.appointment_date.strftime('%d/%m/%Y')
            hora = appointment.appointment_time.strftime('%I:%M %p')
            
            org_name = "OCEANO OPTICO"
            org_phone = getattr(settings, 'BUSINESS_PHONE', '300 123 4567')
            
            if hasattr(appointment, 'organization') and appointment.organization:
                org = appointment.organization
                org_name = org.name.upper()
                org_phone = org.phone or org_phone
            
            subject = f'Recordatorio: Cita Mañana - {org_name}'
            
            text_content = f"""
Hola {appointment.full_name},

🔔 Este es un recordatorio de tu cita.

MAÑANA tienes una cita agendada:

📅 Fecha: {fecha}
🕐 Hora: {hora}

¡Nos vemos mañana!

Si necesitas cancelar, llámanos:
📞 {org_phone}

--
{org_name}
            """.strip()
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
        .reminder {{ background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 20px 0; text-align: center; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌊 {org_name} 👓</h1>
        <p>Recordatorio de Cita</p>
    </div>
    
    <div class="content">
        <h2>¡Hola {appointment.full_name}!</h2>
        
        <div class="reminder">
            <h2>🔔 Recordatorio</h2>
            <p><strong>MAÑANA</strong> tienes una cita agendada:</p>
            <p style="font-size: 18px;">
                📅 {fecha}<br>
                🕐 {hora}
            </p>
        </div>
        
        <p style="text-align: center;">¡Te esperamos! 😊</p>
        
        <p style="text-align: center; font-size: 14px;">
            Si necesitas cancelar, llámanos:<br>
            <strong>📞 {org_phone}</strong>
        </p>
    </div>
    
    <div class="footer">
        <p>{org_name} | {org_phone}</p>
    </div>
</body>
</html>
            """
            
            msg = EmailMultiAlternatives(subject, text_content, self.from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Recordatorio enviado a {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar recordatorio: {e}")
            return False
    
    def send_appointment_cancelled(self, appointment):
        """
        Notifica que una cita fue cancelada
        
        Args:
            appointment: Objeto Appointment
        
        Returns:
            bool: True si se envió exitosamente
        """
        to_email = getattr(appointment, 'email', None)
        if not to_email:
            return False
        
        try:
            fecha = appointment.appointment_date.strftime('%d/%m/%Y')
            hora = appointment.appointment_time.strftime('%I:%M %p')
            
            org_name = "OCEANO OPTICO"
            org_phone = getattr(settings, 'BUSINESS_PHONE', '300 123 4567')
            booking_url = getattr(settings, 'WEBSITE_URL', 'http://127.0.0.1:8000') + '/agendar/'
            
            if hasattr(appointment, 'organization') and appointment.organization:
                org = appointment.organization
                org_name = org.name.upper()
                org_phone = org.phone or org_phone
            
            subject = f'Cita Cancelada - {org_name}'
            
            text_content = f"""
Hola {appointment.full_name},

Tu cita del día {fecha} a las {hora} ha sido cancelada.

Si deseas reagendar, puedes:
• Llamarnos al: {org_phone}
• Agendar en línea: {booking_url}

¡Gracias!

--
{org_name}
            """.strip()
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #dc3545; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
        .cancelled {{ background: #f8d7da; padding: 20px; border-radius: 8px; border-left: 4px solid #dc3545; margin: 20px 0; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌊 {org_name} 👓</h1>
        <p>Cita Cancelada</p>
    </div>
    
    <div class="content">
        <h2>Hola {appointment.full_name},</h2>
        
        <div class="cancelled">
            <p>Tu cita del día <strong>{fecha}</strong> a las <strong>{hora}</strong> ha sido cancelada.</p>
        </div>
        
        <p>Si deseas reagendar, puedes:</p>
        <ul>
            <li>Llamarnos al: <strong>{org_phone}</strong></li>
            <li>Agendar en línea: <a href="{booking_url}" class="button">Agendar Nueva Cita</a></li>
        </ul>
        
        <p>¡Gracias!</p>
    </div>
    
    <div class="footer">
        <p>{org_name} | {org_phone}</p>
    </div>
</body>
</html>
            """
            
            msg = EmailMultiAlternatives(subject, text_content, self.from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            logger.info(f"Notificación de cancelación enviada a {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar notificación de cancelación: {e}")
            return False


# Instancia global
email_notifier = EmailNotifier()


def notify_new_appointment(appointment):
    """Función auxiliar para enviar notificación de nueva cita"""
    return email_notifier.send_appointment_confirmation(appointment)


def notify_appointment_reminder(appointment):
    """Función auxiliar para enviar recordatorio"""
    return email_notifier.send_appointment_reminder(appointment)


def notify_appointment_cancelled(appointment):
    """Función auxiliar para notificar cancelación"""
    return email_notifier.send_appointment_cancelled(appointment)
