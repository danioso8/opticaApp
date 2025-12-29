"""
Script para probar la conversión de moneda USD a COP
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.currency_utils import (
    get_exchange_rate,
    usd_to_cop,
    usd_to_cop_cents,
    format_cop,
    get_plan_prices_display
)
from apps.organizations.models import SubscriptionPlan
from decimal import Decimal

def test_currency_functions():
    """Probar funciones de conversión de moneda"""
    print("=" * 60)
    print("PRUEBA DE CONVERSIÓN USD A COP")
    print("=" * 60)
    
    # Obtener tasa de cambio
    rate = get_exchange_rate()
    print(f"\n1. Tasa de cambio: 1 USD = {rate:,.0f} COP")
    
    # Probar conversión USD a COP
    test_amounts = [0, 39.99, 89.99, 179.99, 359.99, 719.99]
    
    print("\n2. Conversiones USD → COP:")
    print("-" * 60)
    for amount_usd in test_amounts:
        amount_cop = usd_to_cop(amount_usd)
        amount_cop_cents = usd_to_cop_cents(amount_usd)
        formatted = format_cop(amount_cop)
        
        print(f"${amount_usd:>7.2f} USD → {formatted:>15} → {amount_cop_cents:,} centavos")
    
    # Probar con planes reales
    print("\n3. Precios de planes actuales:")
    print("-" * 60)
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
    
    for plan in plans:
        prices = get_plan_prices_display(plan)
        print(f"\n📦 {plan.name} ({plan.plan_type.upper()})")
        print(f"   Mensual: ${plan.price_monthly} USD → {prices['monthly_cop_formatted']}")
        print(f"            {prices['monthly_cop_cents']:,} centavos para Wompi")
        print(f"   Anual:   ${plan.price_yearly} USD → {prices['yearly_cop_formatted']}")
        print(f"            {prices['yearly_cop_cents']:,} centavos para Wompi")
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas exitosamente")
    print("=" * 60)

def test_wompi_amounts():
    """Verificar que los montos para Wompi sean correctos"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE MONTOS PARA WOMPI")
    print("=" * 60)
    
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
    
    for plan in plans:
        print(f"\n{plan.name}:")
        
        # Mensual
        amount_cop_cents = usd_to_cop_cents(plan.price_monthly)
        amount_cop = usd_to_cop(plan.price_monthly)
        
        print(f"  Mensual:")
        print(f"    - USD: ${plan.price_monthly}")
        print(f"    - COP: ${amount_cop:,.0f} COP")
        print(f"    - Centavos (Wompi): {amount_cop_cents:,}")
        print(f"    - Verificación: {amount_cop_cents / 100:,.2f} COP")
        
        # Anual
        amount_cop_cents_yearly = usd_to_cop_cents(plan.price_yearly)
        amount_cop_yearly = usd_to_cop(plan.price_yearly)
        
        print(f"  Anual:")
        print(f"    - USD: ${plan.price_yearly}")
        print(f"    - COP: ${amount_cop_yearly:,.0f} COP")
        print(f"    - Centavos (Wompi): {amount_cop_cents_yearly:,}")
        print(f"    - Verificación: {amount_cop_cents_yearly / 100:,.2f} COP")

if __name__ == '__main__':
    test_currency_functions()
    test_wompi_amounts()
