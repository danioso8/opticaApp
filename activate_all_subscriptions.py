#!/usr/bin/env python
"""Script para activar todas las suscripciones y hacer un test completo"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import UserSubscription

print("\n" + "="*70)
print("🔧 ACTIVANDO TODAS LAS SUSCRIPCIONES")
print("="*70 + "\n")

subscriptions = UserSubscription.objects.all()

for sub in subscriptions:
    if not sub.is_active:
        sub.is_active = True
        sub.save()
        print(f"✅ Activada suscripción de: {sub.user.username} ({sub.plan.name})")
    else:
        print(f"✓  Ya activa: {sub.user.username} ({sub.plan.name})")

print("\n" + "="*70)
print("✅ TODAS LAS SUSCRIPCIONES ESTÁN ACTIVAS")
print("="*70 + "\n")
