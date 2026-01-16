#!/usr/bin/env python
import os
import sys
import django

# Cambiar al directorio del proyecto
sys.path.insert(0, '/var/www/opticaapp')
os.chdir('/var/www/opticaapp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

django.setup()

from apps.appointments.models import SpecificDateSchedule
from apps.organizations.models import Organization
from apps.appointments.models import AppointmentConfiguration

print("="*60)
print("🔍 DIAGNÓSTICO BOOKING COMPUEASYS")
print("="*60)

try:
    org = Organization.objects.get(slug='compueasys2')
    print(f"\n✅ Organización encontrada:")
    print(f"   ID: {org.id}")
    print(f"   Nombre: {org.name}")
    print(f"   Activa: {org.is_active}")
    print(f"   Slug: {org.slug}")
    
    # Verificar configuración de citas
    config = AppointmentConfiguration.objects.filter(organization=org).first()
    if config:
        print(f"\n📋 Configuración de Citas:")
        print(f"   Sistema Abierto: {config.is_open}")
        print(f"   Duración slots: {config.slot_duration} minutos")
    else:
        print(f"\n⚠️  NO HAY CONFIGURACIÓN DE CITAS")
    
    # Verificar horarios específicos
    specific = SpecificDateSchedule.objects.filter(
        organization=org,
        is_active=True
    ).order_by('date')
    
    print(f"\n📅 Horarios Específicos (SpecificDateSchedule): {specific.count()}")
    if specific.exists():
        for s in specific[:10]:  # Mostrar primeros 10
            try:
                if hasattr(s, 'doctor_profile') and s.doctor_profile:
                    doctor_name = f"{s.doctor_profile.first_name} {s.doctor_profile.last_name}"
                elif hasattr(s, 'doctor') and s.doctor:
                    doctor_name = str(s.doctor)
                else:
                    doctor_name = "Sin doctor"
            except:
                doctor_name = "Error obteniendo doctor"
            print(f"   - {s.date} | {s.start_time}-{s.end_time} | {doctor_name}")
    else:
        print(f"   ⚠️  NO HAY HORARIOS ESPECÍFICOS CONFIGURADOS")
    
    # Verificar horarios semanales (deprecated pero revisar)
    from apps.appointments.models import WorkingHours
    working = WorkingHours.objects.filter(organization=org, is_active=True)
    print(f"\n⏰ Horarios Semanales (WorkingHours - deprecated): {working.count()}")
    if working.exists():
        for w in working:
            days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            print(f"   - {days[w.day_of_week]} | {w.start_time}-{w.end_time}")
    
    # Verificar doctores
    from apps.users.models import DoctorProfile
    doctors = DoctorProfile.objects.filter(organization=org)
    print(f"\n👨‍⚕️ Doctores: {doctors.count()}")
    for d in doctors:
        print(f"   - {d.first_name} {d.last_name} (ID: {d.id})")
    
    print("\n" + "="*60)
    print("🔍 PRUEBA API DISPONIBILIDAD")
    print("="*60)
    
    # Simular llamada a API
    from apps.appointments.views import available_dates
    from django.test import RequestFactory
    from datetime import date, timedelta
    
    factory = RequestFactory()
    request = factory.get(f'/api/available-dates/?organization_id={org.id}')
    
    response = available_dates(request)
    print(f"\n📡 Response Status: {response.status_code}")
    print(f"📦 Response Data: {response.data}")
    
except Organization.DoesNotExist:
    print("❌ No se encontró la organización 'compueasys'")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
