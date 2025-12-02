"""
Script para configurar los planes de suscripción iniciales del sistema SaaS
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import SubscriptionPlan


def create_subscription_plans():
    """Crea los planes de suscripción por defecto"""
    
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
            print(f"✓ Creado: {plan.name}")
        else:
            updated_count += 1
            print(f"↻ Actualizado: {plan.name}")
    
    print(f"\n✓ Proceso completado:")
    print(f"  - {created_count} planes creados")
    print(f"  - {updated_count} planes actualizados")


if __name__ == '__main__':
    print("=" * 60)
    print("CONFIGURACIÓN DE PLANES DE SUSCRIPCIÓN")
    print("=" * 60)
    
    create_subscription_plans()
    
    print("\n" + "=" * 60)
    print("¡Configuración completada!")
    print("=" * 60)
