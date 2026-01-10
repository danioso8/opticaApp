"""
Script para verificar que los módulos se estén verificando correctamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import SubscriptionPlan, PlanFeature
from apps.organizations.plan_features import has_module_access
from apps.users.models import UserSubscription

print("\n" + "="*70)
print("🔍 VERIFICACIÓN DE MÓDULOS Y ACCESO")
print("="*70)

# 1. Ver módulos del plan Free
free_plan = SubscriptionPlan.objects.get(plan_type='free')
print(f"\n📋 Plan FREE:")
print(f"   Módulos asignados: {free_plan.features.count()}")
if free_plan.features.count() > 0:
    print("   Códigos:", [f.code for f in free_plan.features.all()[:10]])

# 2. Ver módulos del plan Enterprise
enterprise_plan = SubscriptionPlan.objects.get(plan_type='enterprise')
print(f"\n📋 Plan ENTERPRISE:")
print(f"   Módulos asignados: {enterprise_plan.features.count()}")
if enterprise_plan.features.count() > 0:
    print("   Primeros 10:", [f.code for f in enterprise_plan.features.all()[:10]])

# 3. Verificar un usuario
try:
    user = User.objects.filter(is_superuser=False).first()
    if user:
        print(f"\n👤 Usuario de prueba: {user.username}")
        
        # Ver su suscripción
        try:
            sub = UserSubscription.objects.get(user=user, is_active=True)
            print(f"   Plan actual: {sub.plan.name} ({sub.plan.plan_type})")
            print(f"   Módulos en su plan: {sub.plan.features.count()}")
        except UserSubscription.DoesNotExist:
            print("   ⚠️ No tiene suscripción activa")
        
        # Probar has_module_access
        test_modules = ['dashboard', 'whatsapp', 'products', 'invoices_dian']
        print(f"\n   Probando acceso a módulos:")
        for module in test_modules:
            has_access = has_module_access(user, module)
            icon = "✅" if has_access else "❌"
            print(f"      {icon} {module}: {has_access}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*70)
print("✅ Verificación completada")
print("="*70 + "\n")
