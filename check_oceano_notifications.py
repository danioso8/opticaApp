#!/usr/bin/env python
"""
Verificar configuración de notificaciones para Oceano Optico.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models_notifications import NotificationSettings

print("\n" + "="*80)
print("🔍 VERIFICACIÓN DE NOTIFICACIONES - OCEANO OPTICO")
print("="*80 + "\n")

try:
    # Buscar usuario por email
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    user = User.objects.filter(email='Oceanoptics4@gmail.com').first()
    
    if not user:
        print("❌ Usuario con email 'Oceanoptics4@gmail.com' no encontrado")
        # Intentar buscar por username
        user = User.objects.filter(username__icontains='oceano').first()
        if user:
            print(f"✅ Usuario encontrado por username: {user.username}")
        else:
            print("❌ No se encontró usuario")
            exit(1)
    else:
        print(f"✅ Usuario encontrado: {user.username} - {user.email}")
    
    # Obtener organización del usuario
    membership = user.organization_memberships.first()
    if not membership:
        print("❌ Usuario no tiene organización asignada")
        exit(1)
    
    org = membership.organization
    print(f"✅ Organización: {org.name} (ID: {org.id})")
    print(f"   Estado: {'Activo' if org.is_active else 'Inactivo'}")
    print()
    
    # Obtener configuración de notificaciones
    settings = NotificationSettings.get_settings(org)
    
    if not settings:
        print("❌ No hay configuración de notificaciones")
        print("   Creando configuración por defecto...")
        settings = NotificationSettings.objects.create(organization=org)
        print("✅ Configuración creada")
    else:
        print("✅ Configuración de notificaciones encontrada")
    
    print("\n📊 CONFIGURACIÓN ACTUAL:")
    print(f"   └─ WhatsApp Local Baileys: {'✓ Habilitado' if settings.local_whatsapp_enabled else '✗ Deshabilitado'}")
    if settings.local_whatsapp_enabled:
        print(f"      URL: {settings.local_whatsapp_url}")
    print(f"   └─ Email: {'✓ Habilitado' if settings.email_enabled else '✗ Deshabilitado'}")
    print(f"   └─ Enviar confirmación: {'✓ Sí' if settings.send_confirmation else '✗ No'}")
    print(f"   └─ Enviar recordatorios: {'✓ Sí' if settings.send_reminder else '✗ No'}")
    print(f"   └─ Enviar cancelaciones: {'✓ Sí' if settings.send_cancellation else '✗ No'}")
    print(f"   └─ Método activo: {settings.get_active_method()}")
    
    # Verificar servidor WhatsApp
    if settings.local_whatsapp_enabled:
        print("\n🔍 Verificando servidor WhatsApp...")
        import requests
        try:
            response = requests.get('http://localhost:3000/status', timeout=2)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Servidor WhatsApp: {data.get('status', 'running')}")
                print(f"   📱 Conexión: {data.get('connection', 'desconocido')}")
            else:
                print(f"   ⚠️  Servidor respondió con código {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("   ❌ Servidor WhatsApp no está respondiendo en localhost:3000")
        except Exception as e:
            print(f"   ❌ Error al conectar: {str(e)}")
    
    # Verificar última cita
    from apps.appointments.models import Appointment
    last_appointment = Appointment.objects.filter(
        organization=org
    ).order_by('-created_at').first()
    
    if last_appointment:
        print(f"\n📅 Última cita agendada:")
        print(f"   └─ Paciente: {last_appointment.full_name}")
        print(f"   └─ Teléfono: {last_appointment.phone_number}")
        print(f"   └─ Fecha: {last_appointment.appointment_date} {last_appointment.appointment_time}")
        print(f"   └─ Creada: {last_appointment.created_at}")
    
    print("\n" + "="*80)
    
    # Sugerencias
    if not settings.local_whatsapp_enabled and not settings.email_enabled:
        print("\n⚠️  PROBLEMA: No hay ningún método de notificación habilitado")
        print("   Solución: Habilita al menos un método en /dashboard/notifications/settings/")
    
    if not settings.send_confirmation:
        print("\n⚠️  ADVERTENCIA: Confirmaciones de citas deshabilitadas")
        print("   Las notificaciones NO se enviarán al agendar")
    
    print()

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
