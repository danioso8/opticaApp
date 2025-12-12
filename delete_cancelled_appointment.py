"""
Script para eliminar cita cancelada específica
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models import Appointment
from datetime import date, time

# Buscar la cita cancelada
cita = Appointment.objects.filter(
    organization_id=2,
    appointment_date='2025-12-20',
    appointment_time='14:40:00'
).first()

if cita:
    print(f"Cita encontrada:")
    print(f"  - Paciente: {cita.full_name}")
    print(f"  - Estado: {cita.status}")
    print(f"  - Fecha: {cita.appointment_date}")
    print(f"  - Hora: {cita.appointment_time}")
    
    if cita.status == 'cancelled':
        cita.delete()
        print("\n✓ Cita cancelada eliminada exitosamente")
        print("Ahora puedes crear una nueva cita en ese horario")
    else:
        print(f"\n⚠ La cita NO está cancelada (Estado: {cita.status})")
        print("No se puede eliminar")
else:
    print("No se encontró ninguna cita en ese horario")
