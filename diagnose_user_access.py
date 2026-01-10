from django.contrib.auth import get_user_model
from apps.users.models import UserSubscription
from apps.organizations.models import OrganizationMember
from apps.organizations.plan_features import has_module_access, get_plan_modules

User = get_user_model()

print("="*70)
print("🔍 DIAGNÓSTICO DE ACCESO A MÓDULOS - danioso8329")
print("="*70)

user = User.objects.get(username='danioso8329')

# Verificar suscripción
subscription = UserSubscription.objects.get(user=user)
print(f"\n📋 Suscripción:")
print(f"   Plan: {subscription.plan.name}")
print(f"   Plan Type: {subscription.plan.plan_type}")
print(f"   Activa: {subscription.is_active}")
print(f"   Trial expirado: {subscription.needs_payment_after_trial()}")

# Verificar membresía
membership = OrganizationMember.objects.filter(
    user=user,
    is_active=True
).select_related('organization').first()

if membership:
    print(f"\n🏢 Organización:")
    print(f"   Nombre: {membership.organization.name}")
    print(f"   Owner: {membership.organization.owner.username}")
    print(f"   Es owner: {membership.organization.owner == user}")
    
    # Verificar suscripción del owner
    if membership.organization.owner != user:
        try:
            owner_sub = UserSubscription.objects.get(user=membership.organization.owner)
            print(f"\n👤 Suscripción del Owner:")
            print(f"   Plan: {owner_sub.plan.name}")
            print(f"   Plan Type: {owner_sub.plan.plan_type}")
            print(f"   Activa: {owner_sub.is_active}")
        except:
            print(f"\n⚠️  Owner no tiene suscripción")

# Obtener módulos del plan
plan_modules = get_plan_modules(subscription.plan.plan_type)
print(f"\n📦 Módulos disponibles en el plan ({len(plan_modules)} módulos):")
for i, module in enumerate(sorted(plan_modules), 1):
    print(f"   {i}. {module}")

# Probar acceso a módulos comunes
test_modules = [
    'dashboard', 'patients', 'appointments', 'invoices_dian',
    'payroll_dian', 'payroll_config', 'workflows', 'promotions',
    'analytics', 'api_access', 'audit'
]

print(f"\n🔐 Prueba de acceso a módulos:")
for module in test_modules:
    access = has_module_access(user, module)
    status = "✅" if access else "❌"
    in_list = "✓" if module in plan_modules else "✗"
    print(f"   {status} {module:25} (en lista: {in_list})")

print("\n" + "="*70)
