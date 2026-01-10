"""
Asociar PlanFeatures al plan Empresarial
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import PlanFeature, SubscriptionPlan

print("=" * 70)
print("ASOCIAR PLANFEATURES AL PLAN EMPRESARIAL")
print("=" * 70)

# Obtener plan enterprise
plan = SubscriptionPlan.objects.get(plan_type='enterprise')
print(f"\n✅ Plan: {plan.name} ({plan.plan_type})")
print(f"   Features actuales: {plan.features.count()}")

# Lista de features que debe tener el plan enterprise
enterprise_features = [
    'dashboard',
    'patients',
    'appointments',
    'doctors',
    'formulas',
    'clinical_history_basic',
    'products',
    'inventory',
    'electronic_invoicing',  # IMPORTANTE
    'whatsapp_integration',
    'notifications_push',
    'analytics_advanced',
    'reports_basic',
    'multi_location',
    'api_rest',
    'payroll_dian',  # IMPORTANTE
    'workflows',
    'promotions',
    'landing_page',
    'audit',
    'permissions_advanced',
    'configuration_advanced',
    'configuration_basic',
    'teams',
    'documents',
    'tasks',
    'sales_pos',
    'cash_register',
]

print(f"\n📦 Features a asociar: {len(enterprise_features)}")
print("-" * 70)

added = 0
already_had = 0
not_found = []

for feature_code in enterprise_features:
    try:
        feature = PlanFeature.objects.get(code=feature_code)
        
        if plan.features.filter(code=feature_code).exists():
            already_had += 1
            print(f"  ⏭️  {feature_code:30s} - Ya estaba asociado")
        else:
            plan.features.add(feature)
            added += 1
            print(f"  ✅ {feature_code:30s} - Agregado")
            
    except PlanFeature.DoesNotExist:
        not_found.append(feature_code)
        print(f"  ❌ {feature_code:30s} - NO EXISTE en PlanFeature")

print("\n" + "=" * 70)
print("RESUMEN")
print("=" * 70)
print(f"✅ Features agregados: {added}")
print(f"⏭️  Ya tenía: {already_had}")
print(f"❌ No encontrados: {len(not_found)}")

if not_found:
    print(f"\n⚠️  Features no encontrados:")
    for code in not_found:
        print(f"   - {code}")

print(f"\n📊 Total features del plan: {plan.features.count()}")

print("\n" + "=" * 70)
print("✅ CONFIGURACIÓN COMPLETADA")
print("=" * 70)
print("\n🔑 Ahora cierra sesión y vuelve a entrar para actualizar la UI")
