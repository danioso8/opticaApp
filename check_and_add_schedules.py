"""
Script para verificar y agregar fechas específicas para pruebas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models import SpecificDateSchedule
from datetime import datetime, timedelta
from django.utils import timezone

def main():
    # Obtener la organización activa
    org = Organization.objects.filter(is_active=True).first()
    
    if not org:
        print("❌ No hay organizaciones activas")
        return
    
    print(f"✅ Organización encontrada: {org.name} (ID: {org.id})")
    
    # Verificar fechas específicas existentes
    existing_schedules = SpecificDateSchedule.objects.filter(
        organization=org,
        date__gte=timezone.now().date()
    ).order_by('date')
    
    print(f"\n📅 Fechas específicas existentes: {existing_schedules.count()}")
    
    if existing_schedules.exists():
        print("\nFechas configuradas:")
        for schedule in existing_schedules[:10]:
            print(f"  - {schedule.date} de {schedule.start_time} a {schedule.end_time}")
        
        if existing_schedules.count() < 10:
            print(f"\n⚠️  Solo hay {existing_schedules.count()} fecha(s) configurada(s)")
            print("¿Deseas agregar más fechas de prueba? (s/n): ", end="")
            response = input().lower().strip()
            
            if response == 's':
                add_test_schedules(org)
    else:
        print("\n⚠️  No hay fechas específicas configuradas")
        print("¿Deseas agregar fechas de prueba? (s/n): ", end="")
        response = input().lower().strip()
        
        if response == 's':
            add_test_schedules(org)

def add_test_schedules(org):
    """Agregar fechas de prueba para los próximos 30 días"""
    from datetime import time
    
    today = timezone.now().date()
    dates_added = 0
    
    print("\n🔧 Agregando fechas de prueba...")
    
    # Agregar fechas de lunes a viernes por los próximos 30 días
    for i in range(1, 31):
        date = today + timedelta(days=i)
        
        # Solo días de lunes a viernes (0 = lunes, 4 = viernes)
        if date.weekday() < 5:
            # Crear dos turnos: mañana (9-13) y tarde (15-19)
            schedules = [
                SpecificDateSchedule(
                    organization=org,
                    date=date,
                    start_time=time(9, 0),
                    end_time=time(13, 0),
                    is_active=True
                ),
                SpecificDateSchedule(
                    organization=org,
                    date=date,
                    start_time=time(15, 0),
                    end_time=time(19, 0),
                    is_active=True
                )
            ]
            
            for schedule in schedules:
                schedule.save()
                dates_added += 1
    
    print(f"✅ Se agregaron {dates_added} horarios de prueba")
    print(f"   Días laborables: Lunes a Viernes")
    print(f"   Turnos: 9:00-13:00 y 15:00-19:00")

if __name__ == '__main__':
    main()
