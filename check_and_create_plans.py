"""
Script para verificar y crear planes de suscripción si no existen
Ejecutar en Render Shell: python check_and_create_plans.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import SubscriptionPlan


def check_and_create_plans():
    """Verifica y crea los planes de suscripción si no existen"""
    
    print("=" * 60)
    print("VERIFICANDO PLANES DE SUSCRIPCIÓN")
    print("=" * 60)
    
    # Verificar planes existentes
    existing_plans = SubscriptionPlan.objects.all()
    print(f"\n📊 Planes existentes en la base de datos: {existing_plans.count()}")
    
    for plan in existing_plans:
        print(f"  • {plan.name} ({plan.plan_type}) - ${plan.price_monthly}/mes")
    
    # Verificar si existe plan empresarial
    enterprise_plan = SubscriptionPlan.objects.filter(plan_type__iexact='enterprise').first()
    
    if enterprise_plan:
        print(f"\n✅ Plan Empresarial encontrado: {enterprise_plan.name}")
    else:
        print("\n⚠️  No se encontró plan empresarial (plan_type='enterprise')")
        
        # Buscar por nombre
        by_name = SubscriptionPlan.objects.filter(name__icontains='empresarial').first()
        if by_name:
            print(f"   Pero encontré uno por nombre: {by_name.name} (tipo: {by_name.plan_type})")
    
    print("\n" + "=" * 60)
    print("CREANDO/ACTUALIZANDO PLANES")
    print("=" * 60)
    
    plans = [
        {
            'name': 'Plan Free',
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
            'price_monthly': 8000.00,
            'price_yearly': 80000.00,
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
            'price_monthly': 50000.00,
            'price_yearly': 500000.00,
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
            'price_monthly': 5000.00,
            'price_yearly': 50000.00,
            'max_users': 999,
            'max_appointments_month': 99999,
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
            print(f"✅ Creado: {plan.name} (${plan.price_monthly}/mes)")
        else:
            updated_count += 1
            print(f"🔄 Actualizado: {plan.name} (${plan.price_monthly}/mes)")
    
    print("\n" + "=" * 60)
    print(f"✅ Proceso completado")
    print(f"   • {created_count} planes creados")
    print(f"   • {updated_count} planes actualizados")
    print("=" * 60)
    
    # Verificar nuevamente plan empresarial
    print("\n🔍 Verificación final:")
    enterprise_plan = SubscriptionPlan.objects.filter(plan_type='enterprise').first()
    if enterprise_plan:
        print(f"✅ Plan Empresarial confirmado: {enterprise_plan.name}")
        print(f"   - Slug: {enterprise_plan.slug}")
        print(f"   - Plan Type: {enterprise_plan.plan_type}")
        print(f"   - Precio: ${enterprise_plan.price_monthly}/mes")
    else:
        print("❌ ERROR: No se pudo crear el plan empresarial")


if __name__ == '__main__':
    check_and_create_plans()
