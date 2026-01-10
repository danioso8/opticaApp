#!/usr/bin/env python
"""
Script para verificar configuración de horarios y fechas disponibles
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
import pytz
from apps.appointments.models import SpecificDateSchedule, BlockedDate
from apps.organizations.models import Organization
from datetime import datetime, timedelta

print("=" * 70)
print("🔍 VERIFICACIÓN DE HORARIOS Y CONFIGURACIÓN")
print("=" * 70)
print()

# Verificar timezone
print("📅 CONFIGURACIÓN DE TIMEZONE:")
print(f"   Django USE_TZ: {django.conf.settings.USE_TZ}")
print(f"   Django TIME_ZONE: {django.conf.settings.TIME_ZONE}")
local_tz = pytz.timezone('America/Bogota')
now_utc = timezone.now()
now_local = now_utc.astimezone(local_tz)
print(f"   Hora UTC: {now_utc}")
print(f"   Hora Local (Bogotá): {now_local}")
print(f"   Fecha hoy (local): {now_local.date()}")
print()

# Verificar organizaciones activas
orgs = Organization.objects.filter(is_active=True)
print(f"📊 ORGANIZACIONES ACTIVAS: {orgs.count()}")
print()

for org in orgs:
    print(f"🏢 {org.name} (ID: {org.id})")
    print("-" * 70)
    
    # Horarios específicos
    today = now_local.date()
    schedules = SpecificDateSchedule.objects.filter(
        organization=org,
        date__gte=today,
        is_active=True
    ).order_by('date')
    
    print(f"   📅 Horarios programados desde hoy ({today}): {schedules.count()}")
    
    if schedules.exists():
        print(f"   Primeros 5 horarios:")
        for schedule in schedules[:5]:
            slots_count = schedule.time_slots.filter(is_available=True).count()
            doctor_name = schedule.doctor_profile.name if schedule.doctor_profile else (schedule.doctor.get_full_name() if schedule.doctor else "Sin doctor")
            print(f"      • {schedule.date} - {doctor_name} - {slots_count} slots disponibles")
    else:
        print(f"      ⚠️  NO HAY HORARIOS CONFIGURADOS")
        print(f"      Necesitas crear horarios en la configuración de citas")
    
    # Fechas bloqueadas
    blocked = BlockedDate.objects.filter(organization=org, date__gte=today).count()
    if blocked > 0:
        print(f"   🚫 Fechas bloqueadas: {blocked}")
    
    # Test del endpoint
    print(f"\n   🧪 TEST ENDPOINT /api/available-dates/?organization_id={org.id}")
    available_dates = []
    for date in schedules.values_list('date', flat=True).distinct():
        is_blocked = BlockedDate.objects.filter(organization=org, date=date).exists()
        if not is_blocked:
            available_dates.append(str(date))
    
    if available_dates:
        print(f"      ✅ Fechas disponibles: {len(available_dates)}")
        print(f"      Primeras 3: {', '.join(available_dates[:3])}")
    else:
        print(f"      ❌ NO HAY FECHAS DISPONIBLES")
    
    print()

print("=" * 70)
print("💡 RECOMENDACIONES:")
print("=" * 70)
if not SpecificDateSchedule.objects.filter(is_active=True, date__gte=today).exists():
    print("⚠️  NO HAY HORARIOS CONFIGURADOS EN EL SISTEMA")
    print("   Solución:")
    print("   1. Ve a Dashboard > Configuración > Horarios Específicos")
    print("   2. Crea horarios para los próximos días/semanas")
    print("   3. Asigna un doctor a cada horario")
    print("   4. Define los time slots (ej: 8:00, 9:00, 10:00, etc.)")
else:
    print("✅ El sistema tiene horarios configurados correctamente")
print("=" * 70)
