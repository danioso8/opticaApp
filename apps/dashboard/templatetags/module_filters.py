from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='multiply')
def multiply(value, arg):
    """Multiplica el valor por el argumento"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''


@register.filter(name='dict_keys')
def dict_keys(value):
    """Retorna las llaves de un diccionario como lista"""
    try:
        if isinstance(value, dict):
            return list(value.keys())
        return []
    except (ValueError, TypeError, AttributeError):
        return []


@register.filter(name='to_list')
def to_list(value):
    """Convierte dict_keys u otros iterables a lista"""
    try:
        return list(value)
    except (ValueError, TypeError):
        return []
