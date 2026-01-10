"""
Listar todas las organizaciones y copiar conceptos a todas ellas
"""

from apps.payroll.models import AccrualConcept, DeductionConcept
from apps.organizations.models import Organization

print("=" * 80)
print("TODAS LAS ORGANIZACIONES")
print("=" * 80)

all_orgs = Organization.objects.all()
print(f"\nTotal organizaciones: {all_orgs.count()}")

for org in all_orgs:
    dev_count = AccrualConcept.objects.filter(organization=org).count()
    ded_count = DeductionConcept.objects.filter(organization=org).count()
    print(f"\n{org.id}. {org.name}")
    print(f"   Devengados: {dev_count}")
    print(f"   Deducciones: {ded_count}")

# Buscar "Océano"
oceano = Organization.objects.filter(name__icontains='océano')
if oceano.exists():
    print(f"\n✓ Encontrada organización Océano: {oceano.first().name}")
else:
    oceano = Organization.objects.filter(name__icontains='oceano')
    if oceano.exists():
        print(f"\n✓ Encontrada organización Oceano: {oceano.first().name}")
    else:
        print("\n✗ NO se encontró organización Océano/Oceano")
