"""
Script de ejemplo para configurar horarios de landing page desde código
Úsalo como referencia o ejecútalo para actualizar configuraciones específicas
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import LandingPageConfig, Organization

def ejemplo_configurar_horarios():
    """
    Ejemplo de cómo configurar los horarios para una landing page específica
    """
    
    # Obtener una organización (ajusta el nombre según tu necesidad)
    org_name = "Oceano Optico"
    
    try:
        org = Organization.objects.get(name=org_name)
        
        # Obtener o crear la configuración de landing page
        config, created = LandingPageConfig.objects.get_or_create(organization=org)
        
        if created:
            print(f"✅ Se creó una nueva configuración para {org_name}")
        else:
            print(f"📝 Actualizando configuración existente para {org_name}")
        
        # Configurar horarios de atención
        config.schedule_weekday_start = "9:00 AM"
        config.schedule_weekday_end = "6:00 PM"
        config.schedule_saturday_start = "10:00 AM"
        config.schedule_saturday_end = "2:00 PM"
        config.schedule_sunday_closed = True  # Cerrado los domingos
        
        # Activar horario de almuerzo
        config.has_lunch_break = True
        config.lunch_break_start = "12:00 PM"
        config.lunch_break_end = "1:00 PM"
        
        # Guardar cambios
        config.save()
        
        print(f"\n✅ Horarios actualizados exitosamente para {org_name}")
        print("\n📅 Configuración aplicada:")
        print(f"   Lunes - Viernes: {config.schedule_weekday_start} - {config.schedule_weekday_end}")
        print(f"   Sábado: {config.schedule_saturday_start} - {config.schedule_saturday_end}")
        print(f"   Domingo: {'Cerrado' if config.schedule_sunday_closed else f'{config.schedule_sunday_start} - {config.schedule_sunday_end}'}")
        print(f"\n🍽️  Horario de Almuerzo:")
        print(f"   {'Activado' if config.has_lunch_break else 'Desactivado'}")
        if config.has_lunch_break:
            print(f"   {config.lunch_break_start} - {config.lunch_break_end}")
        
    except Organization.DoesNotExist:
        print(f"❌ Error: No se encontró la organización '{org_name}'")
        print("\n📋 Organizaciones disponibles:")
        for org in Organization.objects.all():
            print(f"   - {org.name}")

def ejemplo_configurar_sin_almuerzo():
    """
    Ejemplo de configuración sin horario de almuerzo (atención continua)
    """
    
    org_name = "CompuEasys"
    
    try:
        org = Organization.objects.get(name=org_name)
        config, created = LandingPageConfig.objects.get_or_create(organization=org)
        
        # Configurar horarios sin cierre de almuerzo
        config.schedule_weekday_start = "8:00 AM"
        config.schedule_weekday_end = "8:00 PM"
        config.schedule_saturday_start = "9:00 AM"
        config.schedule_saturday_end = "5:00 PM"
        config.schedule_sunday_closed = False  # Abierto los domingos
        config.schedule_sunday_start = "10:00 AM"
        config.schedule_sunday_end = "2:00 PM"
        
        # Desactivar horario de almuerzo
        config.has_lunch_break = False
        
        config.save()
        
        print(f"\n✅ Configuración sin horario de almuerzo aplicada para {org_name}")
        
    except Organization.DoesNotExist:
        print(f"❌ Error: No se encontró la organización '{org_name}'")


if __name__ == '__main__':
    print("=" * 80)
    print("CONFIGURACIÓN DE HORARIOS - EJEMPLOS")
    print("=" * 80)
    
    print("\n1️⃣  Ejemplo 1: Configuración con horario de almuerzo")
    print("-" * 80)
    ejemplo_configurar_horarios()
    
    print("\n\n2️⃣  Ejemplo 2: Configuración sin horario de almuerzo")
    print("-" * 80)
    ejemplo_configurar_sin_almuerzo()
    
    print("\n" + "=" * 80)
    print("💡 TIP: Estos ejemplos muestran cómo configurar los horarios desde código.")
    print("    También puedes hacerlo desde el panel de administración de Django.")
    print("=" * 80)
