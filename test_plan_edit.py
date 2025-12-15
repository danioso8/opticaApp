#!/usr/bin/env python
"""
Script para probar la edición de planes
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import SubscriptionPlan

print("\n" + "="*80)
print("🧪 PRUEBA DE EDICIÓN DE PLANES")
print("="*80 + "\n")

# Obtener plan Pro
plan = SubscriptionPlan.objects.get(id=3)

print(f"📋 Plan antes de cambios:")
print(f"   Nombre: {plan.name}")
print(f"   Max usuarios: {plan.max_users}")
print(f"   Max organizaciones: {plan.max_organizations}")
print(f"   Max citas/mes: {plan.max_appointments_month}")
print(f"   Max pacientes: {plan.max_patients}")
print(f"   Activo: {plan.is_active}")

# Simular cambios
print(f"\n🔧 Aplicando cambios de prueba...")
original_users = plan.max_users
plan.max_users = 15
plan.save()

print(f"\n✅ Plan después de cambios:")
print(f"   Max usuarios: {plan.max_users} (era {original_users})")

# Verificar que se guardó
plan.refresh_from_db()
print(f"\n🔍 Verificación desde BD:")
print(f"   Max usuarios: {plan.max_users}")

# Restaurar valor original
plan.max_users = original_users
plan.save()
print(f"\n↩️  Valor restaurado a: {plan.max_users}")

print("\n" + "="*80)
print("✅ Prueba completada")
print("="*80 + "\n")
