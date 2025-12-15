#!/usr/bin/env python
"""
Verificar límites de organizaciones para usuarios
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserSubscription
from apps.organizations.models import Organization

print("\n" + "="*80)
print("🔍 VERIFICACIÓN DE LÍMITES DE ORGANIZACIONES")
print("="*80 + "\n")

users = User.objects.all()

for user in users:
    print(f"\n{'─'*80}")
    print(f"👤 Usuario: {user.username}")
    print(f"{'─'*80}")
    
    try:
        subscription = UserSubscription.objects.get(user=user)
        plan = subscription.plan
        
        # Contar organizaciones actuales
        current_orgs = user.owned_organizations.filter(is_active=True).count()
        max_orgs = plan.max_organizations
        
        print(f"📋 Plan: {plan.name}")
        print(f"   Tipo: {plan.get_plan_type_display()}")
        print(f"   Estado: {'✅ Activo' if subscription.is_active else '❌ Inactivo'}")
        print(f"   Expirado: {'❌ SÍ' if subscription.is_expired else '✅ NO'}")
        print(f"\n🏢 Organizaciones:")
        print(f"   Límite del plan: {max_orgs if max_orgs < 999999 else '∞ Ilimitado'}")
        print(f"   Organizaciones actuales: {current_orgs}")
        print(f"   Puede crear más: {'✅ SÍ' if subscription.can_create_organizations() else '❌ NO'}")
        
        if current_orgs > 0:
            print(f"\n   Organizaciones creadas:")
            for org in user.owned_organizations.filter(is_active=True):
                print(f"      • {org.name}")
        
    except UserSubscription.DoesNotExist:
        print(f"⚠️  Sin suscripción activa")
        print(f"   Organizaciones actuales: {user.owned_organizations.filter(is_active=True).count()}")

print("\n" + "="*80)
print("✅ Verificación completada")
print("="*80 + "\n")
