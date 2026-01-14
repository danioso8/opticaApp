"""
Script para sincronizar los módulos de plan_features.py con la base de datos
y asociarlos correctamente a cada plan
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import PlanFeature, SubscriptionPlan
from apps.organizations.plan_features import MODULES, PLAN_MODULES

print("\n" + "="*80)
print("🔄 SINCRONIZACIÓN DE MÓDULOS Y PLANES")
print("="*80)

# Paso 1: Crear/Actualizar todos los módulos en la BD
print("\n📦 Paso 1: Sincronizando módulos...")
print("-"*80)

created_modules = 0
updated_modules = 0

for code, info in MODULES.items():
    feature, created = PlanFeature.objects.update_or_create(
        code=code,
        defaults={
            'name': info['name'],
            'description': info['description'],
            'icon': info['icon'],
            'category': info['category'],
            'is_active': True
        }
    )
    
    if created:
        created_modules += 1
        print(f"  ✅ Creado: {code:30s} - {info['name']}")
    else:
        updated_modules += 1
        print(f"  🔄 Actualizado: {code:30s} - {info['name']}")

print(f"\n📊 Módulos creados: {created_modules}")
print(f"📊 Módulos actualizados: {updated_modules}")

# Paso 2: Asociar módulos a cada plan
print("\n🔗 Paso 2: Asociando módulos a planes...")
print("-"*80)

plans = SubscriptionPlan.objects.all()
total_associations = 0

for plan in plans:
    plan_type = plan.plan_type.lower()
    
    if plan_type not in PLAN_MODULES:
        print(f"\n⚠️  Plan '{plan.name}' (tipo: {plan_type}) no encontrado en PLAN_MODULES")
        continue
    
    print(f"\n📋 Plan: {plan.name} ({plan_type})")
    
    # Obtener módulos para este plan
    module_codes = PLAN_MODULES[plan_type]
    
    # Limpiar asociaciones actuales
    current_count = plan.features.count()
    plan.features.clear()
    print(f"   🧹 Removidas {current_count} asociaciones antiguas")
    
    # Agregar nuevas asociaciones
    added = 0
    not_found = []
    
    for module_code in module_codes:
        try:
            feature = PlanFeature.objects.get(code=module_code)
            plan.features.add(feature)
            added += 1
        except PlanFeature.DoesNotExist:
            not_found.append(module_code)
    
    print(f"   ✅ Agregados {added} módulos")
    total_associations += added
    
    if not_found:
        print(f"   ⚠️  No encontrados: {', '.join(not_found)}")

# Paso 3: Verificar resultado
print("\n" + "="*80)
print("📊 VERIFICACIÓN FINAL")
print("="*80)

for plan in plans:
    plan_type = plan.plan_type.lower()
    features_count = plan.features.count()
    expected_count = len(PLAN_MODULES.get(plan_type, []))
    
    status = "✅" if features_count == expected_count else "⚠️"
    print(f"{status} {plan.name:30s} - {features_count}/{expected_count} módulos")
    
    # Mostrar si WhatsApp está incluido
    has_whatsapp = plan.features.filter(code='whatsapp').exists()
    whatsapp_status = "✅ WhatsApp incluido" if has_whatsapp else "❌ Sin WhatsApp"
    print(f"   {whatsapp_status}")

print("\n" + "="*80)
print("✅ SINCRONIZACIÓN COMPLETADA")
print("="*80)
print(f"\n📦 Total módulos en BD: {PlanFeature.objects.count()}")
print(f"🔗 Total asociaciones creadas: {total_associations}")
print("\n💡 Los usuarios deben cerrar sesión y volver a entrar para ver los cambios")
print("="*80 + "\n")
