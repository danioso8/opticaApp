"""
Script para agregar los módulos faltantes a la base de datos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import PlanFeature

# Módulos que faltan en la BD pero están en plan_features.py
missing_modules = [
    {
        'code': 'dian_config',
        'name': 'Configuración DIAN',
        'description': 'Configuración de facturación electrónica DIAN',
        'icon': 'fas fa-cog',
        'category': 'integration',
    },
    {
        'code': 'invoices_basic',
        'name': 'Facturación Básica',
        'description': 'Facturas normales (no electrónicas)',
        'icon': 'fas fa-file-invoice',
        'category': 'sales',
    },
    {
        'code': 'invoices_dian',
        'name': 'Facturación DIAN',
        'description': 'Facturación electrónica DIAN',
        'icon': 'fas fa-file-invoice-dollar',
        'category': 'integration',
    },
    {
        'code': 'landing_config',
        'name': 'Configuración Landing Page',
        'description': 'Configuración de página pública personalizada',
        'icon': 'fas fa-globe',
        'category': 'customization',
    },
    {
        'code': 'notifications_config',
        'name': 'Configuración Notificaciones',
        'description': 'Configuración de notificaciones automáticas',
        'icon': 'fas fa-bell',
        'category': 'communication',
    },
    {
        'code': 'suppliers',
        'name': 'Proveedores',
        'description': 'Gestión de proveedores',
        'icon': 'fas fa-truck',
        'category': 'sales',
    },
    {
        'code': 'whatsapp',
        'name': 'WhatsApp',
        'description': 'Notificaciones por WhatsApp',
        'icon': 'fab fa-whatsapp',
        'category': 'communication',
    },
    {
        'code': 'wompi_payments',
        'name': 'Pagos en Línea Wompi',
        'description': 'Pagos en línea con Wompi',
        'icon': 'fas fa-credit-card',
        'category': 'integration',
    },
]

print("\n" + "="*70)
print("📦 AGREGANDO MÓDULOS FALTANTES")
print("="*70)

added = 0
skipped = 0

for module_data in missing_modules:
    code = module_data['code']
    
    # Verificar si ya existe
    if PlanFeature.objects.filter(code=code).exists():
        print(f"⏭️  Ya existe: {code}")
        skipped += 1
    else:
        # Crear el módulo
        feature = PlanFeature.objects.create(
            code=code,
            name=module_data['name'],
            description=module_data['description'],
            icon=module_data['icon'],
            category=module_data['category'],
            is_active=True
        )
        print(f"✅ Agregado: {code} - {module_data['name']}")
        added += 1

print("\n" + "="*70)
print(f"✅ Módulos agregados: {added}")
print(f"⏭️  Módulos omitidos (ya existían): {skipped}")
print(f"📊 Total en DB ahora: {PlanFeature.objects.count()}")
print("="*70 + "\n")
