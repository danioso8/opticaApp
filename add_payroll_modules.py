#!/usr/bin/env python
"""
Script para agregar módulos faltantes del sistema de nómina
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import PlanFeature

def add_payroll_modules():
    """Agregar módulos de nómina faltantes"""
    
    modules = [
        {
            'code': 'vacations',
            'name': 'Gestión de Vacaciones',
            'description': 'Registro y control de vacaciones de empleados',
            'category': 'other',
            'icon': 'fas fa-umbrella-beach',
            'is_active': True
        },
        {
            'code': 'loans',
            'name': 'Préstamos y Anticipos',
            'description': 'Gestión de préstamos y anticipos a empleados',
            'category': 'other',
            'icon': 'fas fa-hand-holding-usd',
            'is_active': True
        },
        {
            'code': 'pila',
            'name': 'Planilla PILA',
            'description': 'Generación y gestión de planilla integrada de liquidación de aportes',
            'category': 'integration',
            'icon': 'fas fa-file-medical-alt',
            'is_active': True
        },
        {
            'code': 'overtime',
            'name': 'Horas Extra',
            'description': 'Registro y cálculo de horas extras',
            'category': 'other',
            'icon': 'fas fa-clock',
            'is_active': True
        },
        {
            'code': 'absences',
            'name': 'Incapacidades y Ausencias',
            'description': 'Gestión de incapacidades, permisos y ausencias',
            'category': 'other',
            'icon': 'fas fa-user-slash',
            'is_active': True
        },
        {
            'code': 'payroll_reports',
            'name': 'Reportes de Nómina',
            'description': 'Reportes y certificados de nómina',
            'category': 'analytics',
            'icon': 'fas fa-file-invoice',
            'is_active': True
        },
        {
            'code': 'employee_contracts',
            'name': 'Contratos de Empleados',
            'description': 'Gestión de contratos laborales',
            'category': 'other',
            'icon': 'fas fa-file-contract',
            'is_active': True
        },
        {
            'code': 'payroll_processing',
            'name': 'Procesamiento de Nómina',
            'description': 'Cálculo y procesamiento de nómina mensual',
            'category': 'other',
            'icon': 'fas fa-calculator',
            'is_active': True
        },
    ]
    
    print("=" * 70)
    print("🔄 AGREGANDO MÓDULOS DE NÓMINA")
    print("=" * 70)
    print()
    
    created_count = 0
    existing_count = 0
    
    for module_data in modules:
        module, created = PlanFeature.objects.get_or_create(
            code=module_data['code'],
            defaults={
                'name': module_data['name'],
                'description': module_data['description'],
                'category': module_data['category'],
                'icon': module_data['icon'],
                'is_active': module_data['is_active']
            }
        )
        
        if created:
            print(f"✅ Creado: [{module.id:2d}] {module.name} ({module.code})")
            created_count += 1
        else:
            print(f"ℹ️  Ya existe: [{module.id:2d}] {module.name} ({module.code})")
            existing_count += 1
    
    print()
    print("=" * 70)
    print(f"📊 RESUMEN:")
    print(f"   ✅ Módulos creados: {created_count}")
    print(f"   ℹ️  Módulos existentes: {existing_count}")
    print(f"   📦 Total procesados: {len(modules)}")
    
    # Mostrar total de módulos activos
    total_active = PlanFeature.objects.filter(is_active=True).count()
    print(f"   🎯 Total módulos activos en el sistema: {total_active}")
    print("=" * 70)

if __name__ == '__main__':
    add_payroll_modules()
