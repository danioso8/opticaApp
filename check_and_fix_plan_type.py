from django.contrib.auth import get_user_model
from apps.organizations.models import SubscriptionPlan
from apps.users.models import UserSubscription

User = get_user_model()

print("="*70)
print("🔍 VERIFICANDO PLAN EMPRESARIAL")
print("="*70)

# Obtener el plan empresarial
try:
    plan = SubscriptionPlan.objects.get(name='Plan Empresarial')
    print(f"\n✅ Plan encontrado:")
    print(f"   Nombre: {plan.name}")
    print(f"   plan_type actual: '{plan.plan_type}'")
    print(f"   ID: {plan.id}")
    
    # Verificar si plan_type es correcto
    if plan.plan_type != 'enterprise':
        print(f"\n⚠️  El plan_type está incorrecto!")
        print(f"   Actual: '{plan.plan_type}'")
        print(f"   Debería ser: 'enterprise'")
        
        # Corregir el plan_type
        plan.plan_type = 'enterprise'
        plan.save()
        print(f"\n✅ plan_type corregido a 'enterprise'")
    else:
        print(f"\n✅ El plan_type ya está correcto: 'enterprise'")
    
    # Verificar usuarios con este plan
    print(f"\n📋 Usuarios con Plan Empresarial:")
    subscriptions = UserSubscription.objects.filter(plan=plan, is_active=True)
    for sub in subscriptions:
        print(f"   - {sub.user.username}: {sub.plan.name} (plan_type: {sub.plan.plan_type})")
    
except SubscriptionPlan.DoesNotExist:
    print("❌ Plan Empresarial no encontrado")
    print("\n📋 Planes disponibles:")
    for p in SubscriptionPlan.objects.all():
        print(f"   - {p.name} (plan_type: '{p.plan_type}')")

print("\n" + "="*70)
