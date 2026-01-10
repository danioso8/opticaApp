"""
Template tags para verificar features y permisos de planes
"""
from django import template
from apps.organizations.models import SubscriptionPlan, PlanFeature

register = template.Library()


@register.filter
def has_feature(user, feature_code):
    """
    Verifica si el usuario tiene acceso a un feature específico
    Uso: {% if user|has_feature:'whatsapp_integration' %}
    """
    try:
        # Obtener la organización actual del request (se debe pasar en context)
        request = user._request if hasattr(user, '_request') else None
        if not request or not hasattr(request, 'organization'):
            return False
        
        org = request.organization
        if not org or not org.subscription:
            return False
        
        # Verificar si el plan tiene el feature
        return org.subscription.plan.features.filter(code=feature_code).exists()
    except:
        return False


@register.filter
def get_feature_required_plan(feature_code):
    """
    Obtiene el plan mínimo requerido para un feature
    Retorna: 'free', 'basic', 'professional', 'premium'
    """
    try:
        feature = PlanFeature.objects.get(code=feature_code)
        
        # Buscar el plan más básico que incluye este feature
        plans_order = ['free', 'basic', 'professional', 'premium']
        for plan_type in plans_order:
            plan = SubscriptionPlan.objects.filter(
                plan_type=plan_type,
                features__code=feature_code
            ).first()
            if plan:
                return plan_type
        return 'premium'
    except:
        return 'premium'


@register.filter
def get_plan_badge(plan_type):
    """
    Retorna el badge visual para cada tipo de plan
    """
    badges = {
        'free': '',
        'basic': '<span class="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full font-semibold ml-1">BÁSICO</span>',
        'professional': '<span class="text-xs bg-purple-100 text-purple-800 px-2 py-0.5 rounded-full font-semibold ml-1">PRO</span>',
        'premium': '<span class="text-xs bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full font-semibold ml-1">💎 PREMIUM</span>',
        'enterprise': '<span class="text-xs bg-gradient-to-r from-purple-500 to-pink-500 text-white px-2 py-0.5 rounded-full font-semibold ml-1">👑 EMPRESARIAL</span>',
    }
    return badges.get(plan_type, '')


@register.simple_tag(takes_context=True)
def user_plan_type(context):
    """
    Retorna el tipo de plan del usuario actual
    """
    request = context.get('request')
    if not request or not hasattr(request, 'organization'):
        return 'free'
    
    org = request.organization
    if not org or not org.subscription:
        return 'free'
    
    return org.subscription.plan.plan_type


@register.simple_tag(takes_context=True)
def has_plan_access(context, required_plan_type):
    """
    Verifica si el usuario tiene un plan igual o superior al requerido
    Uso: {% has_plan_access 'professional' as can_access %}{% if can_access %}...{% endif %}
    """
    request = context.get('request')
    if not request or not hasattr(request, 'organization'):
        return False
    
    org = request.organization
    if not org or not org.subscription:
        current_plan = 'free'
    else:
        current_plan = org.subscription.plan.plan_type
    
    # Orden de planes
    plan_hierarchy = {'free': 0, 'basic': 1, 'professional': 2, 'premium': 3, 'enterprise': 4}
    
    current_level = plan_hierarchy.get(current_plan, 0)
    required_level = plan_hierarchy.get(required_plan_type, 4)
    
    return current_level >= required_level


@register.inclusion_tag('dashboard/components/feature_lock.html', takes_context=True)
def show_feature_lock(context, feature_code, feature_name):
    """
    Muestra un ícono de candado y badge si el usuario no tiene acceso al feature
    """
    request = context.get('request')
    has_access = False
    required_plan = 'premium'
    
    try:
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            # Usar la función has_module_access para verificar
            from apps.organizations.plan_features import has_module_access
            has_access = has_module_access(request.user, feature_code)
        
        if not has_access:
            required_plan = get_feature_required_plan(feature_code)
    except:
        pass
    
    return {
        'has_access': has_access,
        'required_plan': required_plan,
        'feature_code': feature_code,
        'feature_name': feature_name,
    }
