"""
Verificar PlanFeature para electronic_invoicing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import PlanFeature, SubscriptionPlan

print("=" * 70)
print("VERIFICACIÓN DE PlanFeature")
print("=" * 70)

# Listar todos los PlanFeature
print("\nTodos los PlanFeature en la base de datos:")
print("-" * 70)
features = PlanFeature.objects.all()
if features.exists():
    for feat in features:
        print(f"  - {feat.code}: {feat.name}")
else:
    print("  ❌ No hay PlanFeature registrados")

# Buscar electronic_invoicing específicamente
print("\n" + "=" * 70)
print("Buscar 'electronic_invoicing':")
print("-" * 70)

try:
    elec_inv = PlanFeature.objects.get(code='electronic_invoicing')
    print(f"✅ Encontrado: {elec_inv.name}")
    print(f"   Descripción: {elec_inv.description}")
    print(f"   Categoría: {elec_inv.category}")
    
    # Ver qué planes lo tienen
    plans = SubscriptionPlan.objects.filter(features__code='electronic_invoicing')
    print(f"\n   Planes que lo incluyen:")
    for plan in plans:
        print(f"     - {plan.name} ({plan.plan_type})")
        
except PlanFeature.DoesNotExist:
    print("❌ NO existe PlanFeature con code='electronic_invoicing'")
    print("\n💡 SOLUCIÓN: Necesitas crear este PlanFeature o")
    print("   usar el sistema PLAN_MODULES en lugar de PlanFeature")

print("\n" + "=" * 70)
print("Plan Empresarial:")
print("-" * 70)

try:
    plan = SubscriptionPlan.objects.get(plan_type='enterprise')
    print(f"✅ Plan: {plan.name}")
    print(f"   Features asociados: {plan.features.count()}")
    
    if plan.features.exists():
        print("\n   Lista de features:")
        for feat in plan.features.all():
            print(f"     - {feat.code}: {feat.name}")
    else:
        print("   ⚠️ Este plan NO tiene features asociados")
        print("   El sidebar mostrará candados en todo")
        
except SubscriptionPlan.DoesNotExist:
    print("❌ Plan enterprise no encontrado")

print("\n" + "=" * 70)
