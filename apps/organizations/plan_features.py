"""
Sistema de control de acceso a módulos por plan de suscripción
"""

# Definición de todos los módulos del sistema
MODULES = {
    # Core - Disponibles en todos los planes
    'dashboard': {
        'name': 'Dashboard',
        'description': 'Panel principal con estadísticas',
        'icon': 'fas fa-home',
        'category': 'core',
    },
    'patients': {
        'name': 'Pacientes',
        'description': 'Gestión de pacientes',
        'icon': 'fas fa-users',
        'category': 'core',
    },
    'appointments': {
        'name': 'Citas',
        'description': 'Agendamiento de citas',
        'icon': 'fas fa-calendar-alt',
        'category': 'core',
    },
    'doctors': {
        'name': 'Doctores',
        'description': 'Gestión de doctores/optómetras',
        'icon': 'fas fa-user-md',
        'category': 'core',
    },
    'landing_config': {
        'name': 'Landing Page',
        'description': 'Configuración de página pública',
        'icon': 'fas fa-globe',
        'category': 'core',
    },
    'invoices_basic': {
        'name': 'Facturación Básica',
        'description': 'Facturas normales (no electrónicas)',
        'icon': 'fas fa-file-invoice',
        'category': 'core',
    },
    'clinical_history': {
        'name': 'Historia Clínica',
        'description': 'Historias clínicas de pacientes',
        'icon': 'fas fa-notes-medical',
        'category': 'medical',
    },
    
    # Inventario - Desde plan Básico
    'products': {
        'name': 'Productos',
        'description': 'Catálogo de productos',
        'icon': 'fas fa-box',
        'category': 'inventory',
    },
    'inventory': {
        'name': 'Inventario',
        'description': 'Control de stock',
        'icon': 'fas fa-boxes',
        'category': 'inventory',
    },
    'suppliers': {
        'name': 'Proveedores',
        'description': 'Gestión de proveedores',
        'icon': 'fas fa-truck',
        'category': 'inventory',
    },
    
    # Facturación Avanzada - Desde plan Profesional
    'invoices_dian': {
        'name': 'Facturación DIAN',
        'description': 'Facturación electrónica DIAN',
        'icon': 'fas fa-file-invoice-dollar',
        'category': 'billing',
    },
    'dian_config': {
        'name': 'Configuración DIAN',
        'description': 'Configuración de facturación electrónica',
        'icon': 'fas fa-cog',
        'category': 'billing',
    },
    
    # Comunicación - Desde plan Profesional
    'whatsapp': {
        'name': 'WhatsApp',
        'description': 'Notificaciones por WhatsApp',
        'icon': 'fab fa-whatsapp',
        'category': 'communication',
    },
    'notifications_config': {
        'name': 'Config. Notificaciones',
        'description': 'Configuración de notificaciones',
        'icon': 'fas fa-bell',
        'category': 'communication',
    },
    
    # Pagos - Desde plan Profesional
    'wompi_payments': {
        'name': 'Pagos en Línea',
        'description': 'Pagos con Wompi',
        'icon': 'fas fa-credit-card',
        'category': 'payments',
    },
    
    # Analytics - Desde plan Premium
    'analytics': {
        'name': 'Analytics Avanzado',
        'description': 'Reportes y estadísticas avanzadas',
        'icon': 'fas fa-chart-line',
        'category': 'analytics',
    },
    'reports': {
        'name': 'Reportes',
        'description': 'Reportes personalizados',
        'icon': 'fas fa-file-alt',
        'category': 'analytics',
    },
    
    # Gestión - Desde plan Premium
    'team_management': {
        'name': 'Gestión de Equipo',
        'description': 'Administración de usuarios y roles',
        'icon': 'fas fa-users-cog',
        'category': 'management',
    },
    'multi_location': {
        'name': 'Múltiples Ubicaciones',
        'description': 'Gestión de múltiples sucursales',
        'icon': 'fas fa-map-marked-alt',
        'category': 'management',
    },
    
    # API - Solo Empresarial
    'api_access': {
        'name': 'Acceso API',
        'description': 'API REST para integraciones',
        'icon': 'fas fa-code',
        'category': 'integration',
    },
}

# Matriz de acceso: Módulos permitidos por cada plan
PLAN_MODULES = {
    'free': [
        # Core básico
        'dashboard',
        'patients',
        'appointments',
        'doctors',
        'landing_config',
        'invoices_basic',
        'clinical_history',
    ],
    'basic': [
        # Todo lo de Free +
        'dashboard',
        'patients',
        'appointments',
        'doctors',
        'landing_config',
        'invoices_basic',
        'clinical_history',
        # + Inventario
        'products',
        'inventory',
        'suppliers',
        # + Gestión de equipo (hasta 3 usuarios)
        'team_management',
    ],
    'professional': [
        # Todo lo de Basic +
        'dashboard',
        'patients',
        'appointments',
        'doctors',
        'landing_config',
        'invoices_basic',
        'clinical_history',
        'products',
        'inventory',
        'suppliers',
        'team_management',
        # + Facturación DIAN
        'invoices_dian',
        'dian_config',
        # + Comunicación
        'whatsapp',
        'notifications_config',
        # + Pagos
        'wompi_payments',
    ],
    'premium': [
        # Todo lo de Professional +
        'dashboard',
        'patients',
        'appointments',
        'doctors',
        'landing_config',
        'invoices_basic',
        'clinical_history',
        'products',
        'inventory',
        'suppliers',
        'invoices_dian',
        'dian_config',
        'whatsapp',
        'notifications_config',
        'wompi_payments',
        # + Analytics
        'analytics',
        'reports',
        # + Gestión
        'team_management',
        'multi_location',
    ],
    'enterprise': [
        # Todo lo de Premium + API + Todas las funcionalidades avanzadas
        'dashboard',
        'patients',
        'appointments',
        'doctors',
        'landing_config',
        'invoices_basic',
        'clinical_history',
        'products',
        'inventory',
        'suppliers',
        'invoices_dian',
        'dian_config',
        'whatsapp',
        'notifications_config',
        'wompi_payments',
        'analytics',
        'reports',
        'team_management',
        'multi_location',
        'api_access',
        # + Nómina Electrónica
        'payroll_dian',
        'payroll_config',
        # + Marketing y Automatización
        'workflows',
        'promotions',
        'email_marketing',
        # + Adicionales Enterprise
        'audit',
        'permissions_advanced',
        'configuration_advanced',
    ],
}


def get_plan_modules(plan_type):
    """
    Obtiene la lista de módulos permitidos para un plan
    
    Args:
        plan_type (str): Tipo de plan ('free', 'basic', 'professional', 'premium', 'enterprise')
    
    Returns:
        list: Lista de códigos de módulos permitidos
    """
    return PLAN_MODULES.get(plan_type, PLAN_MODULES['free'])


def has_module_access(user, module_code):
    """
    Verifica si un usuario tiene acceso a un módulo específico
    
    Args:
        user: Usuario de Django
        module_code (str): Código del módulo a verificar
    
    Returns:
        bool: True si tiene acceso, False si no
    """
    # Superusuarios tienen acceso a todo
    if user.is_superuser:
        return True
    
    # Primero verificar la suscripción de la organización (si pertenece a alguna)
    try:
        from apps.organizations.models import OrganizationMember
        from apps.users.models import UserSubscription
        
        # Buscar membresía activa del usuario
        membership = OrganizationMember.objects.filter(
            user=user,
            is_active=True,
            organization__is_active=True
        ).select_related('organization').first()
        
        if membership and membership.organization:
            # Si la organización tiene suscripción, usar esa
            org_subscription = UserSubscription.objects.filter(
                user=membership.organization.owner,
                is_active=True
            ).first()
            
            if org_subscription and not org_subscription.needs_payment_after_trial():
                plan_type = org_subscription.plan.plan_type
                allowed_modules = get_plan_modules(plan_type)
                return module_code in allowed_modules
        
        # Si no hay suscripción de organización, verificar suscripción personal del usuario
        subscription = UserSubscription.objects.get(user=user)
        
        # Verificar que la suscripción esté activa
        if not subscription.is_active:
            return False
        
        # Si el trial expiró y no ha pagado, bloquear todo excepto dashboard
        if subscription.needs_payment_after_trial():
            return module_code == 'dashboard'
        
        # Obtener módulos del plan
        plan_type = subscription.plan.plan_type
        allowed_modules = get_plan_modules(plan_type)
        
        return module_code in allowed_modules
        
    except:
        # Si no tiene suscripción, solo acceso a dashboard
        return module_code == 'dashboard'


def get_user_modules(user):
    """
    Obtiene todos los módulos a los que el usuario tiene acceso
    
    Args:
        user: Usuario de Django
    
    Returns:
        dict: Diccionario con módulos agrupados por categoría
    """
    # Superusuarios tienen acceso a todo
    if user.is_superuser:
        allowed_modules = list(MODULES.keys())
    else:
        try:
            from apps.users.models import UserSubscription
            subscription = UserSubscription.objects.get(user=user)
            
            # Si el trial expiró, solo dashboard
            if subscription.needs_payment_after_trial():
                allowed_modules = ['dashboard']
            else:
                plan_type = subscription.plan.plan_type
                allowed_modules = get_plan_modules(plan_type)
        except:
            allowed_modules = ['dashboard']
    
    # Organizar por categorías
    modules_by_category = {}
    for module_code in allowed_modules:
        if module_code in MODULES:
            module = MODULES[module_code]
            category = module['category']
            
            if category not in modules_by_category:
                modules_by_category[category] = []
            
            modules_by_category[category].append({
                'code': module_code,
                **module
            })
    
    return modules_by_category


def get_module_info(module_code):
    """
    Obtiene la información completa de un módulo
    
    Args:
        module_code (str): Código del módulo
    
    Returns:
        dict: Información del módulo o None si no existe
    """
    return MODULES.get(module_code)


def get_required_plan_for_module(module_code):
    """
    Obtiene el plan mínimo requerido para acceder a un módulo
    
    Args:
        module_code (str): Código del módulo
    
    Returns:
        str: Tipo de plan requerido ('free', 'basic', 'professional', 'premium', 'enterprise')
    """
    for plan_type in ['free', 'basic', 'professional', 'premium', 'enterprise']:
        if module_code in PLAN_MODULES[plan_type]:
            return plan_type
    
    return 'enterprise'  # Por defecto, requiere el plan más alto


def get_all_modules_with_access(user):
    """
    Obtiene todos los módulos con información de acceso
    
    Args:
        user: Usuario de Django
    
    Returns:
        list: Lista de módulos con flag 'has_access'
    """
    all_modules = []
    
    for code, info in MODULES.items():
        has_access = has_module_access(user, code)
        required_plan = get_required_plan_for_module(code)
        
        all_modules.append({
            'code': code,
            'has_access': has_access,
            'required_plan': required_plan,
            **info
        })
    
    return all_modules
