"""
Script para verificar parámetros clínicos en la base de datos de Render
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models import ClinicalParameter
from apps.organizations.models import Organization

print("=" * 80)
print("VERIFICANDO PARÁMETROS CLÍNICOS EN BASE DE DATOS")
print("=" * 80)

# Obtener todas las organizaciones
orgs = Organization.objects.all()
print(f"\n📊 Total de organizaciones: {orgs.count()}")
for org in orgs:
    print(f"   - {org.name} (ID: {org.id})")

# Verificar parámetros clínicos
total_params = ClinicalParameter.objects.all().count()
active_params = ClinicalParameter.objects.filter(is_active=True).count()

print(f"\n📋 Total de parámetros clínicos: {total_params}")
print(f"✅ Parámetros activos: {active_params}")

# Tipos de parámetros que necesitamos
param_types_needed = [
    'lens_type',
    'lens_material', 
    'lens_coating',
    'treatment',
    'lens_brand',
    'frame_type',
    'medication',
    'topical_medication',
    'systemic_medication',
    'contact_lens_type',
    'contact_lens_brand',
    'contact_lens_material',
    'contact_lens_wearing',
    'therapy',
    'visual_therapy',
    'complementary_exam',
    'lab_test',
    'recommendation',
    'follow_up_reason',
    'referral_specialty'
]

print("\n" + "=" * 80)
print("DESGLOSE POR TIPO DE PARÁMETRO")
print("=" * 80)

for param_type in param_types_needed:
    params = ClinicalParameter.objects.filter(
        parameter_type=param_type,
        is_active=True
    )
    count = params.count()
    
    status = "✅" if count > 0 else "❌"
    print(f"\n{status} {param_type}: {count} parámetros")
    
    if count > 0:
        # Mostrar primeros 5
        for p in params[:5]:
            org_info = f"[{p.organization.name}]" if p.organization else "[GLOBAL]"
            print(f"   - {p.name} {org_info}")
        if count > 5:
            print(f"   ... y {count - 5} más")

# Verificar parámetros globales vs organizacionales
print("\n" + "=" * 80)
print("PARÁMETROS GLOBALES VS ORGANIZACIONALES")
print("=" * 80)

global_params = ClinicalParameter.objects.filter(organization__isnull=True, is_active=True).count()
org_params = ClinicalParameter.objects.filter(organization__isnull=False, is_active=True).count()

print(f"🌍 Parámetros globales (disponibles para todos): {global_params}")
print(f"🏢 Parámetros por organización: {org_params}")

# Verificar si faltan parámetros básicos
print("\n" + "=" * 80)
print("PARÁMETROS FALTANTES")
print("=" * 80)

missing = []
for param_type in param_types_needed:
    count = ClinicalParameter.objects.filter(
        parameter_type=param_type,
        is_active=True
    ).count()
    if count == 0:
        missing.append(param_type)

if missing:
    print("❌ Faltan los siguientes tipos de parámetros:")
    for m in missing:
        print(f"   - {m}")
    print("\n⚠️  ACCIÓN REQUERIDA: Necesitas crear estos parámetros en la base de datos de Render")
else:
    print("✅ Todos los tipos de parámetros existen")

print("\n" + "=" * 80)
print("FIN DEL REPORTE")
print("=" * 80)
