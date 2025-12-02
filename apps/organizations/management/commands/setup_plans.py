from django.core.management.base import BaseCommand
from apps.organizations.models import SubscriptionPlan


class Command(BaseCommand):
    help = 'Configura los planes de suscripción iniciales'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Configurando planes de suscripción...'))
        
        plans = [
            {
                'name': 'Plan Gratuito',
                'slug': 'free',
                'plan_type': 'free',
                'price_monthly': 0,
                'price_yearly': 0,
                'max_users': 1,
                'max_appointments_month': 50,
                'max_patients': 100,
                'max_storage_mb': 100,
                'whatsapp_integration': False,
                'custom_branding': False,
                'api_access': False,
                'priority_support': False,
                'analytics': False,
                'multi_location': False,
            },
            {
                'name': 'Plan Básico',
                'slug': 'basic',
                'plan_type': 'basic',
                'price_monthly': 29.99,
                'price_yearly': 299.99,
                'max_users': 3,
                'max_appointments_month': 200,
                'max_patients': 500,
                'max_storage_mb': 500,
                'whatsapp_integration': True,
                'custom_branding': False,
                'api_access': False,
                'priority_support': False,
                'analytics': True,
                'multi_location': False,
            },
            {
                'name': 'Plan Profesional',
                'slug': 'professional',
                'plan_type': 'professional',
                'price_monthly': 79.99,
                'price_yearly': 799.99,
                'max_users': 10,
                'max_appointments_month': 1000,
                'max_patients': 2000,
                'max_storage_mb': 2048,
                'whatsapp_integration': True,
                'custom_branding': True,
                'api_access': True,
                'priority_support': True,
                'analytics': True,
                'multi_location': True,
            },
            {
                'name': 'Plan Empresarial',
                'slug': 'enterprise',
                'plan_type': 'enterprise',
                'price_monthly': 149.99,
                'price_yearly': 1499.99,
                'max_users': 999,
                'max_appointments_month': 9999,
                'max_patients': 10000,
                'max_storage_mb': 10240,
                'whatsapp_integration': True,
                'custom_branding': True,
                'api_access': True,
                'priority_support': True,
                'analytics': True,
                'multi_location': True,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.update_or_create(
                slug=plan_data['slug'],
                defaults=plan_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Creado: {plan.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Actualizado: {plan.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ {created_count} planes creados'))
        self.stdout.write(self.style.SUCCESS(f'✓ {updated_count} planes actualizados'))
