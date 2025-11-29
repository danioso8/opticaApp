import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models import SpecificDateSchedule
from django.utils import timezone

print("=" * 60)
print("VERIFICACIÓN DE HORARIOS ESPECÍFICOS")
print("=" * 60)

schedules = SpecificDateSchedule.objects.all()
print(f"\nTotal de horarios específicos: {schedules.count()}")

if schedules.exists():
    print("\nHorarios configurados:")
    for schedule in schedules:
        print(f"  - {schedule.date.strftime('%d/%m/%Y (%A)')} | {schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')} | Activo: {schedule.is_active}")
        if schedule.notes:
            print(f"    Notas: {schedule.notes}")
else:
    print("\n⚠️  NO HAY HORARIOS ESPECÍFICOS CONFIGURADOS")
    print("\nPara agregar horarios, ve a:")
    print("http://127.0.0.1:8000/dashboard/configuration/")
    print("\nO ejecuta el script setup_specific_dates.py:")
    print("python setup_specific_dates.py")

print("\n" + "=" * 60)
