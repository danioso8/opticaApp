"""
Comando para enviar notificaciones a usuarios cuyas suscripciones están próximas a renovarse
Se debe ejecutar diariamente mediante un cron job o tarea programada
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta, datetime

from apps.users.models import UserSubscription, PaymentMethod


class Command(BaseCommand):
    help = 'Envía recordatorios a usuarios cuyas suscripciones están próximas a renovarse'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-before',
            type=int,
            default=7,
            help='Días antes de la renovación para enviar el recordatorio (default: 7)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula el envío sin mandar emails reales'
        )

    def handle(self, *args, **options):
        days_before = options['days_before']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS(
            f'\n{"="*70}\n'
            f'Enviando recordatorios de renovación de suscripciones\n'
            f'Días antes de renovación: {days_before}\n'
            f'Modo: {"DRY RUN (simulación)" if dry_run else "PRODUCCIÓN"}\n'
            f'{"="*70}\n'
        ))
        
        # Fecha objetivo: suscripciones que vencen en X días
        target_date = timezone.now() + timedelta(days=days_before)
        next_day = target_date + timedelta(days=1)
        
        # Buscar suscripciones que vencen exactamente en X días
        subscriptions_to_notify = UserSubscription.objects.filter(
            is_active=True,
            auto_renew=True,
            end_date__gte=target_date,
            end_date__lt=next_day
        ).select_related('user', 'plan')
        
        self.stdout.write(f'\nSuscripciones encontradas: {subscriptions_to_notify.count()}\n')
        
        stats = {
            'total': subscriptions_to_notify.count(),
            'sent': 0,
            'skipped': 0,
            'error': 0,
        }
        
        for subscription in subscriptions_to_notify:
            result = self.send_renewal_reminder(subscription, days_before, dry_run)
            stats[result] += 1
        
        # Mostrar resumen
        self.stdout.write(self.style.SUCCESS(
            f'\n{"="*70}\n'
            f'Resumen de recordatorios:\n'
            f'  Total procesadas: {stats["total"]}\n'
            f'  Emails enviados: {stats["sent"]}\n'
            f'  Omitidas: {stats["skipped"]}\n'
            f'  Errores: {stats["error"]}\n'
            f'{"="*70}\n'
        ))

    def send_renewal_reminder(self, subscription, days_before, dry_run=False):
        """
        Envía email recordatorio de renovación próxima
        
        Returns:
            str: 'sent', 'skipped', o 'error'
        """
        user = subscription.user
        
        self.stdout.write(f'\nProcesando: {user.username} - {subscription.plan.name}')
        
        # Verificar si tiene método de pago
        payment_method = PaymentMethod.objects.filter(
            user=user,
            is_active=True,
            is_default=True
        ).first()
        
        # Calcular monto de renovación
        if subscription.billing_cycle == 'yearly':
            renewal_amount = subscription.plan.price_yearly
        else:
            renewal_amount = subscription.plan.price_monthly
        
        # Preparar contexto del email
        context = {
            'user': user,
            'subscription': subscription,
            'plan': subscription.plan,
            'renewal_date': subscription.end_date,
            'days_until_renewal': days_before,
            'renewal_amount': renewal_amount,
            'renewal_amount_cop': renewal_amount * 4000,  # Conversión aproximada USD -> COP
            'billing_cycle': subscription.get_billing_cycle_display(),
            'has_payment_method': payment_method is not None,
            'payment_method': payment_method,
            'auto_renew_enabled': subscription.auto_renew,
            'current_year': datetime.now().year,
            'manage_url': f"{settings.SITE_URL}/users/subscription/manage/",
        }
        
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'  [DRY RUN] Se enviaría email a: {user.email}'
            ))
            self.stdout.write(f'  Plan: {subscription.plan.name}')
            self.stdout.write(f'  Vence en: {days_before} días')
            self.stdout.write(f'  Monto: ${renewal_amount:,.2f} USD')
            self.stdout.write(f'  Método de pago: {"Sí" if payment_method else "NO"} ⚠️')
            return 'sent'
        
        try:
            # Determinar tipo de email según tenga o no método de pago
            if payment_method:
                subject = f'Tu suscripción se renovará en {days_before} días'
                template = 'users/emails/renewal_reminder.html'
            else:
                subject = f'⚠️ Acción requerida: Tu suscripción vence en {days_before} días'
                template = 'users/emails/renewal_reminder_no_payment.html'
            
            # Renderizar email
            html_message = render_to_string(template, context)
            
            # Enviar email
            send_mail(
                subject=subject,
                message='',  # Texto plano vacío, usamos HTML
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS(
                f'  ✓ Email enviado a {user.email}'
            ))
            
            return 'sent'
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'  ✗ Error al enviar email: {str(e)}'
            ))
            return 'error'
