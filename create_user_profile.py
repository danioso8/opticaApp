"""
Crear UserProfile para danioso8329 y asignarlo a CompuEasys
"""

from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.users.models import UserProfile

print("=" * 80)
print("CREANDO USERPROFILE PARA danioso8329")
print("=" * 80)

# Obtener usuario y organización
usuario = User.objects.get(username='danioso8329')
org = Organization.objects.get(id=2)

print(f"\n👤 Usuario: {usuario.username}")
print(f"🏢 Organización: {org.name} (ID: {org.id})")

# Crear o actualizar UserProfile
profile, created = UserProfile.objects.get_or_create(
    user=usuario,
    defaults={
        'phone': '',
    }
)

if created:
    print(f"\n✅ UserProfile creado")
else:
    print(f"\n⊙ UserProfile ya existía")

# Asignar organización si el campo existe
print(f"\n🔧 Configurando organización...")
print(f"   Campos disponibles en UserProfile:")
for field in profile._meta.get_fields():
    print(f"      - {field.name}")

# Intentar diferentes formas de asignar la organización
assigned = False

if hasattr(profile, 'organization'):
    profile.organization = org
    profile.save()
    print(f"\n✅ Asignado a profile.organization")
    assigned = True
elif hasattr(profile, 'current_organization'):
    profile.current_organization = org
    profile.save()
    print(f"\n✅ Asignado a profile.current_organization")
    assigned = True

# Verificar
print(f"\n📊 Verificación final:")
profile_updated = UserProfile.objects.get(user=usuario)
print(f"   UserProfile existe: ✅")
if hasattr(profile_updated, 'organization'):
    print(f"   Organización: {profile_updated.organization}")
elif hasattr(profile_updated, 'current_organization'):
    print(f"   Organización: {profile_updated.current_organization}")
else:
    print(f"   ⚠️  UserProfile no tiene campo de organización")
    print(f"   Nota: La organización se asigna por sesión o middleware")

print(f"\n✅ Proceso completado")
print(f"\nNOTA: Si aún no ves los empleados, cierra sesión y vuelve a entrar.")
