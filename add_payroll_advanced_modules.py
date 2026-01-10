import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import PlanFeature

print("=" * 70)
print("📋 AGREGANDO MÓDULOS AVANZADOS DE NÓMINA Y RECURSOS HUMANOS")
print("=" * 70)

# Módulos a agregar
new_modules = [
    {
        'code': 'vacations',
        'name': 'Gestión de Vacaciones',
        'description': 'Control de solicitudes, aprobaciones y liquidación de vacaciones de empleados',
        'category': 'other',
        'icon': 'fas fa-umbrella-beach',
        'is_active': True
    },
    {
        'code': 'loans',
        'name': 'Préstamos a Empleados',
        'description': 'Gestión de préstamos, cuotas y descuentos automáticos en nómina',
        'category': 'other',
        'icon': 'fas fa-hand-holding-usd',
        'is_active': True
    },
    {
        'code': 'pila',
        'name': 'PILA - Planilla Integrada',
        'description': 'Generación y presentación de PILA (Planilla Integrada de Liquidación de Aportes)',
        'category': 'integration',
        'icon': 'fas fa-file-invoice',
        'is_active': True
    },
    {
        'code': 'social_security',
        'name': 'Seguridad Social',
        'description': 'Cálculo y gestión de aportes a seguridad social (Salud, Pensión, ARL)',
        'category': 'other',
        'icon': 'fas fa-shield-alt',
        'is_active': True
    },
    {
        'code': 'overtime',
        'name': 'Horas Extras y Recargos',
        'description': 'Registro y liquidación de horas extras, nocturnas, dominicales y festivos',
        'category': 'other',
        'icon': 'fas fa-clock',
        'is_active': True
    },
    {
        'code': 'payroll_reports',
        'name': 'Reportes de Nómina',
        'description': 'Reportes detallados de nómina, provisiones, costos laborales y estadísticas',
        'category': 'analytics',
        'icon': 'fas fa-file-contract',
        'is_active': True
    },
    {
        'code': 'attendance',
        'name': 'Control de Asistencia',
        'description': 'Registro de entradas, salidas, tardanzas y ausencias de empleados',
        'category': 'other',
        'icon': 'fas fa-user-check',
        'is_active': True
    },
    {
        'code': 'benefits',
        'name': 'Beneficios Extralegales',
        'description': 'Gestión de bonificaciones, auxilio de transporte, alimentación y otros beneficios',
        'category': 'other',
        'icon': 'fas fa-gift',
        'is_active': True
    },
    {
        'code': 'severance',
        'name': 'Liquidación de Prestaciones',
        'description': 'Cálculo de cesantías, intereses, primas y liquidaciones finales',
        'category': 'other',
        'icon': 'fas fa-calculator',
        'is_active': True
    },
    {
        'code': 'payslips',
        'name': 'Desprendibles de Pago',
        'description': 'Generación y envío automático de desprendibles de nómina a empleados',
        'category': 'communication',
        'icon': 'fas fa-file-pdf',
        'is_active': True
    },
]

added = 0
skipped = 0

for module_data in new_modules:
    # Verificar si ya existe
    exists = PlanFeature.objects.filter(code=module_data['code']).exists()
    
    if exists:
        print(f"⚠️  Ya existe: {module_data['code']} - {module_data['name']}")
        skipped += 1
    else:
        # Crear el módulo
        module = PlanFeature.objects.create(**module_data)
        print(f"✅ Agregado [{module.id:2d}]: {module.code:25s} - {module.name}")
        added += 1

print("\n" + "=" * 70)
print(f"📊 Resumen:")
print(f"   ✅ Módulos agregados: {added}")
print(f"   ⚠️  Módulos omitidos (ya existían): {skipped}")
print(f"   📁 Total módulos ahora: {PlanFeature.objects.count()}")
print("=" * 70)
