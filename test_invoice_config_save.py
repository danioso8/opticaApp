"""
Script para verificar que la configuración de factura se guarde correctamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.billing.models import InvoiceConfiguration
from apps.organizations.models import Organization

# Obtener la primera organización
org = Organization.objects.first()

if not org:
    print("❌ No hay organizaciones en el sistema")
    exit(1)

print(f"📋 Verificando configuración para: {org.name}")
print("=" * 60)

# Obtener o crear configuración
config = InvoiceConfiguration.get_config(org)

print(f"\n✅ Configuración encontrada: ID {config.id}")
print("\n📊 VALORES ACTUALES:")
print(f"  IVA: {config.iva_porcentaje}%")
print(f"  Aplicar IVA automático: {config.aplicar_iva_automatico}")
print(f"  Descuento máximo: {config.descuento_maximo_porcentaje}%")
print(f"  Permitir descuentos: {config.permitir_descuento_items}")
print(f"  Aplicar Retefuente: {config.aplicar_retefuente} ({config.retefuente_porcentaje}%)")
print(f"  Aplicar ReteIVA: {config.aplicar_reteiva} ({config.reteiva_porcentaje}%)")
print(f"  Permitir pagos parciales: {config.permitir_pagos_parciales}")

print(f"\n📧 CONFIGURACIÓN DE EMAIL:")
print(f"  Enviar email automático: {config.enviar_email_factura}")
print(f"  Email remitente: {config.email_remitente or '(usar email de organización)'}")
print(f"  Asunto: {config.email_asunto}")
print(f"  Mensaje: {config.email_mensaje[:50]}..." if len(config.email_mensaje) > 50 else config.email_mensaje)

print("\n" + "=" * 60)
print("✅ Script completado exitosamente")
