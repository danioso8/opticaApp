import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models_notifications import NotificationSettings
from apps.organizations.models import Organization

# Organización 23 (CompuEasys)
org = Organization.objects.get(id=23)
settings = NotificationSettings.get_settings(org)

print(f"\n=== Configurando WhatsApp Baileys para {org.name} ===\n")

# IMPORTANTE: Desactivar Twilio y activar Baileys
settings.whatsapp_enabled = False  # Desactivar Twilio
settings.local_whatsapp_enabled = True  # Activar Baileys
settings.email_enabled = False  # Desactivar Email (opcional)

# Activar notificaciones automáticas
settings.send_confirmation = True
settings.send_reminder = True
settings.send_cancellation = True

settings.save()

print("✅ Configuración actualizada:")
print(f"   - WhatsApp (Twilio): {settings.whatsapp_enabled}")
print(f"   - WhatsApp Local (Baileys): {settings.local_whatsapp_enabled}")
print(f"   - Email: {settings.email_enabled}")
print(f"\n   Método activo: {settings.get_active_method()}")
print(f"\n¡Listo! Ahora el sistema usará WhatsApp Baileys para las notificaciones.")
