"""
Script para revisar todas las citas del 20 de diciembre
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models import Appointment

# Buscar todas las citas del 20 de diciembre
citas = Appointment.objects.filter(
    organization_id=2,
    appointment_date='2025-12-20'
).order_by('appointment_time')

print(f"=== Citas del 20 de Diciembre 2025 - Organización #2 ===\n")

if citas.exists():
    for cita in citas:
        print(f"ID: {cita.id}")
        print(f"  Paciente: {cita.full_name}")
        print(f"  Hora: {cita.appointment_time}")
        print(f"  Estado: {cita.status}")
        print(f"  Teléfono: {cita.phone_number}")
        print("-" * 50)
else:
    print("No hay citas registradas para esa fecha")

print(f"\nTotal: {citas.count()} citas")
