from django import template

register = template.Library()

@register.filter
def attr(obj, attr_name):
    """
    Get an attribute from an object dynamically.
    Usage: {{ form|attr:"field_name" }}
    """
    try:
        return getattr(obj, attr_name)
    except AttributeError:
        return None

@register.filter
def split(value, delimiter=','):
    """
    Split a string by a delimiter.
    Usage: {{ value|split:", " }}
    """
    if not value:
        return []
    return [item.strip() for item in str(value).split(delimiter) if item.strip()]
