from django.contrib.auth import get_user_model
from apps.organizations.models import Organization, OrganizationMember

User = get_user_model()

# Obtener usuario y organización
user = User.objects.get(username='danioso8')
org = Organization.objects.first()

# Crear o obtener membership
member, created = OrganizationMember.objects.get_or_create(
    user=user,
    organization=org,
    defaults={
        'role': 'admin',
        'is_active': True
    }
)

if created:
    print(f'✅ Miembro creado: {user.username} -> {org.name} (Admin)')
else:
    print(f'ℹ️ Miembro ya existía: {user.username} -> {org.name}')
