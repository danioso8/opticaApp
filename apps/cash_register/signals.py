"""
Señales para el módulo de Caja
Integración automática con Ventas
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.sales.models import Sale
from .models import CashMovement, CashRegister


@receiver(post_save, sender=Sale)
def create_cash_movement_on_sale(sender, instance, created, **kwargs):
    """
    Crea automáticamente un movimiento de caja cuando se realiza una venta en efectivo
    
    Lógica inteligente:
    - Solo si la venta es nueva (created=True)
    - Solo si el estado es 'completed'
    - Solo si el método de pago es 'cash' (efectivo)
    - Solo si hay una caja abierta para la organización
    - Si no hay caja abierta, permite la venta normal sin error
    """
    # Solo procesar ventas nuevas
    if not created:
        return
    
    # Solo procesar ventas completadas
    if instance.status != 'completed':
        return
    
    # Solo procesar pagos en efectivo
    if instance.payment_method != 'cash':
        return
    
    try:
        # Buscar si hay una caja abierta en la organización
        caja_abierta = CashRegister.objects.filter(
            organization=instance.organization,
            status='OPEN',
            is_active=True
        ).first()
        
        # Si NO hay caja abierta, permitir la venta sin registrar en caja
        if not caja_abierta:
            print(f"[INFO] Venta {instance.sale_number} registrada. No hay caja abierta.")
            return
        
        # Si hay caja abierta, registrar el movimiento automáticamente
        CashMovement.objects.create(
            cash_register=caja_abierta,
            organization=instance.organization,
            movement_type='INCOME',
            category='SALE',
            payment_method='CASH',
            amount=instance.total,
            description=f"Venta {instance.sale_number} - {instance.get_customer_display()}",
            reference=instance.sale_number,
            sale=instance,
            created_by=instance.sold_by
        )
        
        print(f"[SUCCESS] ✅ Movimiento de caja registrado: ${instance.total:,.2f} (Venta {instance.sale_number})")
        
    except Exception as e:
        # Si hay algún error, no impedir la venta
        print(f"[WARNING] Error al crear movimiento de caja para venta {instance.sale_number}: {str(e)}")
        # La venta se completa de todos modos
        pass
