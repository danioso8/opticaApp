import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.appointments.models import SpecificDateSchedule, AppointmentConfiguration
from apps.patients.models import Doctor
from datetime import date, datetime, time, timedelta

print("="*70)
print("CONFIGURAR FECHAS DE BOOKING PARA COMPUEASYS")
print("="*70)

# Obtener CompuEasys
try:
    org = Organization.objects.get(slug='compueasys')
    print(f"\n✅ Organización: {org.name} (ID: {org.id})")
except Organization.DoesNotExist:
    print("\n❌ CompuEasys no existe")
    exit(1)

# Verificar configuración de citas
config, created = AppointmentConfiguration.objects.get_or_create(
    organization=org,
    defaults={
        'is_open': True,
        'max_days_in_advance': 60,
        'appointment_duration': 30,
        'allow_cancel_hours_before': 24
    }
)

if created:
    print(f"✅ AppointmentConfiguration creada")
else:
    print(f"✅ AppointmentConfiguration existe")
    if not config.is_open:
        config.is_open = True
        config.save()
        print(f"   ⚠️ Sistema estaba cerrado - ahora ABIERTO")

# Buscar doctores de la organización
doctors = Doctor.objects.filter(organization=org)
print(f"\n📋 Doctores en CompuEasys: {doctors.count()}")

if doctors.count() == 0:
    print("   ⚠️ No hay doctores - las fechas se crearán sin doctor asignado")
    doctor = None
else:
    doctor = doctors.first()
    print(f"   ✅ Usando doctor: {doctor.full_name}")

# Verificar fechas existentes
today = date.today()
existing_dates = SpecificDateSchedule.objects.filter(
    organization=org,
    date__gte=today,
    is_active=True
).count()

print(f"\n📅 Fechas específicas existentes: {existing_dates}")

if existing_dates > 0:
    print("   ✅ Ya hay fechas configuradas")
    print("\n¿Desea agregar MÁS fechas? (s/n): ", end='')
    response = input().lower()
    if response != 's':
        print("\n✋ Cancelado por el usuario")
        exit(0)

# Crear fechas para los próximos 60 días (solo días laborables)
print(f"\n{'='*70}")
print("CREANDO FECHAS ESPECÍFICAS")
print("="*70)

start_date = today + timedelta(days=1)  # Empezar desde mañana
end_date = start_date + timedelta(days=60)

# Horarios por defecto
schedules = [
    {'day': 0, 'start': '08:00', 'end': '12:00', 'slot_duration': 30},  # Lunes
    {'day': 1, 'start': '08:00', 'end': '12:00', 'slot_duration': 30},  # Martes
    {'day': 2, 'start': '08:00', 'end': '12:00', 'slot_duration': 30},  # Miércoles
    {'day': 3, 'start': '08:00', 'end': '12:00', 'slot_duration': 30},  # Jueves
    {'day': 4, 'start': '08:00', 'end': '12:00', 'slot_duration': 30},  # Viernes
    {'day': 5, 'start': '09:00', 'end': '13:00', 'slot_duration': 30},  # Sábado
]

dates_created = 0
current_date = start_date

while current_date <= end_date:
    # Solo días laborables (lunes a sábado)
    if current_date.weekday() < 6:  # 0=Lunes, 5=Sábado, 6=Domingo
        # Buscar horario para este día
        schedule = next((s for s in schedules if s['day'] == current_date.weekday()), None)
        
        if schedule:
            # Verificar si ya existe
            existing = SpecificDateSchedule.objects.filter(
                organization=org,
                date=current_date,
                is_active=True
            ).first()
            
            if not existing:
                SpecificDateSchedule.objects.create(
                    organization=org,
                    doctor_profile=doctor,
                    date=current_date,
                    start_time=datetime.strptime(schedule['start'], '%H:%M').time(),
                    end_time=datetime.strptime(schedule['end'], '%H:%M').time(),
                    slot_duration=schedule['slot_duration'],
                    is_active=True
                )
                dates_created += 1
                print(f"   ✅ {current_date} ({current_date.strftime('%A')}) - {schedule['start']} a {schedule['end']}")
    
    current_date += timedelta(days=1)

print(f"\n{'='*70}")
print(f"✅ FECHAS CREADAS: {dates_created}")
print("="*70)

# Verificar resultado final
total_dates = SpecificDateSchedule.objects.filter(
    organization=org,
    date__gte=today,
    is_active=True
).count()

print(f"\n📊 RESUMEN:")
print(f"   - Organización: {org.name}")
print(f"   - Fechas disponibles: {total_dates}")
print(f"   - Rango: {today} a {end_date}")
print(f"   - Sistema abierto: {config.is_open}")
print(f"\n✅ El booking debería funcionar ahora!")
print(f"\n🌐 Prueba en: http://localhost:8000/booking/{org.slug}")
print("\n" + "="*70)
