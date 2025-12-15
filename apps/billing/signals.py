"""
Señales para el módulo de facturación
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Payment, InvoiceItem


@receiver(post_save, sender=Payment)
def payment_saved(sender, instance, created, **kwargs):
    """
    Cuando se guarda un pago, actualiza el saldo de la factura.
    Ya se maneja en Payment.save() pero por si acaso.
    """
    if instance.invoice_id:
        instance.invoice.actualizar_saldo()


@receiver(post_delete, sender=Payment)
def payment_deleted(sender, instance, **kwargs):
    """
    Cuando se elimina un pago, recalcula el saldo de la factura
    """
    if instance.invoice_id:
        instance.invoice.actualizar_saldo()


@receiver(post_save, sender=InvoiceItem)
def invoice_item_saved(sender, instance, created, **kwargs):
    """
    Cuando se guarda un item, recalcula totales de la factura.
    Ya se maneja en InvoiceItem.save() pero por si acaso.
    """
    if instance.invoice_id:
        instance.invoice.calcular_totales()


@receiver(post_delete, sender=InvoiceItem)
def invoice_item_deleted(sender, instance, **kwargs):
    """
    Cuando se elimina un item, recalcula totales de la factura
    """
    if instance.invoice_id:
        instance.invoice.calcular_totales()
