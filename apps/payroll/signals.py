"""
Signals para el módulo de nómina
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Accrual, Deduction, PayrollEntry


@receiver(post_save, sender=Accrual)
@receiver(post_delete, sender=Accrual)
@receiver(post_save, sender=Deduction)
@receiver(post_delete, sender=Deduction)
def update_payroll_entry_totals(sender, instance, **kwargs):
    """
    Actualiza los totales de la entrada de nómina cuando se crea, 
    actualiza o elimina un devengado o deducción
    """
    if isinstance(instance, (Accrual, Deduction)):
        instance.entrada.calculate_totals()
