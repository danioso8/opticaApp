"""
Script para resolver problemas de pacientes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models import Patient
from apps.organizations.models import Organization

# Obtener la organización
org = Organization.objects.filter(slug='compueasys').first()

if not org:
    print("❌ No se encontró la organización CompuEasys")
    exit()

print(f"✅ Organización: {org.name} (ID: {org.id})")
print()

# 1. Buscar y eliminar "Andres Gomez"
print("🔍 Buscando paciente 'Andres Gomez'...")
andres = Patient.objects.filter(
    organization=org,
    full_name__icontains='Andres Gomez'
).first()

if andres:
    print(f"✅ Encontrado: {andres.full_name} (Cédula: {andres.identification})")
    print(f"   ID: {andres.id}")
    andres.delete()
    print("🗑️  Paciente 'Andres Gomez' eliminado exitosamente")
else:
    print("⚠️  No se encontró paciente 'Andres Gomez'")

print()

# 2. Buscar paciente con cédula 71360801
print("🔍 Buscando paciente con cédula 71360801...")
existing = Patient.objects.filter(identification='71360801').first()

if existing:
    print(f"✅ Encontrado: {existing.full_name}")
    print(f"   Organización: {existing.organization.name}")
    print(f"   Teléfono: {existing.phone_number}")
    print(f"   Email: {existing.email}")
    print(f"   ID: {existing.id}")
    
    # Verificar si es de otra organización
    if existing.organization.id != org.id:
        print(f"⚠️  Este paciente pertenece a otra organización: {existing.organization.name}")
        print("   No se puede modificar automáticamente.")
    else:
        # Actualizar datos en lugar de eliminar
        print("📝 Actualizando datos del paciente existente...")
        existing.full_name = 'Daniel Andres Osorio Velasquez'
        existing.save()
        print(f"✅ Paciente actualizado: {existing.full_name}")
        print("   (Se mantuvo el ID para preservar facturas y ventas)")
else:
    print("⚠️  No se encontró paciente con cédula 71360801")
    
    # Crear nuevo paciente
    print("\n🆕 Creando paciente 'Daniel Andres Osorio Velasquez'...")
    new_patient = Patient.objects.create(
        organization=org,
        full_name='Daniel Andres Osorio Velasquez',
        identification_type='CC',
        identification='71360801',
        phone_number='',  # Agregar teléfono si lo tienes
        email='',  # Agregar email si lo tienes
    )
    print(f"✅ Paciente creado exitosamente!")
    print(f"   Nombre: {new_patient.full_name}")
    print(f"   Cédula: {new_patient.identification}")
    print(f"   ID: {new_patient.id}")

print()
print("=" * 60)
print("✅ PROCESO COMPLETADO")
print("=" * 60)

# Mostrar todos los pacientes de CompuEasys
print("\n📋 Lista de pacientes en CompuEasys:")
all_patients = Patient.objects.filter(organization=org)
for p in all_patients:
    print(f"   • {p.full_name} - CC: {p.identification} - Tel: {p.phone_number or 'N/A'}")

print(f"\n📊 Total de pacientes: {all_patients.count()}")
