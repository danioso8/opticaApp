from django.contrib.auth import get_user_model
from apps.users.models import UserSubscription
from apps.organizations.models import SubscriptionPlan
from datetime import datetime, timedelta

User = get_user_model()
user = User.objects.get(username='danioso8329')
print(f'Usuario encontrado: {user.username}')

# Crear/actualizar plan empresarial
plan, created = SubscriptionPlan.objects.get_or_create(
    name='Plan Empresarial',
    defaults={
        'plan_type': 'enterprise',
        'price': 0,
        'max_users': 999999,
        'max_organizations': 999999,
        'max_appointments_per_month': 999999,
        'max_patients': 999999,
        'max_storage_mb': 999999,
        'allows_billing': True,
        'max_invoices_per_month': 999999,
        'is_active': True,
    }
)

# Actualizar todos los límites a ilimitado
plan.max_users = 999999
plan.max_organizations = 999999
plan.max_appointments_per_month = 999999
plan.max_patients = 999999
plan.max_storage_mb = 999999
plan.allows_billing = True
plan.max_invoices_per_month = 999999
plan.whatsapp_messages_included = 999999
plan.max_whatsapp_messages = 999999
plan.is_active = True
plan.save()

print(f'Plan configurado: {plan.name}')

# Actualizar suscripción existente
from django.utils import timezone
sub = UserSubscription.objects.get(user=user)
sub.plan = plan
sub.start_date = timezone.now()
sub.end_date = timezone.now() + timedelta(days=3650)  # 10 años
sub.is_active = True
sub.auto_renew = True
sub.save()

print('✅ Usuario danioso8329 configurado con Plan Empresarial Ilimitado')
print(f'Válido hasta: {sub.end_date}')
