from apps.organizations.models import SubscriptionPlan

plan = SubscriptionPlan.objects.get(name='Plan Empresarial')
print(f'Nombre: {plan.name}')
print(f'plan_type actual: "{plan.plan_type}"')
print(f'Slug: {plan.slug}')

# Ver todos los planes y sus tipos
print(f'\n=== Todos los Planes ===')
for p in SubscriptionPlan.objects.all():
    print(f'{p.name}: plan_type="{p.plan_type}", slug="{p.slug}"')
