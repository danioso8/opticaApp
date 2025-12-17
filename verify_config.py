"""
Script para verificar los valores guardados en InvoiceConfiguration
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.billing.models import InvoiceConfiguration
from apps.organizations.models import Organization

print("=" * 80)
print("VERIFICACIÓN DE CONFIGURACIONES GUARDADAS")
print("=" * 80)

# Obtener todas las organizaciones
orgs = Organization.objects.filter(is_active=True)

for org in orgs:
    print(f"\n🏢 ORGANIZACIÓN: {org.name}")
    print("-" * 80)
    
    # Obtener configuración
    try:
        config = InvoiceConfiguration.objects.filter(organization=org).first()
        
        if not config:
            print("   ❌ No tiene configuración de facturación")
            continue
        
        print(f"\n   📊 CONFIGURACIÓN BÁSICA:")
        print(f"      IVA: {config.iva_porcentaje}%")
        print(f"      Aplicar IVA automático: {config.aplicar_iva_automatico}")
        print(f"      Descuento máximo: {config.descuento_maximo_porcentaje}%")
        print(f"      Permitir descuentos: {config.permitir_descuento_items}")
        print(f"      Retefuente: {config.aplicar_retefuente} ({config.retefuente_porcentaje}%)")
        print(f"      ReteIVA: {config.aplicar_reteiva} ({config.reteiva_porcentaje}%)")
        
        print(f"\n   📧 CONFIGURACIÓN DE EMAIL:")
        print(f"      Enviar email automático: {config.enviar_email_factura}")
        print(f"      Email remitente: '{config.email_remitente}'")
        print(f"      Asunto: '{config.email_asunto}'")
        print(f"      Mensaje: '{config.email_mensaje[:50]}...'")
        
        print(f"\n   🔧 CONFIGURACIÓN SMTP:")
        print(f"      Host: '{config.smtp_host}'")
        print(f"      Puerto: {config.smtp_port}")
        print(f"      Usuario: '{config.smtp_username}'")
        print(f"      Contraseña: {'*' * 10 if config.smtp_password else '(vacía)'}")
        print(f"      Usar TLS: {config.smtp_use_tls}")
        
        # Verificar si está completa
        smtp_completo = all([
            config.smtp_host,
            config.smtp_port,
            config.smtp_username,
            config.smtp_password
        ])
        
        print(f"\n   {'✅' if smtp_completo else '⚠️'} Configuración SMTP: {'COMPLETA' if smtp_completo else 'INCOMPLETA'}")
        
    except Exception as e:
        print(f"   ❌ Error al obtener configuración: {e}")

print("\n" + "=" * 80)
print("VERIFICACIÓN COMPLETADA")
print("=" * 80)
