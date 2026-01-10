from django.contrib.auth import get_user_model
from apps.users.models import UserSubscription
from apps.organizations.models import SubscriptionPlan
from apps.organizations.plan_features import has_module_access, PLAN_MODULES

User = get_user_model()

print("=" * 60)
print("VERIFICACIÓN DE CONFIGURACIÓN ENTERPRISE")
print("=" * 60)

# Verificar usuario
user = User.objects.get(username='danioso8329')
print(f"\n✅ Usuario: {user.username}")

# Verificar suscripción
sub = UserSubscription.objects.get(user=user)
print(f"✅ Suscripción activa: {sub.is_active}")
print(f"✅ Plan: {sub.plan.name}")
print(f"✅ Plan Type: {sub.plan.plan_type}")
print(f"✅ Válido hasta: {sub.end_date}")

# Verificar módulos disponibles
print(f"\n📦 MÓDULOS ENTERPRISE DISPONIBLES:")
print(f"Total de módulos: {len(PLAN_MODULES.get('enterprise', []))}")
print("-" * 60)

enterprise_modules = PLAN_MODULES.get('enterprise', [])
for i, module in enumerate(enterprise_modules, 1):
    print(f"{i:2d}. {module}")

# Verificar acceso a módulos críticos
print("\n🔐 VERIFICACIÓN DE ACCESO A MÓDULOS CRÍTICOS:")
print("-" * 60)

critical_modules = [
    'billing',
    'invoices',
    'invoices_dian',
    'payroll',
    'payroll_dian',
    'payroll_config',
    'marketing',
    'promotions',
    'workflows',
    'analytics',
]

for module in critical_modules:
    has_access = has_module_access(user, module)
    status = "✅" if has_access else "❌"
    print(f"{status} {module}: {'ACCESO PERMITIDO' if has_access else 'ACCESO DENEGADO'}")

# Verificar ErrorLog model
print("\n🔍 VERIFICACIÓN DE MODELO ERRORLOG:")
print("-" * 60)
try:
    from apps.audit.models import ErrorLog
    count = ErrorLog.objects.count()
    print(f"✅ Modelo ErrorLog disponible")
    print(f"✅ Errores registrados: {count}")
except Exception as e:
    print(f"❌ Error al acceder a ErrorLog: {e}")

print("\n" + "=" * 60)
print("VERIFICACIÓN COMPLETADA")
print("=" * 60)
