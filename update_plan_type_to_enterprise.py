import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import SubscriptionPlan

# Actualizar el plan empresarial a plan_type='enterprise'
plan = SubscriptionPlan.objects.get(id=8)
print(f"Plan actual: {plan.name}")
print(f"Tipo actual: {plan.plan_type}")

plan.plan_type = 'enterprise'
plan.save()

print(f"\n✓ Plan actualizado correctamente")
print(f"Nuevo tipo: {plan.plan_type}")
