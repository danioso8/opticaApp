from apps.organizations.models import SubscriptionPlan, PlanFeature

# Obtener el Plan Empresarial
plan = SubscriptionPlan.objects.get(name='Plan Empresarial')

print(f'=== {plan.name} ===')
print(f'Tipo: {plan.plan_type}')
print(f'\n=== Campos Booleanos de Características ===')
print(f'allow_electronic_invoicing: {plan.allow_electronic_invoicing}')
print(f'whatsapp_integration: {plan.whatsapp_integration}')
print(f'custom_branding: {plan.custom_branding}')
print(f'api_access: {plan.api_access}')
print(f'priority_support: {plan.priority_support}')
print(f'analytics: {plan.analytics}')
print(f'multi_location: {plan.multi_location}')

print(f'\n=== Features M2M Asignadas ===')
features = plan.features.all()
print(f'Total: {features.count()}')
for feature in features:
    print(f'  ✓ {feature.code}: {feature.name} ({feature.category})')

print(f'\n=== TODAS las Features Disponibles en el Sistema ===')
all_features = PlanFeature.objects.filter(is_active=True)
print(f'Total disponibles: {all_features.count()}')
for feature in all_features:
    has_it = plan.features.filter(code=feature.code).exists()
    status = '✓' if has_it else '✗'
    print(f'  {status} {feature.code}: {feature.name} ({feature.category})')
