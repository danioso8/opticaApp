"""
Test completo de acceso a módulos para usuario danioso8
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.organizations.plan_features import has_module_access, get_plan_modules
from apps.users.models import UserSubscription
from apps.organizations.models import OrganizationMember

User = get_user_model()

print("=" * 80)
print("TEST DE ACCESO A MÓDULOS - USUARIO danioso8")
print("=" * 80)

# Obtener usuario
user = User.objects.get(username='danioso8')
print(f"\n✅ Usuario: {user.username} (ID: {user.id})")
print(f"   Superuser: {user.is_superuser}")

# Verificar suscripción
print("\n" + "=" * 80)
print("1. VERIFICACIÓN DE SUSCRIPCIÓN")
print("=" * 80)

try:
    subscription = UserSubscription.objects.get(user=user)
    print(f"✅ Suscripción encontrada:")
    print(f"   Plan: {subscription.plan.name}")
    print(f"   Plan Type: {subscription.plan.plan_type}")
    print(f"   Activa: {subscription.is_active}")
    print(f"   Trial: {subscription.is_trial}")
    print(f"   Payment Status: {subscription.payment_status}")
    
    # Verificar needs_payment_after_trial
    needs_payment = subscription.needs_payment_after_trial()
    print(f"   Needs Payment After Trial: {needs_payment}")
    
    if needs_payment:
        print(f"\n❌ PROBLEMA DETECTADO: La suscripción requiere pago después del trial")
        print(f"   Esto bloqueará el acceso a todos los módulos excepto dashboard")
except UserSubscription.DoesNotExist:
    print("❌ NO tiene suscripción")
    subscription = None

# Verificar membresía
print("\n" + "=" * 80)
print("2. VERIFICACIÓN DE MEMBRESÍA A ORGANIZACIÓN")
print("=" * 80)

membership = OrganizationMember.objects.filter(
    user=user,
    is_active=True,
    organization__is_active=True
).select_related('organization').first()

if membership:
    print(f"✅ Membresía activa encontrada:")
    print(f"   Organización: {membership.organization.name}")
    print(f"   Rol: {membership.role}")
    print(f"   Owner: {membership.organization.owner}")
    
    # Verificar suscripción del owner
    if membership.organization.owner:
        try:
            owner_sub = UserSubscription.objects.filter(
                user=membership.organization.owner,
                is_active=True
            ).first()
            
            if owner_sub:
                print(f"\n✅ Suscripción del owner:")
                print(f"   Plan: {owner_sub.plan.name}")
                print(f"   Plan Type: {owner_sub.plan.plan_type}")
                print(f"   Needs Payment: {owner_sub.needs_payment_after_trial()}")
            else:
                print(f"\n⚠️ Owner no tiene suscripción activa")
        except Exception as e:
            print(f"\n❌ Error verificando owner: {e}")
else:
    print("⚠️ No tiene membresía activa")

# Test de acceso a TODOS los módulos
print("\n" + "=" * 80)
print("3. TEST DE ACCESO A TODOS LOS MÓDULOS ENTERPRISE")
print("=" * 80)

# Lista completa de módulos enterprise
all_modules = [
    'dashboard', 'patients', 'appointments', 'doctors', 'landing_config',
    'invoices_basic', 'invoices', 'billing', 'clinical_history', 'products',
    'inventory', 'suppliers', 'invoices_dian', 'dian_config', 'whatsapp',
    'notifications_config', 'wompi_payments', 'analytics', 'reports',
    'team_management', 'multi_location', 'api_access', 'payroll',
    'payroll_dian', 'payroll_config', 'workflows', 'promotions', 'marketing',
    'email_marketing', 'audit', 'permissions_advanced', 'configuration_advanced',
    'cash_register', 'sales', 'employees'
]

print(f"\nProbando acceso a {len(all_modules)} módulos...\n")

denied_modules = []
allowed_modules = []

for module in all_modules:
    has_access = has_module_access(user, module)
    status = "✅" if has_access else "❌"
    
    if has_access:
        allowed_modules.append(module)
    else:
        denied_modules.append(module)
    
    # Solo mostrar los denegados en detalle
    if not has_access:
        print(f"{status} {module:25s} - ACCESO DENEGADO")

# Resumen
print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print(f"✅ Módulos con acceso: {len(allowed_modules)}/{len(all_modules)}")
print(f"❌ Módulos denegados: {len(denied_modules)}/{len(all_modules)}")

if denied_modules:
    print(f"\n❌ MÓDULOS SIN ACCESO:")
    for module in denied_modules:
        print(f"   - {module}")
    
    print(f"\n🔍 DIAGNÓSTICO DEL PROBLEMA:")
    if subscription and subscription.needs_payment_after_trial():
        print(f"   ❌ La suscripción requiere pago después del trial")
        print(f"   ❌ Esto bloquea el acceso a todos los módulos excepto dashboard")
        print(f"\n💡 SOLUCIÓN:")
        print(f"   Ejecutar: python fix_local_enterprise.py")
        print(f"   Esto configurará is_trial=False y payment_status='paid'")
else:
    print(f"\n✅ PERFECTO! Todos los módulos están accesibles")

print("\n" + "=" * 80)
