"""
Script para configurar Render: Migraciones + Superuser + Planes
Ejecutar en Shell de Render: python setup_render_superuser.py
"""
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import SubscriptionPlan, Organization

User = get_user_model()

print("\n" + "="*60)
print("🚀 CONFIGURACIÓN INICIAL DE RENDER")
print("="*60 + "\n")

# 1. Crear Superuser
print("👤 PASO 1: Crear Superuser para Dashboard Admin")
print("-" * 60)

# Credenciales del superuser
SUPERUSER_USERNAME = "admin"
SUPERUSER_EMAIL = "admin@oceanoptico.com"
SUPERUSER_PASSWORD = "Admin2025!"  # CAMBIAR DESPUÉS

if User.objects.filter(username=SUPERUSER_USERNAME).exists():
    print(f"⚠️  El usuario '{SUPERUSER_USERNAME}' ya existe")
    superuser = User.objects.get(username=SUPERUSER_USERNAME)
else:
    superuser = User.objects.create_superuser(
        username=SUPERUSER_USERNAME,
        email=SUPERUSER_EMAIL,
        password=SUPERUSER_PASSWORD
    )
    print(f"✅ Superuser creado exitosamente!")
    print(f"   Username: {SUPERUSER_USERNAME}")
    print(f"   Email: {SUPERUSER_EMAIL}")
    print(f"   Password: {SUPERUSER_PASSWORD}")
    print(f"\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login!")

# 2. Crear Planes de Suscripción
print("\n📋 PASO 2: Crear Planes de Suscripción")
print("-" * 60)

planes_existentes = SubscriptionPlan.objects.count()
if planes_existentes > 0:
    print(f"ℹ️  Ya existen {planes_existentes} planes:")
    for plan in SubscriptionPlan.objects.all():
        print(f"   • {plan.name} - ${plan.price_monthly}/mes")
else:
    print("✨ Creando planes de suscripción...\n")
    
    planes = [
        {
            "name": "Plan Gratuito",
            "slug": "plan-gratuito",
            "plan_type": "free",
            "price_monthly": 0.00,
            "price_yearly": 0.00,
            "max_users": 1,
            "max_patients": 50,
            "max_appointments_month": 30,
            "whatsapp_integration": False,
            "email_notifications": True,
            "custom_branding": False,
            "analytics": False,
        },
        {
            "name": "Plan Básico",
            "slug": "plan-basico",
            "plan_type": "basic",
            "price_monthly": 29.99,
            "price_yearly": 299.99,
            "max_users": 3,
            "max_patients": 200,
            "max_appointments_month": 100,
            "whatsapp_integration": True,
            "email_notifications": True,
            "custom_branding": False,
            "analytics": False,
        },
        {
            "name": "Plan Profesional",
            "slug": "plan-profesional",
            "plan_type": "professional",
            "price_monthly": 59.99,
            "price_yearly": 599.99,
            "max_users": 10,
            "max_patients": 1000,
            "max_appointments_month": 500,
            "whatsapp_integration": True,
            "email_notifications": True,
            "custom_branding": True,
            "analytics": True,
        },
        {
            "name": "Plan Empresarial",
            "slug": "plan-empresarial",
            "plan_type": "enterprise",
            "price_monthly": 99.99,
            "price_yearly": 999.99,
            "max_users": 999999,
            "max_patients": 999999,
            "max_appointments_month": 999999,
            "whatsapp_integration": True,
            "email_notifications": True,
            "custom_branding": True,
            "analytics": True,
        }
    ]
    
    for plan_data in planes:
        plan = SubscriptionPlan.objects.create(is_active=True, **plan_data)
        print(f"✅ {plan.name} creado - ${plan.price_monthly}/mes")
    
    print(f"\n✅ Total: {SubscriptionPlan.objects.count()} planes creados")

# 3. Crear Organización para el Superuser
print("\n🏢 PASO 3: Crear Organización Admin")
print("-" * 60)

if Organization.objects.filter(slug='admin-org').exists():
    print("⚠️  La organización admin ya existe")
    admin_org = Organization.objects.get(slug='admin-org')
else:
    # Obtener el plan gratuito para el admin
    free_plan = SubscriptionPlan.objects.filter(plan_type='free').first()
    
    admin_org = Organization.objects.create(
        name="Administración OCEANO OPTICO",
        slug="admin-org",
        email="admin@oceanoptico.com",
        phone="3001234567",
        address="Oficina Principal",
        is_active=True,
        subscription_plan=free_plan
    )
    
    # Asignar el superuser a la organización
    superuser.organization = admin_org
    superuser.save()
    
    print(f"✅ Organización '{admin_org.name}' creada")
    print(f"   Slug: {admin_org.slug}")
    print(f"   Plan: {admin_org.subscription_plan.name}")

# Resumen Final
print("\n" + "="*60)
print("✅ CONFIGURACIÓN COMPLETADA")
print("="*60)
print("\n📊 RESUMEN:")
print(f"   • Superusers: {User.objects.filter(is_superuser=True).count()}")
print(f"   • Planes: {SubscriptionPlan.objects.count()}")
print(f"   • Organizaciones: {Organization.objects.count()}")

print("\n🔐 ACCESO AL DASHBOARD ADMIN:")
print(f"   URL: https://tu-app.onrender.com/admin/")
print(f"   Username: {SUPERUSER_USERNAME}")
print(f"   Password: {SUPERUSER_PASSWORD}")
print(f"\n   ⚠️  CAMBIA LA CONTRASEÑA INMEDIATAMENTE!")

print("\n🎉 ¡Sistema listo para producción!")
print("="*60 + "\n")
