import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models import ClinicalParameter

# Ver todos los parámetros clínicos
print("\n=== PARÁMETROS CLÍNICOS ===\n")

materials = ClinicalParameter.objects.filter(parameter_type='lens_material', is_active=True)
print(f"Materiales de lente ({materials.count()}):")
for m in materials:
    print(f"  - {m.name} (org: {m.organization})")

coatings = ClinicalParameter.objects.filter(parameter_type='lens_coating', is_active=True)
print(f"\nTratamientos/Recubrimientos ({coatings.count()}):")
for c in coatings:
    print(f"  - {c.name} (org: {c.organization})")

meds = ClinicalParameter.objects.filter(parameter_type='medication', is_active=True)
print(f"\nMedicamentos ({meds.count()}):")
for med in meds:
    print(f"  - {med.name} (org: {med.organization})")
