"""
Script para verificar configuración de notificaciones
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models_notifications import NotificationSettings
from apps.organizations.models import Organization

def check_settings():
    """Verifica la configuración de notificaciones"""
    
    print("\n" + "="*60)
    print("CONFIGURACIÓN DE NOTIFICACIONES")
    print("="*60 + "\n")
    
    organizations = Organization.objects.all()
    
    for org in organizations:
        print(f"\n📋 Organización: {org.name} (ID: {org.id})")
        print("-" * 60)
        
        try:
            settings = NotificationSettings.get_settings(org)
            
            if not settings:
                print("❌ No hay configuración de notificaciones")
                print("   Creando configuración por defecto...")
                settings = NotificationSettings.objects.create(organization=org)
                print("   ✅ Configuración creada")
            
            print(f"\n   Método activo: {settings.get_active_method()}")
            print(f"   WhatsApp Local (Baileys): {'✅' if settings.local_whatsapp_enabled else '❌'}")
            print(f"   Email: {'✅' if settings.email_enabled else '❌'}")
            
            print(f"\n   📨 Tipos de notificaciones habilitadas:")
            print(f"      Confirmación: {'✅' if settings.send_confirmation else '❌'}")
            print(f"      Recordatorio: {'✅' if settings.send_reminder else '❌'}")
            print(f"      Cancelación: {'✅' if settings.send_cancellation else '❌'}")
            
            print(f"\n   ⏰ Configuración:")
            print(f"      Minutos antes de llegar: {settings.arrival_minutes_before}")
            print(f"      Horas de recordatorio: {settings.reminder_hours_before}")
            
            if settings.confirmation_message_template:
                print(f"\n   📝 Plantilla de confirmación personalizada: Sí")
            else:
                print(f"\n   📝 Plantilla de confirmación personalizada: No (usando predeterminada)")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    check_settings()
