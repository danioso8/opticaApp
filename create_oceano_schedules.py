#!/usr/bin/env python
"""
Script para crear horarios de trabajo para OCÉANO ÓPTICO
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models import WorkingHours, AppointmentConfiguration
from datetime import time

def create_schedules():
    """Crear horarios de trabajo"""
    print("=" * 70)
    print("⏰ CREANDO HORARIOS PARA OCÉANO ÓPTICO")
    print("=" * 70)
    print()
    
    org = Organization.objects.get(id=4, name='OCÉANO ÓPTICO')
    print(f"✅ Organización: {org.name} (ID: {org.id})")
    print()
    
    # Configuración de citas
    config, created = AppointmentConfiguration.objects.get_or_create(
        organization=org,
        defaults={
            'is_open': True,
            'appointment_duration': 30,
            'days_in_advance': 30,
            'allow_same_day': True,
            'max_appointments_per_day': 20
        }
    )
    if created:
        print(f"✅ Configuración de citas creada")
    else:
        config.is_open = True
        config.save()
        print(f"✅ Configuración de citas actualizada (Sistema abierto)")
    print()
    
    # Horarios de trabajo (Lunes a Viernes: 8:00 - 18:00, Sábado: 8:00 - 14:00)
    schedules = [
        # Lunes a Viernes
        {'day': 0, 'start': '08:00', 'end': '18:00'},  # Lunes
        {'day': 1, 'start': '08:00', 'end': '18:00'},  # Martes
        {'day': 2, 'start': '08:00', 'end': '18:00'},  # Miércoles
        {'day': 3, 'start': '08:00', 'end': '18:00'},  # Jueves
        {'day': 4, 'start': '08:00', 'end': '18:00'},  # Viernes
        {'day': 5, 'start': '08:00', 'end': '14:00'},  # Sábado
    ]
    
    days_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    print("⏰ Creando horarios de trabajo:")
    for schedule in schedules:
        hour, created = WorkingHours.objects.get_or_create(
            organization=org,
            day_of_week=schedule['day'],
            defaults={
                'start_time': schedule['start'],
                'end_time': schedule['end'],
                'is_active': True
            }
        )
        if created:
            print(f"   ✅ {days_names[schedule['day']]}: {schedule['start']} - {schedule['end']}")
        else:
            hour.start_time = schedule['start']
            hour.end_time = schedule['end']
            hour.is_active = True
            hour.save()
            print(f"   🔄 {days_names[schedule['day']]}: {schedule['start']} - {schedule['end']} (actualizado)")
    
    print()
    print("=" * 70)
    print("✅ HORARIOS CREADOS CORRECTAMENTE")
    print("=" * 70)
    print()
    print("📋 Resumen:")
    print(f"   Organización: {org.name}")
    print(f"   Sistema: {'🟢 Abierto' if config.is_open else '🔴 Cerrado'}")
    print(f"   Horarios activos: {WorkingHours.objects.filter(organization=org, is_active=True).count()}")
    print(f"   Duración cita: {config.appointment_duration} min")
    print(f"   Días adelante: {config.days_in_advance}")
    print("=" * 70)

if __name__ == '__main__':
    create_schedules()
