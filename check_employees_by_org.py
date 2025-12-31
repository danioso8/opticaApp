"""
Script para verificar empleados por organización
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.dashboard.models_employee import Employee
from apps.organizations.models import Organization, OrganizationMember

print("=" * 80)
print("VERIFICACIÓN DE EMPLEADOS POR ORGANIZACIÓN")
print("=" * 80)

# Listar todas las organizaciones
orgs = Organization.objects.all()
print(f"\n📋 Total de organizaciones: {orgs.count()}\n")

for org in orgs:
    print(f"\n🏢 Organización: {org.name} (ID: {org.id})")
    print("-" * 80)
    
    # Empleados de esta organización
    employees = Employee.objects.filter(organization=org)
    print(f"   👥 Empleados: {employees.count()}")
    
    for emp in employees:
        user_info = f" -> Usuario: {emp.user.username}" if emp.user else " (SIN USUARIO)"
        print(f"      - {emp.full_name} ({emp.get_position_display}){user_info}")
    
    # Miembros del equipo (usuarios con acceso)
    members = OrganizationMember.objects.filter(organization=org)
    print(f"\n   🔐 Miembros del equipo (con acceso): {members.count()}")
    
    for member in members:
        print(f"      - {member.user.get_full_name() or member.user.username} ({member.get_role_display}) - {member.user.username}")

print("\n" + "=" * 80)
print("FIN DEL REPORTE")
print("=" * 80)
