"""
Script para verificar organizaciones y limpiar datos específicos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models import Doctor
from apps.organizations.models import Organization

def verify_organizations():
    print("🔍 Verificando organizaciones...")
    
    all_orgs = Organization.objects.all()
    print(f"\n📋 Total de organizaciones: {all_orgs.count()}")
    for org in all_orgs:
        print(f"  - ID: {org.id}, Nombre: {org.name}, Activa: {org.is_active}")
    
    print("\n🔍 Verificando doctores...")
    all_doctors = Doctor.objects.all()
    print(f"\n📋 Total de doctores: {all_doctors.count()}")
    for doctor in all_doctors:
        org_status = "ACTIVA" if doctor.organization.is_active else "INACTIVA"
        print(f"  - {doctor.full_name} (ID: {doctor.identification})")
        print(f"    Organización: {doctor.organization.name} (ID: {doctor.organization.id}) - {org_status}")
    
    # Buscar el doctor específico
    print("\n🔍 Buscando doctor con ID 71360801...")
    try:
        doctor = Doctor.objects.get(identification='71360801')
        print(f"\n✅ Doctor encontrado:")
        print(f"  Nombre: {doctor.full_name}")
        print(f"  Organización: {doctor.organization.name} (ID: {doctor.organization.id})")
        print(f"  Org activa: {doctor.organization.is_active}")
        
        confirm = input("\n¿Deseas eliminar este doctor específico? (s/n): ")
        if confirm.lower() == 's':
            doctor.delete()
            print("✅ Doctor eliminado exitosamente")
        else:
            print("❌ Operación cancelada")
            
    except Doctor.DoesNotExist:
        print("❌ Doctor con ID 71360801 no encontrado")

if __name__ == '__main__':
    verify_organizations()
