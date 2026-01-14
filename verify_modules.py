"""
Script para verificar los módulos existentes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import ModulePermission
from collections import defaultdict

print("📋 Módulos del Sistema\n")
print("=" * 80)

# Agrupar por categoría
modules_by_category = defaultdict(list)
for module in ModulePermission.objects.filter(is_active=True).order_by('category', 'order', 'name'):
    modules_by_category[module.category].append(module)

# Mostrar por categoría
for category, modules in sorted(modules_by_category.items()):
    cat_display = dict(ModulePermission.MODULE_CATEGORIES).get(category, category)
    print(f"\n🏷️  {cat_display.upper()}")
    print("-" * 80)
    for module in modules:
        print(f"  • {module.name:<30} ({module.code})")
        if module.description:
            print(f"    {module.description}")

print("\n" + "=" * 80)
print(f"📊 Total: {ModulePermission.objects.filter(is_active=True).count()} módulos activos")
