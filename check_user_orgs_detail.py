from django.contrib.auth import get_user_model
from apps.users.models import UserSubscription
from apps.organizations.models import Organization

User = get_user_model()

user = User.objects.get(username='danioso8329')
print(f'Usuario: {user.username}')

# Ver suscripción
try:
    sub = UserSubscription.objects.get(user=user)
    print(f'\n=== Suscripción ===')
    print(f'Plan: {sub.plan.name}')
    print(f'Max organizaciones: {sub.plan.max_organizations}')
    print(f'Activa: {sub.is_active}')
    print(f'Expirada: {sub.is_expired}')
    print(f'can_create_organizations(): {sub.can_create_organizations()}')
except Exception as e:
    print(f'Error obteniendo suscripción: {e}')

# Ver organizaciones que posee
print(f'\n=== Organizaciones como Owner ===')
owned = Organization.objects.filter(owner=user)
print(f'Total: {owned.count()}')
for org in owned:
    print(f'  - {org.name} (activa: {org.is_active})')

# Ver todas las organizaciones donde es miembro
print(f'\n=== Como Miembro ===')
from apps.organizations.models import OrganizationUser
memberships = OrganizationUser.objects.filter(user=user)
print(f'Total: {memberships.count()}')
for membership in memberships:
    print(f'  - {membership.organization.name} (rol: {membership.role})')
