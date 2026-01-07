"""
Script para crear datos de prueba del sistema de nómina
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.payroll.models import Employee, AccrualConcept, DeductionConcept, PayrollPeriod, Incapacity
from apps.organizations.models import Organization
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta

# Obtener organización y usuario
org = Organization.objects.first()
user = User.objects.first()

print('=== CREANDO CONCEPTOS DE NÓMINA ===')

# Crear conceptos si no existen
salario_basico, created = AccrualConcept.objects.get_or_create(
    organization=org,
    codigo='SAL-001',
    defaults={
        'nombre': 'Salario Básico',
        'tipo': 'BASICO',
        'activo': True
    }
)
print(f'✓ Concepto Salario Básico: {"creado" if created else "ya existe"}')

auxilio, created = AccrualConcept.objects.get_or_create(
    organization=org,
    codigo='AUX-001',
    defaults={
        'nombre': 'Auxilio de Transporte',
        'tipo': 'AUXILIO_TRANSPORTE',
        'activo': True
    }
)
print(f'✓ Concepto Auxilio Transporte: {"creado" if created else "ya existe"}')

horas_extras, created = AccrualConcept.objects.get_or_create(
    organization=org,
    codigo='HEX-001',
    defaults={
        'nombre': 'Horas Extras',
        'tipo': 'HORAS_EXTRAS',
        'activo': True
    }
)
print(f'✓ Concepto Horas Extras: {"creado" if created else "ya existe"}')

incapacidad_concepto, created = AccrualConcept.objects.get_or_create(
    organization=org,
    codigo='INC-001',
    defaults={
        'nombre': 'Incapacidad',
        'tipo': 'INCAPACIDAD',
        'activo': True
    }
)
print(f'✓ Concepto Incapacidad: {"creado" if created else "ya existe"}')

# Deducciones
salud, created = DeductionConcept.objects.get_or_create(
    organization=org,
    codigo='DED-SAL',
    defaults={
        'nombre': 'Salud (4%)',
        'tipo': 'SALUD',
        'es_obligatoria': True,
        'porcentaje_base': Decimal('4.00'),
        'activo': True
    }
)
print(f'✓ Deducción Salud: {"creado" if created else "ya existe"}')

pension, created = DeductionConcept.objects.get_or_create(
    organization=org,
    codigo='DED-PEN',
    defaults={
        'nombre': 'Pensión (4%)',
        'tipo': 'PENSION',
        'es_obligatoria': True,
        'porcentaje_base': Decimal('4.00'),
        'activo': True
    }
)
print(f'✓ Deducción Pensión: {"creado" if created else "ya existe"}')

print('\n=== CREANDO EMPLEADOS ===')

# Empleado 1: Sin incapacidad
emp1, created = Employee.objects.get_or_create(
    organization=org,
    numero_documento='1234567890',
    defaults={
        'tipo_documento': 'CC',
        'primer_nombre': 'Juan',
        'segundo_nombre': 'Carlos',
        'primer_apellido': 'Pérez',
        'segundo_apellido': 'González',
        'email': 'juan.perez@test.com',
        'telefono': '3001234567',
        'direccion': 'Calle 123 #45-67',
        'ciudad': 'Bogotá',
        'departamento': 'Cundinamarca',
        'tipo_contrato': 'INDEFINIDO',
        'fecha_ingreso': date(2025, 1, 1),
        'cargo': 'Vendedor Senior',
        'salario_basico': Decimal('2500000'),
        'activo': True
    }
)
print(f'✓ Empleado 1 - Juan Pérez: {"creado" if created else "ya existe"} - Salario: $2,500,000')

# Empleado 2: Con incapacidad común
emp2, created = Employee.objects.get_or_create(
    organization=org,
    numero_documento='0987654321',
    defaults={
        'tipo_documento': 'CC',
        'primer_nombre': 'María',
        'segundo_nombre': 'Fernanda',
        'primer_apellido': 'Rodríguez',
        'segundo_apellido': 'López',
        'email': 'maria.rodriguez@test.com',
        'telefono': '3009876543',
        'direccion': 'Carrera 45 #67-89',
        'ciudad': 'Bogotá',
        'departamento': 'Cundinamarca',
        'tipo_contrato': 'INDEFINIDO',
        'fecha_ingreso': date(2024, 6, 1),
        'cargo': 'Contadora',
        'salario_basico': Decimal('3000000'),
        'activo': True
    }
)
print(f'✓ Empleado 2 - María Rodríguez: {"creado" if created else "ya existe"} - Salario: $3,000,000')

# Empleado 3: Con incapacidad laboral
emp3, created = Employee.objects.get_or_create(
    organization=org,
    numero_documento='1122334455',
    defaults={
        'tipo_documento': 'CC',
        'primer_nombre': 'Pedro',
        'segundo_nombre': 'Antonio',
        'primer_apellido': 'Martínez',
        'segundo_apellido': 'Sánchez',
        'email': 'pedro.martinez@test.com',
        'telefono': '3112233445',
        'direccion': 'Avenida 80 #12-34',
        'ciudad': 'Bogotá',
        'departamento': 'Cundinamarca',
        'tipo_contrato': 'INDEFINIDO',
        'fecha_ingreso': date(2023, 3, 15),
        'cargo': 'Operario',
        'salario_basico': Decimal('1500000'),
        'activo': True
    }
)
print(f'✓ Empleado 3 - Pedro Martínez: {"creado" if created else "ya existe"} - Salario: $1,500,000')

print('\n=== CREANDO INCAPACIDADES ===')

# Incapacidad 1: Enfermedad común para María (5 días)
inc1, created = Incapacity.objects.get_or_create(
    organization=org,
    employee=emp2,
    tipo='COMUN',
    fecha_inicio=date(2026, 1, 10),
    fecha_fin=date(2026, 1, 14),
    defaults={
        'diagnostico': 'Gripe común',
        'numero_incapacidad': 'INC-2026-001',
        'estado': 'APROBADA',
        'aprobada_por': user,
        'fecha_aprobacion': date.today(),
        'created_by': user
    }
)
print(f'✓ Incapacidad 1 - María (Enfermedad Común): {"creada" if created else "ya existe"}')
print(f'  Fecha: 10-14 enero (5 días) - Valor: ${inc1.total_incapacidad:,.0f}')

# Incapacidad 2: Accidente laboral para Pedro (7 días)
inc2, created = Incapacity.objects.get_or_create(
    organization=org,
    employee=emp3,
    tipo='LABORAL',
    fecha_inicio=date(2026, 1, 15),
    fecha_fin=date(2026, 1, 21),
    defaults={
        'diagnostico': 'Esguince tobillo derecho - accidente en trabajo',
        'numero_incapacidad': 'INC-2026-002',
        'estado': 'APROBADA',
        'aprobada_por': user,
        'fecha_aprobacion': date.today(),
        'created_by': user
    }
)
print(f'✓ Incapacidad 2 - Pedro (Accidente Laboral): {"creada" if created else "ya existe"}')
print(f'  Fecha: 15-21 enero (7 días) - Valor: ${inc2.total_incapacidad:,.0f}')

print('\n=== CREANDO PERÍODO DE NÓMINA ===')

# Crear período
periodo, created = PayrollPeriod.objects.get_or_create(
    organization=org,
    nombre='Nómina Enero 2026 - PRUEBA',
    defaults={
        'tipo_periodo': 'MENSUAL',
        'fecha_inicio': date(2026, 1, 1),
        'fecha_fin': date(2026, 1, 31),
        'fecha_pago': date(2026, 2, 5),
        'estado': 'BORRADOR',
        'observaciones': 'Período de prueba con incapacidades',
        'created_by': user
    }
)
print(f'✓ Período: {"creado" if created else "ya existe"} - {periodo.nombre}')
print(f'  Estado: {periodo.estado}')
print(f'  Fechas: 01/01/2026 - 31/01/2026')
print(f'  ID del período: {periodo.pk}')

print('\n' + '='*60)
print('✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE')
print('='*60)
print(f'\n📋 RESUMEN:')
print(f'   • 3 empleados activos')
print(f'   • 2 incapacidades APROBADAS')
print(f'   • 1 período en estado BORRADOR')
print(f'\n🎯 SIGUIENTE PASO:')
print(f'   Ir a: http://127.0.0.1:8000/dashboard/payroll/periodos/{periodo.pk}/')
print(f'   Y hacer clic en CALCULAR')
print('='*60)
