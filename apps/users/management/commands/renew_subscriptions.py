"""
Comando para renovar automáticamente las suscripciones que están próximas a vencer
Se debe ejecutar diariamente mediante un cron job o tarea programada
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction as db_transaction
from datetime import timedelta
from decimal import Decimal
import uuid

from apps.users.models import (
    UserSubscription,
    PaymentMethod,
    Transaction,
    SubscriptionRenewalLog
)
from apps.users.wompi_service import wompi_service
from apps.users.payment_views import send_subscription_renewal_failed_email


class Command(BaseCommand):
    help = 'Renueva automáticamente las suscripciones que están próximas a vencer'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-before',
            type=int,
            default=3,
            help='Días antes del vencimiento para intentar renovar (default: 3)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la ejecución sin realizar cambios'
        )

    def handle(self, *args, **options):
        days_before = options['days_before']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS(
            f'\n{"="*60}\n'
            f'Iniciando proceso de renovación automática de suscripciones\n'
            f'Días antes del vencimiento: {days_before}\n'
            f'Modo: {"DRY RUN (simulación)" if dry_run else "PRODUCCIÓN"}\n'
            f'{"="*60}\n'
        ))
        
        # Obtener suscripciones que necesitan renovación
        renewal_date = timezone.now() + timedelta(days=days_before)
        
        subscriptions_to_renew = UserSubscription.objects.filter(
            is_active=True,
            auto_renew=True,
            end_date__lte=renewal_date,
            end_date__gt=timezone.now()
        ).select_related('user', 'plan')
        
        self.stdout.write(f'\nSuscripciones encontradas: {subscriptions_to_renew.count()}\n')
        
        stats = {
            'total': subscriptions_to_renew.count(),
            'success': 0,
            'failed': 0,
            'skipped': 0,
        }
        
        for subscription in subscriptions_to_renew:
            result = self.process_subscription_renewal(subscription, dry_run)
            stats[result] += 1
        
        # Mostrar resumen
        self.stdout.write(self.style.SUCCESS(
            f'\n{"="*60}\n'
            f'Resumen de renovaciones:\n'
            f'  Total procesadas: {stats["total"]}\n'
            f'  Exitosas: {stats["success"]}\n'
            f'  Fallidas: {stats["failed"]}\n'
            f'  Omitidas: {stats["skipped"]}\n'
            f'{"="*60}\n'
        ))

    def process_subscription_renewal(self, subscription, dry_run=False):
        """
        Procesa la renovación de una suscripción individual
        
        Returns:
            str: 'success', 'failed', o 'skipped'
        """
        user = subscription.user
        
        self.stdout.write(f'\nProcesando: {user.username} - {subscription.plan.name}')
        
        # Verificar si tiene método de pago predeterminado
        payment_method = PaymentMethod.objects.filter(
            user=user,
            is_active=True,
            is_default=True
        ).first()
        
        if not payment_method:
            self.stdout.write(self.style.WARNING(
                f'  ⚠ Usuario sin método de pago predeterminado'
            ))
            
            if not dry_run:
                self._log_renewal_attempt(
                    subscription,
                    status='skipped',
                    error='No hay método de pago predeterminado'
                )
                send_subscription_renewal_failed_email(
                    subscription,
                    'No tienes un método de pago predeterminado configurado.'
                )
            
            return 'skipped'
        
        # Calcular monto a cobrar
        if subscription.billing_cycle == 'yearly':
            amount = subscription.plan.price_yearly
        else:
            amount = subscription.plan.price_monthly
        
        amount_in_cents = int(amount * 100)
        
        self.stdout.write(f'  Monto a cobrar: ${amount:,.2f} COP')
        
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'  [DRY RUN] Se cobraría con tarjeta: {payment_method.card_brand} ****{payment_method.card_last_four}'
            ))
            return 'success'
        
        # Generar referencia única
        reference = f"RENEWAL-{user.id}-{subscription.id}-{uuid.uuid4().hex[:8]}"
        
        # Crear transacción
        try:
            with db_transaction.atomic():
                success, transaction, error = wompi_service.create_transaction(
                    amount_in_cents=amount_in_cents,
                    currency='COP',
                    customer_email=user.email,
                    payment_method_id=payment_method.id,
                    reference=reference,
                    subscription_id=subscription.id
                )
                
                if success:
                    # Extender la fecha de vencimiento
                    if subscription.billing_cycle == 'yearly':
                        subscription.end_date = subscription.end_date + timedelta(days=365)
                    else:
                        subscription.end_date = subscription.end_date + timedelta(days=30)
                    
                    subscription.payment_status = 'paid'
                    subscription.amount_paid = amount
                    subscription.save()
                    
                    # Marcar transacción como aprobada
                    transaction.mark_as_approved()
                    
                    # Log del intento exitoso
                    renewal_log = self._log_renewal_attempt(
                        subscription,
                        transaction=transaction,
                        status='success',
                        amount=amount
                    )
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ Renovación exitosa. Nueva fecha de vencimiento: {subscription.end_date.strftime("%Y-%m-%d")}'
                    ))
                    
                    return 'success'
                else:
                    # Log del intento fallido
                    self._log_renewal_attempt(
                        subscription,
                        transaction=transaction,
                        status='failed',
                        error=error,
                        amount=amount
                    )
                    
                    # Enviar email de notificación
                    send_subscription_renewal_failed_email(subscription, error)
                    
                    self.stdout.write(self.style.ERROR(
                        f'  ✗ Error al procesar pago: {error}'
                    ))
                    
                    return 'failed'
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'  ✗ Excepción: {str(e)}'
            ))
            
            self._log_renewal_attempt(
                subscription,
                status='failed',
                error=str(e),
                amount=amount
            )
            
            send_subscription_renewal_failed_email(subscription, str(e))
            
            return 'failed'
    
    def _log_renewal_attempt(
        self,
        subscription,
        transaction=None,
        status='pending',
        error='',
        amount=None
    ):
        """Registra un intento de renovación en el log"""
        if amount is None:
            if subscription.billing_cycle == 'yearly':
                amount = subscription.plan.price_yearly
            else:
                amount = subscription.plan.price_monthly
        
        renewal_log = SubscriptionRenewalLog.objects.create(
            subscription=subscription,
            transaction=transaction,
            status=status,
            amount_attempted=amount,
            error_message=error,
            email_sent=bool(error),  # Si hay error, se envía email
        )
        
        if status in ['success', 'failed']:
            renewal_log.completed_at = timezone.now()
            renewal_log.save()
        
        return renewal_log
