"""
Template tags para verificar acceso a módulos en las plantillas
"""
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def has_feature(context, feature_code):
    """
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
    
    user = request.user
    
    if not hasattr(user, 'subscription'):
        return False
    
    subscription = user.subscription
    if not subscription.is_active:
        return False
    
    return subscription.plan.has_feature(feature_code)


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
