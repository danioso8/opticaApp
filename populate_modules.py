#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para poblar módulos iniciales del sistema À la Carte
Ejecutar: python manage.py shell < populate_modules.py
"""

from apps.organizations.models import PlanFeature, ModulePricing

print("=" * 80)
print("🚀 POBLANDO MÓDULOS INICIALES")
print("=" * 80)

# Definición de módulos con sus precios
MODULES = [
    # ========== MÓDULOS CORE (Esenciales) ==========
    {
        'code': 'dashboard',
        'name': 'Dashboard',
        'description': 'Panel principal con estadísticas y métricas en tiempo real',
        'category': 'other',
        'icon': 'fa-chart-line',
        'price': 0.00,  # Siempre gratis
        'can_purchase': False,
    },
    {
        'code': 'appointments',
        'name': 'Gestión de Citas',
        'description': 'Agenda, calendario, recordatorios automáticos y gestión de citas',
        'category': 'other',
        'icon': 'fa-calendar-alt',
        'price': 3.00,
        'can_purchase': True,
    },
    {
        'code': 'patients',
        'name': 'Gestión de Pacientes',
        'description': 'Base de datos completa de pacientes con historial',
        'category': 'medical',
        'icon': 'fa-user-injured',
        'price': 2.00,
        'can_purchase': True,
    },
    
    # ========== MÓDULOS MÉDICOS ==========
    {
        'code': 'clinical_history',
        'name': 'Historias Clínicas',
        'description': 'Historias clínicas digitales completas con antecedentes y diagnósticos',
        'category': 'medical',
        'icon': 'fa-file-medical',
        'price': 5.00,
        'can_purchase': True,
    },
    {
        'code': 'visual_exams',
        'name': 'Exámenes Visuales',
        'description': 'Registro de exámenes optométricos, refracción, tonometría',
        'category': 'medical',
        'icon': 'fa-eye',
        'price': 4.00,
        'can_purchase': True,
    },
    {
        'code': 'prescriptions',
        'name': 'Prescripciones',
        'description': 'Generación de fórmulas médicas y recetas',
        'category': 'medical',
        'icon': 'fa-prescription',
        'price': 3.00,
        'can_purchase': True,
    },
    {
        'code': 'exam_orders',
        'name': 'Órdenes de Exámenes',
        'description': 'Creación y seguimiento de órdenes de exámenes especiales',
        'category': 'medical',
        'icon': 'fa-clipboard-list',
        'price': 3.00,
        'can_purchase': True,
    },
    
    # ========== MÓDULOS COMERCIALES ==========
    {
        'code': 'pos',
        'name': 'Punto de Venta (POS)',
        'description': 'Sistema completo de ventas con facturación y cobros',
        'category': 'sales',
        'icon': 'fa-cash-register',
        'price': 4.00,
        'can_purchase': True,
    },
    {
        'code': 'inventory',
        'name': 'Inventario',
        'description': 'Control de inventario, stock, alertas y movimientos',
        'category': 'inventory',
        'icon': 'fa-boxes',
        'price': 5.00,
        'can_purchase': True,
    },
    {
        'code': 'invoicing_dian',
        'name': 'Facturación Electrónica DIAN',
        'description': 'Facturación electrónica certificada para Colombia',
        'category': 'sales',
        'icon': 'fa-file-invoice',
        'price': 8.00,
        'can_purchase': True,
    },
    {
        'code': 'crm',
        'name': 'CRM Avanzado',
        'description': 'Gestión de relaciones con clientes, seguimiento de oportunidades',
        'category': 'sales',
        'icon': 'fa-users-cog',
        'price': 4.00,
        'can_purchase': True,
    },
    
    # ========== MÓDULOS COMUNICACIÓN ==========
    {
        'code': 'whatsapp',
        'name': 'WhatsApp Notificaciones',
        'description': 'Notificaciones automáticas por WhatsApp (incluye 100 msg/mes)',
        'category': 'communication',
        'icon': 'fa-whatsapp',
        'price': 4.00,
        'can_purchase': True,
    },
    {
        'code': 'email_marketing',
        'name': 'Email Marketing',
        'description': 'Campañas de email, newsletters y comunicación masiva',
        'category': 'communication',
        'icon': 'fa-envelope',
        'price': 2.00,
        'can_purchase': True,
    },
    {
        'code': 'promotions',
        'name': 'Promociones y Campañas',
        'description': 'Gestión de promociones, descuentos y campañas de marketing',
        'category': 'communication',
        'icon': 'fa-bullhorn',
        'price': 3.00,
        'can_purchase': True,
    },
    
    # ========== MÓDULOS AVANZADOS ==========
    {
        'code': 'payroll',
        'name': 'Nómina',
        'description': 'Gestión completa de nómina, pagos y prestaciones',
        'category': 'other',
        'icon': 'fa-money-check-alt',
        'price': 6.00,
        'can_purchase': True,
    },
    {
        'code': 'reports',
        'name': 'Reportes Avanzados',
        'description': 'Reportes personalizados, analytics y exportación de datos',
        'category': 'analytics',
        'icon': 'fa-chart-bar',
        'price': 3.00,
        'can_purchase': True,
    },
    {
        'code': 'analytics',
        'name': 'Analytics Dashboard',
        'description': 'Análisis avanzado de métricas, KPIs y tendencias',
        'category': 'analytics',
        'icon': 'fa-chart-pie',
        'price': 4.00,
        'can_purchase': True,
    },
    {
        'code': 'api_access',
        'name': 'Acceso API',
        'description': 'API REST para integraciones con sistemas externos',
        'category': 'integration',
        'icon': 'fa-code',
        'price': 10.00,
        'can_purchase': True,
    },
    {
        'code': 'multi_location',
        'name': 'Multi-Sede',
        'description': 'Gestión de múltiples sedes y consolidación de datos',
        'category': 'other',
        'icon': 'fa-store-alt',
        'price': 8.00,
        'can_purchase': True,
    },
    {
        'code': 'team_management',
        'name': 'Gestión de Equipo',
        'description': 'Control de usuarios, roles y permisos granulares',
        'category': 'other',
        'icon': 'fa-users',
        'price': 3.00,
        'can_purchase': True,
    },
    {
        'code': 'ar_tryon',
        'name': 'Probador Virtual AR',
        'description': 'Realidad aumentada para prueba virtual de monturas',
        'category': 'customization',
        'icon': 'fa-glasses',
        'price': 5.00,
        'can_purchase': True,
    },
    {
        'code': 'workflows',
        'name': 'Automatizaciones',
        'description': 'Flujos de trabajo automatizados y reglas de negocio',
        'category': 'other',
        'icon': 'fa-project-diagram',
        'price': 4.00,
        'can_purchase': True,
    },
    {
        'code': 'tasks',
        'name': 'Gestión de Tareas',
        'description': 'Sistema de tareas, pendientes y seguimiento de actividades',
        'category': 'other',
        'icon': 'fa-tasks',
        'price': 2.00,
        'can_purchase': True,
    },
]

print(f"\n📦 Creando {len(MODULES)} módulos...")
print("-" * 80)

created_count = 0
updated_count = 0

for module_data in MODULES:
    # Crear o actualizar PlanFeature
    feature, created = PlanFeature.objects.update_or_create(
        code=module_data['code'],
        defaults={
            'name': module_data['name'],
            'description': module_data['description'],
            'category': module_data['category'],
            'icon': module_data['icon'],
            'price_monthly': module_data['price'],
            'can_purchase_separately': module_data['can_purchase'],
            'is_active': True,
        }
    )
    
    # Crear ModulePricing si el módulo es comprable
    if module_data['can_purchase'] and module_data['price'] > 0:
        pricing, pricing_created = ModulePricing.objects.update_or_create(
            module=feature,
            defaults={
                'base_price_monthly': module_data['price'],
                'discount_4_modules': 10.00,  # 10% descuento
                'discount_7_modules': 20.00,  # 20% descuento
                'is_available': True,
            }
        )
        pricing_status = "✅ Pricing creado" if pricing_created else "♻️  Pricing actualizado"
    else:
        pricing_status = "🆓 Gratis/No comprable"
    
    status = "✅ CREADO" if created else "♻️  ACTUALIZADO"
    
    print(f"{status}: {feature.name} (${module_data['price']}/mes) - {pricing_status}")
    
    if created:
        created_count += 1
    else:
        updated_count += 1

print("-" * 80)
print(f"\n📊 RESUMEN:")
print(f"   ✅ Módulos creados: {created_count}")
print(f"   ♻️  Módulos actualizados: {updated_count}")
print(f"   📦 Total de módulos: {PlanFeature.objects.count()}")
print(f"   💰 Configuraciones de precio: {ModulePricing.objects.count()}")

print("\n💡 PRECIOS POR CATEGORÍA:")
print("-" * 80)

categories = {
    'other': 'CORE / Otros',
    'medical': 'MÉDICOS',
    'sales': 'COMERCIALES',
    'communication': 'COMUNICACIÓN',
    'analytics': 'ANÁLISIS',
    'integration': 'INTEGRACIÓN',
    'inventory': 'INVENTARIO',
    'customization': 'PERSONALIZACIÓN',
}

for cat_code, cat_name in categories.items():
    modules = PlanFeature.objects.filter(category=cat_code, is_active=True)
    if modules.exists():
        total = sum(m.price_monthly for m in modules)
        print(f"\n{cat_name}:")
        for m in modules:
            price_str = "GRATIS" if m.price_monthly == 0 else f"${m.price_monthly:.2f}/mes"
            print(f"  • {m.name}: {price_str}")
        if total > 0:
            print(f"  └─ Total categoría: ${total:.2f}/mes")

print("\n" + "=" * 80)
print("✅ MÓDULOS POBLADOS EXITOSAMENTE")
print("=" * 80)

# Estadísticas de precios
all_modules = PlanFeature.objects.filter(is_active=True, price_monthly__gt=0)
if all_modules.exists():
    cheapest = all_modules.order_by('price_monthly').first()
    expensive = all_modules.order_by('-price_monthly').first()
    total_if_all = sum(m.price_monthly for m in all_modules)
    
    print(f"\n💰 ESTADÍSTICAS DE PRECIOS:")
    print(f"   Módulo más económico: {cheapest.name} (${cheapest.price_monthly}/mes)")
    print(f"   Módulo más costoso: {expensive.name} (${expensive.price_monthly}/mes)")
    print(f"   Precio si compra TODOS los módulos: ${total_if_all:.2f}/mes")
    print(f"   Con descuento 20% (7+ módulos): ${total_if_all * 0.8:.2f}/mes")
    
print()
