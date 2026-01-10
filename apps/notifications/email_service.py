"""
Servicio de envío de emails para notificaciones
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_email_notification(channel_obj):
    """
    Envía una notificación por email
    
    Args:
        channel_obj: Objeto NotificationChannel
    """
    notification = channel_obj.notification
    recipient_email = channel_obj.recipient
    
    # Asunto del email
    subject = notification.title
    
    # Mensaje plano
    plain_message = notification.message
    
    # Mensaje HTML (opcional - se puede crear una plantilla)
    html_message = f"""
    <html>
        <body>
            <h2>{notification.title}</h2>
            <p>{notification.message}</p>
            {f'<a href="{notification.action_url}">{notification.action_label or "Ver más"}</a>' if notification.action_url else ''}
            <hr>
            <p><small>Este es un mensaje automático de {notification.organization.name}</small></p>
        </body>
    </html>
    """
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        raise Exception(f"Error enviando email: {str(e)}")
