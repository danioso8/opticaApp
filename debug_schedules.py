"""
Script para depurar horarios disponibles en producción
Ejecutar en Render Shell con: python debug_schedules.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opticaApp.settings')
django.setup()

from apps.appointments.models import SpecificDateSchedule, WorkingHours
from apps.organizations.models import Organization
from apps.patients.models import Doctor
from datetime import datetime, timedelta
from django.utils import timezone

print("=" * 60)
print("DEPURACIÓN DE HORARIOS")
print("=" * 60)

# Obtener organización
org_id = 2
try:
    org = Organization.objects.get(id=org_id)
    print(f"\n✓ Organización: {org.name} (ID: {org.id})")
except Organization.DoesNotExist:
    print(f"\n✗ No se encontró organización con ID {org_id}")
    exit()

# Listar doctores
print("\n" + "=" * 60)
print("DOCTORES DISPONIBLES")
print("=" * 60)
doctors = Doctor.objects.filter(organization=org)
for doc in doctors:
    print(f"  - ID: {doc.id} | Nombre: {doc.full_name}")

# Listar horarios específicos
print("\n" + "=" * 60)
print("HORARIOS ESPECÍFICOS (SpecificDateSchedule)")
print("=" * 60)
today = timezone.now().date()
specific_schedules = SpecificDateSchedule.objects.filter(
    organization=org,
    date__gte=today,
    is_active=True
).order_by('date', 'start_time')

if specific_schedules.exists():
    for schedule in specific_schedules:
        print(f"\n  Fecha: {schedule.date}")
        print(f"  Horario: {schedule.start_time} - {schedule.end_time}")
        print(f"  Duración slot: {schedule.slot_duration} min")
        print(f"  Doctor (profile): {schedule.doctor_profile_id} - {schedule.doctor_profile}")
        print(f"  Doctor (user - deprecated): {schedule.doctor_id} - {schedule.doctor}")
        print(f"  Activo: {schedule.is_active}")
        print(f"  Notas: {schedule.notes}")
else:
    print("  No hay horarios específicos configurados")

# Listar horarios recurrentes
print("\n" + "=" * 60)
print("HORARIOS RECURRENTES (WorkingHours)")
print("=" * 60)
working_hours = WorkingHours.objects.filter(
    organization=org,
    is_active=True
).order_by('day_of_week', 'start_time')

days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
if working_hours.exists():
    for wh in working_hours:
        print(f"  - {days[wh.day_of_week]}: {wh.start_time} - {wh.end_time}")
else:
    print("  No hay horarios recurrentes configurados")

# Simular llamada a API
print("\n" + "=" * 60)
print("SIMULACIÓN DE API")
print("=" * 60)

# Probar fecha de mañana
tomorrow = today + timedelta(days=1)
print(f"\nFecha a consultar: {tomorrow}")

# Sin filtro de doctor
print("\nSIN FILTRO DE DOCTOR:")
specific_no_filter = SpecificDateSchedule.objects.filter(
    organization=org,
    date=tomorrow,
    is_active=True
)
print(f"  Horarios encontrados: {specific_no_filter.count()}")
for s in specific_no_filter:
    print(f"    - {s.start_time} - {s.end_time} (Doctor: {s.doctor_profile_id})")

# Con filtro de doctor ID=2
print("\nCON FILTRO doctor_id=2:")
from django.db.models import Q
specific_with_filter = SpecificDateSchedule.objects.filter(
    Q(doctor_profile_id=2) | Q(doctor_id=2),
    organization=org,
    date=tomorrow,
    is_active=True
)
print(f"  Horarios encontrados: {specific_with_filter.count()}")
for s in specific_with_filter:
    print(f"    - {s.start_time} - {s.end_time} (Doctor profile: {s.doctor_profile_id}, Doctor user: {s.doctor_id})")

print("\n" + "=" * 60)
print("FIN DE DEPURACIÓN")
print("=" * 60)
