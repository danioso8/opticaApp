"""
Verificar features del plan enterprise de la organización
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization

print("=" * 80)
print("VERIFICACIÓN DE FEATURES DE LA ORGANIZACIÓN")
print("=" * 80)

org = Organization.objects.get(slug='compueasys')
print(f"\n🏢 Organización: {org.name}")

sub = org.current_subscription
if sub:
    print(f"\n✅ Suscripción activa:")
    print(f"   Plan: {sub.plan.name}")
    print(f"   Plan Type: {sub.plan.plan_type}")
    print(f"   Vence en: {sub.days_remaining} días")
    
    print(f"\n📦 Features del plan:")
    print("-" * 80)
    features = sub.plan.features.all()
    print(f"   Total: {features.count()} features")
    
    if features.exists():
        for feat in features:
            print(f"   ✅ {feat.code:30s} - {feat.name}")
        
        # Verificar específicamente los críticos
        print(f"\n🔍 Verificación de features críticos:")
        print("-" * 80)
        
        critical = ['electronic_invoicing', 'payroll_dian', 'workflows', 'promotions']
        for code in critical:
            has_it = features.filter(code=code).exists()
            status = "✅" if has_it else "❌"
            print(f"   {status} {code}")
            
    else:
        print(f"   ❌ El plan NO tiene features asociados")
        print(f"\n   💡 SOLUCIÓN:")
        print(f"      Ejecutar: python associate_enterprise_features.py")
        
    # Probar el método has_feature
    print(f"\n🧪 Prueba de org.has_feature():")
    print("-" * 80)
    test_features = ['electronic_invoicing', 'payroll_dian', 'dashboard', 'patients']
    for code in test_features:
        result = org.has_feature(code)
        status = "✅" if result else "❌"
        print(f"   {status} has_feature('{code}'): {result}")
        
else:
    print(f"\n❌ Sin suscripción activa")

print("\n" + "=" * 80)
