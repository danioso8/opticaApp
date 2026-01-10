#!/usr/bin/env python
"""
Script para verificar configuración de OCÉANO ÓPTICO
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models import WorkingHours, AppointmentConfiguration
from apps.patients.models import Doctor

def check_config():
    """Verificar configuración de OCÉANO ÓPTICO"""
    print("=" * 70)
    print("🔍 VERIFICANDO CONFIGURACIÓN DE OCÉANO ÓPTICO")
    print("=" * 70)
    print()
    
    try:
        org = Organization.objects.get(name='OCÉANO ÓPTICO')
        print(f"✅ Organización encontrada: {org.name} (ID: {org.id})")
        print()
        
        # Verificar configuración de citas
        config = AppointmentConfiguration.objects.filter(organization=org).first()
        if config:
            print("📋 Configuración de Citas:")
            print(f"   Sistema abierto: {'✅ Sí' if config.is_open else '❌ No'}")
            print(f"   Duración de cita: {config.appointment_duration} min")
            print(f"   Días adelante: {config.days_in_advance}")
            print(f"   Mismo día: {'✅ Sí' if config.allow_same_day else '❌ No'}")
        else:
            print("⚠️  No hay configuración de citas")
        print()
        
        # Verificar horarios de trabajo
        hours = WorkingHours.objects.filter(organization=org)
        print(f"⏰ Horarios de Trabajo ({hours.count()} registros):")
        if hours.exists():
            days = {
                0: 'Lunes', 1: 'Martes', 2: 'Miércoles',
                3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
            }
            for h in hours.order_by('day_of_week'):
                status = '✅ Activo' if h.is_active else '❌ Inactivo'
                print(f"   {days[h.day_of_week]:10s}: {h.start_time} - {h.end_time} ({status})")
        else:
            print("   ⚠️  No hay horarios configurados")
        print()
        
        # Verificar doctores
        doctors = Doctor.objects.filter(organization=org)
        print(f"👨‍⚕️ Doctores ({doctors.count()} registros):")
        if doctors.exists():
            for doc in doctors:
                status = '✅ Activo' if doc.is_active else '❌ Inactivo'
                schedules = doc.schedules.count() if hasattr(doc, 'schedules') else 0
                print(f"   {doc.get_full_name():30s} ({status}) - {schedules} horarios")
        else:
            print("   ⚠️  No hay doctores configurados")
        print()
        
    except Organization.DoesNotExist:
        print("❌ Organización 'OCÉANO ÓPTICO' no encontrada")
        print()
        print("Organizaciones disponibles:")
        for org in Organization.objects.all():
            print(f"   - {org.name}")
    
    print("=" * 70)

if __name__ == '__main__':
    check_config()
