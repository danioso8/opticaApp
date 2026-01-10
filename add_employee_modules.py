"""
Agregar módulos faltantes: empleados y nómina básica
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import PlanFeature

# Módulos que faltan
new_modules = [
    {
        'code': 'employees',
        'name': 'Gestión de Empleados',
        'description': 'Administración de empleados y personal',
        'icon': 'fas fa-user-tie',
        'category': 'other',
    },
    {
        'code': 'payroll',
        'name': 'Nómina Básica',
        'description': 'Nómina y gestión de pagos a empleados',
        'icon': 'fas fa-money-check-alt',
        'category': 'other',
    },
]

print("\n" + "="*70)
print("📦 AGREGANDO MÓDULOS DE EMPLEADOS Y NÓMINA")
print("="*70)

added = 0
for module_data in new_modules:
    code = module_data['code']
    
    if PlanFeature.objects.filter(code=code).exists():
        print(f"⏭️  Ya existe: {code}")
    else:
        feature = PlanFeature.objects.create(
            code=code,
            name=module_data['name'],
            description=module_data['description'],
            icon=module_data['icon'],
            category=module_data['category'],
            is_active=True
        )
        print(f"✅ Agregado: {code} - {module_data['name']}")
        added += 1

print("\n" + "="*70)
print(f"✅ Módulos nuevos agregados: {added}")
print(f"📊 Total en BD ahora: {PlanFeature.objects.count()}")
print("="*70 + "\n")
