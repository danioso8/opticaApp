#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear señales (signals) que se ejecutan automáticamente
Ejecutar: python manage.py shell < create_signals.py
"""

print("=" * 80)
print("📝 CREANDO ARCHIVO DE SEÑALES")
print("=" * 80)

signals_content = '''# -*- coding: utf-8 -*-
"""
Señales para el sistema de trials y módulos
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.organizations.models import Organization, OrganizationModule, TrialStatus
from apps.organizations.tasks import send_welcome_email_after_registration
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Organization)
def create_trial_on_organization_created(sender, instance, created, **kwargs):
    """
    Cuando se crea una organización nueva, crear su TrialStatus
    y enviar email de bienvenida
    """
    if created:
        # Crear TrialStatus
        trial, trial_created = TrialStatus.objects.get_or_create(
            organization=instance,
            defaults={
                'state': 'active',
            }
        )
        
        if trial_created:
            logger.info(f"✅ Trial creado para {instance.name}")
            
            # Enviar bienvenida (async con Celery)
            send_welcome_email_after_registration.delay(instance.id)
        

@receiver(post_save, sender=OrganizationModule)
def log_module_purchase(sender, instance, created, **kwargs):
    """
    Cuando se compra un módulo, crear notificación
    """
    if created:
        from apps.organizations.models import SubscriptionNotification
        
        SubscriptionNotification.objects.create(
            organization=instance.organization,
            notification_type='module_added',
            channel='in_app',
            message=f'Módulo "{instance.module.name}" agregado a tu plan',
            delivered=True,
        )
        
        logger.info(f"📦 Módulo {instance.module.name} comprado por {instance.organization.name}")
'''

# Escribir archivo
with open('/var/www/opticaapp/apps/organizations/signals.py', 'w', encoding='utf-8') as f:
    f.write(signals_content)

print("✅ Archivo signals.py creado")
print("=" * 80)
