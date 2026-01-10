"""
Verificar que el sistema de verificación de módulos funciona correctamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import SubscriptionPlan
from apps.organizations.plan_features import has_module_access
from apps.users.models import UserSubscription

print("\n" + "="*70)
print("🔍 PRUEBA DE VERIFICACIÓN DE ACCESO A MÓDULOS")
print("="*70)

# Obtener módulos del plan Free
free_plan = SubscriptionPlan.objects.get(plan_type='free')
free_modules = set(free_plan.features.values_list('code', flat=True))

print(f"\n📋 Plan Free tiene {len(free_modules)} módulos:")
for mod in sorted(free_modules):
    print(f"   ✅ {mod}")

# Módulos que NO están en Free
from apps.organizations.models import PlanFeature
all_modules = set(PlanFeature.objects.values_list('code', flat=True))
not_in_free = all_modules - free_modules

print(f"\n❌ Módulos NO disponibles en Free ({len(not_in_free)}):")
for mod in sorted(not_in_free):
    print(f"   🔒 {mod}")

# Probar con un usuario del plan Free
try:
    user_free = User.objects.filter(
        usersubscription__plan__plan_type='free',
        usersubscription__is_active=True
    ).first()
    
    if user_free:
        print(f"\n👤 Usuario de prueba: {user_free.username}")
        sub = UserSubscription.objects.get(user=user_free, is_active=True)
        print(f"   Plan: {sub.plan.name}")
        
        print("\n🧪 Probando acceso:")
        
        # Probar módulos que SÍ debe tener
        test_has = ['dashboard', 'patients', 'appointments', 'invoices_basic']
        print("\n   Módulos que SÍ debe tener acceso:")
        for mod in test_has:
            if mod in free_modules:
                has_access = has_module_access(user_free, mod)
                icon = "✅" if has_access else "❌ ERROR"
                print(f"      {icon} {mod}: {has_access}")
        
        # Probar módulos que NO debe tener
        test_not_has = ['whatsapp_integration', 'electronic_invoicing', 'payroll_dian', 'api_rest']
        print("\n   Módulos que NO debe tener acceso:")
        for mod in test_not_has:
            if mod in not_in_free:
                has_access = has_module_access(user_free, mod)
                icon = "✅ OK" if not has_access else "❌ ERROR - tiene acceso cuando NO debería"
                print(f"      {icon} {mod}: {has_access}")
    else:
        print("\n⚠️ No hay usuarios con plan Free para probar")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("✅ Verificación completada")
print("="*70 + "\n")
