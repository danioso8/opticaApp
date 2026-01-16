#!/usr/bin/env python3
"""
Script para configurar fechas de booking en producción
Ejecutar en el servidor: python3 fix_compueasys_booking_prod.py
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, '/var/www/opticaapp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.appointments.models import SpecificDateSchedule, AppointmentConfiguration
from apps.patients.models import Doctor
from datetime import date, datetime, time, timedelta

print("="*70)
print("CONFIGURAR FECHAS DE BOOKING - PRODUCCIÓN")
print("="*70)

# Buscar todas las organizaciones que no tienen fechas
from django.utils import timezone
today = timezone.now().date()

orgs = Organization.objects.filter(is_active=True)
print(f"\n📋 Organizaciones activas: {orgs.count()}\n")

for org in orgs:
    dates_count = SpecificDateSchedule.objects.filter(
        organization=org,
        date__gte=today,
        is_active=True
    ).count()
    
    print(f"{'='*70}")
    print(f"Organización: {org.name} (slug: {org.slug})")
    print(f"Fechas disponibles: {dates_count}")
    
    if dates_count == 0:
        print("❌ SIN FECHAS - Configurando...")
        
        # Crear/verificar configuración
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
            print("   ✅ Sistema de citas ABIERTO")
        
        # Buscar doctores
        doctors = Doctor.objects.filter(organization=org)
        doctor = doctors.first() if doctors.exists() else None
        
        if doctor:
            print(f"   ✅ Doctor: {doctor.full_name}")
        else:
            print("   ⚠️ Sin doctores - fechas sin asignar")
        
        # Crear fechas (próximos 60 días, lunes a sábado)
        start_date = today + timedelta(days=1)
        end_date = start_date + timedelta(days=60)
        
        schedules = [
            {'day': 0, 'start': '08:00', 'end': '12:00', 'slot': 30},  # Lunes
            {'day': 1, 'start': '08:00', 'end': '12:00', 'slot': 30},  # Martes
            {'day': 2, 'start': '08:00', 'end': '12:00', 'slot': 30},  # Miércoles
            {'day': 3, 'start': '08:00', 'end': '12:00', 'slot': 30},  # Jueves
            {'day': 4, 'start': '08:00', 'end': '12:00', 'slot': 30},  # Viernes
            {'day': 5, 'start': '09:00', 'end': '13:00', 'slot': 30},  # Sábado
        ]
        
        created_count = 0
        current_date = start_date
        
        while current_date <= end_date:
            if current_date.weekday() < 6:  # Lunes a Sábado
                schedule = next((s for s in schedules if s['day'] == current_date.weekday()), None)
                
                if schedule:
                    SpecificDateSchedule.objects.create(
                        organization=org,
                        doctor_profile=doctor,
                        date=current_date,
                        start_time=datetime.strptime(schedule['start'], '%H:%M').time(),
                        end_time=datetime.strptime(schedule['end'], '%H:%M').time(),
                        slot_duration=schedule['slot'],
                        is_active=True
                    )
                    created_count += 1
            
            current_date += timedelta(days=1)
        
        print(f"   ✅ Creadas {created_count} fechas")
        print(f"   🌐 URL: https://optikaapp.com/booking/{org.slug}")
    else:
        print(f"✅ Ya tiene {dates_count} fechas configuradas")
    
    print()

print("="*70)
print("✅ CONFIGURACIÓN COMPLETADA")
print("="*70)
