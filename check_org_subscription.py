"""
Verificar suscripciones: Usuario vs Organización
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import UserSubscription
from apps.organizations.models import Organization, Subscription

User = get_user_model()

print("=" * 80)
print("VERIFICACIÓN DE SUSCRIPCIONES: USUARIO vs ORGANIZACIÓN")
print("=" * 80)

# Usuario
user = User.objects.get(username='danioso8')
print(f"\n👤 USUARIO: {user.username}")
print("-" * 80)

try:
    user_sub = UserSubscription.objects.get(user=user)
    print(f"✅ Suscripción Personal:")
    print(f"   Plan: {user_sub.plan.name}")
    print(f"   Plan Type: {user_sub.plan.plan_type}")
    print(f"   Activa: {user_sub.is_active}")
    print(f"   Vence en: {user_sub.days_remaining} días")
except UserSubscription.DoesNotExist:
    print("❌ Sin suscripción personal")

# Organización
print(f"\n🏢 ORGANIZACIÓN: CompuEasys")
print("-" * 80)

try:
    org = Organization.objects.get(slug='compueasys')
    print(f"✅ Organización encontrada: {org.name}")
    print(f"   Owner: {org.owner.username if org.owner else 'Sin owner'}")
    print(f"   Activa: {org.is_active}")
    
    # Verificar si tiene suscripción
    print(f"\n   Verificando suscripción de la organización...")
    
    # Método 1: current_subscription property
    current_sub = org.current_subscription
    if current_sub:
        print(f"\n   ✅ current_subscription (property):")
        print(f"      Plan: {current_sub.plan.name}")
        print(f"      Plan Type: {current_sub.plan.plan_type}")
        print(f"      Activa: {current_sub.is_active}")
        print(f"      Vence en: {current_sub.days_remaining} días")
    else:
        print(f"\n   ❌ current_subscription es None")
    
    # Método 2: Buscar Subscription directamente
    try:
        org_subs = Subscription.objects.filter(organization=org)
        print(f"\n   Subscription en BD: {org_subs.count()}")
        
        for sub in org_subs:
            print(f"\n   Suscripción encontrada:")
            print(f"      ID: {sub.id}")
            print(f"      Plan: {sub.plan.name}")
            print(f"      Plan Type: {sub.plan.plan_type}")
            print(f"      Activa: {sub.is_active}")
            print(f"      Inicio: {sub.start_date}")
            print(f"      Fin: {sub.end_date}")
            
    except Exception as e:
        print(f"   ❌ Error buscando Subscription: {e}")
    
except Organization.DoesNotExist:
    print("❌ Organización no encontrada")

print("\n" + "=" * 80)
print("DIAGNÓSTICO")
print("=" * 80)

if org.current_subscription:
    if org.current_subscription.plan.plan_type != 'enterprise':
        print(f"\n❌ PROBLEMA ENCONTRADO:")
        print(f"   La organización tiene plan: {org.current_subscription.plan.plan_type}")
        print(f"   Pero se requiere: enterprise")
        print(f"\n💡 SOLUCIÓN:")
        print(f"   Cambiar el plan de la organización a enterprise")
    else:
        print(f"\n✅ La organización tiene plan enterprise")
        print(f"   Verifica que tenga los features asociados")
else:
    print(f"\n❌ PROBLEMA ENCONTRADO:")
    print(f"   La organización NO tiene suscripción")
    print(f"\n💡 SOLUCIÓN:")
    print(f"   Crear Subscription para CompuEasys con plan enterprise")

print("\n" + "=" * 80)
