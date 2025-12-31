import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import Organization, OrganizationMember

# Obtener el usuario actual (probablemente el que estás usando)
users = User.objects.all()
print(f"Total usuarios: {users.count()}")

for user in users:
    print(f"\n👤 Usuario: {user.username} ({user.email})")
    
    # Verificar si tiene membresía en alguna organización
    memberships = OrganizationMember.objects.filter(user=user)
    
    if memberships.exists():
        print(f"   ✅ Tiene {memberships.count()} membresía(s)")
        for membership in memberships:
            print(f"      - {membership.organization.name} ({membership.get_role_display()})")
    else:
        print(f"   ❌ NO TIENE MEMBRESÍA EN NINGUNA ORGANIZACIÓN")
        
        # Buscar organizaciones disponibles
        orgs = Organization.objects.all()
        print(f"   Organizaciones disponibles: {orgs.count()}")
        
        if orgs.exists():
            org = orgs.first()
            # Crear membresía como owner del primer usuario, staff para los demás
            role = 'owner' if not OrganizationMember.objects.filter(organization=org).exists() else 'staff'
            membership = OrganizationMember.objects.create(
                organization=org,
                user=user,
                role=role
            )
            print(f"   ✅ Membresía creada en: {org.name} como {membership.get_role_display()}")
        else:
            print(f"   ⚠️ No hay organizaciones en el sistema. Creando una...")
            org = Organization.objects.create(
                name="Océano Óptico",
                slug="oceano-optico",
                is_active=True
            )
            membership = OrganizationMember.objects.create(
                organization=org,
                user=user,
                role='owner'
            )
            print(f"   ✅ Organización creada y membresía asignada: {org.name} como {membership.get_role_display()}")

print("\n✅ Proceso completado!")
