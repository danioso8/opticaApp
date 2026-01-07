"""
Script para verificar y actualizar límites de organizaciones en Plan Básico
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import SubscriptionPlan

print("\n" + "="*80)
print("📊 VERIFICANDO LÍMITES DE ORGANIZACIONES POR PLAN")
print("="*80 + "\n")

plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')

for plan in plans:
    print(f"📦 {plan.name} ({plan.plan_type})")
    print(f"   Organizaciones: {plan.max_organizations if not plan.unlimited_organizations else '∞ Ilimitadas'}")
    print(f"   Usuarios: {plan.max_users if not plan.unlimited_users else '∞ Ilimitados'}")
    print()

print("\n" + "="*80)
print("¿Cuántas organizaciones debería permitir el Plan Básico?")
print("="*80)
print("\nOpciones recomendadas:")
print("  1 = Una sola organización (actual)")
print("  3 = Hasta 3 organizaciones")
print("  5 = Hasta 5 organizaciones")
print()
