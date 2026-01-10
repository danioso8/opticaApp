"""
Mover empleados de CompuEasys ID:1 a ID:2 y eliminar ID:1
"""

from apps.organizations.models import Organization
from apps.payroll.models import Employee, Incapacity, EmployeeLoan

print("=" * 80)
print("MOVIENDO EMPLEADOS Y ELIMINANDO ORGANIZACIÓN")
print("=" * 80)

# Obtener organizaciones
org1 = Organization.objects.get(id=1)
org2 = Organization.objects.get(id=2)

print(f"\n📋 Organización origen: {org1.name} (ID: {org1.id})")
print(f"📋 Organización destino: {org2.name} (ID: {org2.id})")

# Contar elementos
empleados = Employee.objects.filter(organization=org1)
incapacidades = Incapacity.objects.filter(organization=org1)
prestamos = EmployeeLoan.objects.filter(organization=org1)

print(f"\n📊 Elementos a mover:")
print(f"   - Empleados: {empleados.count()}")
print(f"   - Incapacidades: {incapacidades.count()}")
print(f"   - Préstamos: {prestamos.count()}")

# Mover empleados
print(f"\n🔄 Moviendo empleados...")
for emp in empleados:
    print(f"   ✓ {emp.primer_nombre} {emp.primer_apellido} - {emp.cargo}")
    emp.organization = org2
    emp.save()

# Mover incapacidades
print(f"\n🔄 Moviendo incapacidades...")
for inc in incapacidades:
    print(f"   ✓ {inc.numero_incapacidad} - {inc.employee.primer_nombre}")
    inc.organization = org2
    inc.save()

# Mover préstamos
print(f"\n🔄 Moviendo préstamos...")
for prest in prestamos:
    print(f"   ✓ {prest.numero_prestamo} - {prest.employee.primer_nombre}")
    prest.organization = org2
    prest.save()

# Verificar que org1 no tenga más datos
print(f"\n🔍 Verificando organización ID:1...")
emp_count = Employee.objects.filter(organization=org1).count()
inc_count = Incapacity.objects.filter(organization=org1).count()
prest_count = EmployeeLoan.objects.filter(organization=org1).count()

print(f"   Empleados restantes: {emp_count}")
print(f"   Incapacidades restantes: {inc_count}")
print(f"   Préstamos restantes: {prest_count}")

if emp_count == 0 and inc_count == 0 and prest_count == 0:
    print(f"\n🗑️  Eliminando organización ID:1...")
    org1.delete()
    print(f"   ✅ Organización eliminada")
else:
    print(f"\n⚠️  No se puede eliminar, aún tiene datos")

# Verificar resultado final
print(f"\n" + "=" * 80)
print("RESULTADO FINAL")
print("=" * 80)

org2_emps = Employee.objects.filter(organization=org2)
print(f"\n🏢 {org2.name} (ID: {org2.id}):")
print(f"   Empleados: {org2_emps.count()}")
for emp in org2_emps:
    print(f"      ✓ {emp.primer_nombre} {emp.primer_apellido} - {emp.cargo}")

print(f"\n✅ PROCESO COMPLETADO")
