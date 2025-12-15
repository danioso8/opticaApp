#!/usr/bin/env python
"""
Script para corregir citas sin organización asignada
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models import Appointment
from apps.organizations.models import Organization

print("\n" + "="*70)
print("🔧 CORRECCIÓN DE CITAS SIN ORGANIZACIÓN")
print("="*70 + "\n")

# Buscar citas sin organización
appointments_without_org = Appointment.objects.filter(organization__isnull=True)
count = appointments_without_org.count()

print(f"📊 Encontradas {count} citas sin organización asignada\n")

if count == 0:
    print("✅ No hay citas para corregir")
    sys.exit(0)

# Mostrar detalles de las citas
print("Detalles de las citas:")
for apt in appointments_without_org:
    print(f"\n   📅 Cita ID: {apt.id}")
    print(f"      Paciente: {apt.full_name if hasattr(apt, 'full_name') else 'N/A'}")
    print(f"      Fecha: {apt.appointment_date if hasattr(apt, 'appointment_date') else 'N/A'}")
    print(f"      Hora: {apt.appointment_time if hasattr(apt, 'appointment_time') else 'N/A'}")
    print(f"      Estado: {apt.status}")
    
    # Intentar determinar organización por el paciente o doctor
    suggested_org = None
    
    if hasattr(apt, 'patient') and apt.patient and hasattr(apt.patient, 'organization'):
        suggested_org = apt.patient.organization
        print(f"      → Paciente pertenece a: {suggested_org.name}")
    
    if hasattr(apt, 'doctor') and apt.doctor and hasattr(apt.doctor, 'organization'):
        if suggested_org is None:
            suggested_org = apt.doctor.organization
        print(f"      → Doctor pertenece a: {apt.doctor.organization.name}")

# Estrategia de corrección
print(f"\n{'─'*70}")
print("🔍 ESTRATEGIA DE CORRECCIÓN:")
print(f"{'─'*70}\n")

# Obtener la primera organización activa como fallback
default_org = Organization.objects.filter(is_active=True).first()

if not default_org:
    print("❌ No hay organizaciones activas. No se puede corregir.")
    sys.exit(1)

print(f"Organización predeterminada: {default_org.name}\n")

# Corregir cada cita
fixed_count = 0
for apt in appointments_without_org:
    target_org = None
    reason = ""
    
    # Prioridad 1: Organización del paciente
    if hasattr(apt, 'patient') and apt.patient and hasattr(apt.patient, 'organization') and apt.patient.organization:
        target_org = apt.patient.organization
        reason = f"Organización del paciente ({apt.patient.organization.name})"
    
    # Prioridad 2: Organización del doctor
    elif hasattr(apt, 'doctor') and apt.doctor and hasattr(apt.doctor, 'organization') and apt.doctor.organization:
        target_org = apt.doctor.organization
        reason = f"Organización del doctor ({apt.doctor.organization.name})"
    
    # Prioridad 3: Organización predeterminada
    else:
        target_org = default_org
        reason = f"Organización predeterminada ({default_org.name})"
    
    # Asignar organización
    apt.organization = target_org
    apt.save()
    
    print(f"✅ Cita ID {apt.id} → {reason}")
    fixed_count += 1

print(f"\n{'='*70}")
print(f"✅ CORRECCIÓN COMPLETADA")
print(f"{'='*70}")
print(f"\n   Total de citas corregidas: {fixed_count}")
print(f"\n{'='*70}\n")

# Verificar que ya no haya citas sin organización
remaining = Appointment.objects.filter(organization__isnull=True).count()
if remaining == 0:
    print("🎉 ¡Perfecto! Ya no hay citas sin organización\n")
else:
    print(f"⚠️  Aún quedan {remaining} citas sin organización\n")
