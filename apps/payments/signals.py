# -*- coding: utf-8 -*-
"""
Señales para el módulo de pagos
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.payments.models import Transaction, Invoice


@receiver(post_save, sender=Transaction)
def handle_transaction_completed(sender, instance, **kwargs):
    """
    Cuando una transacción se completa, crear factura si no existe
    """
    if instance.status == 'completed' and not instance.invoice:
        from datetime import timedelta
        from django.utils import timezone
        from apps.payments.models import InvoiceItem
        
        # Crear factura
        today = timezone.now().date()
        
        invoice = Invoice.objects.create(
            organization=instance.organization,
            status='paid',
            subtotal=instance.amount,
            total=instance.amount,
            currency=instance.currency,
            billing_period_start=today,
            billing_period_end=today + timedelta(days=30),
            due_date=today,
            paid_at=instance.completed_at,
        )
        
        # Agregar items de la factura
        for module in instance.modules.all():
            InvoiceItem.objects.create(
                invoice=invoice,
                module=module,
                description=module.name,
                quantity=1,
                unit_price=module.price_monthly,
                total_price=module.price_monthly,
            )
        
        # Asociar factura a transacción
        instance.invoice = invoice
        instance.save(update_fields=['invoice'])
