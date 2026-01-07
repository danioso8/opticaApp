"""
Script completo de validación de configuración de email
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from apps.appointments.models import Appointment
from apps.organizations.models import Organization
import logging

logging.basicConfig(level=logging.DEBUG)

print('=' * 80)
print('DIAGNÓSTICO COMPLETO DE CONFIGURACIÓN DE EMAIL')
print('=' * 80)

# 1. Verificar configuración
print('\n1️⃣  CONFIGURACIÓN DE EMAIL EN SETTINGS')
print('-' * 80)
print(f'DEBUG: {settings.DEBUG}')
print(f'USE_EMAIL_NOTIFICATIONS: {getattr(settings, "USE_EMAIL_NOTIFICATIONS", "NO DEFINIDO")}')
print(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
print(f'EMAIL_HOST: {settings.EMAIL_HOST}')
print(f'EMAIL_PORT: {settings.EMAIL_PORT}')
print(f'EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
print(f'EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}')
print(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
print(f'EMAIL_HOST_PASSWORD: {"✅ Configurado (" + "*" * 10 + ")" if settings.EMAIL_HOST_PASSWORD else "❌ NO CONFIGURADO"}')
print(f'DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
print(f'EMAIL_TIMEOUT: {getattr(settings, "EMAIL_TIMEOUT", "NO DEFINIDO")}')

# 2. Verificar NotificationSettings
print('\n2️⃣  CONFIGURACIÓN DE NOTIFICACIONES EN BASE DE DATOS')
print('-' * 80)
try:
    from apps.appointments.models_notifications import NotificationSettings
    
    org = Organization.objects.get(id=23)
    notification_settings = NotificationSettings.get_settings(org)
    
    print(f'Organización: {org.name}')
    print(f'Email habilitado: {notification_settings.email_enabled}')
    print(f'WhatsApp local habilitado: {notification_settings.local_whatsapp_enabled}')
    print(f'Enviar confirmación: {notification_settings.send_confirmation}')
    print(f'Enviar recordatorio: {notification_settings.send_reminder}')
    print(f'Método activo: {notification_settings.get_active_method()}')
    
except Exception as e:
    print(f'❌ Error al obtener configuración: {e}')

# 3. Verificar que exista una cita con email
print('\n3️⃣  VERIFICACIÓN DE CITAS CON EMAIL')
print('-' * 80)
appointments_with_email = Appointment.objects.filter(organization_id=23).exclude(email__isnull=True).exclude(email='')
print(f'Citas con email en org 23: {appointments_with_email.count()}')
if appointments_with_email.exists():
    last = appointments_with_email.last()
    print(f'Última cita con email: ID={last.id}, Email={last.email}, Nombre={last.full_name}')
else:
    print('⚠️  NO HAY CITAS CON EMAIL - Las notificaciones por email no se enviarán')

# 4. Prueba de envío simple
print('\n4️⃣  PRUEBA DE ENVÍO SIMPLE')
print('-' * 80)
try:
    result = send_mail(
        subject='✅ Prueba OpticaApp - Configuración correcta',
        message='Si recibes este mensaje, la configuración SMTP está correcta.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['danioso8@gmail.com'],
        fail_silently=False,
    )
    print(f'✅ Email enviado correctamente (resultado: {result})')
    print('📧 Revisa tu bandeja de entrada: danioso8@gmail.com')
except Exception as e:
    print(f'❌ ERROR al enviar email simple:')
    print(f'   Tipo: {type(e).__name__}')
    print(f'   Mensaje: {str(e)}')
    import traceback
    traceback.print_exc()

# 5. Prueba con EmailNotifier
print('\n5️⃣  PRUEBA CON EmailNotifier')
print('-' * 80)
try:
    from apps.appointments.email_notifier import EmailNotifier
    
    email_notifier = EmailNotifier()
    print(f'EmailNotifier inicializado:')
    print(f'  - Habilitado: {email_notifier.enabled}')
    print(f'  - From email: {email_notifier.from_email}')
    
    # Crear una cita de prueba en memoria (sin guardar)
    from datetime import datetime, timedelta
    
    test_appointment = Appointment(
        organization=org,
        full_name="Prueba Email Test",
        phone_number="3007915262",
        email="danioso8@gmail.com",  # Email de prueba
        appointment_date=datetime.now().date() + timedelta(days=1),
        appointment_time=datetime.now().time(),
        status='confirmed'
    )
    
    print('\nIntentando enviar email de confirmación...')
    result = email_notifier.send_appointment_confirmation(test_appointment)
    
    if result:
        print('✅ Email de confirmación enviado exitosamente')
    else:
        print('❌ Email de confirmación NO se envió')
    
except Exception as e:
    print(f'❌ ERROR en EmailNotifier:')
    print(f'   Tipo: {type(e).__name__}')
    print(f'   Mensaje: {str(e)}')
    import traceback
    traceback.print_exc()

# 6. Verificar get_notifier
print('\n6️⃣  VERIFICACIÓN DE get_notifier()')
print('-' * 80)
try:
    from apps.appointments.notifications import get_notifier
    
    notifier = get_notifier(org)
    print(f'Tipo de notificador: {type(notifier).__name__}')
    print(f'Módulo: {type(notifier).__module__}')
    
    if hasattr(notifier, 'enabled'):
        print(f'Habilitado: {notifier.enabled}')
    if hasattr(notifier, 'from_email'):
        print(f'From email: {notifier.from_email}')
        
except Exception as e:
    print(f'❌ Error en get_notifier: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '=' * 80)
print('FIN DEL DIAGNÓSTICO')
print('=' * 80)
