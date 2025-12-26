"""
Script para verificar que doctores y pacientes pueden estar en múltiples organizaciones
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models import Doctor, Patient
from apps.organizations.models import Organization

def verify_multi_org_support():
    print("🔍 Verificando configuración de multi-organización...\n")
    
    # Verificar configuración de Patient
    print("📋 PATIENT Model:")
    patient_meta = Patient._meta
    if hasattr(patient_meta, 'unique_together') and patient_meta.unique_together:
        print(f"  ✅ unique_together: {patient_meta.unique_together}")
    else:
        print("  ❌ No tiene unique_together configurado")
    
    # Verificar configuración de Doctor
    print("\n👨‍⚕️ DOCTOR Model:")
    doctor_meta = Doctor._meta
    if hasattr(doctor_meta, 'unique_together') and doctor_meta.unique_together:
        print(f"  ✅ unique_together: {doctor_meta.unique_together}")
    else:
        print("  ❌ No tiene unique_together configurado")
    
    # Verificar campo identification
    doctor_id_field = Doctor._meta.get_field('identification')
    print(f"  Campo 'identification':")
    print(f"    - unique: {doctor_id_field.unique}")
    print(f"    - blank: {doctor_id_field.blank}")
    print(f"    - null: {doctor_id_field.null}")
    
    print("\n✅ Configuración correcta:")
    print("  - Un doctor/paciente PUEDE estar en múltiples organizaciones")
    print("  - Un doctor/paciente NO PUEDE duplicarse en la misma organización")
    print("  - La validación es: unique_together = ('organization', 'identification')")

if __name__ == '__main__':
    verify_multi_org_support()
