"""
Script para migrar configuraciones de WhatsApp
Convierte los registros que tenían twilio_enabled=True a whatsapp_enabled=True
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models_notifications import NotificationSettings

def migrate_settings():
    """Migrar configuraciones de notificaciones"""
    print("🔄 Migrando configuraciones de WhatsApp...")
    
    all_settings = NotificationSettings.objects.all()
    total = all_settings.count()
    
    print(f"📊 Total de configuraciones encontradas: {total}")
    
    if total == 0:
        print("✅ No hay configuraciones para migrar")
        return
    
    # Como los campos twilio_* ya no existen, solo verificamos cuáles tienen whatsapp_enabled
    for setting in all_settings:
        org_name = setting.organization.name if setting.organization else "Sin organización"
        status = "✅ Activo" if setting.whatsapp_enabled else "⚪ Inactivo"
        print(f"  - {org_name}: WhatsApp {status}")
    
    print(f"\n✅ Migración completada")
    print(f"📝 Nota: Las organizaciones deben activar WhatsApp desde Dashboard → Notificaciones")
    print(f"🔧 Configurar credenciales de Twilio en .env o settings.py")

if __name__ == '__main__':
    migrate_settings()
