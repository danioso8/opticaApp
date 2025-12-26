"""
Script para limpiar doctores huérfanos (sin organización válida o de usuarios eliminados)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models import Doctor
from apps.organizations.models import Organization

def cleanup_orphan_doctors():
    print("🔍 Buscando doctores huérfanos...")
    
    # Buscar doctores cuya organización ya no existe o está inactiva
    orphan_doctors = Doctor.objects.filter(
        organization__isnull=False
    ).exclude(
        organization__is_active=True
    )
    
    orphan_count = orphan_doctors.count()
    
    if orphan_count == 0:
        print("✅ No se encontraron doctores huérfanos")
        
        # Mostrar todos los doctores para verificar
        all_doctors = Doctor.objects.all()
        print(f"\n📋 Total de doctores en la base de datos: {all_doctors.count()}")
        for doctor in all_doctors:
            print(f"  - {doctor.full_name} (ID: {doctor.identification}, Org: {doctor.organization})")
        
        return
    
    print(f"⚠️  Se encontraron {orphan_count} doctores huérfanos:")
    for doctor in orphan_doctors:
        print(f"  - {doctor.full_name} (ID: {doctor.identification}, Org: {doctor.organization})")
    
    confirm = input("\n¿Deseas eliminar estos doctores huérfanos? (s/n): ")
    
    if confirm.lower() == 's':
        deleted_count = orphan_doctors.delete()[0]
        print(f"✅ Se eliminaron {deleted_count} doctores huérfanos")
    else:
        print("❌ Operación cancelada")

if __name__ == '__main__':
    cleanup_orphan_doctors()
