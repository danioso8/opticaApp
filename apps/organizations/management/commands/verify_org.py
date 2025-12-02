from django.core.management.base import BaseCommand
from apps.organizations.models import Organization, SubscriptionPlan, Subscription
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Verificar y crear organización por defecto'

    def handle(self, *args, **options):
        """Verificar organizaciones existentes"""
        
        org_count = Organization.objects.count()
        self.stdout.write(f"\n{'='*50}")
        self.stdout.write(f"Organizaciones existentes: {org_count}")
        self.stdout.write(f"{'='*50}\n")
        
        if org_count == 0:
            self.stdout.write(self.style.ERROR("❌ No hay organizaciones"))
            self.stdout.write("\nCreando organización por defecto...")
            
            # Crear organización
            org = Organization.objects.create(
                name="Óptica Principal",
                subdomain="optica",
                email="admin@optica.com",
                phone="+57 300 123 4567",
                address="Calle Principal #123",
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Organización creada: {org.name}"))
            
            # Obtener plan Free
            free_plan = SubscriptionPlan.objects.filter(name="Free").first()
            if free_plan:
                subscription = Subscription.objects.create(
                    organization=org,
                    plan=free_plan,
                    status='active',
                    start_date=datetime.now().date(),
                    end_date=(datetime.now() + timedelta(days=365)).date()
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Suscripción creada: {subscription.plan.name}"))
            else:
                self.stdout.write(self.style.WARNING("⚠️ No se encontró plan Free"))
                self.stdout.write("Ejecuta: python manage.py setup_plans")
        else:
            self.stdout.write(self.style.SUCCESS("✅ Organizaciones encontradas:\n"))
            for org in Organization.objects.all():
                self.stdout.write(f"  ID: {org.id}")
                self.stdout.write(f"  Nombre: {org.name}")
                self.stdout.write(f"  Subdominio: {org.subdomain}")
                self.stdout.write(f"  Email: {org.email}")
                self.stdout.write(f"  Activa: {org.is_active}")
                
                # Verificar suscripción
                subscription = Subscription.objects.filter(organization=org).first()
                if subscription:
                    self.stdout.write(f"  Suscripción: {subscription.plan.name} ({subscription.status})")
                else:
                    self.stdout.write(self.style.WARNING("  ⚠️ Sin suscripción activa"))
                
                self.stdout.write("-" * 50)
        
        self.stdout.write("\n" + "="*50)
