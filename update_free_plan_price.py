"""
Script para actualizar el precio del Plan Free
Precio post-trial: $12 USD/mes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import SubscriptionPlan
from decimal import Decimal

def update_free_plan():
    """Actualiza el Plan Free con el precio post-trial"""
    
    print("=" * 70)
    print("ACTUALIZACIÓN DE PLAN FREE - PRECIO POST-TRIAL")
    print("=" * 70)
    
    try:
        # Buscar el plan Free
        free_plan = SubscriptionPlan.objects.get(plan_type='free')
        
        print(f"\n📋 Plan encontrado: {free_plan.name}")
        print(f"   Precio actual mensual: ${free_plan.price_monthly}")
        print(f"   Precio actual anual: ${free_plan.price_yearly}")
        
        # Actualizar precios
        free_plan.price_monthly = Decimal('12.00')  # $12 USD/mes después del trial
        free_plan.price_yearly = Decimal('120.00')  # $120 USD/año (10 meses pagando)
        free_plan.save()
        
        print(f"\n✅ Plan actualizado exitosamente!")
        print(f"   Nuevo precio mensual: ${free_plan.price_monthly} USD")
        print(f"   Nuevo precio anual: ${free_plan.price_yearly} USD")
        
        print(f"\n💡 NOTA:")
        print(f"   - Los primeros 3 meses son GRATIS (período de prueba)")
        print(f"   - Después de 3 meses, el plan cuesta ${free_plan.price_monthly} USD/mes")
        print(f"   - Los usuarios existentes mantendrán su suscripción actual")
        
    except SubscriptionPlan.DoesNotExist:
        print("\n❌ ERROR: Plan Free no encontrado")
        print("   Asegúrate de que existe un plan con plan_type='free'")
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False
    
    print("\n" + "=" * 70)
    return True

if __name__ == '__main__':
    update_free_plan()
