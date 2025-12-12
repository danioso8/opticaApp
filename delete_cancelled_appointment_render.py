"""
Script para eliminar cita cancelada - EJECUTAR EN RENDER SHELL
Uso: python delete_cancelled_appointment_render.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models import Appointment

# Buscar la cita que está bloqueando el horario
cita = Appointment.objects.filter(
    organization_id=2,
    appointment_date='2025-12-20',
    appointment_time='14:40:00'
).first()

if cita:
    print(f"\n=== CITA ENCONTRADA ===")
    print(f"ID: {cita.id}")
    print(f"Paciente: {cita.full_name}")
    print(f"Estado: {cita.status}")
    print(f"Fecha: {cita.appointment_date}")
    print(f"Hora: {cita.appointment_time}")
    print(f"Teléfono: {cita.phone_number}")
    
    if cita.status == 'cancelled':
        confirmacion = input("\n¿Eliminar esta cita cancelada? (si/no): ")
        if confirmacion.lower() == 'si':
            cita.delete()
            print("\n✓ Cita eliminada exitosamente")
            print("Ahora puedes crear una nueva cita en ese horario")
        else:
            print("Operación cancelada")
    else:
        print(f"\n⚠ ADVERTENCIA: La cita NO está cancelada")
        print(f"Estado actual: {cita.status}")
        print("\nOpciones:")
        print("1. Si quieres eliminarla de todas formas, descomenta la línea cita.delete()")
        print("2. Si quieres cancelarla primero: cita.status = 'cancelled'; cita.save()")
        # cita.delete()  # Descomenta esta línea si quieres forzar la eliminación
else:
    print("\n✗ No se encontró ninguna cita en ese horario")
    print("\nVerificando todas las citas del 20/12/2025...")
    
    todas = Appointment.objects.filter(
        organization_id=2,
        appointment_date='2025-12-20'
    ).order_by('appointment_time')
    
    if todas.exists():
        print(f"\nSe encontraron {todas.count()} citas:")
        for c in todas:
            print(f"  - {c.appointment_time} | {c.full_name} | Estado: {c.status}")
    else:
        print("No hay citas para esa fecha")
