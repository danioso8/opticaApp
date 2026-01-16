#!/usr/bin/env python3
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models import SpecificDateSchedule, AppointmentConfiguration
from apps.patients.models import Doctor
from datetime import date, datetime, timedelta

print("="*70)
print("CONFIGURAR FECHAS PARA COMPUEASYS2")
print("="*70)

org = Organization.objects.get(slug='compueasys2')
print(f"\nOrganización: {org.name} (ID: {org.id})")

# Configuración
config, created = AppointmentConfiguration.objects.get_or_create(
    organization=org,
    defaults={
        'is_open': True,
        'max_days_in_advance': 60,
        'appointment_duration': 30,
        'allow_cancel_hours_before': 24
    }
)

if not config.is_open:
    config.is_open = True
    config.save()

print(f"Config: {'Creada' if created else 'Existe'} - Abierto: {config.is_open}")

# Doctor
doctor = Doctor.objects.filter(organization=org).first()
print(f"Doctor: {doctor.full_name if doctor else 'Sin doctor'}")

# Crear fechas
today = date.today()
start_date = today + timedelta(days=1)
end_date = start_date + timedelta(days=60)

schedules = [
    {'day': 0, 'start': '08:00', 'end': '12:00', 'slot': 30},
    {'day': 1, 'start': '08:00', 'end': '12:00', 'slot': 30},
    {'day': 2, 'start': '08:00', 'end': '12:00', 'slot': 30},
    {'day': 3, 'start': '08:00', 'end': '12:00', 'slot': 30},
    {'day': 4, 'start': '08:00', 'end': '12:00', 'slot': 30},
    {'day': 5, 'start': '09:00', 'end': '13:00', 'slot': 30},
]

created = 0
current = start_date

while current <= end_date:
    if current.weekday() < 6:
        schedule = next((s for s in schedules if s['day'] == current.weekday()), None)
        if schedule:
            existing = SpecificDateSchedule.objects.filter(
                organization=org,
                date=current,
                is_active=True
            ).first()
            
            if not existing:
                SpecificDateSchedule.objects.create(
                    organization=org,
                    doctor_profile=doctor,
                    date=current,
                    start_time=datetime.strptime(schedule['start'], '%H:%M').time(),
                    end_time=datetime.strptime(schedule['end'], '%H:%M').time(),
                    slot_duration=schedule['slot'],
                    is_active=True
                )
                created += 1
    
    current += timedelta(days=1)

total = SpecificDateSchedule.objects.filter(
    organization=org,
    date__gte=today,
    is_active=True
).count()

print(f"\nCreadas: {created}")
print(f"Total disponibles: {total}")
print(f"\nURL: https://optikaapp.com/booking/{org.slug}")
print("="*70)
