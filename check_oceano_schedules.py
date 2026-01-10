import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models import WorkingHours, SpecificSchedule

# Buscar OCÉANO ÓPTICO
orgs = Organization.objects.filter(name__icontains='OCÉANO')
if orgs.exists():
    for org in orgs:
        print(f"\n=== {org.name} ===")
        print(f"ID: {org.id}")
        
        # Horarios regulares
        regular_hours = WorkingHours.objects.filter(organization=org)
        print(f"\n📅 Horarios Regulares: {regular_hours.count()}")
        for wh in regular_hours:
            print(f"  {wh.get_day_display()}: {wh.start_time} - {wh.end_time} ({wh.slot_duration} min) - Activo: {wh.is_active}")
        
        # Horarios específicos
        specific_schedules = SpecificSchedule.objects.filter(organization=org)
        print(f"\n📆 Horarios Específicos: {specific_schedules.count()}")
        for ss in specific_schedules:
            print(f"  {ss.date}: {ss.start_time} - {ss.end_time} - Activo: {ss.is_active}")
else:
    print("No se encontró OCÉANO ÓPTICO")
