"""
Script de diagnóstico para verificar permisos de usuario en local
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import UserSubscription
from apps.organizations.models import Organization, OrganizationMember, SubscriptionPlan
from apps.organizations.plan_features import has_module_access, PLAN_MODULES, get_plan_modules

User = get_user_model()

print("=" * 70)
print("DIAGNÓSTICO DE PERMISOS - ENTORNO LOCAL")
print("=" * 70)

# 1. Listar todos los usuarios
print("\n1. USUARIOS EN EL SISTEMA:")
print("-" * 70)
users = User.objects.all()
for user in users:
    print(f"  - {user.username} (ID: {user.id}) - Email: {user.email}")
    print(f"    Superuser: {user.is_superuser}")

# Pedir al usuario que elija
print("\n¿Con qué usuario quieres hacer el diagnóstico?")
username = input("Escribe el username (o presiona Enter para usar el primero): ").strip()

if not username and users.exists():
    user = users.first()
    print(f"Usando usuario: {user.username}")
elif username:
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ Usuario '{username}' no encontrado")
        exit(1)
else:
    print("❌ No hay usuarios en el sistema")
    exit(1)

print(f"\n{'='*70}")
print(f"DIAGNÓSTICO PARA: {user.username}")
print(f"{'='*70}")

# 2. Verificar suscripción del usuario
print("\n2. SUSCRIPCIÓN DEL USUARIO:")
print("-" * 70)
try:
    subscription = UserSubscription.objects.get(user=user)
    print(f"✅ Usuario tiene suscripción")
    print(f"   Plan: {subscription.plan.name}")
    print(f"   Plan Type: {subscription.plan.plan_type}")
    print(f"   Activa: {subscription.is_active}")
    print(f"   Inicio: {subscription.start_date}")
    print(f"   Fin: {subscription.end_date}")
    print(f"   Trial: {subscription.is_trial}")
except UserSubscription.DoesNotExist:
    print("❌ Usuario NO tiene suscripción")
    subscription = None

# 3. Verificar membresías a organizaciones
print("\n3. ORGANIZACIONES DEL USUARIO:")
print("-" * 70)
memberships = OrganizationMember.objects.filter(user=user)
if memberships.exists():
    for membership in memberships:
        print(f"✅ Organización: {membership.organization.name}")
        print(f"   Slug: {membership.organization.slug}")
        print(f"   Activa: {membership.is_active}")
        print(f"   Rol: {membership.role}")
        print(f"   Org Activa: {membership.organization.is_active}")
        
        # Verificar suscripción de la organización
        if hasattr(membership.organization, 'subscription'):
            org_sub = membership.organization.subscription
            print(f"   Plan Org: {org_sub.plan.name} (Type: {org_sub.plan.plan_type})")
            print(f"   Suscripción activa: {org_sub.is_active}")
        else:
            print(f"   ⚠️ Organización sin suscripción")
else:
    print("⚠️ Usuario NO pertenece a ninguna organización")

# 4. Verificar todos los planes en el sistema
print("\n4. PLANES DISPONIBLES EN EL SISTEMA:")
print("-" * 70)
plans = SubscriptionPlan.objects.all()
for plan in plans:
    print(f"  - {plan.name} (Type: {plan.plan_type}) - Activo: {plan.is_active}")

# 5. Verificar módulos disponibles según plan
if subscription:
    print(f"\n5. MÓDULOS DISPONIBLES PARA PLAN '{subscription.plan.plan_type.upper()}':")
    print("-" * 70)
    modules = get_plan_modules(subscription.plan.plan_type)
    print(f"Total: {len(modules)} módulos")
    for i, module in enumerate(modules, 1):
        print(f"  {i:2d}. {module}")

# 6. Verificar acceso a módulos críticos
print("\n6. VERIFICACIÓN DE ACCESO A MÓDULOS CRÍTICOS:")
print("-" * 70)

critical_modules = [
    'billing',
    'invoices',
    'invoices_dian',
    'dian_config',
    'payroll',
    'payroll_dian',
    'payroll_config',
    'marketing',
    'promotions',
    'workflows',
]

for module in critical_modules:
    has_access = has_module_access(user, module)
    status = "✅" if has_access else "❌"
    print(f"{status} {module:20s} - {'ACCESO PERMITIDO' if has_access else 'ACCESO DENEGADO'}")

# 7. Verificar función has_module_access con detalle
print("\n7. ANÁLISIS DETALLADO DE has_module_access():")
print("-" * 70)

print(f"user.is_superuser: {user.is_superuser}")

# Simular la lógica de has_module_access
if user.is_superuser:
    print("✅ Usuario es superuser - Acceso total")
else:
    # Verificar membresía
    membership = OrganizationMember.objects.filter(
        user=user,
        is_active=True,
        organization__is_active=True
    ).select_related('organization', 'organization__subscription', 'organization__subscription__plan').first()
    
    if membership and hasattr(membership.organization, 'subscription'):
        org_plan = membership.organization.subscription.plan
        print(f"✅ Membresía encontrada")
        print(f"   Organización: {membership.organization.name}")
        print(f"   Plan: {org_plan.name} (Type: {org_plan.plan_type})")
        print(f"   Módulos del plan: {len(get_plan_modules(org_plan.plan_type))}")
    else:
        print("⚠️ Sin membresía activa con suscripción")
        
        # Fallback a suscripción personal
        try:
            user_sub = UserSubscription.objects.select_related('plan').get(user=user, is_active=True)
            print(f"✅ Usando suscripción personal")
            print(f"   Plan: {user_sub.plan.name} (Type: {user_sub.plan.plan_type})")
            print(f"   Módulos del plan: {len(get_plan_modules(user_sub.plan.plan_type))}")
        except UserSubscription.DoesNotExist:
            print("❌ Sin suscripción personal activa")

print("\n" + "=" * 70)
print("DIAGNÓSTICO COMPLETADO")
print("=" * 70)
