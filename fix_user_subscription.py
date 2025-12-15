"""
Script para verificar y corregir suscripciones de usuario
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserSubscription
from apps.organizations.models import Organization, OrganizationMember, Subscription, SubscriptionPlan

# Buscar el usuario
username = "danioso83"
user = User.objects.filter(username=username).first()

if not user:
    print(f"❌ Usuario {username} no encontrado")
    exit()

print(f"\n{'='*70}")
print(f"🔍 DIAGNÓSTICO DE SUSCRIPCIONES - {user.username}")
print(f"{'='*70}\n")

# 1. Verificar UserSubscription
print("1️⃣  UserSubscription (apps/users):")
try:
    user_sub = UserSubscription.objects.get(user=user)
    print(f"   ✅ Encontrada: {user_sub.plan.name}")
    print(f"   📅 Ciclo: {user_sub.billing_cycle}")
    print(f"   💰 Estado Pago: {user_sub.payment_status}")
    print(f"   🔴 Activa: {user_sub.is_active}")
except UserSubscription.DoesNotExist:
    print(f"   ❌ No tiene UserSubscription")
    user_sub = None

# 2. Verificar OrganizationMember
print(f"\n2️⃣  Organizaciones del usuario:")
org_members = OrganizationMember.objects.filter(user=user)
if org_members.exists():
    for member in org_members:
        print(f"   ✅ Miembro de: {member.organization.name} (Rol: {member.role})")
        
        # 3. Verificar Subscription de la organización
        print(f"\n3️⃣  Suscripciones de la organización '{member.organization.name}':")
        org_subs = Subscription.objects.filter(organization=member.organization)
        
        if org_subs.exists():
            for idx, sub in enumerate(org_subs, 1):
                print(f"   {idx}. Plan: {sub.plan.name}")
                print(f"      📅 Ciclo: {sub.billing_cycle}")
                print(f"      💰 Estado Pago: {sub.payment_status}")
                print(f"      🔴 Activa: {sub.is_active}")
                print(f"      📆 Desde: {sub.start_date.strftime('%Y-%m-%d')}")
                print(f"      📆 Hasta: {sub.end_date.strftime('%Y-%m-%d')}")
        else:
            print(f"   ❌ No tiene suscripciones de organización")
else:
    print(f"   ❌ No es miembro de ninguna organización")

# 4. Proponer corrección
print(f"\n{'='*70}")
print(f"🔧 CORRECCIÓN AUTOMÁTICA")
print(f"{'='*70}\n")

# Obtener plan empresarial
plan_empresarial = SubscriptionPlan.objects.filter(name__icontains="Empresarial").first()

if not plan_empresarial:
    print("❌ No se encontró el Plan Empresarial")
    exit()

print(f"✅ Plan objetivo: {plan_empresarial.name}")

# Actualizar UserSubscription
if user_sub:
    user_sub.plan = plan_empresarial
    user_sub.payment_status = 'paid'
    user_sub.is_active = True
    user_sub.save()
    print(f"✅ UserSubscription actualizada a {plan_empresarial.name}")
else:
    print(f"⚠️  No se puede actualizar UserSubscription (no existe)")

# Actualizar/Crear Subscription de la organización
org_member = OrganizationMember.objects.filter(user=user).first()
if org_member:
    org = org_member.organization
    
    # Desactivar todas las suscripciones anteriores
    Subscription.objects.filter(organization=org, is_active=True).update(is_active=False)
    
    # Crear nueva suscripción empresarial
    from django.utils import timezone
    from datetime import timedelta
    
    new_sub = Subscription.objects.create(
        organization=org,
        plan=plan_empresarial,
        billing_cycle='yearly',
        payment_status='paid',
        is_active=True,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=365)
    )
    print(f"✅ Nueva suscripción de organización creada: {new_sub.plan.name}")
else:
    print(f"⚠️  No se puede actualizar suscripción de organización (no es miembro)")

print(f"\n{'='*70}")
print(f"✅ CORRECCIÓN COMPLETADA")
print(f"{'='*70}\n")

# Verificar resultado
print("📊 ESTADO FINAL:\n")
user_sub = UserSubscription.objects.get(user=user)
print(f"UserSubscription: {user_sub.plan.name}")

org_member = OrganizationMember.objects.filter(user=user).first()
if org_member:
    org_sub = Subscription.objects.filter(organization=org_member.organization, is_active=True).first()
    if org_sub:
        print(f"Organization Subscription: {org_sub.plan.name}")
    else:
        print(f"Organization Subscription: ❌ No activa")
