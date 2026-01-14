"""
Script para sincronizar TODOS los módulos del sistema con la base de datos
Asegura que todos los módulos existan en ModulePermission
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import ModulePermission

# Lista completa de TODOS los módulos del sistema
ALL_MODULES = [
    # Core / Núcleo
    {
        'code': 'dashboard',
        'name': 'Dashboard',
        'description': 'Panel principal con métricas y resúmenes',
        'category': 'core',
        'icon': 'fa-home',
        'url_pattern': '/dashboard/',
    },
    {
        'code': 'profile',
        'name': 'Mi Perfil',
        'description': 'Gestión del perfil de usuario',
        'category': 'core',
        'icon': 'fa-user',
        'url_pattern': '/dashboard/profile/',
    },
    
    # Médico
    {
        'code': 'appointments',
        'name': 'Citas',
        'description': 'Gestión de citas médicas y agenda',
        'category': 'medical',
        'icon': 'fa-calendar-check',
        'url_pattern': '/dashboard/appointments/',
    },
    {
        'code': 'patients',
        'name': 'Pacientes',
        'description': 'Gestión de pacientes y fichas clínicas',
        'category': 'medical',
        'icon': 'fa-users',
        'url_pattern': '/dashboard/patients/',
    },
    {
        'code': 'clinical',
        'name': 'Historias Clínicas',
        'description': 'Historias clínicas y consultas',
        'category': 'medical',
        'icon': 'fa-file-medical',
        'url_pattern': '/dashboard/clinical/',
    },
    {
        'code': 'exams',
        'name': 'Exámenes',
        'description': 'Gestión de exámenes y resultados',
        'category': 'medical',
        'icon': 'fa-stethoscope',
        'url_pattern': '/dashboard/exams/',
    },
    {
        'code': 'prescriptions',
        'name': 'Recetas',
        'description': 'Recetas médicas y fórmulas',
        'category': 'medical',
        'icon': 'fa-prescription',
        'url_pattern': '/dashboard/prescriptions/',
    },
    
    # Ventas
    {
        'code': 'sales',
        'name': 'Ventas',
        'description': 'Gestión de ventas y cotizaciones',
        'category': 'sales',
        'icon': 'fa-shopping-cart',
        'url_pattern': '/dashboard/sales/',
    },
    {
        'code': 'products',
        'name': 'Productos',
        'description': 'Catálogo de productos y servicios',
        'category': 'sales',
        'icon': 'fa-boxes',
        'url_pattern': '/dashboard/products/',
    },
    {
        'code': 'customers',
        'name': 'Clientes',
        'description': 'Gestión de clientes',
        'category': 'sales',
        'icon': 'fa-user-tie',
        'url_pattern': '/dashboard/customers/',
    },
    
    # Inventario
    {
        'code': 'inventory',
        'name': 'Inventario',
        'description': 'Control de stock e inventarios',
        'category': 'inventory',
        'icon': 'fa-warehouse',
        'url_pattern': '/dashboard/inventory/',
    },
    {
        'code': 'suppliers',
        'name': 'Proveedores',
        'description': 'Gestión de proveedores',
        'category': 'inventory',
        'icon': 'fa-truck',
        'url_pattern': '/dashboard/suppliers/',
    },
    
    # Financiero / Caja
    {
        'code': 'cash_register',
        'name': 'Caja Registradora',
        'description': 'Gestión de caja y movimientos de efectivo',
        'category': 'sales',
        'icon': 'fa-cash-register',
        'url_pattern': '/dashboard/cash-register/',
    },
    {
        'code': 'billing',
        'name': 'Facturación',
        'description': 'Facturación y gestión de facturas',
        'category': 'sales',
        'icon': 'fa-file-invoice-dollar',
        'url_pattern': '/dashboard/billing/',
    },
    {
        'code': 'invoicing_electronic',
        'name': 'Facturación Electrónica',
        'description': 'Facturación electrónica DIAN',
        'category': 'sales',
        'icon': 'fa-file-invoice',
        'url_pattern': '/dashboard/invoicing/',
    },
    
    # Nómina y RRHH
    {
        'code': 'payroll',
        'name': 'Nómina',
        'description': 'Gestión de nómina y pagos',
        'category': 'settings',
        'icon': 'fa-money-check-alt',
        'url_pattern': '/dashboard/payroll/',
    },
    {
        'code': 'employees',
        'name': 'Empleados',
        'description': 'Gestión de empleados y recursos humanos',
        'category': 'settings',
        'icon': 'fa-id-card',
        'url_pattern': '/dashboard/employees/',
    },
    
    # Marketing
    {
        'code': 'promotions',
        'name': 'Promociones',
        'description': 'Campañas promocionales y marketing',
        'category': 'sales',
        'icon': 'fa-bullhorn',
        'url_pattern': '/dashboard/promotions/',
    },
    {
        'code': 'campaigns',
        'name': 'Campañas',
        'description': 'Campañas de marketing y comunicación',
        'category': 'sales',
        'icon': 'fa-envelope',
        'url_pattern': '/dashboard/campaigns/',
    },
    
    # Reportes
    {
        'code': 'reports',
        'name': 'Reportes',
        'description': 'Reportes y análisis',
        'category': 'reports',
        'icon': 'fa-chart-bar',
        'url_pattern': '/dashboard/reports/',
    },
    {
        'code': 'analytics',
        'name': 'Analíticas',
        'description': 'Análisis de datos y métricas',
        'category': 'reports',
        'icon': 'fa-chart-line',
        'url_pattern': '/dashboard/analytics/',
    },
    
    # Configuración
    {
        'code': 'settings',
        'name': 'Configuración',
        'description': 'Configuración general del sistema',
        'category': 'settings',
        'icon': 'fa-cog',
        'url_pattern': '/dashboard/settings/',
    },
    {
        'code': 'team',
        'name': 'Equipo',
        'description': 'Gestión de equipo y permisos',
        'category': 'settings',
        'icon': 'fa-users-cog',
        'url_pattern': '/dashboard/team/',
    },
    {
        'code': 'notifications',
        'name': 'Notificaciones',
        'description': 'Configuración de notificaciones',
        'category': 'settings',
        'icon': 'fa-bell',
        'url_pattern': '/dashboard/notifications/',
    },
    {
        'code': 'workflows',
        'name': 'Automatizaciones',
        'description': 'Flujos de trabajo y automatizaciones',
        'category': 'settings',
        'icon': 'fa-project-diagram',
        'url_pattern': '/dashboard/workflows/',
    },
    {
        'code': 'documents',
        'name': 'Documentos',
        'description': 'Gestión de documentos y plantillas',
        'category': 'settings',
        'icon': 'fa-file-alt',
        'url_pattern': '/dashboard/documents/',
    },
]


def sync_modules():
    """Sincroniza todos los módulos con la base de datos"""
    print("🔄 Sincronizando módulos del sistema...\n")
    
    created_count = 0
    updated_count = 0
    
    for module_data in ALL_MODULES:
        code = module_data['code']
        
        # Buscar o crear el módulo
        module, created = ModulePermission.objects.get_or_create(
            code=code,
            defaults=module_data
        )
        
        if created:
            print(f"✅ Creado: {module.name} ({code})")
            created_count += 1
        else:
            # Actualizar datos si es necesario
            updated = False
            for field, value in module_data.items():
                if field != 'code' and getattr(module, field) != value:
                    setattr(module, field, value)
                    updated = True
            
            if updated:
                module.save()
                print(f"🔄 Actualizado: {module.name} ({code})")
                updated_count += 1
            else:
                print(f"⏭️  Ya existe: {module.name} ({code})")
    
    print(f"\n📊 Resumen:")
    print(f"  • Módulos creados: {created_count}")
    print(f"  • Módulos actualizados: {updated_count}")
    print(f"  • Total de módulos: {ModulePermission.objects.count()}")
    print("\n✅ Sincronización completada")


if __name__ == '__main__':
    sync_modules()
