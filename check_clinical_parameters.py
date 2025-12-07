#!/usr/bin/env python
"""
Script para verificar los parámetros clínicos en la base de datos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models import ClinicalParameter
from apps.organizations.models import Organization

# Obtener la primera organización
org = Organization.objects.first()
if not org:
    print("❌ No hay organizaciones en la base de datos")
    exit(1)

print(f"✅ Organización: {org.name}")
print(f"ID: {org.id}")
print()

# Tipos de parámetros que debemos tener
param_types = [
    'lens_type',
    'lens_material', 
    'lens_coating',
    'lens_brand',
    'frame_type',
    'contact_lens_type',
    'contact_lens_brand',
    'contact_lens_material',
    'contact_lens_wearing',
    'diagnosis',
    'diagnosis_category',
    'treatment',
    'therapy',
    'visual_therapy',
    'complementary_exam',
    'lab_test',
    'medication',
    'topical_medication',
    'systemic_medication',
    'recommendation',
    'referral_specialty',
    'follow_up_reason',
]

print("=" * 80)
print("VERIFICACIÓN DE PARÁMETROS CLÍNICOS")
print("=" * 80)
print()

total_params = 0
missing_types = []

for param_type in param_types:
    params = ClinicalParameter.objects.filter(
        organization=org,
        parameter_type=param_type,
        is_active=True
    )
    count = params.count()
    total_params += count
    
    status = "✅" if count > 0 else "❌"
    print(f"{status} {param_type:30} : {count:3} parámetros")
    
    if count == 0:
        missing_types.append(param_type)
    elif count <= 3:
        # Mostrar los parámetros si son pocos
        for p in params:
            print(f"     - {p.name}")

print()
print("=" * 80)
print(f"TOTAL: {total_params} parámetros activos")
print("=" * 80)

if missing_types:
    print()
    print("⚠️ TIPOS DE PARÁMETROS FALTANTES:")
    for pt in missing_types:
        print(f"   - {pt}")
    print()
    print("💡 SOLUCIÓN: Necesitas crear parámetros clínicos desde el panel de administración")
    print("   o ejecutar un script de población de datos.")
else:
    print()
    print("✅ Todos los tipos de parámetros tienen datos")
