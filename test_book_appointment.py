"""
Script para probar el endpoint de agendamiento de citas
Uso: python manage.py shell < test_book_appointment.py
"""
import os
import django
from datetime import date, time, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models import Appointment, AppointmentConfiguration, SpecificDateSchedule
from apps.organizations.models import Organization
from apps.appointments.serializers import AppointmentCreateSerializer

print("=" * 60)
print("TEST: Agendar Cita desde Landing Page")
print("=" * 60)

# 1. Verificar organizaciones disponibles
print("\n1. Organizaciones disponibles:")
orgs = Organization.objects.filter(is_active=True)
for org in orgs:
    print(f"   - ID: {org.id} | {org.name}")

if not orgs.exists():
    print("   ⚠️  No hay organizaciones activas")
else:
    org = orgs.first()
    print(f"\n   ✓ Usando organización: {org.name} (ID: {org.id})")
    
    # 2. Verificar configuración
    print("\n2. Verificando configuración:")
    config = AppointmentConfiguration.get_config(org)
    if config:
        print(f"   - Sistema: {'Abierto ✓' if config.is_open else 'Cerrado ✗'}")
        print(f"   - Duración slot: {config.slot_duration} min")
        print(f"   - Días anticipación: {config.advance_booking_days}")
    else:
        print("   ⚠️  No hay configuración (se creará automáticamente)")
    
    # 3. Verificar horarios específicos
    print("\n3. Horarios específicos disponibles:")
    tomorrow = date.today() + timedelta(days=1)
    schedules = SpecificDateSchedule.objects.filter(
        organization=org,
        date__gte=tomorrow,
        is_active=True
    ).order_by('date')[:5]
    
    if schedules.exists():
        for sch in schedules:
            print(f"   - {sch.date}: {sch.start_time} a {sch.end_time}")
        
        # 4. Intentar agendar cita de prueba
        test_schedule = schedules.first()
        print(f"\n4. Intentando agendar cita de prueba:")
        print(f"   - Fecha: {test_schedule.date}")
        print(f"   - Hora: {test_schedule.start_time}")
        
        test_data = {
            'full_name': 'Test Usuario',
            'phone_number': '+573001234567',
            'email': 'test@example.com',
            'appointment_date': test_schedule.date,
            'appointment_time': test_schedule.start_time,
            'organization_id': org.id
        }
        
        serializer = AppointmentCreateSerializer(data=test_data)
        if serializer.is_valid():
            # No guardar realmente, solo validar
            print("   ✓ Validación exitosa")
            print(f"   ✓ Datos válidos: {serializer.validated_data}")
            
            # Verificar si ya existe una cita en ese horario
            existing = Appointment.objects.filter(
                organization=org,
                appointment_date=test_schedule.date,
                appointment_time=test_schedule.start_time
            ).exclude(status='cancelled')
            
            if existing.exists():
                print("   ⚠️  Ya existe una cita en ese horario")
            else:
                print("   ✓ Horario disponible para agendar")
        else:
            print("   ✗ Error de validación:")
            for field, errors in serializer.errors.items():
                print(f"     - {field}: {errors}")
    else:
        print("   ⚠️  No hay horarios específicos configurados")
        print("\n   Sugerencia: Crear horarios con:")
        print("   python manage.py shell")
        print("   >>> from apps.appointments.models import SpecificDateSchedule")
        print("   >>> from apps.organizations.models import Organization")
        print("   >>> from datetime import date, time, timedelta")
        print("   >>> org = Organization.objects.first()")
        print("   >>> tomorrow = date.today() + timedelta(days=1)")
        print("   >>> SpecificDateSchedule.objects.create(")
        print("   ...     organization=org,")
        print("   ...     date=tomorrow,")
        print("   ...     start_time=time(8, 0),")
        print("   ...     end_time=time(18, 0),")
        print("   ...     is_active=True")
        print("   ... )")

print("\n" + "=" * 60)
print("Fin del test")
print("=" * 60)
