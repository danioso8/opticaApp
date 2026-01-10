"""
Servicio de envío de WhatsApp para notificaciones
Integración con servidor Baileys existente (puerto 3000)
"""
import requests
from django.conf import settings


def send_whatsapp_notification(channel_obj):
    """
    Envía una notificación por WhatsApp
    
    Args:
        channel_obj: Objeto NotificationChannel
    """
    notification = channel_obj.notification
    phone_number = channel_obj.recipient
    
    # Formatear mensaje
    message = f"""
*{notification.title}*

{notification.message}

{f'👉 {notification.action_label}: {notification.action_url}' if notification.action_url else ''}

---
_{notification.organization.name}_
""".strip()
    
    # URL del servidor WhatsApp (ya existe en puerto 3000)
    whatsapp_server_url = getattr(settings, 'WHATSAPP_SERVER_URL', 'http://localhost:3000')
    
    try:
        response = requests.post(
            f"{whatsapp_server_url}/send-message",
            json={
                'phone': phone_number,
                'message': message
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return True
        else:
            raise Exception(f"WhatsApp server error: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error conectando con servidor WhatsApp: {str(e)}")
