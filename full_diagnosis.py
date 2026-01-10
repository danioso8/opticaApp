from django.contrib.auth import get_user_model
from apps.organizations.models import Organization, OrganizationMember
from apps.users.models import UserSubscription
from apps.organizations.plan_features import has_module_access, get_plan_modules

User = get_user_model()

user = User.objects.get(username='danioso8329')
print(f'=== Usuario: {user.username} ===')
print(f'is_superuser: {user.is_superuser}')
print(f'is_staff: {user.is_staff}')

# Suscripción personal
try:
    personal_sub = UserSubscription.objects.get(user=user)
    print(f'\nSuscripción personal:')
    print(f'  Plan: {personal_sub.plan.name} ({personal_sub.plan.plan_type})')
    print(f'  Activa: {personal_sub.is_active}')
    print(f'  Módulos del plan: {len(get_plan_modules(personal_sub.plan.plan_type))}')
except Exception as e:
    print(f'\nSin suscripción personal: {e}')

# Membresía
membership = OrganizationMember.objects.filter(
    user=user,
    is_active=True,
    organization__is_active=True
).select_related('organization').first()

if membership:
    org = membership.organization
    print(f'\nMembresía en: {org.name}')
    print(f'  Owner: {org.owner.username} (ID: {org.owner.id})')
    print(f'  User ID: {user.id}')
    print(f'  Es el owner: {org.owner.id == user.id}')
    
    # Suscripción del owner
    try:
        owner_sub = UserSubscription.objects.get(user=org.owner)
        print(f'\nSuscripción del owner ({org.owner.username}):')
        print(f'  Plan: {owner_sub.plan.name} ({owner_sub.plan.plan_type})')
        print(f'  Activa: {owner_sub.is_active}')
        print(f'  needs_payment_after_trial: {owner_sub.needs_payment_after_trial()}')
    except Exception as e:
        print(f'\nError obteniendo suscripción del owner: {e}')

# Probar acceso a módulos clave
print(f'\n=== Prueba de Acceso a Módulos ===')
test_modules = ['dashboard', 'payroll_dian', 'workflows', 'promotions', 'reports']
for mod in test_modules:
    access = has_module_access(user, mod)
    print(f'{mod}: {"✓ SÍ" if access else "✗ NO"}')
