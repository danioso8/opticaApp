"""
Template tags para verificar acceso a módulos en las plantillas
"""
from django import template
from apps.organizations.plan_features import (
    has_module_access, 
    get_user_modules, 
    get_required_plan_for_module,
    get_module_info
)

register = template.Library()


@register.simple_tag(takes_context=True)
def has_module(context, module_code):
    """
    Verifica si el usuario tiene acceso a un módulo específico
    
    Uso en templates:
        {% load plan_features %}
        {% has_module 'whatsapp' as has_whatsapp %}
        {% if has_whatsapp %}
            <a href="{% url 'whatsapp:dashboard' %}">WhatsApp</a>
        {% endif %}
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return False
    
    return has_module_access(request.user, module_code)


@register.simple_tag(takes_context=True)
def user_modules(context):
    """
    Retorna la lista de códigos de módulos a los que el usuario tiene acceso
    
    Uso en templates:
        {% load plan_features %}
        {% user_modules as modules %}
        {% if 'products' in modules %}
            <a href="{% url 'products:list' %}">Productos</a>
        {% endif %}
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return []
    
    return get_user_modules(request.user)


@register.simple_tag
def module_required_plan(module_code):
    """
    Retorna el plan mínimo requerido para un módulo
    
    Uso en templates:
        {% module_required_plan 'analytics' %}
    """
    return get_required_plan_for_module(module_code)


@register.simple_tag
def module_info(module_code):
    """
    Retorna información completa de un módulo
    
    Uso en templates:
        {% module_info 'whatsapp' as info %}
        {{ info.name }} - {{ info.description }}
    """
    return get_module_info(module_code)


@register.inclusion_tag('organizations/module_badge.html', takes_context=True)
def module_badge(context, module_code):
    """
    Muestra un badge de "Upgrade" si el usuario no tiene acceso al módulo
    
    MODIFICADO: Ahora siempre indica acceso completo (sin candados)
    
    Uso en templates:
        {% load plan_features %}
        {% module_badge 'whatsapp' %}
    """
    request = context.get('request')
    has_access = True  # MODIFICADO: Siempre tiene acceso
    required_plan = get_required_plan_for_module(module_code)
    module_data = get_module_info(module_code)
    
    # CÓDIGO ORIGINAL DESHABILITADO:
    # if request and request.user.is_authenticated:
    #     has_access = has_module_access(request.user, module_code)
    
    return {
        'has_access': has_access,
        'module_code': module_code,
        'required_plan': required_plan,
        'module_name': module_data.get('name', module_code) if module_data else module_code,
    }
# LEGACY: Mantener compatibilidad con código antiguo
@register.simple_tag(takes_context=True)
def has_feature(context, feature_code):
    """
    LEGACY: Redirige al nuevo sistema de módulos
    Verifica si el usuario tiene acceso a un módulo
    
    Uso en templates:
        {% load plan_features %}
        {% has_feature 'whatsapp_integration' as has_whatsapp %}
        {% if has_whatsapp %}
            <button>Enviar WhatsApp</button>
        {% endif %}
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return False
    
    # Usar el nuevo sistema
    return has_module_access(request.user, feature_code)


@register.inclusion_tag('organizations/feature_lock.html', takes_context=True)
def feature_lock(context, feature_code, feature_name="esta funcionalidad"):
    """
    Muestra un mensaje de actualización si el usuario no tiene el módulo
    
    Uso en templates:
        {% load plan_features %}
        {% feature_lock 'whatsapp_integration' 'WhatsApp' %}
    """
    request = context.get('request')
    has_access = False
    
    if request and request.user.is_authenticated:
        user = request.user
        if hasattr(user, 'subscription') and user.subscription.is_active:
            has_access = user.subscription.plan.has_feature(feature_code)
    
    return {
        'has_access': has_access,
        'feature_name': feature_name,
        'request': request
    }


@register.filter
def user_has_feature(user, feature_code):
    """
    Filtro para verificar acceso a módulos
    
    Uso en templates:
        {% if request.user|user_has_feature:'whatsapp_integration' %}
            ...
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False
    
    if not hasattr(user, 'subscription'):
        return False
    
    subscription = user.subscription
    if not subscription.is_active:
        return False
    
    return subscription.plan.has_feature(feature_code)


@register.simple_tag(takes_context=True)
def get_plan_features(context):
    """
    Obtiene todos los módulos disponibles del plan del usuario
    
    Uso en templates:
        {% get_plan_features as features %}
        {% for feature in features %}
            <li>{{ feature.name }}</li>
        {% endfor %}
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return []
    
    user = request.user
    if not hasattr(user, 'subscription'):
        return []
    
    subscription = user.subscription
    if not subscription.is_active:
        return []
    
    return subscription.plan.features.filter(is_active=True)
