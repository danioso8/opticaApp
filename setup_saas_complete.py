from django.contrib.auth.models import User
from apps.organizations.models import Organization, SubscriptionPlan, Subscription
from datetime import datetime, timedelta
from django.utils import timezone

print("=" * 80)
print("CONFIGURANDO SISTEMA SAAS - PLANES Y USUARIOS")
print("=" * 80)

# 1. CREAR PLANES DE SUBSCRIPCIÓN
print("\n1. Creando planes de subscripción...")

plans_data = [
    {
        'name': 'Plan Gratuito',
        'slug': 'plan-gratuito',
        'plan_type': 'free',
        'price_monthly': 0.00,
        'price_yearly': 0.00,
        'max_patients': 10,
        'max_users': 1,
        'max_organizations': 1,
        'max_appointments_month': 20,
        'max_storage_mb': 100,
        'allow_electronic_invoicing': False,
        'max_invoices_month': 0,
        'whatsapp_integration': False,
        'custom_branding': False,
        'api_access': False,
        'priority_support': False,
        'analytics': False,
        'multi_location': False,
        'is_active': True
    },
    {
        'name': 'Plan Básico',
        'slug': 'plan-basico',
        'plan_type': 'basic',
        'price_monthly': 29.99,
        'price_yearly': 299.99,
        'max_patients': 100,
        'max_users': 3,
        'max_organizations': 1,
        'max_appointments_month': 200,
        'max_storage_mb': 500,
        'allow_electronic_invoicing': True,
        'max_invoices_month': 50,
        'whatsapp_integration': False,
        'custom_branding': False,
        'api_access': False,
        'priority_support': False,
        'analytics': True,
        'multi_location': False,
        'is_active': True
    },
    {
        'name': 'Plan Profesional',
        'slug': 'plan-profesional',
        'plan_type': 'professional',
        'price_monthly': 79.99,
        'price_yearly': 799.99,
        'max_patients': 500,
        'max_users': 10,
        'max_organizations': 3,
        'max_appointments_month': 1000,
        'max_storage_mb': 2000,
        'allow_electronic_invoicing': True,
        'max_invoices_month': 200,
        'whatsapp_integration': True,
        'custom_branding': True,
        'api_access': False,
        'priority_support': False,
        'analytics': True,
        'multi_location': True,
        'is_active': True
    },
    {
        'name': 'Plan Empresarial',
        'slug': 'plan-empresarial',
        'plan_type': 'enterprise',
        'price_monthly': 199.99,
        'price_yearly': 1999.99,
        'max_patients': 9999,  # prácticamente ilimitado
        'max_users': 50,
        'max_organizations': 10,
        'max_appointments_month': 5000,
        'max_storage_mb': 10000,
        'allow_electronic_invoicing': True,
        'max_invoices_month': 0,  # ilimitado
        'whatsapp_integration': True,
        'custom_branding': True,
        'api_access': True,
        'priority_support': True,
        'analytics': True,
        'multi_location': True,
        'is_active': True
    }
]

created_plans = {}
for plan_data in plans_data:
    plan, created = SubscriptionPlan.objects.get_or_create(
        slug=plan_data['slug'],
        defaults=plan_data
    )
    if created:
        print(f"   ✅ Creado: {plan.name} - ${plan.price_monthly}/mes")
    else:
        print(f"   ℹ️  Ya existe: {plan.name}")
    created_plans[plan.name] = plan

# 2. CREAR USUARIO JULIO ZAPATA
print("\n2. Creando usuario Julio Zapata...")

julio, created = User.objects.get_or_create(
    username='juliozapata',
    defaults={
        'first_name': 'Julio',
        'last_name': 'Zapata',
        'email': 'julio.zapata@optica.com',
        'is_staff': False,
        'is_superuser': False,
        'is_active': True
    }
)

if created:
    julio.set_password('temporal123')  # Usuario debe cambiar contraseña
    julio.save()
    print(f"   ✅ Usuario creado: {julio.username}")
    print(f"      Email: {julio.email}")
    print(f"      Contraseña temporal: temporal123")
else:
    print(f"   ℹ️  Usuario ya existe: {julio.username}")

# 3. ASIGNAR SUBSCRIPCIONES A ORGANIZACIONES EXISTENTES
print("\n3. Asignando subscripciones a organizaciones...")

orgs = Organization.objects.all()
plan_basico = created_plans.get('Plan Básico')

for org in orgs:
    # Verificar si ya tiene subscripción
    existing_sub = Subscription.objects.filter(organization=org).first()
    
    if existing_sub:
        print(f"   ℹ️  {org.name} ya tiene subscripción: {existing_sub.plan.name}")
    else:
        # Crear subscripción con Plan Básico por defecto
        subscription = Subscription.objects.create(
            organization=org,
            plan=plan_basico,
            billing_cycle='monthly',
            payment_status='paid',
            is_active=True,
            auto_renew=True
        )
        print(f"   ✅ Subscripción creada para {org.name}: {plan_basico.name}")

# 4. RESUMEN FINAL
print("\n" + "=" * 80)
print("RESUMEN FINAL")
print("=" * 80)

print(f"\nPlanes creados: {SubscriptionPlan.objects.count()}")
for plan in SubscriptionPlan.objects.all():
    print(f"   - {plan.name}: ${plan.price_monthly}/mes | ${plan.price_yearly}/año ({plan.max_patients} pacientes, {plan.max_users} usuarios)")

print(f"\nUsuarios totales: {User.objects.count()}")
for user in User.objects.all():
    print(f"   - {user.username} ({user.email})")

print(f"\nOrganizaciones con subscripción: {Subscription.objects.count()}")
for sub in Subscription.objects.all():
    status_text = 'Activa' if sub.is_active and not sub.is_expired else 'Inactiva/Expirada'
    print(f"   - {sub.organization.name}: {sub.plan.name} ({sub.billing_cycle}) - {status_text}")

print("\n" + "=" * 80)
print("✅ CONFIGURACIÓN COMPLETADA")
print("=" * 80)
print("\nAccede al admin en: https://opticaapp-4e16.onrender.com/saas-admin/")
print(f"Usuario Julio: juliozapata / temporal123")
print(f"Admin: danioso8 / [tu contraseña]")
