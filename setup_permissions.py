"""
Script para crear los módulos y permisos del sistema
Ejecutar: python setup_permissions.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import ModulePermission

def create_permissions():
    """Crea todos los módulos y permisos del sistema"""
    
    modules = [
        # CORE
        {'code': 'dashboard', 'name': 'Dashboard', 'category': 'core', 'icon': 'fa-home', 'order': 1},
        {'code': 'organizations', 'name': 'Mis Empresas', 'category': 'core', 'icon': 'fa-building', 'order': 2},
        
        # VENTAS Y FACTURACIÓN
        {'code': 'sales', 'name': 'Ventas', 'category': 'sales', 'icon': 'fa-cash-register', 'order': 10},
        {'code': 'sales_dashboard', 'name': 'Dashboard Ventas', 'category': 'sales', 'icon': 'fa-chart-line', 'order': 11},
        {'code': 'invoices', 'name': 'Facturas Electrónicas', 'category': 'sales', 'icon': 'fa-file-invoice', 'order': 12},
        {'code': 'credit_notes', 'name': 'Notas Crédito', 'category': 'sales', 'icon': 'fa-file-invoice-dollar', 'order': 13},
        {'code': 'sales_reports', 'name': 'Reportes de Ventas', 'category': 'sales', 'icon': 'fa-chart-bar', 'order': 14},
        
        # PACIENTES Y CITAS
        {'code': 'patients', 'name': 'Pacientes', 'category': 'medical', 'icon': 'fa-users', 'order': 20},
        {'code': 'appointments', 'name': 'Citas', 'category': 'medical', 'icon': 'fa-calendar-check', 'order': 21},
        {'code': 'appointment_scheduling', 'name': 'Agendamiento', 'category': 'medical', 'icon': 'fa-calendar-plus', 'order': 22},
        {'code': 'exam_orders', 'name': 'Exámenes Especiales', 'category': 'medical', 'icon': 'fa-microscope', 'order': 23},
        
        # PROFESIONALES
        {'code': 'doctors', 'name': 'Doctores/Optómetras', 'category': 'medical', 'icon': 'fa-user-md', 'order': 25},
        {'code': 'laboratories', 'name': 'Laboratorios Ópticos', 'category': 'medical', 'icon': 'fa-flask', 'order': 26},
        
        # PERSONAL Y NÓMINA
        {'code': 'employees', 'name': 'Empleados', 'category': 'settings', 'icon': 'fa-users', 'order': 30},
        {'code': 'payroll', 'name': 'Nómina Electrónica', 'category': 'settings', 'icon': 'fa-money-check-alt', 'order': 31},
        {'code': 'payroll_workflow', 'name': 'Workflow Nómina', 'category': 'settings', 'icon': 'fa-tasks', 'order': 32},
        {'code': 'contracts', 'name': 'Contratos Laborales', 'category': 'settings', 'icon': 'fa-file-contract', 'order': 33},
        {'code': 'vacations', 'name': 'Vacaciones', 'category': 'settings', 'icon': 'fa-umbrella-beach', 'order': 34},
        {'code': 'employee_loans', 'name': 'Préstamos Empleados', 'category': 'settings', 'icon': 'fa-hand-holding-usd', 'order': 35},
        {'code': 'social_benefits', 'name': 'Prestaciones Sociales', 'category': 'settings', 'icon': 'fa-piggy-bank', 'order': 36},
        {'code': 'provisions', 'name': 'Provisiones', 'category': 'settings', 'icon': 'fa-calculator', 'order': 37},
        {'code': 'pila', 'name': 'PILA', 'category': 'settings', 'icon': 'fa-file-medical-alt', 'order': 38},
        {'code': 'incapacities', 'name': 'Incapacidades', 'category': 'settings', 'icon': 'fa-notes-medical', 'order': 39},
        
        # FINANZAS
        {'code': 'cash_register', 'name': 'Caja y Tesorería', 'category': 'reports', 'icon': 'fa-cash-register', 'order': 40},
        {'code': 'accounts_receivable', 'name': 'Cuentas por Cobrar', 'category': 'reports', 'icon': 'fa-file-invoice-dollar', 'order': 41},
        {'code': 'accounts_payable', 'name': 'Cuentas por Pagar', 'category': 'reports', 'icon': 'fa-receipt', 'order': 42},
        {'code': 'financial_reports', 'name': 'Reportes Financieros', 'category': 'reports', 'icon': 'fa-chart-pie', 'order': 43},
        
        # INVENTARIO Y COMPRAS
        {'code': 'inventory', 'name': 'Inventario', 'category': 'inventory', 'icon': 'fa-boxes', 'order': 50},
        {'code': 'products', 'name': 'Productos', 'category': 'inventory', 'icon': 'fa-box', 'order': 51},
        {'code': 'suppliers', 'name': 'Proveedores', 'category': 'inventory', 'icon': 'fa-truck', 'order': 52},
        {'code': 'purchase_orders', 'name': 'Órdenes de Compra', 'category': 'inventory', 'icon': 'fa-shopping-cart', 'order': 53},
        {'code': 'goods_receipt', 'name': 'Recepción de Mercancía', 'category': 'inventory', 'icon': 'fa-dolly', 'order': 54},
        
        # MARKETING
        {'code': 'promotions', 'name': 'Promociones', 'category': 'sales', 'icon': 'fa-tags', 'order': 60},
        {'code': 'campaigns', 'name': 'Campañas', 'category': 'sales', 'icon': 'fa-bullhorn', 'order': 61},
        {'code': 'whatsapp', 'name': 'WhatsApp Masivo', 'category': 'sales', 'icon': 'fab fa-whatsapp', 'order': 62},
        
        # CONFIGURACIÓN
        {'code': 'general_settings', 'name': 'Configuración General', 'category': 'settings', 'icon': 'fa-cog', 'order': 70},
        {'code': 'invoice_config', 'name': 'Config. Facturación', 'category': 'settings', 'icon': 'fa-file-invoice', 'order': 71},
        {'code': 'dian_config', 'name': 'Config. DIAN', 'category': 'settings', 'icon': 'fa-building-columns', 'order': 72},
        {'code': 'whatsapp_config', 'name': 'Config. WhatsApp', 'category': 'settings', 'icon': 'fab fa-whatsapp', 'order': 73},
        {'code': 'landing_page', 'name': 'Landing Page', 'category': 'settings', 'icon': 'fa-paint-brush', 'order': 74},
        {'code': 'clinical_parameters', 'name': 'Parámetros Clínicos', 'category': 'settings', 'icon': 'fa-pills', 'order': 75},
        {'code': 'team_management', 'name': 'Equipo y Permisos', 'category': 'settings', 'icon': 'fa-users-cog', 'order': 76},
    ]
    
    created_count = 0
    updated_count = 0
    
    for module_data in modules:
        module, created = ModulePermission.objects.update_or_create(
            code=module_data['code'],
            defaults=module_data
        )
        
        if created:
            created_count += 1
            print(f"✅ Creado: {module.name}")
        else:
            updated_count += 1
            print(f"🔄 Actualizado: {module.name}")
    
    print(f"\n{'='*50}")
    print(f"✅ Módulos creados: {created_count}")
    print(f"🔄 Módulos actualizados: {updated_count}")
    print(f"📊 Total: {created_count + updated_count}")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    create_permissions()
