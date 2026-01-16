#!/usr/bin/env python3
"""
Script para limpiar todas las sesiones de WhatsApp y empezar de cero
Esto permite que los usuarios escaneen el QR nuevamente con sesiones limpias
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.whatsapp_baileys_client import whatsapp_baileys_client
import json

print("\n" + "="*70)
print("🧹 LIMPIEZA DE SESIONES DE WHATSAPP")
print("="*70)

# Organizaciones a limpiar
organizations = [2, 4]

for org_id in organizations:
    print(f"\n📋 Limpiando sesión para organización {org_id}...")
    
    try:
        # 1. Obtener estado actual
        status = whatsapp_baileys_client.get_status(org_id)
        if status:
            print(f"   Estado actual: {status.get('status')}")
            print(f"   Conectado: {status.get('connected')}")
            print(f"   Teléfono: {status.get('phone_number', 'N/A')}")
        
        # 2. Forzar limpieza de sesión
        print(f"   🔧 Ejecutando limpieza forzada...")
        result = whatsapp_baileys_client.force_clean_session(org_id)
        
        if result and result.get('success'):
            print(f"   ✅ Sesión limpiada exitosamente")
            print(f"   💡 El usuario debe escanear el código QR en el módulo de WhatsApp")
        else:
            error = result.get('error') if result else 'Sin respuesta'
            print(f"   ⚠️  Limpieza completada con advertencias: {error}")
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

print("\n" + "="*70)
print("✅ PROCESO COMPLETADO")
print("="*70)
print("\n📱 SIGUIENTES PASOS:")
print("   1. Ir a https://www.optikaapp.com/dashboard/whatsapp-baileys/")
print("   2. Escanear el código QR con WhatsApp")
print("   3. Una vez conectado, el sistema mantendrá la sesión automáticamente")
print("   4. No será necesario volver a escanear después de reinicios del servidor")
print("\n")
