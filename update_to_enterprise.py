"""
Script para diagnosticar y actualizar suscripciones
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserSubscription  
from apps.organizations.models import Organization, OrganizationMember, Subscription, SubscriptionPlan
from django.utils import timezone
from datetime import timedelta

print("\n" + "="*70)
print("🔧 ACTUALIZACIÓN DE SUSCRIPCIÓN A PLAN EMPRESARIAL")
print("="*70 + "\n")

# Usuario a actualizar
username = "danioso83"
user = User.objects.filter(username=username).first()

if not user:
    print(f"❌ Usuario '{username}' no encontrado")
    sys.exit(1)

print(f"✅ Usuario encontrado: {user.username} (ID: {user.id})")

# Obtener plan empresarial
plan_empresarial = SubscriptionPlan.objects.filter(name__icontains="Empresarial").first()

if not plan_empresarial:
    print("❌ Plan Empresarial no encontrado")
    sys.exit(1)

print(f"✅ Plan objetivo: {plan_empresarial.name}\n")

# 1. Actualizar UserSubscription
print("1️⃣  Actualizando UserSubscription...")
try:
    user_sub = UserSubscription.objects.get(user=user)
    print(f"   Anterior: {user_sub.plan.name}")
    
    user_sub.plan = plan_empresarial
    user_sub.payment_status = 'paid'
    user_sub.is_active = True
    user_sub.billing_cycle = 'yearly'
    user_sub.end_date = timezone.now() + timedelta(days=365)
    user_sub.save()
    
    print(f"   ✅ Actualizado a: {user_sub.plan.name}")
except UserSubscription.DoesNotExist:
    print("   ❌ UserSubscription no existe")

# 2. Actualizar Subscription de la organización
print("\n2️⃣  Actualizando Subscription de Organización...")
org_member = OrganizationMember.objects.filter(user=user).first()

if not org_member:
    print("   ❌ Usuario no es miembro de ninguna organización")
else:
    org = org_member.organization
    print(f"   Organización: {org.name}")
    
    # Desactivar suscripciones anteriores
    old_subs = Subscription.objects.filter(organization=org, is_active=True)
    print(f"   Desactivando {old_subs.count()} suscripciones antiguas...")
    old_subs.update(is_active=False)
    
    # Crear nueva suscripción empresarial
    new_sub = Subscription.objects.create(
        organization=org,
        plan=plan_empresarial,
        billing_cycle='yearly',
        payment_status='paid',
        is_active=True,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=365),
        amount_paid=0  # Empresarial sin costo para testing
    )
    
    print(f"   ✅ Nueva suscripción creada: {new_sub.plan.name}\n")

# 3. Verificar resultado
print("="*70)
print("✅ ACTUALIZACIÓN COMPLETADA")
print("="*70 + "\n")

print("📊 Estado Final:\n")

# UserSubscription
try:
    user_sub = UserSubscription.objects.get(user=user)
    print(f"   UserSubscription:")
    print(f"     - Plan: {user_sub.plan.name}")
    print(f"     - Ciclo: {user_sub.billing_cycle}")
    print(f"     - Estado: {'Activa' if user_sub.is_active else 'Inactiva'}")
    print(f"     - Pago: {user_sub.payment_status}\n")
except:
    print(f"   ❌ UserSubscription no encontrada\n")

# Organization Subscription
org_member = OrganizationMember.objects.filter(user=user).first()
if org_member:
    active_sub = Subscription.objects.filter(
        organization=org_member.organization,
        is_active=True
    ).first()
    
    if active_sub:
        print(f"   Organization Subscription:")
        print(f"     - Plan: {active_sub.plan.name}")
        print(f"     - Ciclo: {active_sub.billing_cycle}")
        print(f"     - Estado: {'Activa' if active_sub.is_active else 'Inactiva'}")
        print(f"     - Pago: {active_sub.payment_status}")
        print(f"     - Hasta: {active_sub.end_date.strftime('%Y-%m-%d')}\n")
    else:
        print(f"   ❌ No hay suscripción activa de organización\n")

print("="*70)
print("🎉 LISTO! El usuario ahora tiene Plan Empresarial")
print("="*70 + "\n")
