import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models import ClinicalParameter
from apps.organizations.models import Organization

# Obtener la organización Compueasys
org = Organization.objects.get(name='Compueasys')

# Crear algunos tratamientos/recubrimientos de ejemplo si no existen
treatments = [
    {'name': 'N/A', 'category': 'Sin Descripción', 'description': 'No aplica tratamiento'},
    {'name': 'VISUENS', 'category': 'Sin Descripción', 'description': 'Tratamiento Visuens'},
    {'name': 'sdhuskh', 'category': 'Medicamento', 'description': 'Tratamiento sdhuskh'},
    {'name': 'syfirgf', 'category': 'Sin Descripción', 'description': 'Tratamiento syfirgf'},
]

print("\n=== CREANDO TRATAMIENTOS/RECUBRIMIENTOS ===\n")

for treatment in treatments:
    obj, created = ClinicalParameter.objects.get_or_create(
        organization=org,
        parameter_type='lens_coating',
        name=treatment['name'],
        defaults={
            'category': treatment['category'],
            'description': treatment['description'],
            'is_active': True,
            'display_order': 0
        }
    )
    if created:
        print(f"✓ Creado: {obj.name}")
    else:
        print(f"- Ya existe: {obj.name}")

# Verificar
coatings = ClinicalParameter.objects.filter(
    organization=org,
    parameter_type='lens_coating',
    is_active=True
)
print(f"\nTotal de tratamientos/recubrimientos: {coatings.count()}")
for c in coatings:
    print(f"  - {c.name} ({c.category})")
