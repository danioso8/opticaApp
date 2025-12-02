"""
✅ Verificador Rápido - Ejecutar ANTES de configurar en Render
Este script verifica que todo esté listo localmente

Uso:
1. Abre una terminal de comandos (CMD o PowerShell)
2. Navega a la carpeta del proyecto: cd D:\ESCRITORIO\OpticaApp
3. Ejecuta: python manage.py shell
4. Copia y pega este contenido completo
"""

print("\n" + "="*70)
print("🔍 VERIFICADOR RÁPIDO DEL SISTEMA DE NOTIFICACIONES")
print("="*70 + "\n")

# Imports
try:
    from apps.organizations.models import Organization
    from apps.appointments.models_notifications import NotificationSettings
    from apps.appointments.models import Appointment
    from django.contrib.auth.models import User
    print("✅ Imports exitosos")
except ImportError as e:
    print(f"❌ Error en imports: {e}")
    exit()

# 1. Verificar Organizaciones
print("\n📊 ORGANIZACIONES:")
print("-"*70)
orgs = Organization.objects.all()
if orgs.exists():
    for org in orgs:
        print(f"  ✓ {org.name}")
        print(f"    ID: {org.id}")
        print(f"    Owner: {org.owner.username}")
        print(f"    Email: {org.email or 'No definido'}")
        print(f"    Activa: {'Sí' if org.is_active else 'No'}")
else:
    print("  ⚠️  No hay organizaciones registradas")

# 2. Verificar Usuarios
print("\n👥 USUARIOS:")
print("-"*70)
users = User.objects.all()
print(f"  Total: {users.count()}")
for user in users[:5]:  # Primeros 5
    print(f"  • {user.username} - {user.email}")
    print(f"    Staff: {user.is_staff} | Superuser: {user.is_superuser}")

# 3. Verificar NotificationSettings
print("\n⚙️  CONFIGURACIÓN DE NOTIFICACIONES:")
print("-"*70)
settings_count = NotificationSettings.objects.count()
print(f"  Configuraciones existentes: {settings_count}")

if settings_count == 0:
    print("  ⚠️  No hay configuraciones creadas")
    print("  📝 Creando configuraciones por defecto...")
    
    for org in orgs:
        settings, created = NotificationSettings.objects.get_or_create(
            organization=org,
            defaults={
                'email_enabled': True,
                'twilio_enabled': False,
                'local_whatsapp_enabled': True,
                'send_confirmation': True,
                'send_reminder': True,
                'send_cancellation': True,
            }
        )
        if created:
            print(f"  ✅ Creada para: {org.name}")
else:
    print("  ✅ Configuraciones existentes:")
    for settings in NotificationSettings.objects.all():
        print(f"\n  📱 {settings.organization.name}:")
        print(f"     Email: {'✓' if settings.email_enabled else '✗'}")
        print(f"     Twilio: {'✓' if settings.twilio_enabled else '✗'}")
        print(f"     WhatsApp Local: {'✓' if settings.local_whatsapp_enabled else '✗'}")
        print(f"     Método activo: {settings.get_active_method() or 'Ninguno'}")

# 4. Verificar Citas
print("\n📅 CITAS:")
print("-"*70)
appointments = Appointment.objects.all()
print(f"  Total de citas: {appointments.count()}")
if appointments.exists():
    recent = appointments.order_by('-created_at')[:3]
    print("  Últimas 3 citas:")
    for apt in recent:
        print(f"    • {apt.full_name} - {apt.phone_number}")
        print(f"      Fecha: {apt.appointment_date} {apt.appointment_time}")
        print(f"      Org: {apt.organization.name if apt.organization else 'N/A'}")

# 5. Verificar Modelos de la BD
print("\n🗄️  VERIFICACIÓN DE TABLAS:")
print("-"*70)
try:
    # Verificar que las tablas existan
    Organization.objects.count()
    print("  ✅ Tabla organizations_organization")
    
    NotificationSettings.objects.count()
    print("  ✅ Tabla appointments_notificationsettings")
    
    Appointment.objects.count()
    print("  ✅ Tabla appointments_appointment")
    
    User.objects.count()
    print("  ✅ Tabla auth_user")
    
except Exception as e:
    print(f"  ❌ Error: {e}")

# 6. Test del Notifier
print("\n🔔 NOTIFICADOR:")
print("-"*70)
try:
    from apps.appointments.notifications import get_notifier
    
    # Test para cada organización
    for org in orgs[:3]:  # Primeras 3
        notifier = get_notifier(org)
        print(f"  {org.name}:")
        print(f"    Tipo: {type(notifier).__name__}")
        print(f"    Habilitado: {getattr(notifier, 'enabled', 'N/A')}")
except Exception as e:
    print(f"  ⚠️  Error: {e}")

# 7. Verificar URLs
print("\n🌐 URLS DEL DASHBOARD:")
print("-"*70)
from django.urls import reverse, NoReverseMatch

urls_to_check = [
    ('dashboard:home', 'Dashboard principal'),
    ('dashboard:login', 'Login'),
    ('dashboard:configuration', 'Configuración'),
    ('dashboard:notification_settings', 'Notificaciones'),
    ('dashboard:save_notification_settings', 'Guardar notificaciones'),
    ('dashboard:test_notification', 'Test de notificación'),
]

for url_name, description in urls_to_check:
    try:
        url = reverse(url_name)
        print(f"  ✅ {description}: {url}")
    except NoReverseMatch:
        print(f"  ❌ {description}: No encontrada")

# 8. Estado de Django
print("\n⚙️  DJANGO:")
print("-"*70)
from django.conf import settings as django_settings

print(f"  Debug: {django_settings.DEBUG}")
print(f"  Base de datos: {django_settings.DATABASES['default']['ENGINE']}")
print(f"  Zona horaria: {django_settings.TIME_ZONE}")
print(f"  Idioma: {django_settings.LANGUAGE_CODE}")

# Email config
if hasattr(django_settings, 'EMAIL_HOST'):
    print(f"  Email Host: {django_settings.EMAIL_HOST}")
    print(f"  Email Port: {django_settings.EMAIL_PORT}")
    print(f"  Email configurado: {'✓' if django_settings.EMAIL_HOST_USER else '✗'}")

# Twilio config
if hasattr(django_settings, 'TWILIO_ACCOUNT_SID'):
    has_twilio = bool(django_settings.TWILIO_ACCOUNT_SID)
    print(f"  Twilio configurado: {'✓' if has_twilio else '✗'}")

# 9. Resumen Final
print("\n" + "="*70)
print("📋 RESUMEN:")
print("="*70)

issues = []
if orgs.count() == 0:
    issues.append("❌ No hay organizaciones")
else:
    print(f"✅ Organizaciones: {orgs.count()}")

if NotificationSettings.objects.count() == 0:
    issues.append("❌ No hay configuraciones de notificaciones")
else:
    print(f"✅ Configuraciones: {NotificationSettings.objects.count()}")

if users.count() == 0:
    issues.append("❌ No hay usuarios")
else:
    print(f"✅ Usuarios: {users.count()}")

print(f"ℹ️  Citas: {appointments.count()}")

if issues:
    print("\n⚠️  PROBLEMAS ENCONTRADOS:")
    for issue in issues:
        print(f"  {issue}")
else:
    print("\n🎉 ¡Todo listo para Render!")

print("\n" + "="*70)
print("🚀 PRÓXIMOS PASOS:")
print("="*70)
print("1. Ve a tu dashboard de Render")
print("2. Espera a que termine el deploy")
print("3. Configura las variables de entorno (EMAIL_HOST, etc.)")
print("4. Ejecuta los comandos del archivo SINCRONIZACION_RENDER.md")
print("5. Accede a tu app y prueba el dashboard")
print("\n" + "="*70 + "\n")

# Salir
print("Para salir de Python shell, escribe: exit()\n")
