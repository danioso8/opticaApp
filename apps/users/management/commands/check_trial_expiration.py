"""
Comando para verificar y notificar trials que están por vencer
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta

from apps.users.models import UserSubscription


class Command(BaseCommand):
    help = 'Verifica trials que están por vencer y envía notificaciones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Notificar usuarios cuyo trial vence en N días (por defecto: 7)',
        )
        parser.add_argument(
            '--send-emails',
            action='store_true',
            help='Enviar emails de notificación',
        )

    def handle(self, *args, **options):
        days_before = options['days']
        send_emails = options['send_emails']
        
        self.stdout.write(self.style.SUCCESS(f'\n🔔 Verificando trials que vencen en {days_before} días...\n'))
        
        # Buscar suscripciones en trial que vencen pronto
        target_date = timezone.now() + timedelta(days=days_before)
        
        trials_expiring = UserSubscription.objects.filter(
            is_trial=True,
            trial_ends_at__lte=target_date,
            trial_ends_at__gte=timezone.now(),
            payment_status='paid',  # Aún no han pagado
        ).select_related('user', 'plan')
        
        total = trials_expiring.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING(f'No hay trials que venzan en {days_before} días'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'📊 Usuarios encontrados: {total}\n'))
        self.stdout.write('-' * 80)
        
        for subscription in trials_expiring:
            days_left = subscription.trial_days_remaining
            user = subscription.user
            plan = subscription.plan
            
            self.stdout.write(
                f'👤 {user.username:<20} | '
                f'📧 {user.email:<30} | '
                f'⏰ {days_left} días restantes'
            )
            
            # Enviar email si está habilitado
            if send_emails:
                try:
                    self.send_trial_expiring_email(subscription, days_left)
                    self.stdout.write(self.style.SUCCESS('   ✅ Email enviado'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'   ❌ Error al enviar email: {str(e)}'))
        
        self.stdout.write('-' * 80)
        self.stdout.write(self.style.SUCCESS(f'\n✅ Proceso completado. Total procesados: {total}\n'))

    def send_trial_expiring_email(self, subscription, days_left):
        """Envía email de notificación de trial por vencer"""
        user = subscription.user
        plan = subscription.plan
        
        subject = f'Tu período de prueba vence en {days_left} días'
        
        message = f"""
Hola {user.get_full_name() or user.username},

Tu período de prueba gratuito de OpticaApp está por terminar.

📅 Días restantes: {days_left}
📆 Fecha de vencimiento: {subscription.trial_ends_at.strftime('%d/%m/%Y')}

💰 Para continuar disfrutando de OpticaApp después del período de prueba:
   - Precio: ${plan.price_monthly} USD/mes
   - Pago seguro con Wompi

✨ Al continuar tendrás acceso a:
   • Gestión ilimitada de pacientes
   • Agendamiento de citas
   • Historia clínica completa
   • Landing page personalizada
   • Y mucho más...

👉 Actualiza tu suscripción aquí:
   {settings.WEBSITE_URL}/users/subscription/trial-expired/

Si tienes alguna pregunta, no dudes en contactarnos.

Saludos,
El equipo de OpticaApp
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
