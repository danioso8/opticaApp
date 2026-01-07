"""
Verificar configuración de notificaciones de CompuEasys
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models_notifications import NotificationSettings

org = Organization.objects.get(slug='compueasys')
settings = NotificationSettings.get_settings(org)

print(f"Organización: {org.name}")
print(f"WhatsApp habilitado: {settings.whatsapp_enabled}")
print(f"Email habilitado: {settings.email_enabled}")
print(f"Enviar confirmación: {settings.send_confirmation}")
print(f"Método activo: {settings.get_active_method()}")
