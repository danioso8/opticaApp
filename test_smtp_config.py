"""
Script para probar el envío de emails con configuración SMTP por organización
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.billing.models import InvoiceConfiguration
from apps.billing.email_service import EmailService
from apps.organizations.models import Organization

# Obtener primera organización
org = Organization.objects.first()

if not org:
    print("❌ No hay organizaciones en el sistema")
    exit(1)

print(f"🏢 Organización: {org.name}")
print("=" * 60)

# Obtener configuración
config = InvoiceConfiguration.get_config(org)

print(f"\n📧 CONFIGURACIÓN SMTP:")
print(f"  Servidor: {config.smtp_host}")
print(f"  Puerto: {config.smtp_port}")
print(f"  TLS: {config.smtp_use_tls}")
print(f"  Usuario: {config.smtp_username}")
print(f"  Contraseña: {'*' * len(config.smtp_password) if config.smtp_password else '(no configurada)'}")
print(f"  Email remitente: {config.email_remitente}")

print(f"\n✉️ CONFIGURACIÓN DE EMAILS:")
print(f"  Enviar automático: {config.enviar_email_factura}")
print(f"  Asunto: {config.email_asunto}")
print(f"  Mensaje: {config.email_mensaje[:50]}...")

# Validar configuración SMTP
if not all([config.smtp_host, config.smtp_port, config.smtp_username, config.smtp_password]):
    print("\n❌ CONFIGURACIÓN SMTP INCOMPLETA")
    print("   Por favor complete todos los campos SMTP en la configuración de facturación")
    exit(1)

print("\n" + "=" * 60)
print("🔍 PROBANDO CONEXIÓN SMTP...")
print("=" * 60)

# Crear servicio de email
email_service = EmailService(config)

# Probar conexión
success, message = email_service.probar_conexion()

if success:
    print(f"\n✅ {message}")
    print("\n💡 La configuración SMTP está correcta y lista para usar")
    print(f"   Los emails se enviarán desde: {config.email_remitente or config.smtp_username}")
else:
    print(f"\n❌ {message}")
    print("\n💡 Verifica:")
    print("   1. El servidor SMTP y puerto son correctos")
    print("   2. El usuario (email) es correcto")
    print("   3. La contraseña es correcta (usa contraseña de aplicación para Gmail)")
    print("   4. TLS está activado si usas puerto 587")

print("\n" + "=" * 60)
