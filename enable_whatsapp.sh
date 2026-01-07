#!/bin/bash
cd /var/www/opticaapp
source venv/bin/activate
python manage.py shell << 'PYEOF'
from apps.appointments.models_notifications import NotificationSettings
from apps.organizations.models import Organization

org = Organization.objects.get(id=23)
settings = NotificationSettings.get_settings(org)

print('\n=== ESTADO ACTUAL ===')
print(f'local_whatsapp_enabled: {settings.local_whatsapp_enabled}')
print(f'email_enabled: {settings.email_enabled}')
print(f'Metodo activo: {settings.get_active_method()}')

settings.local_whatsapp_enabled = True
settings.send_confirmation = True
settings.save()

print('\n=== NUEVO ESTADO ===')
print(f'local_whatsapp_enabled: {settings.local_whatsapp_enabled}')
print(f'email_enabled: {settings.email_enabled}')
print(f'Metodo activo: {settings.get_active_method()}')
print(f'Enviar confirmaciones: {settings.send_confirmation}')
print('\nWhatsApp activado correctamente')
PYEOF
