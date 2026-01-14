#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Limpiar módulos con precios incorrectos y mostrar resumen
"""
from apps.organizations.models import PlanFeature, ModulePricing
from decimal import Decimal

print("=" * 80)
print("🧹 LIMPIANDO MÓDULOS CON PRECIOS INCORRECTOS")
print("=" * 80)

# Módulos que deben ser gratis o tienen precios incorrectos
modules_to_fix = [
    ('whatsapp_integration', 0),  # Debe usar el nuevo 'whatsapp'
    ('advanced_analytics', 0),  # Debe usar el nuevo 'analytics'
    ('api_rest', 0),  # Debe usar el nuevo 'api_access'
    ('electronic_invoicing_dian', 0),  # Debe usar el nuevo 'invoicing_dian'
    ('electronic_payroll_dian', 0),  # Debe ser gratis o eliminado
]

for code, new_price in modules_to_fix:
    try:
        feature = PlanFeature.objects.get(code=code)
        old_price = feature.price_monthly
        feature.price_monthly = Decimal(str(new_price))
        feature.is_active = False if new_price == 0 else True
        feature.save()
        
        # Desactivar pricing si existe
        try:
            pricing = ModulePricing.objects.get(module=feature)
            pricing.is_available = False
            pricing.save()
            print(f"✅ {feature.name}: ${old_price} → ${new_price} (Pricing desactivado)")
        except ModulePricing.DoesNotExist:
            print(f"✅ {feature.name}: ${old_price} → ${new_price}")
            
    except PlanFeature.DoesNotExist:
        print(f"⚠️  Módulo '{code}' no encontrado")

print("\n" + "=" * 80)
print("📊 RESUMEN FINAL DE MÓDULOS ACTIVOS Y COMPRABLES")
print("=" * 80)

# Obtener módulos comprables activos
active_modules = PlanFeature.objects.filter(
    is_active=True,
    can_purchase_separately=True,
    price_monthly__gt=0
).order_by('category', 'price_monthly')

total = Decimal('0')
by_category = {}

for module in active_modules:
    if module.category not in by_category:
        by_category[module.category] = []
    by_category[module.category].append(module)
    total += module.price_monthly

categories_names = {
    'other': '📦 CORE / Otros',
    'medical': '🏥 MÉDICOS',
    'sales': '💰 COMERCIALES',
    'communication': '📱 COMUNICACIÓN',
    'analytics': '📊 ANÁLISIS',
    'integration': '🔗 INTEGRACIÓN',
    'inventory': '📦 INVENTARIO',
    'customization': '🎨 PERSONALIZACIÓN',
}

for cat_code, cat_name in categories_names.items():
    if cat_code in by_category:
        print(f"\n{cat_name}:")
        cat_total = Decimal('0')
        for m in by_category[cat_code]:
            print(f"  • {m.name:.<40} ${m.price_monthly:>6.2f}/mes")
            cat_total += m.price_monthly
        print(f"  {'└─ Subtotal':.<40} ${cat_total:>6.2f}/mes")

print("\n" + "=" * 80)
print(f"💰 TOTAL SI COMPRA TODOS LOS MÓDULOS: ${total:.2f}/mes")
print(f"💎 Con descuento 10% (4-6 módulos):    ${float(total) * 0.9:.2f}/mes")
print(f"💎 Con descuento 20% (7+ módulos):     ${float(total) * 0.8:.2f}/mes")
print("=" * 80)

print(f"\n✅ Total de módulos comprables activos: {active_modules.count()}")
print(f"💰 Configuraciones de precio activas: {ModulePricing.objects.filter(is_available=True).count()}")
