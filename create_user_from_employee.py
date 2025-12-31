"""
Script para crear usuario desde un empleado existente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.dashboard.models_employee import Employee
from apps.organizations.models import OrganizationMember

# Buscar el empleado cajero de CompuEasys
employee = Employee.objects.filter(
    organization__name='CompuEasys',
    position='VENDEDOR'
).first()

if not employee:
    print("❌ No se encontró el empleado cajero en CompuEasys")
    exit()

print(f"✅ Empleado encontrado: {employee.full_name}")
print(f"   Organización: {employee.organization.name}")
print(f"   Cargo: {employee.get_position_display()}")
print(f"   Email: {employee.email}")

# Verificar si ya tiene usuario
if employee.user:
    print(f"⚠️  Este empleado ya tiene un usuario: {employee.user.username}")
    user = employee.user
else:
    # Crear usuario
    username = input("\n📝 Ingresa el nombre de usuario para iniciar sesión: ").strip()
    password = input("🔒 Ingresa la contraseña: ").strip()
    
    # Verificar que el username no exista
    if User.objects.filter(username=username).exists():
        print(f"❌ El usuario '{username}' ya existe")
        exit()
    
    # Crear el usuario
    user = User.objects.create_user(
        username=username,
        email=employee.email,
        first_name=employee.first_name,
        last_name=employee.last_name,
        password=password
    )
    
    # Vincular el usuario con el empleado
    employee.user = user
    employee.save()
    
    print(f"✅ Usuario creado: {username}")

# Verificar si ya es miembro de la organización
member = OrganizationMember.objects.filter(
    user=user,
    organization=employee.organization
).first()

if member:
    print(f"⚠️  Ya es miembro de {employee.organization.name} con rol: {member.get_role_display()}")
else:
    # Crear miembro de la organización con rol de cajero
    member = OrganizationMember.objects.create(
        user=user,
        organization=employee.organization,
        role='cashier',  # Rol de cajero
        is_active=True
    )
    print(f"✅ Miembro de organización creado con rol: {member.get_role_display()}")

print("\n" + "=" * 80)
print("✅ PROCESO COMPLETADO")
print("=" * 80)
print(f"   Usuario: {user.username}")
print(f"   Nombre: {user.get_full_name()}")
print(f"   Email: {user.email}")
print(f"   Organización: {employee.organization.name}")
print(f"   Rol: {member.get_role_display()}")
print(f"   Estado: {'Activo' if member.is_active else 'Inactivo'}")
print("\n👉 Ahora puede iniciar sesión con:")
print(f"   Usuario: {user.username}")
print(f"   Contraseña: [la que configuraste]")
print("=" * 80)
