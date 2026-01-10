"""
Crear OrganizationMember para danioso8329
"""

from django.contrib.auth.models import User
from apps.organizations.models import Organization, OrganizationMember

print("=" * 80)
print("CREANDO MEMBRESÍA PARA danioso8329")
print("=" * 80)

# Obtener usuario y organización
usuario = User.objects.get(username='danioso8329')
org = Organization.objects.get(id=2)

print(f"\n👤 Usuario: {usuario.username}")
print(f"🏢 Organización: {org.name} (ID: {org.id})")

# Verificar si ya existe membresía
existing = OrganizationMember.objects.filter(user=usuario, organization=org)
print(f"\nMembresías existentes: {existing.count()}")

if existing.exists():
    for m in existing:
        print(f"   - {m.organization.name} - Rol: {m.role} - Activo: {m.is_active}")

# Crear o actualizar membresía
member, created = OrganizationMember.objects.get_or_create(
    user=usuario,
    organization=org,
    defaults={
        'role': 'OWNER',  # O 'ADMIN'
        'is_active': True,
    }
)

if created:
    print(f"\n✅ Membresía creada")
else:
    print(f"\n⊙ Membresía ya existía")
    # Asegurarse de que esté activa
    if not member.is_active:
        member.is_active = True
        member.save()
        print(f"   ✅ Activada")

print(f"\n📊 Membresía final:")
print(f"   Usuario: {member.user.username}")
print(f"   Organización: {member.organization.name}")
print(f"   Rol: {member.role}")
print(f"   Activo: {member.is_active}")

# Listar todas las membresías del usuario
print(f"\n📋 Todas las membresías de {usuario.username}:")
all_members = OrganizationMember.objects.filter(user=usuario)
for m in all_members:
    print(f"   - {m.organization.name} ({m.role}) - {'✅ Activo' if m.is_active else '❌ Inactivo'}")

print(f"\n✅ Proceso completado")
print(f"\n💡 IMPORTANTE: Cierra sesión y vuelve a entrar para que tome efecto")
