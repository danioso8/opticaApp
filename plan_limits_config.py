#!/usr/bin/env python
"""
SISTEMA DE CONFIGURACIÓN DE LÍMITES Y CARACTERÍSTICAS DE PLANES
================================================================

Este archivo define todos los límites, características y configuraciones
de los planes de suscripción. Se actualiza automáticamente cuando se
desarrollan nuevas funcionalidades.

ÚLTIMA ACTUALIZACIÓN: 2025-12-15
"""

# Valor especial para indicar "ilimitado"
UNLIMITED = 999999

# ============================================================================
# CONFIGURACIÓN DE PLANES
# ============================================================================

PLAN_CONFIGURATIONS = {
    'free': {
        'name': 'Plan Free',
        'plan_type': 'free',
        'price_monthly': 0.00,
        'price_yearly': 0.00,
        
        # LÍMITES PRINCIPALES
        'limits': {
            'max_users': 1,                    # Usuarios que pueden acceder
            'max_organizations': 1,            # Empresas/Sucursales
            'max_appointments_month': 20,      # Citas por mes
            'max_patients': 1,                 # Pacientes registrados
            'max_storage_mb': 100,             # Almacenamiento en MB
        },
        
        # FACTURACIÓN ELECTRÓNICA DIAN
        'electronic_invoicing': {
            'enabled': False,
            'max_invoices_month': 0,           # 0 = deshabilitado
        },
        
        # CARACTERÍSTICAS LEGACY
        'features_legacy': {
            'whatsapp_integration': False,
            'custom_branding': False,
            'api_access': False,
            'priority_support': False,
            'analytics': False,
            'multi_location': False,
        },
        
        # MÓDULOS DEL SISTEMA (códigos de PlanFeature)
        'modules': [
            'basic_appointments',
            'basic_patients',
        ],
    },
    
    'basic': {
        'name': 'Plan Básico',
        'plan_type': 'basic',
        'price_monthly': 80000.00,
        'price_yearly': 800000.00,
        
        # LÍMITES PRINCIPALES
        'limits': {
            'max_users': 2,
            'max_organizations': 2,
            'max_appointments_month': 100,
            'max_patients': 4,
            'max_storage_mb': 500,
        },
        
        # FACTURACIÓN ELECTRÓNICA DIAN
        'electronic_invoicing': {
            'enabled': False,
            'max_invoices_month': 0,
        },
        
        # CARACTERÍSTICAS LEGACY
        'features_legacy': {
            'whatsapp_integration': True,
            'custom_branding': False,
            'api_access': False,
            'priority_support': False,
            'analytics': False,
            'multi_location': True,
        },
        
        # MÓDULOS DEL SISTEMA
        'modules': [
            'basic_appointments',
            'basic_patients',
            'inventory_basic',
            'reports_basic',
        ],
    },
    
    'professional': {
        'name': 'Plan Pro',
        'plan_type': 'professional',
        'price_monthly': 200000.00,
        'price_yearly': 2000000.00,
        
        # LÍMITES PRINCIPALES
        'limits': {
            'max_users': 10,
            'max_organizations': 10,
            'max_appointments_month': 1000,
            'max_patients': 10,
            'max_storage_mb': 2000,
        },
        
        # FACTURACIÓN ELECTRÓNICA DIAN
        'electronic_invoicing': {
            'enabled': True,
            'max_invoices_month': 20,          # 20 facturas mensuales
        },
        
        # CARACTERÍSTICAS LEGACY
        'features_legacy': {
            'whatsapp_integration': True,
            'custom_branding': True,
            'api_access': True,
            'priority_support': True,
            'analytics': True,
            'multi_location': True,
        },
        
        # MÓDULOS DEL SISTEMA
        'modules': [
            'basic_appointments',
            'basic_patients',
            'inventory_basic',
            'inventory_advanced',
            'reports_basic',
            'reports_advanced',
            'electronic_invoicing',
            'crm_basic',
        ],
    },
    
    'enterprise': {
        'name': 'Plan Empresarial',
        'plan_type': 'enterprise',
        'price_monthly': 500000.00,
        'price_yearly': 5000000.00,
        
        # LÍMITES PRINCIPALES (TODOS ILIMITADOS)
        'limits': {
            'max_users': UNLIMITED,
            'max_organizations': UNLIMITED,
            'max_appointments_month': UNLIMITED,
            'max_patients': UNLIMITED,
            'max_storage_mb': 10000,           # 10GB
        },
        
        # FACTURACIÓN ELECTRÓNICA DIAN
        'electronic_invoicing': {
            'enabled': True,
            'max_invoices_month': 0,           # 0 = ilimitado
        },
        
        # CARACTERÍSTICAS LEGACY (TODAS HABILITADAS)
        'features_legacy': {
            'whatsapp_integration': True,
            'custom_branding': True,
            'api_access': True,
            'priority_support': True,
            'analytics': True,
            'multi_location': True,
        },
        
        # MÓDULOS DEL SISTEMA (TODOS)
        'modules': [
            'basic_appointments',
            'basic_patients',
            'inventory_basic',
            'inventory_advanced',
            'reports_basic',
            'reports_advanced',
            'electronic_invoicing',
            'crm_basic',
            'crm_advanced',
            'ar_try_on',
            'telemedicine',
        ],
    },
}


# ============================================================================
# NUEVAS FUNCIONALIDADES - AGREGAR AQUÍ AL DESARROLLAR
# ============================================================================

"""
INSTRUCCIONES PARA AGREGAR NUEVAS FUNCIONALIDADES:

1. Cuando desarrolles una nueva funcionalidad que tenga límites, agrégala aquí
2. Define el límite para cada plan
3. Ejecuta el script de sincronización para actualizar la base de datos

EJEMPLO - Agregar límite de "Campañas de Marketing":

'limits': {
    ...
    'max_marketing_campaigns': 5,  # Agregar en cada plan
}

EJEMPLO - Agregar nuevo módulo:

'modules': [
    ...
    'marketing_campaigns',  # Agregar en los planes correspondientes
]

Luego ejecutar: python sync_plan_limits.py
"""

# ============================================================================
# FUNCIONES DE AYUDA
# ============================================================================

def get_plan_config(plan_type):
    """Obtiene la configuración completa de un plan"""
    return PLAN_CONFIGURATIONS.get(plan_type)


def get_all_limits():
    """Obtiene todos los tipos de límites definidos"""
    # Tomar límites del plan más completo (enterprise)
    return list(PLAN_CONFIGURATIONS['enterprise']['limits'].keys())


def get_unlimited_value():
    """Retorna el valor que representa 'ilimitado'"""
    return UNLIMITED


def is_unlimited(value):
    """Verifica si un valor representa ilimitado"""
    return value >= UNLIMITED


def format_limit(value, unit=''):
    """Formatea un valor de límite para mostrar"""
    if is_unlimited(value):
        return '∞ Ilimitado'
    return f"{value:,} {unit}".strip()


# ============================================================================
# VALIDACIONES
# ============================================================================

def validate_plan_config():
    """Valida que todas las configuraciones de planes sean correctas"""
    errors = []
    
    required_keys = ['name', 'plan_type', 'price_monthly', 'price_yearly', 
                     'limits', 'electronic_invoicing', 'features_legacy', 'modules']
    
    for plan_type, config in PLAN_CONFIGURATIONS.items():
        # Verificar claves requeridas
        for key in required_keys:
            if key not in config:
                errors.append(f"Plan '{plan_type}' falta clave: {key}")
        
        # Verificar límites requeridos
        if 'limits' in config:
            required_limits = ['max_users', 'max_organizations', 'max_appointments_month', 
                              'max_patients', 'max_storage_mb']
            for limit in required_limits:
                if limit not in config['limits']:
                    errors.append(f"Plan '{plan_type}' falta límite: {limit}")
    
    return errors


# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("📋 CONFIGURACIÓN DE PLANES DE SUSCRIPCIÓN")
    print("="*70 + "\n")
    
    # Validar configuración
    print("🔍 Validando configuración...")
    errors = validate_plan_config()
    
    if errors:
        print("\n❌ ERRORES ENCONTRADOS:\n")
        for error in errors:
            print(f"  • {error}")
        print()
    else:
        print("✅ Configuración válida\n")
        
        # Mostrar resumen
        print("-"*70)
        print("RESUMEN DE PLANES:")
        print("-"*70 + "\n")
        
        for plan_type, config in PLAN_CONFIGURATIONS.items():
            print(f"📦 {config['name']} ({plan_type})")
            print(f"   Precio: ${config['price_monthly']:,.2f}/mes")
            print(f"   Límites:")
            for limit, value in config['limits'].items():
                print(f"      • {limit}: {format_limit(value)}")
            print(f"   Facturación: {'✅ Habilitada' if config['electronic_invoicing']['enabled'] else '❌ Deshabilitada'}")
            print(f"   Módulos: {len(config['modules'])} disponibles")
            print()
        
        print("-"*70)
        print(f"Total de límites definidos: {len(get_all_limits())}")
        print("-"*70 + "\n")
