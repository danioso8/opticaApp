import json
from django.contrib.auth.models import User
from apps.organizations.models import Organization, OrganizationMember

print("=" * 80)
print("ANALIZANDO USUARIOS Y ORGANIZACIONES EN BACKUP")
print("=" * 80)

# Leer el backup
with open('backup_final.json', 'r', encoding='latin-1') as f:
    backup_data = json.load(f)

# Extraer información de UserProfiles
print("\nUSERPROFILES EN BACKUP:")
userprofiles = []
for item in backup_data:
    if item['model'] == 'users.userprofile':
        fields = item['fields']
        userprofiles.append({
            'pk': item['pk'],
            'user_id': fields.get('user'),
            'organization_id': fields.get('organization'),
            'role': fields.get('role', 'member'),
            'is_active': fields.get('is_active', True)
        })
        print(f"  UserProfile {item['pk']}: User={fields.get('user')}, Org={fields.get('organization')}, Role={fields.get('role')}")

# Extraer doctores
print("\nDOCTORES EN BACKUP:")
doctors = []
for item in backup_data:
    if item['model'] == 'patients.doctor':
        fields = item['fields']
        doctors.append({
            'pk': item['pk'],
            'full_name': fields.get('full_name'),
            'identification': fields.get('identification'),
            'organization_id': fields.get('organization')
        })
        print(f"  Doctor {item['pk']}: {fields.get('full_name')} - Org={fields.get('organization')}")

print("\n" + "=" * 80)
print("ESTADO ACTUAL EN PRODUCCIÓN")
print("=" * 80)

# Ver usuarios actuales
print("\nUSUARIOS EN PRODUCCIÓN:")
users = User.objects.all()
for user in users:
    print(f"  [{user.id}] {user.username} - {user.first_name} {user.last_name} ({user.email})")

# Ver organizaciones actuales
print("\nORGANIZACIONES EN PRODUCCIÓN:")
orgs = Organization.objects.all()
org_map = {}
for org in orgs:
    print(f"  [{org.id}] {org.name} - Owner: {org.owner.username}")
    org_map[org.id] = org

# Ver membresías actuales
print("\nMEMBRESÍAS ACTUALES:")
members = OrganizationMember.objects.all()
if members.exists():
    for member in members:
        print(f"  {member.user.username} en {member.organization.name} - Role: {member.role}")
else:
    print("  (No hay membresías configuradas)")

print("\n" + "=" * 80)
print("CREANDO MEMBRESÍAS BASADAS EN EL BACKUP")
print("=" * 80)

# Mapeo de usuarios conocidos
# Del backup sabíamos que había 3 UserProfiles
# Necesitamos crear las relaciones correctas

# Obtener el usuario danioso8 (es el owner actual de las organizaciones)
danioso_user = User.objects.get(username='danioso8')
julio_user = User.objects.get(username='juliozapata')

# Opción 1: Hacer a danioso8 miembro de todas las organizaciones como admin
print("\nAsignando a danioso8 como admin de todas las organizaciones...")
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
        print(f"  ✅ {danioso_user.username} agregado a {org.name} como admin")
    else:
        print(f"  ℹ️  {danioso_user.username} ya es miembro de {org.name}")

# Opción 2: Asignar a Julio Zapata como miembro de alguna organización
# Por ejemplo, de "Oceano Optico SJ" que era la principal
oceano_org = Organization.objects.filter(name__icontains='Oceano').first()
if oceano_org:
    print(f"\nAsignando a juliozapata como miembro de {oceano_org.name}...")
    member, created = OrganizationMember.objects.get_or_create(
        user=julio_user,
        organization=oceano_org,
        defaults={
            'role': 'member',
            'is_active': True
        }
    )
    if created:
        print(f"  ✅ {julio_user.username} agregado a {oceano_org.name} como member")
    else:
        print(f"  ℹ️  {julio_user.username} ya es miembro de {oceano_org.name}")

# Ahora verificar doctores y crear sus membresías
print("\nVerificando doctores y sus organizaciones...")
from apps.patients.models import Doctor

all_doctors = Doctor.objects.all()
for doctor in all_doctors:
    if doctor.organization_id:
        org = Organization.objects.filter(id=doctor.organization_id).first()
        if org:
            print(f"  Doctor {doctor.full_name} pertenece a {org.name}")
            # Si el doctor tiene un usuario asociado (por UserProfile), crear membresía
            # Como no tenemos el mapeo completo, esto se haría manualmente

print("\n" + "=" * 80)
print("RESUMEN FINAL")
print("=" * 80)

print(f"\nUsuarios totales: {User.objects.count()}")
print(f"Organizaciones totales: {Organization.objects.count()}")
print(f"Membresías configuradas: {OrganizationMember.objects.count()}")

print("\nMEMBRESÍAS DETALLADAS:")
for member in OrganizationMember.objects.all():
    print(f"  - {member.user.username} → {member.organization.name} ({member.role})")

print("\n" + "=" * 80)
print("RECOMENDACIONES")
print("=" * 80)
print("""
Basado en el backup original:
- El backup NO incluía los usuarios (auth.user)
- Solo tenía 3 UserProfiles pero sin los datos de usuario completos
- Los doctores estaban asignados a organizaciones

Para completar la configuración:
1. Julio Zapata ha sido creado y asignado a una organización
2. danioso8 es admin de todas las organizaciones
3. Si necesitas crear más usuarios específicos, proporciona:
   - Nombre completo
   - Email
   - Usuario
   - Organización a la que pertenece
   - Rol (admin/member/viewer)
""")
