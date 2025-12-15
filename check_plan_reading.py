#!/usr/bin/env python
"""
Verificar cómo se lee el plan del usuario
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserSubscription

print("\n" + "="*80)
print("🔍 VERIFICACIÓN DE LECTURA DE PLANES POR USUARIO")
print("="*80 + "\n")

user = User.objects.get(username='OceanoSJ')
print(f"👤 Usuario: {user.username}")

# Método 1: Get directo
sub1 = UserSubscription.objects.get(user=user)
print(f"\n📋 Método 1 - Get directo:")
print(f"   Plan: {sub1.plan.name}")
print(f"   max_organizations: {sub1.plan.max_organizations}")
print(f"   max_appointments: {sub1.plan.max_appointments_month}")
print(f"   max_patients: {sub1.plan.max_patients}")

# Método 2: Get con select_related
sub2 = UserSubscription.objects.select_related('plan').get(user=user)
print(f"\n📋 Método 2 - Con select_related:")
print(f"   Plan: {sub2.plan.name}")
print(f"   max_organizations: {sub2.plan.max_organizations}")
print(f"   max_appointments: {sub2.plan.max_appointments_month}")
print(f"   max_patients: {sub2.plan.max_patients}")

# Método 3: Refrescar desde BD
sub1.refresh_from_db()
sub1.plan.refresh_from_db()
print(f"\n📋 Método 3 - Después de refresh_from_db:")
print(f"   Plan: {sub1.plan.name}")
print(f"   max_organizations: {sub1.plan.max_organizations}")
print(f"   max_appointments: {sub1.plan.max_appointments_month}")
print(f"   max_patients: {sub1.plan.max_patients}")

# Verificar can_create_organizations
print(f"\n🔍 Verificación de límites:")
print(f"   can_create_organizations(): {sub1.can_create_organizations()}")
print(f"   is_active: {sub1.is_active}")
print(f"   is_expired: {sub1.is_expired}")

current_orgs = user.owned_organizations.filter(is_active=True).count()
print(f"   Organizaciones actuales: {current_orgs}")
print(f"   Límite del plan: {sub1.plan.max_organizations if sub1.plan.max_organizations < 999999 else '∞'}")

print("\n" + "="*80)
print("✅ Verificación completada")
print("="*80 + "\n")
