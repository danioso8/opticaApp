"""
Script para crear datos de prueba de nómina para el usuario danioso8329
"""

from django.contrib.auth.models import User
from apps.payroll.models import Employee, EmployeeLoan, Incapacity, PayrollPeriod
from apps.organizations.models import Organization
from decimal import Decimal
from datetime import datetime, timedelta

print("=" * 80)
print("CREANDO DATOS DE PRUEBA PARA NÓMINA")
print("=" * 80)

# Obtener usuario danioso8329
try:
    usuario = User.objects.get(username='danioso8329')
    print(f"\n✓ Usuario encontrado: {usuario.username}")
except User.DoesNotExist:
    print("\n✗ Usuario danioso8329 no encontrado")
    exit(1)

# Obtener la organización del usuario
try:
    org = usuario.userprofile.organization
    print(f"✓ Organización: {org.name}")
except:
    # Si no tiene organización, usar la primera disponible
    org = Organization.objects.first()
    print(f"✓ Usando organización: {org.name}")

print("\n" + "=" * 80)
print("CREANDO 5 EMPLEADOS")
print("=" * 80)

empleados_data = [
    {
        'tipo_documento': 'CC',
        'numero_documento': '1000123456',
        'primer_nombre': 'Carlos',
        'segundo_nombre': 'Alberto',
        'primer_apellido': 'Rodríguez',
        'segundo_apellido': 'Pérez',
        'email': 'carlos.rodriguez@ejemplo.com',
        'telefono': '3101234567',
        'cargo': 'Vendedor',
        'salario_basico': Decimal('1500000'),
        'tipo_contrato': 'INDEFINIDO',
    },
    {
        'tipo_documento': 'CC',
        'numero_documento': '1000234567',
        'primer_nombre': 'María',
        'segundo_nombre': 'Elena',
        'primer_apellido': 'Gómez',
        'segundo_apellido': 'Torres',
        'email': 'maria.gomez@ejemplo.com',
        'telefono': '3102345678',
        'cargo': 'Optómetra',
        'salario_basico': Decimal('2500000'),
        'tipo_contrato': 'INDEFINIDO',
    },
    {
        'tipo_documento': 'CC',
        'numero_documento': '1000345678',
        'primer_nombre': 'Juan',
        'segundo_nombre': 'Pablo',
        'primer_apellido': 'Martínez',
        'segundo_apellido': 'López',
        'email': 'juan.martinez@ejemplo.com',
        'telefono': '3103456789',
        'cargo': 'Asesor de Ventas',
        'salario_basico': Decimal('1800000'),
        'tipo_contrato': 'INDEFINIDO',
    },
    {
        'tipo_documento': 'CC',
        'numero_documento': '1000456789',
        'primer_nombre': 'Ana',
        'segundo_nombre': 'Lucía',
        'primer_apellido': 'Hernández',
        'segundo_apellido': 'Castro',
        'email': 'ana.hernandez@ejemplo.com',
        'telefono': '3104567890',
        'cargo': 'Cajera',
        'salario_basico': Decimal('1300000'),
        'tipo_contrato': 'INDEFINIDO',
    },
    {
        'tipo_documento': 'CC',
        'numero_documento': '1000567890',
        'primer_nombre': 'Luis',
        'segundo_nombre': 'Fernando',
        'primer_apellido': 'Ramírez',
        'segundo_apellido': 'Díaz',
        'email': 'luis.ramirez@ejemplo.com',
        'telefono': '3105678901',
        'cargo': 'Gerente',
        'salario_basico': Decimal('3500000'),
        'tipo_contrato': 'INDEFINIDO',
    },
]

empleados_creados = []
for emp_data in empleados_data:
    empleado, created = Employee.objects.get_or_create(
        numero_documento=emp_data['numero_documento'],
        organization=org,
        defaults={
            **emp_data,
            'activo': True,
            'fecha_ingreso': datetime.now().date() - timedelta(days=365),  # 1 año atrás
            'direccion': 'Calle Principal #123',
            'ciudad': 'Moniquirá',
            'departamento': 'Boyacá',
            'pais': 'CO',
        }
    )
    if created:
        print(f"  ✓ {empleado.primer_nombre} {empleado.primer_apellido} - {empleado.cargo} - ${empleado.salario_basico:,.0f}")
        empleados_creados.append(empleado)
    else:
        print(f"  ⊙ {empleado.primer_nombre} {empleado.primer_apellido} (ya existe)")
        empleados_creados.append(empleado)

print(f"\n✅ {len(empleados_creados)} empleados disponibles")

print("\n" + "=" * 80)
print("CREANDO 2 INCAPACIDADES")
print("=" * 80)

# Incapacidad para María Gómez
incapacidad1, created1 = Incapacity.objects.get_or_create(
    employee=empleados_creados[1],  # María
    numero_incapacidad='INC-2026-001',
    defaults={
        'organization': org,
        'tipo': 'COMUN',
        'fecha_inicio': datetime.now().date() - timedelta(days=10),
        'fecha_fin': datetime.now().date() - timedelta(days=7),
        'dias_incapacidad': 3,
        'porcentaje_pago': Decimal('66.67'),
        'diagnostico': 'Gripe común',
        'observaciones': 'Incapacidad por enfermedad general',
    }
)
if created1:
    print(f"  ✓ Incapacidad #{incapacidad1.numero_incapacidad} - {incapacidad1.employee.primer_nombre} {incapacidad1.employee.primer_apellido} - {incapacidad1.dias_incapacidad} días")
else:
    print(f"  ⊙ Incapacidad #{incapacidad1.numero_incapacidad} (ya existe)")

# Incapacidad para Juan Martínez
incapacidad2, created2 = Incapacity.objects.get_or_create(
    employee=empleados_creados[2],  # Juan
    numero_incapacidad='INC-2026-002',
    defaults={
        'organization': org,
        'tipo': 'COMUN',
        'fecha_inicio': datetime.now().date() - timedelta(days=5),
        'fecha_fin': datetime.now().date() - timedelta(days=3),
        'dias_incapacidad': 2,
        'porcentaje_pago': Decimal('66.67'),
        'diagnostico': 'Dolor de espalda',
        'observaciones': 'Incapacidad por lumbalgia',
    }
)
if created2:
    print(f"  ✓ Incapacidad #{incapacidad2.numero_incapacidad} - {incapacidad2.employee.primer_nombre} {incapacidad2.employee.primer_apellido} - {incapacidad2.dias_incapacidad} días")
else:
    print(f"  ⊙ Incapacidad #{incapacidad2.numero_incapacidad} (ya existe)")

print("\n" + "=" * 80)
print("CREANDO 1 PRÉSTAMO")
print("=" * 80)

# Préstamo para Carlos Rodríguez
prestamo, created = EmployeeLoan.objects.get_or_create(
    employee=empleados_creados[0],  # Carlos
    numero_prestamo='PRES-2026-001',
    defaults={
        'organization': org,
        'fecha_solicitud': datetime.now().date() - timedelta(days=100),
        'fecha_aprobacion': datetime.now().date() - timedelta(days=95),
        'fecha_desembolso': datetime.now().date() - timedelta(days=90),
        'monto_solicitado': Decimal('2000000'),
        'monto_aprobado': Decimal('2000000'),
        'tasa_interes': Decimal('1.5'),
        'numero_cuotas': 12,
        'valor_cuota': Decimal('175000'),
        'cuotas_pagadas': 4,  # 4 cuotas pagadas
        'total_pagado': Decimal('700000'),
        'saldo_pendiente': Decimal('1300000'),
        'estado': 'ACTIVO',
        'observaciones': 'Préstamo para calamidad doméstica',
    }
)
if created:
    print(f"  ✓ Préstamo #{prestamo.numero_prestamo} - {prestamo.employee.primer_nombre} {prestamo.employee.primer_apellido}")
    print(f"    Monto: ${prestamo.monto_aprobado:,.0f} | Cuota: ${prestamo.valor_cuota:,.0f} | Saldo: ${prestamo.saldo_pendiente:,.0f}")
else:
    print(f"  ⊙ Préstamo #{prestamo.numero_prestamo} (ya existe)")

print("\n" + "=" * 80)
print("✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE")
print("=" * 80)
print(f"\n📊 Resumen:")
print(f"   - Empleados: {len(empleados_creados)}")
print(f"   - Incapacidades: 2")
print(f"   - Préstamos: 1")
print(f"\n🏢 Organización: {org.name}")
print(f"👤 Usuario: {usuario.username}")
print("\n" + "=" * 80)
