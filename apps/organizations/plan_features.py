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
    
    # Módulos adicionales Empresariales
    'invoices': {
        'name': 'Facturación General',
        'description': 'Sistema completo de facturación',
        'icon': 'fas fa-file-invoice',
        'category': 'billing',
    },
    'billing': {
        'name': 'Billing Completo',
        'description': 'Módulo de facturación completo',
        'icon': 'fas fa-receipt',
        'category': 'billing',
    },
    'payroll': {
        'name': 'Nómina',
        'description': 'Sistema de nómina general',
        'icon': 'fas fa-money-check-alt',
        'category': 'hr',
    },
    'payroll_dian': {
        'name': 'Nómina Electrónica DIAN',
        'description': 'Nómina electrónica según DIAN',
        'icon': 'fas fa-file-invoice-dollar',
        'category': 'hr',
    },
    'payroll_config': {
        'name': 'Configuración Nómina',
        'description': 'Configuración del sistema de nómina',
        'icon': 'fas fa-cog',
        'category': 'hr',
    },
    'workflows': {
        'name': 'Workflows',
        'description': 'Flujos de trabajo automatizados',
        'icon': 'fas fa-project-diagram',
        'category': 'automation',
    },
    'promotions': {
        'name': 'Promociones',
        'description': 'Campañas y promociones',
        'icon': 'fas fa-tags',
        'category': 'marketing',
    },
    'marketing': {
        'name': 'Marketing',
        'description': 'Herramientas de marketing',
        'icon': 'fas fa-bullhorn',
        'category': 'marketing',
    },
    'email_marketing': {
        'name': 'Email Marketing',
        'description': 'Campañas de email marketing',
        'icon': 'fas fa-envelope',
        'category': 'marketing',
    },
    'audit': {
        'name': 'Auditoría',
        'description': 'Registro de auditoría del sistema',
        'icon': 'fas fa-clipboard-list',
        'category': 'security',
    },
    'permissions_advanced': {
        'name': 'Permisos Avanzados',
        'description': 'Control avanzado de permisos',
        'icon': 'fas fa-user-shield',
        'category': 'security',
    },
    'configuration_advanced': {
        'name': 'Configuración Avanzada',
        'description': 'Configuraciones avanzadas del sistema',
        'icon': 'fas fa-sliders-h',
        'category': 'configuration',
    },
    'cash_register': {
        'name': 'Caja Registradora',
        'description': 'Gestión de caja y tesorería',
        'icon': 'fas fa-cash-register',
        'category': 'sales',
    },
    'sales': {
        'name': 'Ventas',
        'description': 'Módulo de ventas',
        'icon': 'fas fa-shopping-cart',
        'category': 'sales',
    },
    'employees': {
        'name': 'Empleados',
        'description': 'Gestión de empleados',
        'icon': 'fas fa-user-tie',
        'category': 'hr',
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
        # Inventario básico
        'products',
        'inventory',
        'suppliers',
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
        # Inventario
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
        'invoices',  # Facturación general
        'billing',  # Módulo billing completo
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
        'payroll',  # Nómina general
        'payroll_dian',
        'payroll_config',
        # + Marketing y Automatización
        'workflows',
        'promotions',
        'marketing',  # Marketing general
        'email_marketing',
        # + Adicionales Enterprise
        'audit',
        'permissions_advanced',
        'configuration_advanced',
        # + Otros módulos
        'cash_register',  # Caja registradora
        'sales',  # Ventas
        'employees',  # Empleados
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
    basándose en los módulos asignados a su plan
    
    Args:
        user: Usuario de Django
        module_code (str): Código del módulo a verificar
    
    Returns:
        bool: True si tiene acceso, False si no
    """
    # Superusuarios tienen acceso a todo
    if user.is_superuser:
        return True
    
    try:
        from apps.organizations.models import OrganizationMember, Subscription
        from apps.users.models import UserSubscription
        
        # Primero intentar obtener suscripción de organización
        membership = OrganizationMember.objects.filter(
            user=user,
            is_active=True,
            organization__is_active=True
        ).select_related('organization').first()
        
        if membership and membership.organization:
            organization = membership.organization
            org_subscription = organization.current_subscription
            
            if org_subscription and org_subscription.is_active:
                # Verificar si el módulo está en los features del plan
                return org_subscription.plan.features.filter(code=module_code, is_active=True).exists()
        
        # Si no hay organización, verificar suscripción personal del usuario
        subscription = UserSubscription.objects.filter(
            user=user,
            is_active=True
        ).select_related('plan').first()
        
        if not subscription:
            return False
        
        # Si el trial expiró y no ha pagado, bloquear todo excepto dashboard
        if subscription.needs_payment_after_trial():
            return module_code == 'dashboard'
        
        # Verificar si el módulo está en los features del plan
        return subscription.plan.features.filter(code=module_code, is_active=True).exists()
        
    except Exception as e:
        # Si hay error, denegar acceso por seguridad
        return False


def get_user_modules(user):
    """
    Obtiene todos los módulos a los que el usuario tiene acceso
    basándose en los módulos asignados a su plan
    
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
            from apps.organizations.models import OrganizationMember
            from apps.users.models import UserSubscription
            
            allowed_codes = []
            
            # Intentar obtener módulos de organización primero
            membership = OrganizationMember.objects.filter(
                user=user,
                is_active=True,
                organization__is_active=True
            ).select_related('organization').first()
            
            if membership and membership.organization:
                org_subscription = membership.organization.current_subscription
                if org_subscription and org_subscription.is_active:
                    allowed_codes = list(org_subscription.plan.features.filter(
                        is_active=True
                    ).values_list('code', flat=True))
            
            # Si no hay organización, usar suscripción personal
            if not allowed_codes:
                subscription = UserSubscription.objects.filter(
                    user=user,
                    is_active=True
                ).select_related('plan').first()
                
                if subscription:
                    # Si el trial expiró, solo dashboard
                    if subscription.needs_payment_after_trial():
                        allowed_codes = ['dashboard']
                    else:
                        allowed_codes = list(subscription.plan.features.filter(
                            is_active=True
                        ).values_list('code', flat=True))
                else:
                    allowed_codes = ['dashboard']
            
            allowed_modules = allowed_codes
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
