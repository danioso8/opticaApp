import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.organizations.models import Organization, OrganizationMember
from apps.users.models import UserSubscription

User = get_user_model()

print("=" * 80)
print("DIAGNÓSTICO DE PERMISOS")
print("=" * 80)

# Usuario actual
user = User.objects.get(username='danioso8')
print(f"\n1. USUARIO: {user.username}")

# Suscripción del usuario
try:
    user_sub = UserSubscription.objects.get(user=user, is_active=True)
    print(f"   Suscripción personal: {user_sub.plan.name} ({user_sub.plan.plan_type})")
    print(f"   Trial: {user_sub.trial}, Payment status: {user_sub.payment_status}")
except UserSubscription.DoesNotExist:
    print("   ❌ No tiene suscripción personal")

# Membresía en organización
membership = OrganizationMember.objects.filter(
    user=user,
    is_active=True,
    organization__is_active=True
).select_related('organization').first()

if membership:
    org = membership.organization
    print(f"\n2. ORGANIZACIÓN: {org.name}")
    print(f"   Owner: {org.owner.username}")
    print(f"   Es owner: {org.owner == user}")
    
    # Suscripción del OWNER
    try:
        owner_sub = UserSubscription.objects.get(user=org.owner, is_active=True)
        print(f"\n3. SUSCRIPCIÓN DEL OWNER ({org.owner.username}):")
        print(f"   Plan: {owner_sub.plan.name} ({owner_sub.plan.plan_type})")
        print(f"   Trial: {owner_sub.trial}, Payment status: {owner_sub.payment_status}")
        print(f"   Needs payment: {owner_sub.needs_payment_after_trial()}")
    except UserSubscription.DoesNotExist:
        print(f"\n3. ❌ El OWNER ({org.owner.username}) NO tiene suscripción")
    
    # Suscripción de la organización (si existe)
    org_sub = org.current_subscription
    if org_sub:
        print(f"\n4. SUSCRIPCIÓN DE LA ORGANIZACIÓN:")
        print(f"   Plan: {org_sub.plan.name if org_sub.plan else 'N/A'}")
        print(f"   Plan type: {org_sub.plan_type}")
        print(f"   Activa: {org_sub.is_active}")
        print(f"   Vence: {org_sub.end_date}")
else:
    print("\n❌ No pertenece a ninguna organización")

print("\n" + "=" * 80)
print("PROBLEMA IDENTIFICADO:")
print("=" * 80)
print("""
La función has_module_access() en plan_features.py primero verifica la suscripción 
del OWNER de la organización, NO la suscripción de la organización misma.

Líneas 302-307:
    org_subscription = UserSubscription.objects.filter(
        user=membership.organization.owner,  # ← PROBLEMA AQUÍ
        is_active=True
    ).first()

Debería verificar:
    - organization.current_subscription (Subscription model)
    - NO user subscription del owner
""")
print("=" * 80)
