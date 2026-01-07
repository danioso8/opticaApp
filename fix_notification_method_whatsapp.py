"""
Script para cambiar el método de notificación a WhatsApp Local (Baileys)
para la organización CompuEasys
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opticaapp.settings')
django.setup()

from apps.appointments.models_notifications import NotificationSettings
from apps.organizations.models import Organization

# Obtener la organización CompuEasys
org = Organization.objects.get(id=23)
print(f"Organización: {org.name}")

# Obtener o crear la configuración de notificaciones
settings, created = NotificationSettings.objects.get_or_create(
    organization=org,
    defaults={
        'notification_method': 'local_whatsapp',
        'send_confirmation': True,
        'send_reminder': True,
        'send_cancellation': True,
        'send_rescheduling': True,
    }
)

if not created:
    # Actualizar método a WhatsApp Local
    settings.notification_method = 'local_whatsapp'
    settings.send_confirmation = True
    settings.send_reminder = True
    settings.save()
    print(f"✅ Método actualizado de '{settings.notification_method}' a 'local_whatsapp'")
else:
    print(f"✅ Configuración creada con método 'local_whatsapp'")

print(f"\nConfiguración actual:")
print(f"- Método: {settings.notification_method}")
print(f"- Método activo: {settings.get_active_method()}")
print(f"- Confirmación: {settings.send_confirmation}")
print(f"- Recordatorio: {settings.send_reminder}")
print(f"- Cancelación: {settings.send_cancellation}")

print("\n✅ ¡Listo! Ahora las notificaciones automáticas se enviarán por WhatsApp.")
