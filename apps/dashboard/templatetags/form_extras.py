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
