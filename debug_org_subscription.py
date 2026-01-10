from django.contrib.auth import get_user_model
from apps.organizations.models import Organization, OrganizationMember
from apps.users.models import UserSubscription

User = get_user_model()

user = User.objects.get(username='danioso8329')
print(f'Usuario: {user.username} (ID: {user.id})')

# Ver suscripción personal
try:
    personal_sub = UserSubscription.objects.get(user=user)
    print(f'\n=== Suscripción Personal ===')
    print(f'Plan: {personal_sub.plan.name}')
    print(f'Plan type: {personal_sub.plan.plan_type}')
    print(f'Activa: {personal_sub.is_active}')
except:
    print('\nSin suscripción personal')

# Ver organizaciones donde es miembro
memberships = OrganizationMember.objects.filter(user=user, is_active=True)
print(f'\n=== Membresías Activas ({memberships.count()}) ===')
for membership in memberships:
    org = membership.organization
    print(f'\nOrganización: {org.name}')
    print(f'  Owner: {org.owner.username} (ID: {org.owner.id})')
    print(f'  Usuario es owner: {org.owner.id == user.id}')
    
    # Ver suscripción del owner
    try:
        owner_sub = UserSubscription.objects.get(user=org.owner)
        print(f'  Suscripción del owner:')
        print(f'    Plan: {owner_sub.plan.name}')
        print(f'    Plan type: {owner_sub.plan.plan_type}')
        print(f'    Activa: {owner_sub.is_active}')
    except:
        print(f'  ❌ El owner no tiene suscripción')

# Ver organizaciones donde es owner
orgs_owned = Organization.objects.filter(owner=user)
print(f'\n=== Organizaciones como Owner ({orgs_owned.count()}) ===')
for org in orgs_owned:
    print(f'- {org.name} (activa: {org.is_active})')
