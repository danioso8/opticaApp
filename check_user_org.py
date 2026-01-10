"""
Verificar organizaciones del usuario danioso8329
"""

from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.payroll.models import Employee

print("=" * 80)
print("VERIFICANDO ORGANIZACIONES Y EMPLEADOS")
print("=" * 80)

# Obtener usuario
usuario = User.objects.get(username='danioso8329')
print(f"\n👤 Usuario: {usuario.username} ({usuario.email})")

# Ver todas las organizaciones del usuario
try:
    profile = usuario.userprofile
    print(f"\n🏢 Organización principal: {profile.organization.name if profile.organization else 'Ninguna'}")
except:
    print("\n⚠️  Usuario sin perfil")

# Ver organizaciones relacionadas
print(f"\n📋 Buscando organizaciones del usuario...")
# Intentar diferentes formas de encontrar la organización
try:
    from apps.users.models import UserProfile
    if hasattr(usuario, 'profile'):
        print(f"   UserProfile.organization: {usuario.profile.organization.name if usuario.profile.organization else 'Ninguna'}")
except Exception as e:
    print(f"   Error con UserProfile: {e}")

# Ver empleados por organización
print("\n" + "=" * 80)
print("EMPLEADOS POR ORGANIZACIÓN")
print("=" * 80)

for org in Organization.objects.all()[:10]:
    emps = Employee.objects.filter(organization=org)
    if emps.exists():
        print(f"\n🏢 {org.name}:")
        for emp in emps[:10]:
            print(f"   ✓ {emp.numero_documento} - {emp.primer_nombre} {emp.primer_apellido} - {emp.cargo}")
        if emps.count() > 10:
            print(f"   ... y {emps.count() - 10} más")
