import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models import Appointment
from apps.patients.models import Doctor

print('=== Últimas 5 citas ===')
citas = Appointment.objects.order_by('-created_at')[:5]
for a in citas:
    doctor_name = a.doctor.full_name if a.doctor else "SIN ASIGNAR"
    print(f'ID: {a.id} | Paciente: {a.full_name} | Doctor: {doctor_name} | Fecha: {a.appointment_date} {a.appointment_time} | Org: {a.organization_id}')

print('\n=== Doctores disponibles ===')
doctores = Doctor.objects.all()
for d in doctores:
    print(f'ID: {d.id} | Nombre: {d.full_name} | Org: {d.organization_id}')

print('\n=== Buscando cita sin doctor asignado ===')
cita_sin_doctor = Appointment.objects.filter(doctor__isnull=True).order_by('-created_at').first()
if cita_sin_doctor:
    print(f'Encontrada: ID {cita_sin_doctor.id} | Paciente: {cita_sin_doctor.full_name} | Org: {cita_sin_doctor.organization_id}')
    
    # Buscar doctor Daniel Osorio
    daniel = Doctor.objects.filter(full_name__icontains='Daniel').first()
    if daniel:
        print(f'\nAsignando doctor: {daniel.full_name} (ID: {daniel.id})')
        cita_sin_doctor.doctor = daniel
        cita_sin_doctor.save()
        print('✓ Doctor asignado exitosamente')
    else:
        print('No se encontró al doctor Daniel Osorio')
else:
    print('No hay citas sin doctor asignado')
