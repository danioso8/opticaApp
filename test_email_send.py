"""
Script para probar envío de email de verificación
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail

print('=' * 60)
print('CONFIGURACIÓN DE EMAIL')
print('=' * 60)
print(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
print(f'EMAIL_HOST: {settings.EMAIL_HOST}')
print(f'EMAIL_PORT: {settings.EMAIL_PORT}')
print(f'EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
print(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
print(f'EMAIL_HOST_PASSWORD: {"*" * 10 if settings.EMAIL_HOST_PASSWORD else "NO CONFIGURADO"}')
print(f'DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')

print('\n' + '=' * 60)
print('PROBANDO ENVÍO DE EMAIL')
print('=' * 60)

try:
    send_mail(
        subject='Prueba de configuración - OpticaApp',
        message='Este es un email de prueba para verificar la configuración SMTP.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['danioso8@gmail.com'],
        fail_silently=False,
    )
    print('✅ Email enviado correctamente')
    print('📧 Revisa tu bandeja de entrada: danioso8@gmail.com')
except Exception as e:
    print(f'❌ ERROR al enviar email:')
    print(f'   {type(e).__name__}: {str(e)}')
    print('\n⚠️  Verifica que tengas configuradas las variables de entorno:')
    print('   - EMAIL_HOST_USER')
    print('   - EMAIL_HOST_PASSWORD')

print('=' * 60)
