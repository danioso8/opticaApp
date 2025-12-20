from django.contrib.auth.models import User
from apps.organizations.models import Organization, OrganizationMember

print("=" * 80)
print("CREANDO USUARIOS FALTANTES DEL BACKUP")
print("=" * 80)

# Usuario 1: OceanoSJ (era el usuario original principal)
print("\n1. Creando usuario OceanoSJ...")
oceanosj_user, created = User.objects.get_or_create(
    username='OceanoSJ',
    defaults={
        'first_name': 'Oceano',
        'last_name': 'Optico San Juan',
        'email': 'admin@oceanoopticosj.com',
        'is_staff': True,
        'is_superuser': False,
        'is_active': True
    }
)

if created:
    oceanosj_user.set_password('oceano2025')
    oceanosj_user.save()
    print(f"  ✅ Usuario creado: {oceanosj_user.username}")
    print(f"     Email: {oceanosj_user.email}")
    print(f"     Contraseña: oceano2025")
else:
    print(f"  ℹ️  Usuario ya existe: {oceanosj_user.username}")

# Usuario 2: danioso83
print("\n2. Creando usuario danioso83...")
danioso83_user, created = User.objects.get_or_create(
    username='danioso83',
    defaults={
        'first_name': 'Daniel',
        'last_name': 'Osorio',
        'email': 'danioso83@gmail.com',
        'is_staff': False,
        'is_superuser': False,
        'is_active': True
    }
)

if created:
    danioso83_user.set_password('daniel2025')
    danioso83_user.save()
    print(f"  ✅ Usuario creado: {danioso83_user.username}")
    print(f"     Email: {danioso83_user.email}")
    print(f"     Contraseña: daniel2025")
else:
    print(f"  ℹ️  Usuario ya existe: {danioso83_user.username}")

print("\n" + "=" * 80)
print("ASIGNANDO USUARIOS A ORGANIZACIONES")
print("=" * 80)

# Obtener organizaciones
oceano_org = Organization.objects.filter(name__icontains='Oceano').first()
optica_central = Organization.objects.filter(name__icontains='Central').first()
optica_vision = Organization.objects.filter(name__icontains='Vision').first()

# Asignar OceanoSJ como admin de Oceano Optico SJ
if oceano_org:
    print(f"\n1. Asignando OceanoSJ a {oceano_org.name}...")
    
    # Cambiar el owner de la organización a OceanoSJ (era el dueño original)
    oceano_org.owner = oceanosj_user
    oceano_org.save()
    print(f"  ✅ Owner de {oceano_org.name} cambiado a {oceanosj_user.username}")
    
    member, created = OrganizationMember.objects.get_or_create(
        user=oceanosj_user,
        organization=oceano_org,
        defaults={
            'role': 'owner',
            'is_active': True
        }
    )
    if created:
        print(f"  ✅ {oceanosj_user.username} → {oceano_org.name} (owner)")
    else:
        # Actualizar el rol a owner si ya existe
        if member.role != 'owner':
            member.role = 'owner'
            member.save()
            print(f"  ✅ Rol actualizado a owner para {oceanosj_user.username}")
        else:
            print(f"  ℹ️  {oceanosj_user.username} ya es owner de {oceano_org.name}")

# Asignar danioso83 como admin de alguna organización
if optica_central:
    print(f"\n2. Asignando danioso83 a {optica_central.name}...")
    member, created = OrganizationMember.objects.get_or_create(
        user=danioso83_user,
        organization=optica_central,
        defaults={
            'role': 'admin',
            'is_active': True
        }
    )
    if created:
        print(f"  ✅ {danioso83_user.username} → {optica_central.name} (admin)")
    else:
        print(f"  ℹ️  {danioso83_user.username} ya está en {optica_central.name}")

# También darle acceso a Optica Vision
if optica_vision:
    print(f"\n3. Asignando danioso83 a {optica_vision.name}...")
    member, created = OrganizationMember.objects.get_or_create(
        user=danioso83_user,
        organization=optica_vision,
        defaults={
            'role': 'member',
            'is_active': True
        }
    )
    if created:
        print(f"  ✅ {danioso83_user.username} → {optica_vision.name} (member)")
    else:
        print(f"  ℹ️  {danioso83_user.username} ya está en {optica_vision.name}")

print("\n" + "=" * 80)
print("RESUMEN FINAL DE USUARIOS Y ORGANIZACIONES")
print("=" * 80)

print(f"\n📊 Usuarios totales: {User.objects.count()}")
for user in User.objects.all():
    staff_badge = "👔" if user.is_staff else ""
    super_badge = "⭐" if user.is_superuser else ""
    print(f"  {staff_badge}{super_badge} [{user.id}] {user.username} - {user.first_name} {user.last_name} ({user.email})")

print(f"\n🏢 Organizaciones y sus miembros:")
for org in Organization.objects.all():
    print(f"\n  📍 {org.name} (Owner: {org.owner.username})")
    members = OrganizationMember.objects.filter(organization=org).select_related('user')
    for member in members:
        if member.role == 'owner':
            emoji = "👑"
        elif member.role == 'admin':
            emoji = "🔑"
        else:
            emoji = "👤"
        print(f"     {emoji} {member.user.username} ({member.role})")

print("\n" + "=" * 80)
print("CREDENCIALES DE ACCESO")
print("=" * 80)
print("\n🔐 Usuarios creados/actualizados:")
print(f"  1. danioso8 (superadmin)")
print(f"  2. OceanoSJ / oceano2025 (owner de Oceano Optico SJ)")
print(f"  3. juliozapata / temporal123 (member)")
print(f"  4. danioso83 / daniel2025 (admin/member)")

print("\n✅ Organización completada!")
print("🌐 Acceso: https://opticaapp-4e16.onrender.com/")
