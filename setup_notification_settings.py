"""
Script para configurar las notificaciones por defecto
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models_notifications import NotificationSettings

def setup_notifications():
    """Configura notificaciones para todas las organizaciones"""
    
    organizations = Organization.objects.all()
    print(f"Encontradas {organizations.count()} organizaciones")
    
    for org in organizations:
        # Verificar si ya existe configuración
        settings, created = NotificationSettings.objects.get_or_create(
            organization=org,
            defaults={
                # WhatsApp Local habilitado por defecto en desarrollo
                'local_whatsapp_enabled': True,
                'local_whatsapp_url': 'http://localhost:3000',
                
                # Email deshabilitado por defecto
                'email_enabled': False,
                'email_from': 'noreply@opticaapp.com',
                
                # Twilio deshabilitado por defecto
                'twilio_enabled': False,
                
                # Todas las notificaciones automáticas habilitadas
                'send_confirmation': True,
                'send_reminder': True,
                'send_cancellation': True,
            }
        )
        
        if created:
            print(f"✅ Configuración creada para {org.name}")
            print(f"   Método activo: {settings.get_active_method()}")
        else:
            print(f"ℹ️  Configuración ya existe para {org.name}")
            print(f"   Método activo: {settings.get_active_method()}")

if __name__ == '__main__':
    setup_notifications()
    print("\n✅ Configuración de notificaciones completada")
