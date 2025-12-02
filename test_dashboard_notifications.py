"""
Script para probar el sistema de notificaciones localmente
Ejecutar: python manage.py shell < test_dashboard_notifications.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models_notifications import NotificationSettings
from apps.appointments.notifications import get_notifier

print("\n" + "="*70)
print("🧪 TEST DEL SISTEMA DE NOTIFICACIONES")
print("="*70)

# 1. Verificar organizaciones
print("\n📊 ORGANIZACIONES REGISTRADAS:")
print("-"*70)
organizations = Organization.objects.all()
if organizations.exists():
    for org in organizations:
        print(f"  ✓ {org.name} (ID: {org.id})")
        print(f"    Owner: {org.owner.username}")
        print(f"    Email: {org.email}")
else:
    print("  ⚠️  No hay organizaciones registradas")

# 2. Crear/Verificar configuraciones de notificaciones
print("\n⚙️  CONFIGURACIÓN DE NOTIFICACIONES:")
print("-"*70)

for org in organizations:
    settings, created = NotificationSettings.objects.get_or_create(
        organization=org,
        defaults={
            'email_enabled': True,
            'email_from': 'noreply@opticaapp.com',
            'twilio_enabled': False,
            'local_whatsapp_enabled': True,  # Activo en desarrollo
            'local_whatsapp_url': 'http://localhost:3000',
            'send_confirmation': True,
            'send_reminder': True,
            'send_cancellation': True,
        }
    )
    
    status = "CREADA" if created else "EXISTENTE"
    print(f"\n  {org.name}: {status}")
    print(f"    • Email: {'✓' if settings.email_enabled else '✗'}")
    print(f"    • Twilio WhatsApp: {'✓' if settings.twilio_enabled else '✗'}")
    print(f"    • WhatsApp Local: {'✓' if settings.local_whatsapp_enabled else '✗'}")
    print(f"    • Método activo: {settings.get_active_method() or 'Ninguno'}")
    print(f"    • Enviar confirmación: {'✓' if settings.send_confirmation else '✗'}")
    print(f"    • Enviar recordatorio: {'✓' if settings.send_reminder else '✗'}")
    print(f"    • Enviar cancelación: {'✓' if settings.send_cancellation else '✗'}")

# 3. Verificar el notificador
print("\n🔔 NOTIFICADOR GLOBAL:")
print("-"*70)
try:
    from apps.appointments.notifications import notifier
    print(f"  Tipo: {type(notifier).__name__}")
    print(f"  Habilitado: {getattr(notifier, 'enabled', 'N/A')}")
except Exception as e:
    print(f"  ⚠️  Error: {e}")

# 4. Test de URLs
print("\n🌐 URLS DEL DASHBOARD:")
print("-"*70)
print("  Dashboard principal: /dashboard/")
print("  Login: /dashboard/login/")
print("  Configuración: /dashboard/configuracion/")
print("  Notificaciones: /dashboard/configuracion/notificaciones/")

# 5. Verificar rutas en Django
print("\n✅ VERIFICACIÓN DE RUTAS:")
print("-"*70)
from django.urls import reverse
try:
    url = reverse('dashboard:notification_settings')
    print(f"  ✓ notification_settings: {url}")
except Exception as e:
    print(f"  ✗ notification_settings: {e}")

try:
    url = reverse('dashboard:save_notification_settings')
    print(f"  ✓ save_notification_settings: {url}")
except Exception as e:
    print(f"  ✗ save_notification_settings: {e}")

try:
    url = reverse('dashboard:test_notification')
    print(f"  ✓ test_notification: {url}")
except Exception as e:
    print(f"  ✗ test_notification: {e}")

# 6. Resumen final
print("\n" + "="*70)
print("📋 RESUMEN:")
print("="*70)
print(f"  Organizaciones: {organizations.count()}")
print(f"  Configuraciones: {NotificationSettings.objects.count()}")
print(f"  Sistema: {'✅ Listo' if organizations.exists() else '⚠️  Configuración pendiente'}")

print("\n🚀 PRÓXIMOS PASOS:")
print("-"*70)
print("  1. Ejecuta: python manage.py runserver")
print("  2. Ve a: http://127.0.0.1:8000/dashboard/login/")
print("  3. Inicia sesión")
print("  4. Ve a: Configuración → WhatsApp Twilio")
print("  5. Configura tu método preferido (Email o Twilio)")
print("  6. Envía un mensaje de prueba")

print("\n" + "="*70)
print("✅ Verificación completada")
print("="*70 + "\n")
