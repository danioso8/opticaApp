"""
Script para crear planes de suscripción en desarrollo
Ejecutar: python create_subscription_plans_dev.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import SubscriptionPlan

print("\n" + "="*60)
print("CREANDO PLANES DE SUSCRIPCIÓN")
print("="*60 + "\n")

# Plan Gratis
free_plan, created = SubscriptionPlan.objects.get_or_create(
    slug='gratis',
    defaults={
        'name': 'Gratis',
        'plan_type': 'free',
        'price_monthly': 0.00,
        'price_yearly': 0.00,
        'max_users': 1,
        'max_organizations': 1,
        'max_appointments_month': 10,
        'max_patients': 25,
        'max_storage_mb': 50,
        'whatsapp_messages_included': 50,
        'whatsapp_overage_price': 0.025,
        'whatsapp_integration': False,
        'custom_branding': False,
        'api_access': False,
        'priority_support': False,
        'analytics': False,
        'multi_location': False,
        'allow_electronic_invoicing': False,
        'max_invoices_month': 0,
        'ideal_for': 'Ópticas pequeñas o profesionales independientes empezando',
        'coverage_description': 'Plan de inicio para probar la plataforma',
    }
)
if created:
    print("✅ Plan 'Gratis' creado")
else:
    print("ℹ️  Plan 'Gratis' ya existe - actualizado")
    free_plan.whatsapp_messages_included = 50
    free_plan.whatsapp_overage_price = 0.025
    free_plan.save()

# Plan Básico
basic_plan, created = SubscriptionPlan.objects.get_or_create(
    slug='basico',
    defaults={
        'name': 'Básico',
        'plan_type': 'basic',
        'price_monthly': 29.99,
        'price_yearly': 299.00,
        'max_users': 3,
        'max_organizations': 1,
        'max_appointments_month': 100,
        'max_patients': 200,
        'max_storage_mb': 500,
        'whatsapp_messages_included': 100,
        'whatsapp_overage_price': 0.020,
        'whatsapp_integration': True,
        'custom_branding': True,
        'api_access': False,
        'priority_support': False,
        'analytics': True,
        'multi_location': False,
        'allow_electronic_invoicing': False,
        'max_invoices_month': 0,
        'ideal_for': 'Ópticas pequeñas con 2-3 empleados',
        'coverage_description': 'Perfecto para ópticas en crecimiento',
        'plan_badge': 'MÁS POPULAR',
    }
)
if created:
    print("✅ Plan 'Básico' creado")
else:
    print("ℹ️  Plan 'Básico' ya existe - actualizado")
    basic_plan.whatsapp_messages_included = 100
    basic_plan.whatsapp_overage_price = 0.020
    basic_plan.save()

# Plan Profesional
professional_plan, created = SubscriptionPlan.objects.get_or_create(
    slug='profesional',
    defaults={
        'name': 'Profesional',
        'plan_type': 'professional',
        'price_monthly': 79.99,
        'price_yearly': 799.00,
        'max_users': 10,
        'max_organizations': 3,
        'max_appointments_month': 500,
        'max_patients': 1000,
        'max_storage_mb': 2000,
        'whatsapp_messages_included': 500,
        'whatsapp_overage_price': 0.015,
        'whatsapp_integration': True,
        'custom_branding': True,
        'api_access': True,
        'priority_support': True,
        'analytics': True,
        'multi_location': True,
        'allow_electronic_invoicing': True,
        'max_invoices_month': 200,
        'ideal_for': 'Ópticas medianas con múltiples sucursales',
        'coverage_description': 'Solución completa para ópticas en expansión',
        'plan_badge': 'RECOMENDADO',
    }
)
if created:
    print("✅ Plan 'Profesional' creado")
else:
    print("ℹ️  Plan 'Profesional' ya existe - actualizado")
    professional_plan.whatsapp_messages_included = 500
    professional_plan.whatsapp_overage_price = 0.015
    professional_plan.save()

# Plan Empresarial
enterprise_plan, created = SubscriptionPlan.objects.get_or_create(
    slug='empresarial',
    defaults={
        'name': 'Empresarial',
        'plan_type': 'enterprise',
        'price_monthly': 199.99,
        'price_yearly': 1999.00,
        'max_users': 0,  # Ilimitado
        'max_organizations': 10,
        'max_appointments_month': 0,  # Ilimitado
        'max_patients': 0,  # Ilimitado
        'max_storage_mb': 0,  # Ilimitado
        'whatsapp_messages_included': 2000,
        'whatsapp_overage_price': 0.010,
        'whatsapp_integration': True,
        'custom_branding': True,
        'api_access': True,
        'priority_support': True,
        'analytics': True,
        'multi_location': True,
        'allow_electronic_invoicing': True,
        'max_invoices_month': 0,  # Ilimitado
        'ideal_for': 'Cadenas de ópticas y grandes empresas',
        'coverage_description': 'Solución empresarial completa sin límites',
        'plan_badge': 'MEJOR VALOR',
    }
)
if created:
    print("✅ Plan 'Empresarial' creado")
else:
    print("ℹ️  Plan 'Empresarial' ya existe - actualizado")
    enterprise_plan.whatsapp_messages_included = 2000
    enterprise_plan.whatsapp_overage_price = 0.010
    enterprise_plan.save()

print("\n" + "="*60)
print("RESUMEN DE PLANES CREADOS")
print("="*60)

plans = SubscriptionPlan.objects.all().order_by('price_monthly')
for plan in plans:
    print(f"\n📦 {plan.name}")
    print(f"   Precio: ${plan.price_monthly}/mes (${plan.price_yearly}/año)")
    print(f"   WhatsApp: {plan.whatsapp_messages_included} msgs incluidos")
    print(f"   Exceso WhatsApp: ${plan.whatsapp_overage_price} por mensaje")
    print(f"   Citas/mes: {'Ilimitado' if plan.max_appointments_month == 0 else plan.max_appointments_month}")
    print(f"   Pacientes: {'Ilimitado' if plan.max_patients == 0 else plan.max_patients}")
    print(f"   Usuarios: {'Ilimitado' if plan.max_users == 0 else plan.max_users}")
    print(f"   Badge: {plan.plan_badge if plan.plan_badge else 'N/A'}")

print("\n" + "="*60)
print("✅ PLANES LISTOS PARA USAR")
print("="*60 + "\n")
