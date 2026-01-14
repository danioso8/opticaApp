#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Desactivar módulos empresariales antiguos con precios altos
"""
from apps.organizations.models import PlanFeature, ModulePricing

print("=" * 80)
print("🧹 DESACTIVANDO MÓDULOS EMPRESARIALES ANTIGUOS")
print("=" * 80)

# Desactivar módulos con precios mayores a $100
old_modules = PlanFeature.objects.filter(price_monthly__gt=100)

for module in old_modules:
    print(f"❌ Desactivando: {module.name} (${module.price_monthly}/mes)")
    module.is_active = False
    module.save()
    
    # Desactivar pricing
    try:
        pricing = ModulePricing.objects.get(module=module)
        pricing.is_available = False
        pricing.save()
    except ModulePricing.DoesNotExist:
        pass

print(f"\n✅ {old_modules.count()} módulos empresariales desactivados")

print("\n" + "=" * 80)
print("📊 MÓDULOS FINALES ACTIVOS PARA À LA CARTE")
print("=" * 80)

# Obtener módulos comprables activos (precio entre $1 y $100)
active_modules = PlanFeature.objects.filter(
    is_active=True,
    can_purchase_separately=True,
    price_monthly__gt=0,
    price_monthly__lt=100
).order_by('category', 'price_monthly')

categories = {}
for m in active_modules:
    if m.category not in categories:
        categories[m.category] = []
    categories[m.category].append(m)

cat_names = {
    'other': '📦 CORE',
    'medical': '🏥 MÉDICOS', 
    'sales': '💰 COMERCIALES',
    'communication': '📱 COMUNICACIÓN',
    'analytics': '📊 ANÁLISIS',
    'integration': '🔗 INTEGRACIÓN',
    'inventory': '📦 INVENTARIO',
    'customization': '🎨 PERSONALIZACIÓN',
}

total_all = 0
for cat, name in cat_names.items():
    if cat in categories:
        print(f"\n{name}:")
        cat_total = 0
        for m in categories[cat]:
            print(f"  • {m.name:.<35} ${m.price_monthly:>5.2f}/mes")
            cat_total += float(m.price_monthly)
        total_all += cat_total
        print(f"  {'─' * 35} ${cat_total:>5.2f}")

print("\n" + "=" * 80)
print(f"💰 TOTAL (todos los módulos):          ${total_all:.2f}/mes")
print(f"💎 Con 10% descuento (4-6 módulos):    ${total_all * 0.9:.2f}/mes")  
print(f"💎 Con 20% descuento (7+ módulos):     ${total_all * 0.8:.2f}/mes")
print("=" * 80)
print(f"\n✅ {active_modules.count()} módulos disponibles para compra À la Carte")
