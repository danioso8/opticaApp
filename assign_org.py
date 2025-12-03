from django.contrib.auth import get_user_model
from apps.organizations.models import Organization

User = get_user_model()

# Listar usuarios
users = User.objects.all()
print("\n=== USUARIOS ===")
for u in users:
    org = getattr(u, 'organization', None)
    print(f"Username: {u.username} (ID: {u.id})")
    print(f"  Organization: {org}")
    print()

# Obtener organización existente
org = Organization.objects.first()
if org:
    print(f"\n=== ORGANIZACIÓN ENCONTRADA ===")
    print(f"Nombre: {org.name}")
    print(f"Slug: {org.slug}")
    
    # Asignar a todos los usuarios
    print("\n=== ASIGNANDO ORGANIZACIÓN A USUARIOS ===")
    for user in users:
        user.organization = org
        user.save()
        print(f"✅ {user.username} -> {org.name}")
else:
    print("❌ No hay organizaciones en la base de datos")
