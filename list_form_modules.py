"""
Listar módulos tal como aparecen en el formulario de edición de planes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import PlanFeature

print("\n" + "="*70)
print("📋 MÓDULOS EN EL FORMULARIO DE EDICIÓN (ordenados por categoría)")
print("="*70)

available_features = PlanFeature.objects.filter(is_active=True).order_by('category', 'name')

from collections import defaultdict
by_category = defaultdict(list)

for feature in available_features:
    by_category[feature.category].append(feature)

for category in sorted(by_category.keys()):
    features = by_category[category]
    print(f"\n📁 {category.upper()} ({len(features)} módulos):")
    for feature in features:
        icon = feature.icon if feature.icon else "fas fa-cube"
        print(f"   [{feature.id:2d}] ☐ {icon:25s} {feature.name}")

print("\n" + "="*70)
print(f"📊 Total módulos disponibles: {available_features.count()}")
print("="*70 + "\n")
