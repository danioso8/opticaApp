"""
Script para actualizar límite de organizaciones del Plan Básico a 3
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import SubscriptionPlan

print("\n" + "="*80)
print("🔄 ACTUALIZANDO LÍMITE DE ORGANIZACIONES EN PLAN BÁSICO")
print("="*80 + "\n")

try:
    basic_plan = SubscriptionPlan.objects.get(plan_type='basic')
    
    print(f"📦 Plan encontrado: {basic_plan.name}")
    print(f"   Límite anterior de organizaciones: {basic_plan.max_organizations}")
    
    # Actualizar a 3 organizaciones
    basic_plan.max_organizations = 3
    basic_plan.save()
    
    print(f"   ✅ Límite actualizado a: {basic_plan.max_organizations}")
    print()
    print("="*80)
    print("✅ ACTUALIZACIÓN COMPLETADA")
    print("="*80)
    print()
    print("El Plan Básico ahora permite:")
    print(f"  👥 {basic_plan.max_users} usuarios")
    print(f"  🏢 {basic_plan.max_organizations} organizaciones")
    print(f"  📅 {basic_plan.max_appointments_month} citas/mes")
    print(f"  👨‍⚕️ {basic_plan.max_patients} pacientes")
    print()
    
except SubscriptionPlan.DoesNotExist:
    print("❌ Plan Básico no encontrado en la base de datos")
except Exception as e:
    print(f"❌ Error: {e}")
