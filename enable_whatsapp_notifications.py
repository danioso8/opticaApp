"""
Script para activar notificaciones por WhatsApp
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optica_project.settings')
django.setup()

from apps.appointments.models_notifications import NotificationSettings
from apps.organizations.models import Organization

# Buscar CompuEasys
org = Organization.objects.get(id=23, name="CompuEasys")
print(f"\nOrganización: {org.name}")

# Obtener configuración
settings = NotificationSettings.get_settings(org)

print("\n=== ESTADO ACTUAL ===")
print(f"local_whatsapp_enabled: {settings.local_whatsapp_enabled}")
print(f"email_enabled: {settings.email_enabled}")
print(f"Método activo: {settings.get_active_method()}")

# Activar WhatsApp
settings.local_whatsapp_enabled = True
settings.send_confirmation = True  # Asegurarse de que envíe confirmaciones
settings.save()

print("\n=== NUEVO ESTADO ===")
print(f"local_whatsapp_enabled: {settings.local_whatsapp_enabled}")
print(f"email_enabled: {settings.email_enabled}")
print(f"Método activo: {settings.get_active_method()}")
print(f"Enviar confirmaciones: {settings.send_confirmation}")

print("\n✅ WhatsApp activado correctamente")
print("Ahora se enviarán notificaciones automáticas por WhatsApp al crear citas")
