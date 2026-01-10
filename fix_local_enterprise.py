"""
Script para configurar usuario con plan enterprise sin trial en LOCAL
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import UserSubscription
from apps.organizations.models import SubscriptionPlan
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

print("=" * 70)
print("CONFIGURAR USUARIO ENTERPRISE (SIN TRIAL)")
print("=" * 70)

# Obtener o crear usuario danioso8
try:
    user = User.objects.get(username='danioso8')
    print(f"\n✅ Usuario encontrado: {user.username}")
except User.DoesNotExist:
    print("\n❌ Usuario danioso8 no encontrado")
    exit(1)

# Obtener o crear plan enterprise
plan, created = SubscriptionPlan.objects.get_or_create(
    plan_type='enterprise',
    defaults={
        'name': 'Empresarial',
        'price_monthly': 0,
        'price_yearly': 0,
        'max_users': 999999,
        'max_organizations': 999999,
        'max_appointments_month': 999999,
        'max_patients': 999999,
        'max_storage_mb': 999999,
        'allow_electronic_invoicing': True,
        'max_invoices_month': 0,  # Ilimitado
        'is_active': True,
    }
)

if created:
    print(f"✅ Plan enterprise creado: {plan.name}")
else:
    print(f"✅ Plan enterprise encontrado: {plan.name}")
    # Actualizar límites
    plan.max_users = 999999
    plan.max_organizations = 999999
    plan.max_appointments_month = 999999
    plan.max_patients = 999999
    plan.max_storage_mb = 999999
    plan.allow_electronic_invoicing = True
    plan.max_invoices_month = 0
    plan.is_active = True
    plan.save()
    print(f"✅ Plan actualizado a límites ilimitados")

# Obtener o actualizar suscripción
try:
    subscription = UserSubscription.objects.get(user=user)
    print(f"\n✅ Suscripción existente encontrada")
    print(f"   Plan actual: {subscription.plan.name} ({subscription.plan.plan_type})")
    print(f"   Trial: {subscription.is_trial}")
    print(f"   Payment status: {subscription.payment_status}")
    
    # Actualizar a enterprise sin trial
    subscription.plan = plan
    subscription.is_trial = False  # SIN TRIAL
    subscription.trial_end_date = None
    subscription.payment_status = 'paid'  # PAGADO
    subscription.start_date = timezone.now()
    subscription.end_date = timezone.now() + timedelta(days=3650)  # 10 años
    subscription.is_active = True
    subscription.auto_renew = True
    subscription.save()
    
    print(f"\n✅ Suscripción actualizada:")
    print(f"   Plan: {subscription.plan.name}")
    print(f"   Plan Type: {subscription.plan.plan_type}")
    print(f"   Trial: {subscription.is_trial}")
    print(f"   Payment Status: {subscription.payment_status}")
    print(f"   Válido hasta: {subscription.end_date}")
    
except UserSubscription.DoesNotExist:
    print(f"\n⚠️  Creando nueva suscripción")
    subscription = UserSubscription.objects.create(
        user=user,
        plan=plan,
        is_trial=False,
        payment_status='paid',
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=3650),
        is_active=True,
        auto_renew=True,
        billing_cycle='yearly'
    )
    print(f"✅ Suscripción creada")

print(f"\n{'='*70}")
print(f"CONFIGURACIÓN COMPLETADA")
print(f"{'='*70}")
print(f"\n🔑 Ahora cierra sesión y vuelve a entrar para actualizar permisos")
