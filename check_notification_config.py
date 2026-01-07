import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models_notifications import NotificationSettings
from apps.organizations.models import Organization

# Organización 23 (CompuEasys)
org = Organization.objects.get(id=23)
settings = NotificationSettings.get_settings(org)

print("\n=== CONFIGURACIÓN DE NOTIFICACIONES - ORG 23 ===\n")
print(f"Organización: {org.name}")
print(f"\n--- MÉTODOS ACTIVOS ---")
print(f"WhatsApp Local (Baileys): {settings.local_whatsapp_enabled}")
print(f"Email: {settings.email_enabled}")

print(f"\n--- NOTIFICACIONES AUTOMÁTICAS ---")
print(f"Enviar confirmación: {settings.send_confirmation}")
print(f"Enviar recordatorio: {settings.send_reminder}")
print(f"Enviar cancelación: {settings.send_cancellation}")

print(f"\n--- MÉTODO ACTIVO ---")
print(f"get_active_method(): {settings.get_active_method()}")

print(f"\n--- PLANTILLAS ---")
print(f"Horas de recordatorio: {settings.reminder_hours_before}")
print(f"Minutos de anticipación: {settings.arrival_minutes_before}")
