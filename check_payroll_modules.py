import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import PlanFeature

print("=" * 70)
print("📋 MÓDULOS RELACIONADOS CON NÓMINA Y RECURSOS HUMANOS")
print("=" * 70)

# Buscar módulos relacionados con nómina
keywords = ['nomina', 'nómina', 'payroll', 'empleado', 'employee', 'vacacion', 'vacation', 
            'prestamo', 'loan', 'pila', 'rrhh', 'hr', 'human', 'recursos']

found_modules = []
all_modules = PlanFeature.objects.all().order_by('name')

for module in all_modules:
    for keyword in keywords:
        if keyword.lower() in module.name.lower() or keyword.lower() in module.code.lower():
            found_modules.append(module)
            break

if found_modules:
    print(f"\n✅ Módulos encontrados ({len(found_modules)}):\n")
    for module in found_modules:
        status = "✓ Activo" if module.is_active else "✗ Inactivo"
        print(f"   [{module.id:2d}] {status:12s} {module.code:25s} - {module.name}")
else:
    print("\n❌ No se encontraron módulos relacionados con nómina")

print("\n" + "=" * 70)
print(f"📊 Total módulos en sistema: {PlanFeature.objects.count()}")
print("=" * 70)
