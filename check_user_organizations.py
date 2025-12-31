"""
Script para verificar qué organización está viendo el usuario
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import Organization, OrganizationMember
from apps.dashboard.models_employee import Employee

# Usuario danioso8329
user = User.objects.filter(username='danioso8329').first()

if not user:
    print("❌ Usuario no encontrado")
    exit()

print("=" * 80)
print(f"Usuario: {user.username} - {user.get_full_name()}")
print("=" * 80)

# Ver todas las organizaciones donde es miembro
memberships = OrganizationMember.objects.filter(user=user, is_active=True)
print(f"\n📋 Organizaciones donde es miembro ({memberships.count()}):")

for membership in memberships:
    print(f"\n   🏢 {membership.organization.name} (ID: {membership.organization.id})")
    print(f"      Rol: {membership.get_role_display()}")
    
    # Empleados de esta organización
    employees = Employee.objects.filter(organization=membership.organization)
    print(f"      Empleados: {employees.count()}")
    for emp in employees:
        user_info = f" -> Usuario: {emp.user.username}" if emp.user else " (SIN USUARIO)"
        print(f"         - {emp.full_name} ({emp.get_position_display()}){user_info}")

print("\n" + "=" * 80)
print("PROBLEMA: El sistema debe permitir al usuario ELEGIR en qué organización")
print("está trabajando actualmente, y filtrar los empleados según esa elección.")
print("=" * 80)
