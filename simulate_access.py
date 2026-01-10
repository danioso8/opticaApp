from django.contrib.auth import get_user_model
from apps.organizations.models import Organization, OrganizationMember
from apps.users.models import UserSubscription
from apps.organizations.plan_features import has_module_access, get_plan_modules

User = get_user_model()

user = User.objects.get(username='danioso8329')
print(f'=== Simulando acceso de {user.username} ===\n')

# Simular lo que hace has_module_access
module_code = 'invoices_dian'

print(f'1. user.is_superuser: {user.is_superuser}')

# Buscar membresía
membership = OrganizationMember.objects.filter(
    user=user,
    is_active=True,
    organization__is_active=True
).select_related('organization').first()

if membership:
    print(f'2. Membership encontrada: {membership.organization.name}')
    print(f'   Organization activa: {membership.organization.is_active}')
    print(f'   Membership activa: {membership.is_active}')
    print(f'   Owner: {membership.organization.owner.username}')
    
    # Buscar suscripción del owner
    org_subscription = UserSubscription.objects.filter(
        user=membership.organization.owner,
        is_active=True
    ).first()
    
    if org_subscription:
        print(f'3. Suscripción del owner encontrada')
        print(f'   Plan: {org_subscription.plan.name}')
        print(f'   Plan type: {org_subscription.plan.plan_type}')
        print(f'   Activa: {org_subscription.is_active}')
        print(f'   needs_payment_after_trial: {org_subscription.needs_payment_after_trial()}')
        
        if not org_subscription.needs_payment_after_trial():
            plan_type = org_subscription.plan.plan_type
            allowed_modules = get_plan_modules(plan_type)
            print(f'4. Plan type: {plan_type}')
            print(f'   Módulos permitidos: {len(allowed_modules)}')
            print(f'   "{module_code}" en la lista: {module_code in allowed_modules}')
            
            if module_code in allowed_modules:
                print(f'\n✓ DEBERÍA TENER ACCESO')
            else:
                print(f'\n✗ NO TIENE ACCESO - módulo no está en la lista')
                print(f'\nMódulos enterprise:')
                for mod in allowed_modules:
                    print(f'  - {mod}')
    else:
        print(f'3. ❌ No se encontró suscripción activa del owner')
else:
    print(f'2. ❌ No se encontró membership activa')

# Test directo
print(f'\n=== Test Directo ===')
result = has_module_access(user, module_code)
print(f'has_module_access(user, "{module_code}"): {result}')
