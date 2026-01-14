#!/usr/bin/env python
"""
Script para verificar el estado de WhatsApp de Oceano Optico
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/var/www/opticaapp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opticaapp.settings')
django.setup()

from apps.organizations.models import Organization
from apps.whatsapp.models import WhatsAppConnection

# Buscar Oceano Optico
try:
    org = Organization.objects.get(name__icontains='oceano')
    print(f"✅ Organización encontrada:")
    print(f"   ID: {org.id}")
    print(f"   Nombre: {org.name}")
    print(f"   Email: {org.owner.email if org.owner else 'Sin dueño'}")
    print(f"   Plan: {org.subscription_plan.name if org.subscription_plan else 'Sin plan'}")
    print(f"   Activa: {org.is_active}")
    print()
    
    # Buscar conexión de WhatsApp
    try:
        connection = WhatsAppConnection.objects.get(organization=org)
        print(f"📱 WhatsApp Connection:")
        print(f"   ID: {connection.id}")
        print(f"   Conectado: {connection.is_connected}")
        print(f"   Número: {connection.phone_number or 'No configurado'}")
        print(f"   Última actualización: {connection.updated_at}")
        print(f"   Session ID: {connection.session_id or 'Sin sesión'}")
        
        # Verificar si hay archivos de sesión
        session_path = f"/var/www/opticaapp/whatsapp-server/auth_sessions/{org.id}"
        print(f"\n📁 Ruta de sesión: {session_path}")
        
    except WhatsAppConnection.DoesNotExist:
        print("⚠️  No hay conexión de WhatsApp registrada para esta organización")
        
except Organization.DoesNotExist:
    print("❌ No se encontró la organización Oceano Optico")
except Exception as e:
    print(f"❌ Error: {e}")
