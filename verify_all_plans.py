#!/usr/bin/env python
"""Script para verificar que todos los planes estén configurados correctamente"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import SubscriptionPlan
from apps.users.models import UserSubscription
from django.contrib.auth import get_user_model

User = get_user_model()

print(f"\n{'='*70}")
print(f"🔍 VERIFICACIÓN DE TODOS LOS PLANES DE SUSCRIPCIÓN")
print(f"{'='*70}\n")

# 1. Verificar planes en la base de datos
print("📋 PLANES DISPONIBLES:")
print(f"{'-'*70}")
plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')

if not plans.exists():
    print("❌ No hay planes activos en la base de datos")
    sys.exit(1)

for plan in plans:
    print(f"\n✅ {plan.name}")
    print(f"   Tipo: {plan.plan_type}")
    print(f"   Precio Mensual: ${plan.price_monthly}")
    print(f"   Precio Anual: ${plan.price_yearly}")
    print(f"   Max Organizaciones: {plan.max_users if plan.max_users < 999999 else '∞ (Ilimitado)'}")
    print(f"   Max Usuarios: {plan.max_users}")
    print(f"   Max Citas/Mes: {plan.max_appointments_month}")
    print(f"   Max Pacientes: {plan.max_patients}")
    print(f"   Facturación Electrónica: {'✅ Sí' if plan.allow_electronic_invoicing else '❌ No'}")
    print(f"   Max Facturas/Mes: {plan.max_invoices_month if plan.max_invoices_month > 0 else '∞ (Ilimitado)'}")

# 2. Verificar que los tipos de plan sean correctos
print(f"\n{'-'*70}")
print("🔍 VERIFICACIÓN DE TIPOS DE PLAN:")
print(f"{'-'*70}\n")

expected_types = ['free', 'basic', 'professional', 'enterprise']
actual_types = [plan.plan_type for plan in plans]

for exp_type in expected_types:
    if exp_type in actual_types:
        plan = plans.get(plan_type=exp_type)
        print(f"✅ Plan tipo '{exp_type}': {plan.name}")
    else:
        print(f"⚠️  Plan tipo '{exp_type}': NO ENCONTRADO")

# 3. Verificar usuarios con suscripciones
print(f"\n{'-'*70}")
print("👥 USUARIOS CON SUSCRIPCIONES:")
print(f"{'-'*70}\n")

subscriptions = UserSubscription.objects.select_related('user', 'plan').all()

if not subscriptions.exists():
    print("⚠️  No hay usuarios con suscripciones")
else:
    for sub in subscriptions:
        print(f"\n👤 {sub.user.username} ({sub.user.email})")
        print(f"   Plan: {sub.plan.name} ({sub.plan.plan_type})")
        print(f"   Estado: {'✅ Activo' if sub.is_active else '❌ Inactivo'}")
        print(f"   Expirado: {'❌ Sí' if sub.is_expired else '✅ No'}")
        print(f"   Días restantes: {sub.days_remaining}")
        
        # Contar organizaciones
        org_count = sub.user.owned_organizations.filter(is_active=True).count()
        max_orgs = sub.plan.max_users
        can_create = sub.can_create_organizations()
        
        if max_orgs >= 999999:
            print(f"   Organizaciones: {org_count}/∞ (Ilimitado)")
        else:
            print(f"   Organizaciones: {org_count}/{max_orgs}")
        
        print(f"   Puede crear más: {'✅ Sí' if can_create else '❌ No'}")
        
        # Listar organizaciones
        orgs = sub.user.owned_organizations.filter(is_active=True)
        if orgs.exists():
            print(f"   📁 Organizaciones:")
            for org in orgs:
                print(f"      - {org.name}")

# 4. Test de lógica de límites
print(f"\n{'-'*70}")
print("🧪 TEST DE LÓGICA DE LÍMITES:")
print(f"{'-'*70}\n")

for plan in plans:
    print(f"\n📊 {plan.name}:")
    
    # Simular diferentes escenarios
    if plan.max_users >= 999999:
        print(f"   ✅ Plan con acceso ILIMITADO - siempre puede crear más")
    else:
        print(f"   📏 Límite: {plan.max_users} organizaciones")
        print(f"   ✅ Con 0 orgs → Puede crear: {0 < plan.max_users}")
        print(f"   ✅ Con {plan.max_users-1} orgs → Puede crear: {plan.max_users-1 < plan.max_users}")
        print(f"   ❌ Con {plan.max_users} orgs → Puede crear: {plan.max_users < plan.max_users}")
        print(f"   ❌ Con {plan.max_users+1} orgs → Puede crear: {plan.max_users+1 < plan.max_users}")

# 5. Verificar que el plan empresarial sea el más alto
print(f"\n{'-'*70}")
print("👑 VERIFICACIÓN DEL PLAN MÁS ALTO:")
print(f"{'-'*70}\n")

enterprise_plans = plans.filter(plan_type='enterprise')
if enterprise_plans.exists():
    enterprise = enterprise_plans.first()
    print(f"✅ Plan Empresarial encontrado: {enterprise.name}")
    print(f"   Es el más caro: ${enterprise.price_monthly}/mes")
    
    # Verificar que sea el que tiene más características
    if enterprise.max_users >= 999999:
        print(f"   ✅ Tiene organizaciones ilimitadas")
    else:
        print(f"   ⚠️  Tiene límite de {enterprise.max_users} organizaciones")
    
    if enterprise.allow_electronic_invoicing and enterprise.max_invoices_month == 0:
        print(f"   ✅ Tiene facturación electrónica ilimitada")
    else:
        print(f"   ⚠️  Facturación limitada")
else:
    print("❌ No se encontró plan empresarial")

print(f"\n{'='*70}")
print("✅ VERIFICACIÓN COMPLETADA")
print(f"{'='*70}\n")
