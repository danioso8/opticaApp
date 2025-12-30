"""
Comando para inicializar los módulos del sistema
"""
from django.core.management.base import BaseCommand
from apps.organizations.models import ModulePermission


class Command(BaseCommand):
    help = 'Inicializa los módulos del sistema con permisos'

    def handle(self, *args, **kwargs):
        modules = [
            # Núcleo
            {
                'code': 'dashboard',
                'name': 'Dashboard',
                'description': 'Página principal con métricas y resumen',
                'category': 'core',
                'icon': 'fa-tachometer-alt',
                'url_pattern': '/dashboard/',
                'order': 1,
            },
            {
                'code': 'appointments',
                'name': 'Citas',
                'description': 'Gestión de citas y agendamiento',
                'category': 'core',
                'icon': 'fa-calendar-alt',
                'url_pattern': '/dashboard/appointments/',
                'order': 2,
            },
            {
                'code': 'patients',
                'name': 'Pacientes',
                'description': 'Gestión de pacientes y expedientes',
                'category': 'core',
                'icon': 'fa-users',
                'url_pattern': '/dashboard/patients/',
                'order': 3,
            },
            
            # Médico
            {
                'code': 'clinical_history',
                'name': 'Historia Clínica',
                'description': 'Historial clínico completo de pacientes',
                'category': 'medical',
                'icon': 'fa-file-medical',
                'url_pattern': '/dashboard/patients/*/clinical-history/',
                'order': 10,
            },
            {
                'code': 'visual_exams',
                'name': 'Exámenes Visuales',
                'description': 'Exámenes optométricos y visuales',
                'category': 'medical',
                'icon': 'fa-eye',
                'url_pattern': '/dashboard/patients/*/visual-exam/',
                'order': 11,
            },
            {
                'code': 'exam_orders',
                'name': 'Órdenes de Examen',
                'description': 'Órdenes de exámenes especiales',
                'category': 'medical',
                'icon': 'fa-file-prescription',
                'url_pattern': '/dashboard/exam-orders/',
                'order': 12,
            },
            {
                'code': 'doctors',
                'name': 'Doctores',
                'description': 'Gestión de doctores y especialistas',
                'category': 'medical',
                'icon': 'fa-user-md',
                'url_pattern': '/dashboard/doctors/',
                'order': 13,
            },
            
            # Ventas
            {
                'code': 'sales',
                'name': 'Ventas',
                'description': 'Punto de venta y transacciones',
                'category': 'sales',
                'icon': 'fa-cash-register',
                'url_pattern': '/sales/',
                'order': 20,
            },
            {
                'code': 'invoices',
                'name': 'Facturación',
                'description': 'Facturas y facturación electrónica DIAN',
                'category': 'sales',
                'icon': 'fa-file-invoice-dollar',
                'url_pattern': '/billing/invoices/',
                'order': 21,
            },
            {
                'code': 'quotes',
                'name': 'Cotizaciones',
                'description': 'Cotizaciones y presupuestos',
                'category': 'sales',
                'icon': 'fa-file-alt',
                'url_pattern': '/sales/quotes/',
                'order': 22,
            },
            
            # Inventario
            {
                'code': 'products',
                'name': 'Productos',
                'description': 'Catálogo de productos y servicios',
                'category': 'inventory',
                'icon': 'fa-box',
                'url_pattern': '/inventory/products/',
                'order': 30,
            },
            {
                'code': 'inventory',
                'name': 'Inventario',
                'description': 'Control de stock y movimientos',
                'category': 'inventory',
                'icon': 'fa-boxes',
                'url_pattern': '/inventory/',
                'order': 31,
            },
            {
                'code': 'suppliers',
                'name': 'Proveedores',
                'description': 'Gestión de proveedores',
                'category': 'inventory',
                'icon': 'fa-truck',
                'url_pattern': '/inventory/suppliers/',
                'order': 32,
            },
            
            # Reportes
            {
                'code': 'analytics',
                'name': 'Analytics',
                'description': 'Análisis y métricas del negocio',
                'category': 'reports',
                'icon': 'fa-chart-line',
                'url_pattern': '/dashboard/analytics/',
                'order': 40,
            },
            {
                'code': 'reports',
                'name': 'Reportes',
                'description': 'Reportes personalizados',
                'category': 'reports',
                'icon': 'fa-file-chart-line',
                'url_pattern': '/reports/',
                'order': 41,
            },
            
            # Configuración
            {
                'code': 'configuration',
                'name': 'Configuración General',
                'description': 'Configuración del sistema',
                'category': 'settings',
                'icon': 'fa-cog',
                'url_pattern': '/dashboard/configuration/',
                'order': 50,
            },
            {
                'code': 'team_management',
                'name': 'Gestión de Equipo',
                'description': 'Usuarios, roles y permisos',
                'category': 'settings',
                'icon': 'fa-users-cog',
                'url_pattern': '/dashboard/team/',
                'order': 51,
            },
            {
                'code': 'landing_page',
                'name': 'Landing Page',
                'description': 'Personalización de página pública',
                'category': 'settings',
                'icon': 'fa-globe',
                'url_pattern': '/dashboard/configuration/landing-page/',
                'order': 52,
            },
            {
                'code': 'notifications',
                'name': 'Notificaciones',
                'description': 'Configuración de notificaciones',
                'category': 'settings',
                'icon': 'fa-bell',
                'url_pattern': '/dashboard/notifications/',
                'order': 53,
            },
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
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Módulo creado: {module.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Módulo actualizado: {module.name}')
                )

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Completado: {created_count} módulos creados, {updated_count} actualizados'
            )
        )
