"""
Script para configurar horarios de trabajo para CompuEasys
"""
import os
import django
from datetime import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models import WorkingHours

def setup_compueasys_schedule():
    """Configurar horarios de trabajo para CompuEasys"""
    print("⚙️ Configurando horarios para CompuEasys...\n")
    
    # Buscar CompuEasys
    try:
        org = Organization.objects.get(slug='compueasys')
        print(f"✅ Organización: {org.name}\n")
    except Organization.DoesNotExist:
        print("❌ CompuEasys no encontrada")
        return
    
    # Definir horarios (Lunes a Viernes: 9:00 AM - 6:00 PM, Sábado: 9:00 AM - 1:00 PM)
    schedules = [
        # Lunes a Viernes
        {'day': 0, 'name': 'Lunes', 'start': time(9, 0), 'end': time(18, 0)},
        {'day': 1, 'name': 'Martes', 'start': time(9, 0), 'end': time(18, 0)},
        {'day': 2, 'name': 'Miércoles', 'start': time(9, 0), 'end': time(18, 0)},
        {'day': 3, 'name': 'Jueves', 'start': time(9, 0), 'end': time(18, 0)},
        {'day': 4, 'name': 'Viernes', 'start': time(9, 0), 'end': time(18, 0)},
        # Sábado
        {'day': 5, 'name': 'Sábado', 'start': time(9, 0), 'end': time(13, 0)},
    ]
    
    created_count = 0
    updated_count = 0
    
    for schedule in schedules:
        wh, created = WorkingHours.objects.get_or_create(
            organization=org,
            day_of_week=schedule['day'],
            defaults={
                'start_time': schedule['start'],
                'end_time': schedule['end'],
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ {schedule['name']}: {schedule['start']} - {schedule['end']} (creado)")
            created_count += 1
        else:
            # Actualizar si ya existe
            wh.start_time = schedule['start']
            wh.end_time = schedule['end']
            wh.is_active = True
            wh.save()
            print(f"🔄 {schedule['name']}: {schedule['start']} - {schedule['end']} (actualizado)")
            updated_count += 1
    
    print(f"\n📊 Resumen:")
    print(f"   Creados: {created_count}")
    print(f"   Actualizados: {updated_count}")
    print(f"   Total: {created_count + updated_count}")
    print(f"\n✅ ¡Horarios configurados exitosamente!")
    print(f"🌐 Ahora CompuEasys tendrá horarios disponibles para agendar citas")

if __name__ == '__main__':
    setup_compueasys_schedule()
