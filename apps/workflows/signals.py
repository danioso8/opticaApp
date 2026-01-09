"""
Signals para workflows
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.workflows.models import WorkflowInstance, WorkflowApproval


@receiver(post_save, sender=WorkflowInstance)
def workflow_instance_post_save(sender, instance, created, **kwargs):
    """Signal después de crear/actualizar instancia de workflow"""
    if created:
        print(f"Nueva instancia de workflow creada: {instance}")


@receiver(post_save, sender=WorkflowApproval)
def workflow_approval_post_save(sender, instance, created, **kwargs):
    """Signal después de crear/actualizar aprobación"""
    if created:
        print(f"Nueva solicitud de aprobación: {instance}")
