"""
Listar todas las organizaciones en la base de datos
"""

from apps.organizations.models import Organization
from apps.payroll.models import Employee

print("=" * 80)
print("TODAS LAS ORGANIZACIONES EN CONTABO")
print("=" * 80)

orgs = Organization.objects.all()
print(f"\n📊 Total: {orgs.count()} organizaciones\n")

for i, org in enumerate(orgs, 1):
    emps = Employee.objects.filter(organization=org).count()
    print(f"{i}. 🏢 {org.name} (ID: {org.id})")
    print(f"   Empleados: {emps}")
    print(f"   Activa: {org.is_active if hasattr(org, 'is_active') else 'N/A'}")
    print()
