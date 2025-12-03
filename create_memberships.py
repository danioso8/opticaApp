from django.contrib.auth import get_user_model
from apps.organizations.models import Organization, OrganizationMember

User = get_user_model()

# Obtener todos los usuarios
users = User.objects.all()
org = Organization.objects.first()

print(f"\n=== Asignando usuarios a organización: {org.name} ===\n")

for user in users:
    # Verificar si ya tiene un membership
    existing = OrganizationMember.objects.filter(user=user, organization=org).first()
    
    if existing:
        print(f"✓ {user.username} ya tiene membership en {org.name}")
    else:
        # Crear membership
        OrganizationMember.objects.create(
            user=user,
            organization=org,
            role='admin',
            is_active=True
        )
        print(f"✅ {user.username} agregado como admin a {org.name}")

print("\n=== Memberships creados exitosamente ===")
