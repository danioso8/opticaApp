"""
Script para agregar fechas específicas de prueba automáticamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models import SpecificDateSchedule
from datetime import datetime, timedelta, time
from django.utils import timezone

def main():
    # Obtener la organización activa
    org = Organization.objects.filter(is_active=True).first()
    
    if not org:
        print("❌ No hay organizaciones activas")
        return
    
    print(f"✅ Organización: {org.name} (ID: {org.id})")
    
    # Verificar fechas existentes
    existing_count = SpecificDateSchedule.objects.filter(
        organization=org,
        date__gte=timezone.now().date()
    ).count()
    
    print(f"📅 Fechas específicas existentes: {existing_count}")
    
    today = timezone.now().date()
    dates_added = 0
    
    print("\n🔧 Agregando fechas de prueba para los próximos 30 días...")
    
    # Agregar fechas de lunes a viernes por los próximos 30 días
    for i in range(1, 31):
        date = today + timedelta(days=i)
        
        # Solo días de lunes a viernes (0 = lunes, 4 = viernes)
        if date.weekday() < 5:
            # Verificar si ya existen horarios para esta fecha
            existing = SpecificDateSchedule.objects.filter(
                organization=org,
                date=date
            ).exists()
            
            if not existing:
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
    
    print(f"\n✅ Se agregaron {dates_added} horarios nuevos")
    
    # Mostrar resumen
    total_schedules = SpecificDateSchedule.objects.filter(
        organization=org,
        date__gte=today,
        is_active=True
    ).order_by('date')
    
    print(f"📊 Total de horarios disponibles: {total_schedules.count()}")
    print(f"📆 Días con agenda: {total_schedules.values('date').distinct().count()}")
    
    if total_schedules.exists():
        print("\n📋 Próximas fechas disponibles:")
        unique_dates = total_schedules.values('date').distinct()[:10]
        for item in unique_dates:
            date = item['date']
            day_name = date.strftime('%A')
            date_formatted = date.strftime('%d/%m/%Y')
            print(f"  - {day_name.capitalize()}: {date_formatted}")

if __name__ == '__main__':
    main()
