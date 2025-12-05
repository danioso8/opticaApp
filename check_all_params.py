import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models import ClinicalParameter

# Ver TODOS los parámetros clínicos sin filtro de is_active
print("\n=== TODOS LOS PARÁMETROS CLÍNICOS (incluyendo inactivos) ===\n")

all_params = ClinicalParameter.objects.all().order_by('parameter_type', 'name')
print(f"Total: {all_params.count()}\n")

by_type = {}
for param in all_params:
    if param.parameter_type not in by_type:
        by_type[param.parameter_type] = []
    by_type[param.parameter_type].append(param)

for param_type, items in by_type.items():
    print(f"\n{param_type.upper()} ({len(items)}):")
    for item in items:
        status = "✓ Activo" if item.is_active else "✗ Inactivo"
        print(f"  {status} - {item.name} | {item.category or 'Sin categoría'} | Org: {item.organization}")
