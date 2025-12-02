"""
Script para verificar y crear organización por defecto
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization, SubscriptionPlan, Subscription
from datetime import datetime, timedelta

def setup_default_organization():
    """Crear organización por defecto si no existe"""
    
    # Verificar si existe alguna organización
    org_count = Organization.objects.count()
    print(f"Organizaciones existentes: {org_count}")
    
    if org_count == 0:
        print("\n❌ No hay organizaciones. Creando organización por defecto...")
        
        # Crear organización
        org = Organization.objects.create(
            name="Óptica Principal",
            subdomain="optica",
            email="admin@optica.com",
            phone="+57 300 123 4567",
            address="Calle Principal #123",
            is_active=True
        )
        print(f"✅ Organización creada: {org.name}")
        
        # Obtener plan Free
        free_plan = SubscriptionPlan.objects.filter(name="Free").first()
        if free_plan:
            # Crear suscripción
            subscription = Subscription.objects.create(
                organization=org,
                plan=free_plan,
                status='active',
                start_date=datetime.now().date(),
                end_date=(datetime.now() + timedelta(days=365)).date()
            )
            print(f"✅ Suscripción creada: {subscription.plan.name}")
        else:
            print("⚠️ No se encontró plan Free. Ejecuta: python manage.py setup_plans")
    else:
        print("\n✅ Ya existen organizaciones:")
        for org in Organization.objects.all():
            print(f"  - {org.name} (ID: {org.id}, Activa: {org.is_active})")
            
            # Verificar suscripción
            subscription = Subscription.objects.filter(organization=org).first()
            if subscription:
                print(f"    Suscripción: {subscription.plan.name} - {subscription.status}")
            else:
                print("    ⚠️ Sin suscripción activa")

if __name__ == '__main__':
    setup_default_organization()
