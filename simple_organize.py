import json
from django.contrib.auth.models import User
from apps.organizations.models import Organization, OrganizationMember
from apps.patients.models import Doctor

print("=" * 80)
print("ORGANIZANDO USUARIOS Y ORGANIZACIONES")
print("=" * 80)

# Obtener usuarios
danioso_user = User.objects.get(username='danioso8')
julio_user = User.objects.get(username='juliozapata')

print(f"\nUsuarios encontrados:")
print(f"  - {danioso_user.username} (ID: {danioso_user.id})")
print(f"  - {julio_user.username} (ID: {julio_user.id})")

# Obtener todas las organizaciones
orgs = Organization.objects.all()
print(f"\nOrganizaciones encontradas: {orgs.count()}")
for org in orgs:
    print(f"  [{org.id}] {org.name}")

# Crear membresías para danioso8 en todas las organizaciones
print("\n" + "-" * 80)
print("ASIGNANDO danioso8 COMO ADMIN DE TODAS LAS ORGANIZACIONES")
print("-" * 80)

for org in orgs:
    member, created = OrganizationMember.objects.get_or_create(
        user=danioso_user,
        organization=org,
        defaults={
            'role': 'admin',
            'is_active': True
        }
    )
    if created:
        print(f"  ✅ {danioso_user.username} → {org.name} (admin)")
    else:
        print(f"  ℹ️  {danioso_user.username} ya estaba en {org.name}")

# Asignar Julio a Oceano Optico SJ
print("\n" + "-" * 80)
print("ASIGNANDO juliozapata A OCEANO OPTICO SJ")
print("-" * 80)

oceano_org = Organization.objects.filter(name__icontains='Oceano').first()
if oceano_org:
    member, created = OrganizationMember.objects.get_or_create(
        user=julio_user,
        organization=oceano_org,
        defaults={
            'role': 'member',
            'is_active': True
        }
    )
    if created:
        print(f"  ✅ {julio_user.username} → {oceano_org.name} (member)")
    else:
        print(f"  ℹ️  {julio_user.username} ya estaba en {oceano_org.name}")
else:
    print("  ⚠️  No se encontró organización Oceano")

# Mostrar doctores y sus organizaciones
print("\n" + "-" * 80)
print("DOCTORES Y SUS ORGANIZACIONES")
print("-" * 80)

doctors = Doctor.objects.all()
for doctor in doctors:
    org = Organization.objects.filter(id=doctor.organization_id).first()
    org_name = org.name if org else "Sin organización"
    print(f"  - Dr. {doctor.full_name} → {org_name}")

# Resumen final
print("\n" + "=" * 80)
print("RESUMEN FINAL")
print("=" * 80)

print(f"\n📊 Estadísticas:")
print(f"  Usuarios: {User.objects.count()}")
print(f"  Organizaciones: {Organization.objects.count()}")
print(f"  Membresías: {OrganizationMember.objects.count()}")
print(f"  Doctores: {Doctor.objects.count()}")

print(f"\n👥 Membresías configuradas:")
for member in OrganizationMember.objects.all().select_related('user', 'organization'):
    role_emoji = "🔑" if member.role == 'admin' else "👤"
    print(f"  {role_emoji} {member.user.username} → {member.organization.name} ({member.role})")

print("\n✅ Organización completada!")
