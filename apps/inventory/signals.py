from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.sales.models import Sale, Product
from apps.inventory.models import InventoryMovement
from apps.inventory.services.inventory_service import InventoryService


@receiver(post_save, sender=Sale)
def create_inventory_movement_from_sale(sender, instance, created, **kwargs):
    """
    Crear movimientos de inventario automáticos cuando se completa una venta
    """
    if instance.status == 'completed' and not InventoryMovement.objects.filter(
        reference_document=f"SALE-{instance.sale_number}",
        organization=instance.organization
    ).exists():
        
        inventory_service = InventoryService(instance.organization)
        
        # Crear movimiento por cada item de la venta
        for item in instance.items.all():
            try:
                inventory_service.register_movement(
                    product=item.product,
                    movement_type='OUT_SALE',
                    quantity=item.quantity,
                    unit_cost=item.product.cost,
                    created_by=instance.sold_by,
                    reference_document=f"SALE-{instance.sale_number}",
                    reason=f"Venta automática #{instance.sale_number}"
                )
            except ValueError as e:
                # Log error but don't fail the sale
                print(f"Warning: Could not create inventory movement for sale {instance.sale_number}: {e}")
