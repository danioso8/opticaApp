"""
Filtros de plantilla para el módulo de Caja
"""
from django import template
from decimal import Decimal

register = template.Library()


@register.filter(name='currency')
def currency(value):
    """
    Formatea un número como moneda colombiana con separador de miles (puntos)
    Ejemplo: 1000000 -> 1.000.000,00
    """
    try:
        value = Decimal(str(value))
        # Separar parte entera y decimal
        int_part = int(value)
        dec_part = int((value - int_part) * 100)
        
        # Formatear parte entera con puntos
        int_str = str(int_part)
        formatted = ""
        for i, digit in enumerate(reversed(int_str)):
            if i > 0 and i % 3 == 0:
                formatted = "." + formatted
            formatted = digit + formatted
        
        # Agregar parte decimal
        return f"{formatted},{dec_part:02d}"
    except (ValueError, TypeError, AttributeError):
        return "0,00"


@register.filter(name='currency_symbol')
def currency_symbol(value):
    """
    Formatea un número como moneda con símbolo $
    Ejemplo: 1000000 -> $1.000.000,00
    """
    return f"${currency(value)}"
