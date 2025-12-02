"""
Crear plan básico para permitir registros
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import SubscriptionPlan

# Verificar si ya existen planes
existing = SubscriptionPlan.objects.count()
print(f"Planes existentes: {existing}")

if existing == 0:
    print("\n✨ Creando planes de suscripción...\n")
    
    # Plan Gratuito
    free_plan = SubscriptionPlan.objects.create(
        name="Plan Gratuito",
        slug="plan-gratuito",
        plan_type="free",
        price_monthly=0.00,
        price_yearly=0.00,
        max_users=1,
        max_patients=50,
        max_appointments_month=30,
        whatsapp_integration=False,
        email_notifications=True,
        custom_branding=False,
        analytics=False,
        is_active=True
    )
    print(f"✅ {free_plan.name} creado")
    
    # Plan Básico
    basic_plan = SubscriptionPlan.objects.create(
        name="Plan Básico",
        slug="plan-basico",
        plan_type="basic",
        price_monthly=29.99,
        price_yearly=299.99,
        max_users=3,
        max_patients=200,
        max_appointments_month=100,
        whatsapp_integration=True,
        email_notifications=True,
        custom_branding=False,
        analytics=False,
        is_active=True
    )
    print(f"✅ {basic_plan.name} creado")
    
    # Plan Profesional
    pro_plan = SubscriptionPlan.objects.create(
        name="Plan Profesional",
        slug="plan-profesional",
        plan_type="professional",
        price_monthly=59.99,
        price_yearly=599.99,
        max_users=10,
        max_patients=1000,
        max_appointments_month=500,
        whatsapp_integration=True,
        email_notifications=True,
        custom_branding=True,
        analytics=True,
        is_active=True
    )
    print(f"✅ {pro_plan.name} creado")
    
    # Plan Empresarial
    enterprise_plan = SubscriptionPlan.objects.create(
        name="Plan Empresarial",
        slug="plan-empresarial",
        plan_type="enterprise",
        price_monthly=99.99,
        price_yearly=999.99,
        max_users=999999,
        max_patients=999999,
        max_appointments_month=999999,
        whatsapp_integration=True,
        email_notifications=True,
        custom_branding=True,
        analytics=True,
        is_active=True
    )
    print(f"✅ {enterprise_plan.name} creado")
    
    print(f"\n✅ Total de planes creados: {SubscriptionPlan.objects.count()}")
else:
    print("\nℹ️  Ya existen planes de suscripción:")
    for plan in SubscriptionPlan.objects.all():
        print(f"  • {plan.name} - ${plan.price_monthly}/mes")

print("\n🎉 ¡Listo! Ahora puedes registrar usuarios en:")
print("   http://127.0.0.1:8000/organizations/register/\n")
