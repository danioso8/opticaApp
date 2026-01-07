"""
Script para verificar organizaciones y crear una cita con email
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models import Appointment

print('=' * 80)
print('VERIFICANDO ORGANIZACIONES')
print('=' * 80)

orgs = Organization.objects.all()
print(f'\nTotal de organizaciones: {orgs.count()}\n')

for org in orgs:
    print(f'ID: {org.id:3d} | Nombre: {org.name:<30s} | Activa: {org.is_active}')

if orgs.exists():
    org = orgs.first()
    print(f'\n✅ Usando organización: {org.name} (ID: {org.id})')
    
    # Verificar NotificationSettings
    from apps.appointments.models_notifications import NotificationSettings
    notification_settings = NotificationSettings.get_settings(org)
    
    print(f'\nConfiguraci ón de notificaciones:')
    print(f'  Email habilitado: {notification_settings.email_enabled}')
    print(f'  WhatsApp local habilitado: {notification_settings.local_whatsapp_enabled}')
    print(f'  Enviar confirmación: {notification_settings.send_confirmation}')
    print(f'  Método activo: {notification_settings.get_active_method()}')
    
    # Si el método activo no es email, habilitarlo
    if notification_settings.get_active_method() != 'email':
        print('\n⚠️  Habilitando notificaciones por email...')
        notification_settings.email_enabled = True
        notification_settings.local_whatsapp_enabled = False
        notification_settings.send_confirmation = True
        notification_settings.save()
        print('✅ Email habilitado')
    
    # Crear cita de prueba con email
    print('\n' + '=' * 80)
    print('CREANDO CITA DE PRUEBA CON EMAIL')
    print('=' * 80)
    
    tomorrow = datetime.now().date() + timedelta(days=1)
    current_time = datetime.now()
    appointment_time = current_time.replace(second=0, microsecond=0).time()
    
    appointment = Appointment(
        organization=org,
        full_name="Prueba Email ✅",
        phone_number="3007915262",
        email="danioso8@gmail.com",  # ¡IMPORTANTE! Agregar email
        appointment_date=tomorrow,
        appointment_time=appointment_time,
        status='confirmed'
    )
    appointment.save()
    
    print(f'\n✅ Cita creada exitosamente:')
    print(f'   ID: {appointment.id}')
    print(f'   Nombre: {appointment.full_name}')
    print(f'   Teléfono: {appointment.phone_number}')
    print(f'   📧 Email: {appointment.email}')
    print(f'   Fecha: {appointment.appointment_date}')
    print(f'   Hora: {appointment.appointment_time}')
    print('\n🔔 La notificación por EMAIL debería enviarse automáticamente...')
    print('   Revisa tu correo en: danioso8@gmail.com!')
    
else:
    print('\n❌ NO HAY ORGANIZACIONES - Debes crear una primero')
