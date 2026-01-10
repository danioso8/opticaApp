from django.contrib.auth import get_user_model
from apps.organizations.plan_features import has_module_access, get_required_plan_for_module, PLAN_MODULES

User = get_user_model()

user = User.objects.get(username='danioso8329')

# Módulos que dice que no tiene acceso
modules_to_test = [
    'payroll_dian',
    'workflows', 
    'promotions',
    'reports',
    'invoices_dian',
]

print(f'Usuario: {user.username}')
print(f'Es superuser: {user.is_superuser}')

from apps.users.models import UserSubscription
try:
    sub = UserSubscription.objects.get(user=user)
    print(f'Plan: {sub.plan.name}')
    print(f'Plan type: {sub.plan.plan_type}')
    print(f'Suscripción activa: {sub.is_active}')
except:
    print('Sin suscripción')

print(f'\n=== Módulos en plan enterprise ===')
print(f'Total: {len(PLAN_MODULES["enterprise"])}')
for mod in PLAN_MODULES["enterprise"]:
    print(f'  - {mod}')

print(f'\n=== Verificación de Acceso ===')
for module in modules_to_test:
    has_access = has_module_access(user, module)
    required = get_required_plan_for_module(module)
    in_enterprise = module in PLAN_MODULES.get('enterprise', [])
    
    status = "✓ ACCESO" if has_access else "✗ SIN ACCESO"
    print(f'{module}:')
    print(f'  has_module_access(): {status}')
    print(f'  Plan requerido: {required}')
    print(f'  En lista enterprise: {in_enterprise}')
