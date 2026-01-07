"""
Script para activar acceso a facturación electrónica ilimitada
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opticaapp.settings')
django.setup()

from apps.organizations.models import Organization, SubscriptionPlan, Subscription
from django.utils import timezone

# Obtener la organización
org = Organization.objects.first()
print(f"Organización: {org.name}")

# Verificar plan actual
subscription = org.subscriptions.filter(is_active=True).first()
if subscription:
    print(f"\n📋 Suscripción actual:")
    print(f"   Plan: {subscription.plan.name}")
    print(f"   Facturación electrónica: {subscription.plan.allow_electronic_invoicing}")
    print(f"   Límite facturas/mes: {subscription.plan.max_invoices_month} (0=ilimitado)")
    print(f"   Estado: {'✅ Activa' if subscription.is_active else '❌ Inactiva'}")

# Obtener o crear plan Empresarial con facturación ilimitada
plan_empresarial = SubscriptionPlan.objects.filter(name__icontains='empresarial').first()

if not plan_empresarial:
    print("\n⚠️  No existe plan Empresarial. Creando...")
    plan_empresarial = SubscriptionPlan.objects.create(
        name='Plan Empresarial Full',
        description='Acceso completo con facturación electrónica ilimitada DIAN',
        price=0,
        max_users=0,  # Ilimitado
        max_patients=0,  # Ilimitado
        max_appointments_month=0,  # Ilimitado
        allow_inventory=True,
        allow_sales=True,
        allow_reports=True,
        allow_integrations=True,
        allow_whatsapp=True,
        allow_electronic_invoicing=True,
        max_invoices_month=0,  # ILIMITADO ✅
        is_active=True
    )
    print(f"✅ Plan creado: {plan_empresarial.name}")
else:
    # Actualizar el plan para asegurar que tiene facturación ilimitada
    plan_empresarial.allow_electronic_invoicing = True
    plan_empresarial.max_invoices_month = 0  # ILIMITADO
    plan_empresarial.save()
    print(f"\n✅ Plan actualizado: {plan_empresarial.name}")

# Desactivar suscripción anterior si existe
if subscription:
    subscription.is_active = False
    subscription.save()
    print(f"   ❌ Suscripción anterior desactivada")

# Crear nueva suscripción activa
nueva_subscription = Subscription.objects.create(
    organization=org,
    plan=plan_empresarial,
    start_date=timezone.now().date(),
    end_date=None,  # Sin fecha de fin
    is_active=True,
    auto_renew=True
)

print(f"\n🎉 SUSCRIPCIÓN ACTIVADA:")
print(f"   Plan: {nueva_subscription.plan.name}")
print(f"   Facturación Electrónica: ✅ ACTIVADA")
print(f"   Límite facturas: ♾️  ILIMITADAS")
print(f"   Estado: ✅ ACTIVA")

# Verificar acceso a facturas
from apps.billing.models import Invoice
puede, mensaje = Invoice.puede_crear_factura_electronica(org)
print(f"\n🔍 Verificación de acceso:")
print(f"   {mensaje}")

if puede:
    print("\n✅ ¡TODO LISTO! Ahora puedes crear facturas electrónicas ilimitadas")
else:
    print("\n⚠️  Aún hay un problema. Revisa el mensaje anterior")
