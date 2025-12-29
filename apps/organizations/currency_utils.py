"""
Utilidades para conversión de moneda USD a COP
"""
from decimal import Decimal
from django.conf import settings


def get_exchange_rate():
    """
    Obtiene la tasa de cambio USD a COP
    Por defecto usa 4000 COP por USD, pero puede actualizarse
    """
    # Puedes cambiar esta tasa manualmente o conectar una API
    rate = getattr(settings, 'USD_TO_COP_RATE', 4000.00)
    return Decimal(str(rate))


def usd_to_cop(amount_usd):
    """
    Convierte monto en USD a COP
    
    Args:
        amount_usd: Decimal o float en USD
        
    Returns:
        Decimal: Monto en COP
    """
    if isinstance(amount_usd, (int, float)):
        amount_usd = Decimal(str(amount_usd))
    
    exchange_rate = get_exchange_rate()
    amount_cop = amount_usd * exchange_rate
    
    # Redondear a entero (sin centavos en COP)
    return amount_cop.quantize(Decimal('1'))


def usd_to_cop_cents(amount_usd):
    """
    Convierte monto en USD a centavos COP para Wompi
    Wompi requiere el monto en centavos (sin decimales)
    
    Args:
        amount_usd: Decimal o float en USD
        
    Returns:
        int: Monto en centavos COP
    """
    amount_cop = usd_to_cop(amount_usd)
    # Multiplicar por 100 para obtener centavos
    cents = int(amount_cop * 100)
    return cents


def format_cop(amount_cop, include_symbol=True):
    """
    Formatea un monto en COP para mostrar
    
    Args:
        amount_cop: Decimal o int en COP
        include_symbol: Si incluir el símbolo $
        
    Returns:
        str: Monto formateado (ej: "$159,900 COP")
    """
    if isinstance(amount_cop, Decimal):
        amount_cop = int(amount_cop)
    
    # Formatear con separadores de miles
    formatted = "{:,}".format(amount_cop).replace(',', '.')
    
    if include_symbol:
        return f"${formatted} COP"
    return formatted


def get_plan_price_cop(plan):
    """
    Obtiene el precio de un plan en COP
    
    Args:
        plan: Instancia de SubscriptionPlan
        
    Returns:
        dict: {'monthly_cop': Decimal, 'yearly_cop': Decimal, 'exchange_rate': Decimal}
    """
    return {
        'monthly_cop': usd_to_cop(plan.price_monthly),
        'yearly_cop': usd_to_cop(plan.price_yearly),
        'monthly_cop_formatted': format_cop(usd_to_cop(plan.price_monthly)),
        'yearly_cop_formatted': format_cop(usd_to_cop(plan.price_yearly)),
        'exchange_rate': get_exchange_rate(),
    }


def get_plan_prices_display(plan):
    """
    Obtiene los precios de un plan en ambas monedas para mostrar
    
    Args:
        plan: Instancia de SubscriptionPlan
        
    Returns:
        dict con todos los precios formateados
    """
    cop_prices = get_plan_price_cop(plan)
    
    return {
        'monthly_usd': float(plan.price_monthly),
        'yearly_usd': float(plan.price_yearly),
        'monthly_cop': float(cop_prices['monthly_cop']),
        'yearly_cop': float(cop_prices['yearly_cop']),
        'monthly_cop_cents': usd_to_cop_cents(plan.price_monthly),
        'yearly_cop_cents': usd_to_cop_cents(plan.price_yearly),
        'monthly_cop_formatted': cop_prices['monthly_cop_formatted'],
        'yearly_cop_formatted': cop_prices['yearly_cop_formatted'],
        'monthly_usd_formatted': f"${plan.price_monthly} USD",
        'yearly_usd_formatted': f"${plan.price_yearly} USD",
        'exchange_rate': float(cop_prices['exchange_rate']),
    }
