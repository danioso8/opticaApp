"""
Script para crear organización por defecto antes de las migraciones
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import Organization, SubscriptionPlan, Subscription

def create_default_organization():
    """Crea una organización por defecto para migración de datos"""
    
    # Obtener o crear el primer usuario como owner
    user = User.objects.first()
    if not user:
        print("⚠️  No hay usuarios en el sistema. Creando usuario admin...")
        user = User.objects.create_superuser(
            username='admin',
            email='admin@opticaapp.com',
            password='admin123'
        )
        print(f"✓ Usuario admin creado (password: admin123)")
    
    # Crear organización por defecto
    org, created = Organization.objects.get_or_create(
        slug='default-organization',
        defaults={
            'name': 'Organización Principal',
            'email': user.email,
            'owner': user
        }
    )
    
    if created:
        print(f"✓ Organización creada: {org.name} (ID: {org.id})")
        
        # Crear plan gratuito si no existe
        free_plan, _ = SubscriptionPlan.objects.get_or_create(
            slug='free',
            defaults={
                'name': 'Plan Gratuito',
                'plan_type': 'free',
                'price_monthly': 0,
                'price_yearly': 0,
                'max_users': 1,
                'max_appointments_month': 50,
                'max_patients': 100,
                'max_storage_mb': 100,
            }
        )
        
        # Crear suscripción
        Subscription.objects.create(
            organization=org,
            plan=free_plan,
            billing_cycle='monthly',
            payment_status='paid'
        )
        print(f"✓ Suscripción creada con {free_plan.name}")
    else:
        print(f"↻ Organización ya existe: {org.name} (ID: {org.id})")
    
    print(f"\n📝 Usa este ID en las migraciones: {org.id}")
    return org.id

if __name__ == '__main__':
    print("=" * 60)
    print("CREANDO ORGANIZACIÓN POR DEFECTO")
    print("=" * 60)
    org_id = create_default_organization()
    print("=" * 60)
