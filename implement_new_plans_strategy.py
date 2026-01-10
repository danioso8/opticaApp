"""
Script para crear Features y actualizar Planes según nueva estrategia
Ejecutar: python implement_new_plans_strategy.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import PlanFeature, SubscriptionPlan
from decimal import Decimal

def create_plan_features():
    """Crea todos los features/módulos del sistema"""
    print("\n" + "="*60)
    print("CREANDO FEATURES/MÓDULOS DEL SISTEMA")
    print("="*60)
    
    features_data = [
        # CORE FEATURES (Gestión Clínica)
        {'code': 'dashboard', 'name': 'Dashboard Principal', 'category': 'medical', 'icon': 'fa-home', 'description': 'Panel principal con métricas y accesos rápidos'},
        {'code': 'appointments', 'name': 'Gestión de Citas', 'category': 'medical', 'icon': 'fa-calendar-alt', 'description': 'Agendamiento y gestión de citas'},
        {'code': 'patients', 'name': 'Gestión de Pacientes', 'category': 'medical', 'icon': 'fa-user-injured', 'description': 'Registro y gestión de pacientes'},
        {'code': 'clinical_history_basic', 'name': 'Historia Clínica Básica', 'category': 'medical', 'icon': 'fa-file-medical', 'description': 'Historia clínica con campos básicos'},
        {'code': 'doctors', 'name': 'Gestión de Doctores', 'category': 'medical', 'icon': 'fa-user-md', 'description': 'Registro y gestión de profesionales'},
        {'code': 'configuration_basic', 'name': 'Configuración Básica', 'category': 'other', 'icon': 'fa-cog', 'description': 'Configuraciones esenciales del sistema'},
        
        # SALES FEATURES (Ventas)
        {'code': 'sales_pos', 'name': 'Punto de Venta (POS)', 'category': 'sales', 'icon': 'fa-shopping-cart', 'description': 'Sistema de punto de venta', 'price_monthly': Decimal('0.00')},
        {'code': 'promotions', 'name': 'Promociones Automáticas', 'category': 'sales', 'icon': 'fa-tags', 'description': 'Sistema de promociones y descuentos automáticos', 'price_monthly': Decimal('19900.00'), 'can_purchase_separately': True},
        {'code': 'inventory', 'name': 'Control de Inventario', 'category': 'sales', 'icon': 'fa-boxes', 'description': 'Gestión completa de inventario y stock'},
        {'code': 'products', 'name': 'Catálogo de Productos', 'category': 'sales', 'icon': 'fa-glasses', 'description': 'Gestión del catálogo de productos'},
        {'code': 'formulas', 'name': 'Fórmulas Oftálmicas', 'category': 'medical', 'icon': 'fa-prescription-bottle-alt', 'description': 'Gestión de fórmulas y prescripciones'},
        {'code': 'cash_register', 'name': 'Registro de Caja', 'category': 'sales', 'icon': 'fa-money-bill-wave', 'description': 'Control de caja y movimientos de efectivo'},
        
        # ADMIN FEATURES (Administración)
        {'code': 'reports_basic', 'name': 'Reportes Básicos', 'category': 'analytics', 'icon': 'fa-chart-bar', 'description': 'Reportes estándar de ventas y citas'},
        {'code': 'analytics_advanced', 'name': 'Análisis Avanzado', 'category': 'analytics', 'icon': 'fa-chart-line', 'description': 'Análisis predictivo y dashboards personalizados', 'price_monthly': Decimal('29900.00'), 'can_purchase_separately': True},
        {'code': 'documents', 'name': 'Gestión de Documentos', 'category': 'other', 'icon': 'fa-file-alt', 'description': 'Almacenamiento y gestión de documentos'},
        {'code': 'audit', 'name': 'Auditoría del Sistema', 'category': 'other', 'icon': 'fa-clipboard-check', 'description': 'Registro de auditoría y trazabilidad'},
        {'code': 'configuration_advanced', 'name': 'Configuración Avanzada', 'category': 'customization', 'icon': 'fa-cog', 'description': 'Opciones de configuración avanzadas'},
        
        # HR FEATURES (Recursos Humanos)
        {'code': 'teams', 'name': 'Gestión de Equipos', 'category': 'other', 'icon': 'fa-users-cog', 'description': 'Organización de equipos y turnos'},
        {'code': 'payroll_dian', 'name': 'Nómina Electrónica DIAN', 'category': 'integration', 'icon': 'fa-id-card', 'description': 'Nómina electrónica integrada con DIAN', 'price_monthly': Decimal('39900.00'), 'can_purchase_separately': True},
        {'code': 'permissions_advanced', 'name': 'Permisos y Roles Avanzados', 'category': 'other', 'icon': 'fa-user-shield', 'description': 'Sistema avanzado de permisos granulares'},
        
        # AUTOMATION FEATURES (Automatización)
        {'code': 'workflows', 'name': 'Automatización de Workflows', 'category': 'communication', 'icon': 'fa-project-diagram', 'description': 'Flujos de trabajo automatizados', 'price_monthly': Decimal('24900.00'), 'can_purchase_separately': True},
        {'code': 'tasks', 'name': 'Tareas Automáticas', 'category': 'communication', 'icon': 'fa-tasks', 'description': 'Sistema de tareas y recordatorios automáticos'},
        {'code': 'notifications_push', 'name': 'Notificaciones Push', 'category': 'communication', 'icon': 'fa-bell', 'description': 'Notificaciones push en tiempo real'},
        {'code': 'whatsapp_integration', 'name': 'Integración WhatsApp', 'category': 'communication', 'icon': 'fa-whatsapp', 'description': 'Mensajería automática vía WhatsApp Business', 'price_monthly': Decimal('29900.00'), 'can_purchase_separately': True},
        
        # INTEGRATION FEATURES (Integraciones)
        {'code': 'api_rest', 'name': 'API REST', 'category': 'integration', 'icon': 'fa-code', 'description': 'API REST para integraciones externas', 'price_monthly': Decimal('49900.00'), 'can_purchase_separately': True},
        {'code': 'multi_location', 'name': 'Multi-sede', 'category': 'integration', 'icon': 'fa-building', 'description': 'Gestión de múltiples sedes'},
        {'code': 'landing_page', 'name': 'Landing Page Personalizable', 'category': 'customization', 'icon': 'fa-globe', 'description': 'Página de aterrizaje personalizable con SEO'},
        {'code': 'electronic_invoicing', 'name': 'Facturación Electrónica DIAN', 'category': 'integration', 'icon': 'fa-file-invoice', 'description': 'Facturación electrónica integrada con DIAN', 'price_monthly': Decimal('29900.00'), 'can_purchase_separately': True},
    ]
    
    created_count = 0
    for feature_data in features_data:
        feature, created = PlanFeature.objects.get_or_create(
            code=feature_data['code'],
            defaults=feature_data
        )
        if created:
            print(f"   ✅ Feature creado: {feature.name}")
            created_count += 1
        else:
            print(f"   ℹ️  Feature existente: {feature.name}")
    
    print(f"\n✅ Total features creados: {created_count}/{len(features_data)}")
    return {f['code']: PlanFeature.objects.get(code=f['code']) for f in features_data}


def update_subscription_plans(features):
    """Actualiza los planes con nueva estrategia"""
    print("\n" + "="*60)
    print("ACTUALIZANDO PLANES DE SUSCRIPCIÓN")
    print("="*60)
    
    # PLAN FREE
    print("\n📦 Plan Free...")
    free_plan, created = SubscriptionPlan.objects.get_or_create(
        slug='free-trial',
        defaults={
            'name': 'Plan Gratuito',
            'plan_type': 'free',
            'price_monthly': Decimal('0.00'),
            'price_yearly': Decimal('0.00'),
        }
    )
    
    free_plan.max_users = 1
    free_plan.max_organizations = 1
    free_plan.max_appointments_month = 50
    free_plan.max_patients = 100
    free_plan.max_storage_mb = 100
    free_plan.whatsapp_messages_included = 0
    free_plan.allow_electronic_invoicing = False
    free_plan.max_invoices_month = 0
    
    free_plan.coverage_description = "Ideal para probar el sistema sin compromiso durante 30 días"
    free_plan.ideal_for = "Profesionales independientes o ópticas nuevas que quieren evaluar el sistema"
    free_plan.plan_badge = ""
    free_plan.highlighted_features = """Dashboard con métricas básicas
Gestión de hasta 50 citas/mes
Registro de hasta 100 pacientes
Historia clínica básica
Punto de venta simple
Landing page con plantilla predeterminada"""
    
    free_plan.main_benefits = """✅ Sin tarjeta de crédito requerida
✅ 30 días de prueba gratuita
✅ Configuración en menos de 5 minutos
✅ Datos seguros en la nube"""
    
    free_plan.includes_landing_page = True
    free_plan.save()
    
    free_features = ['dashboard', 'appointments', 'patients', 'clinical_history_basic', 
                     'doctors', 'configuration_basic', 'sales_pos', 'products', 
                     'cash_register', 'landing_page']
    free_plan.features.set([features[code] for code in free_features if code in features])
    print(f"   ✅ {free_plan.name} actualizado con {len(free_features)} features")
    
    # PLAN BÁSICO
    print("\n📦 Plan Básico...")
    basic_plan, created = SubscriptionPlan.objects.get_or_create(
        slug='basic',
        defaults={
            'name': 'Plan Básico',
            'plan_type': 'basic',
            'price_monthly': Decimal('49900.00'),
            'price_yearly': Decimal('499000.00'),
        }
    )
    
    basic_plan.max_users = 3
    basic_plan.max_organizations = 1
    basic_plan.max_appointments_month = 0  # Ilimitadas
    basic_plan.max_patients = 0  # Ilimitados
    basic_plan.max_storage_mb = 5120  # 5 GB
    basic_plan.whatsapp_messages_included = 500
    basic_plan.whatsapp_overage_price = Decimal('0.050')  # $50 COP
    basic_plan.allow_electronic_invoicing = False
    basic_plan.unlimited_appointments = True
    basic_plan.unlimited_patients = True
    
    basic_plan.coverage_description = "Perfecto para ópticas pequeñas en crecimiento"
    basic_plan.ideal_for = "Ópticas independientes con 1-3 empleados"
    basic_plan.plan_badge = ""
    basic_plan.highlighted_features = """Todo lo del plan gratuito +
Pacientes y citas ilimitadas
Control completo de inventario
Fórmulas oftálmicas digitales
Reportes básicos de ventas
Landing page personalizable
500 mensajes WhatsApp/mes"""
    
    basic_plan.main_benefits = """✅ Hasta 3 usuarios simultáneos
✅ 5 GB de almacenamiento
✅ Soporte por email y chat
✅ Actualizaciones automáticas"""
    
    basic_plan.includes_landing_page = True
    basic_plan.save()
    
    basic_features = free_features + ['inventory', 'formulas', 'reports_basic', 
                                      'documents', 'configuration_advanced', 'permissions_advanced']
    basic_plan.features.set([features[code] for code in basic_features if code in features])
    print(f"   ✅ {basic_plan.name} actualizado con {len(basic_features)} features")
    
    # PLAN PROFESIONAL
    print("\n📦 Plan Profesional...")
    pro_plan, created = SubscriptionPlan.objects.get_or_create(
        slug='professional',
        defaults={
            'name': 'Plan Profesional',
            'plan_type': 'professional',
            'price_monthly': Decimal('99900.00'),
            'price_yearly': Decimal('999000.00'),
        }
    )
    
    pro_plan.max_users = 10
    pro_plan.max_organizations = 1
    pro_plan.max_appointments_month = 0
    pro_plan.max_patients = 0
    pro_plan.max_storage_mb = 51200  # 50 GB
    pro_plan.whatsapp_messages_included = 2000
    pro_plan.whatsapp_overage_price = Decimal('0.040')  # $40 COP
    pro_plan.allow_electronic_invoicing = True
    pro_plan.max_invoices_month = 500
    pro_plan.unlimited_appointments = True
    pro_plan.unlimited_patients = True
    
    pro_plan.coverage_description = "La solución completa para ópticas medianas en crecimiento"
    pro_plan.ideal_for = "Ópticas con 3-10 empleados que buscan automatización"
    pro_plan.plan_badge = "⭐ MÁS POPULAR"
    pro_plan.highlighted_features = """Todo lo del plan básico +
Promociones automáticas
Análisis avanzado e IA
Auditoría completa del sistema
WhatsApp Business integrado
Facturación electrónica DIAN (500/mes)
Workflows y automatización
Multi-sede (hasta 3)
Acceso API básico"""
    
    pro_plan.main_benefits = """✅ Hasta 10 usuarios simultáneos
✅ 50 GB de almacenamiento
✅ 2.000 mensajes WhatsApp/mes
✅ Soporte prioritario (8 hrs)
✅ Capacitación incluida"""
    
    pro_plan.whatsapp_integration = True
    pro_plan.api_access = True
    pro_plan.analytics = True
    pro_plan.multi_location = True
    pro_plan.includes_landing_page = True
    pro_plan.save()
    
    pro_features = basic_features + ['promotions', 'analytics_advanced', 'audit', 'teams',
                                     'workflows', 'tasks', 'notifications_push', 
                                     'whatsapp_integration', 'electronic_invoicing', 
                                     'multi_location', 'api_rest']
    pro_plan.features.set([features[code] for code in pro_features if code in features])
    print(f"   ✅ {pro_plan.name} actualizado con {len(pro_features)} features")
    
    # PLAN PREMIUM
    print("\n📦 Plan Premium...")
    premium_plan, created = SubscriptionPlan.objects.get_or_create(
        slug='premium',
        defaults={
            'name': 'Plan Premium',
            'plan_type': 'premium',
            'price_monthly': Decimal('199900.00'),
            'price_yearly': Decimal('1999000.00'),
        }
    )
    
    premium_plan.max_users = 0  # Ilimitados
    premium_plan.max_organizations = 0  # Ilimitadas
    premium_plan.max_appointments_month = 0
    premium_plan.max_patients = 0
    premium_plan.max_storage_mb = 0  # Ilimitado
    premium_plan.whatsapp_messages_included = 10000
    premium_plan.whatsapp_overage_price = Decimal('0.030')  # $30 COP
    premium_plan.allow_electronic_invoicing = True
    premium_plan.max_invoices_month = 0  # Ilimitadas
    premium_plan.unlimited_appointments = True
    premium_plan.unlimited_patients = True
    premium_plan.unlimited_users = True
    premium_plan.unlimited_organizations = True
    premium_plan.unlimited_storage = True
    
    premium_plan.coverage_description = "Solución empresarial para cadenas y grandes ópticas"
    premium_plan.ideal_for = "Cadenas de ópticas o negocios con 10+ empleados"
    premium_plan.plan_badge = "💎 EMPRESARIAL"
    premium_plan.highlighted_features = """Acceso completo a TODOS los módulos
Usuarios ilimitados
Multi-sede ilimitado
Almacenamiento ilimitado
10.000 mensajes WhatsApp/mes
Facturación DIAN ilimitada
Nómina electrónica DIAN
API REST completa ilimitada
Análisis predictivo con IA
Implementación personalizada"""
    
    premium_plan.main_benefits = """✅ Todo ilimitado
✅ Soporte 24/7 (2 hrs respuesta)
✅ Gerente de cuenta dedicado
✅ 4 horas capacitación/mes
✅ Migración de datos incluida
✅ Integración personalizada"""
    
    premium_plan.whatsapp_integration = True
    premium_plan.custom_branding = True
    premium_plan.api_access = True
    premium_plan.priority_support = True
    premium_plan.analytics = True
    premium_plan.multi_location = True
    premium_plan.includes_landing_page = True
    premium_plan.save()
    
    # Premium tiene TODOS los features
    all_features_codes = list(features.keys())
    premium_plan.features.set([features[code] for code in all_features_codes])
    print(f"   ✅ {premium_plan.name} actualizado con TODOS los {len(all_features_codes)} features")
    
    print("\n" + "="*60)
    print("✅ PLANES ACTUALIZADOS EXITOSAMENTE")
    print("="*60)


def main():
    print("\n🚀 IMPLEMENTANDO NUEVA ESTRATEGIA DE PLANES Y PERMISOS")
    print("="*60)
    
    try:
        # 1. Crear features
        features = create_plan_features()
        
        # 2. Actualizar planes
        update_subscription_plans(features)
        
        print("\n" + "="*60)
        print("✅ IMPLEMENTACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        print("\n📋 RESUMEN:")
        print(f"   • Features creados: {PlanFeature.objects.count()}")
        print(f"   • Planes configurados: {SubscriptionPlan.objects.filter(is_active=True).count()}")
        print("\n🎯 Próximos pasos:")
        print("   1. Actualizar decoradores de permisos en views")
        print("   2. Actualizar template tags para badges de plan")
        print("   3. Crear modales de upgrade")
        print("   4. Actualizar menú lateral con indicadores de features")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
