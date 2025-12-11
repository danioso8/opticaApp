"""
Script para probar el envío de email
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings


def test_email():
    """Prueba el envío de email"""
    
    print("=" * 60)
    print("PRUEBA DE ENVÍO DE EMAIL")
    print("=" * 60)
    
    print(f"\nConfiguración:")
    print(f"  Host: {settings.EMAIL_HOST}")
    print(f"  Port: {settings.EMAIL_PORT}")
    print(f"  User: {settings.EMAIL_HOST_USER}")
    print(f"  From: {settings.DEFAULT_FROM_EMAIL}")
    print(f"  TLS: {settings.EMAIL_USE_TLS}")
    
    recipient = input(f"\n¿A qué email quieres enviar la prueba? (Enter para {settings.EMAIL_HOST_USER}): ").strip()
    if not recipient:
        recipient = settings.EMAIL_HOST_USER
    
    print(f"\nEnviando email de prueba a: {recipient}")
    
    try:
        send_mail(
            subject='Prueba de Email - OpticaApp',
            message='Este es un correo de prueba del sistema OpticaApp.\n\nSi recibes esto, la configuración de email está funcionando correctamente.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        print("\n✓ Email enviado exitosamente!")
        print(f"  Revisa la bandeja de {recipient}")
        return True
        
    except Exception as e:
        print(f"\n✗ Error al enviar email:")
        print(f"  {type(e).__name__}: {e}")
        return False


if __name__ == '__main__':
    test_email()
