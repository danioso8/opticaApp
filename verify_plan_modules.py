"""
Script para verificar y actualizar módulos asignados a cada plan
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import SubscriptionPlan
from apps.organizations.plan_features import PLAN_MODULES, MODULES

def display_plan_modules():
    """Muestra los módulos configurados para cada plan"""
    
    print("\n" + "="*80)
    print("📋 CONFIGURACIÓN ACTUAL DE MÓDULOS POR PLAN")
    print("="*80 + "\n")
    
    for plan_type, modules in PLAN_MODULES.items():
        print(f"📦 Plan: {plan_type.upper()}")
        print(f"   Total módulos: {len(modules)}")
        print(f"   Módulos incluidos:")
        for module in modules:
            module_info = MODULES.get(module, {})
            name = module_info.get('name', module)
            icon = module_info.get('icon', '')
            print(f"      {icon} {name} ({module})")
        print()

def verify_plan_limits():
    """Verifica los límites de cada plan en la base de datos"""
    
    print("\n" + "="*80)
    print("🔍 VERIFICACIÓN DE LÍMITES DE PLANES EN BASE DE DATOS")
    print("="*80 + "\n")
    
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
    
    if not plans.exists():
        print("⚠️  No hay planes activos en la base de datos")
        return
    
    for plan in plans:
        print(f"📦 {plan.name} ({plan.plan_type})")
        print(f"   💰 Precio: ${plan.price_monthly:,.0f}/mes")
        print(f"   👥 Usuarios: {plan.max_users if not plan.unlimited_users else '∞ Ilimitados'}")
        print(f"   🏢 Organizaciones: {plan.max_organizations if not plan.unlimited_organizations else '∞ Ilimitadas'}")
        print(f"   📅 Citas/mes: {plan.max_appointments_month if not plan.unlimited_appointments else '∞ Ilimitadas'}")
        print(f"   👨‍⚕️ Pacientes: {plan.max_patients if not plan.unlimited_patients else '∞ Ilimitados'}")
        print(f"   💾 Almacenamiento: {plan.max_storage_mb}MB" if not plan.unlimited_storage else "   💾 Almacenamiento: ∞ Ilimitado")
        
        # Módulos disponibles según configuración
        available_modules = PLAN_MODULES.get(plan.plan_type, [])
        print(f"   🔧 Módulos disponibles: {len(available_modules)}")
        
        # Verificar módulo team_management
        if 'team_management' in available_modules:
            print(f"   ✅ Gestión de Equipo: HABILITADO (hasta {plan.max_users} usuarios)")
        else:
            print(f"   ❌ Gestión de Equipo: NO DISPONIBLE")
        
        print()

def compare_plans():
    """Comparación resumida entre planes"""
    
    print("\n" + "="*80)
    print("📊 COMPARACIÓN DE PLANES")
    print("="*80 + "\n")
    
    print(f"{'Característica':<30} {'Free':<15} {'Básico':<15} {'Profesional':<15} {'Empresarial':<15}")
    print("-" * 90)
    
    # Usuarios
    free_users = "1 usuario"
    basic_users = "3 usuarios"
    pro_users = "10 usuarios"
    ent_users = "∞ Ilimitados"
    print(f"{'👥 Usuarios':<30} {free_users:<15} {basic_users:<15} {pro_users:<15} {ent_users:<15}")
    
    # Citas
    free_appts = "50/mes"
    basic_appts = "200/mes"
    pro_appts = "1,500/mes"
    ent_appts = "∞ Ilimitadas"
    print(f"{'📅 Citas':<30} {free_appts:<15} {basic_appts:<15} {pro_appts:<15} {ent_appts:<15}")
    
    # Pacientes
    free_patients = "100"
    basic_patients = "500"
    pro_patients = "3,000"
    ent_patients = "∞ Ilimitados"
    print(f"{'👨‍⚕️ Pacientes':<30} {free_patients:<15} {basic_patients:<15} {pro_patients:<15} {ent_patients:<15}")
    
    # Gestión de Equipo
    free_team = "❌ No"
    basic_team = "✅ Sí"
    pro_team = "✅ Sí"
    ent_team = "✅ Sí"
    print(f"{'🔧 Gestión de Equipo':<30} {free_team:<15} {basic_team:<15} {pro_team:<15} {ent_team:<15}")
    
    # Inventario
    free_inv = "❌ No"
    basic_inv = "✅ Sí"
    pro_inv = "✅ Sí"
    ent_inv = "✅ Sí"
    print(f"{'📦 Inventario':<30} {free_inv:<15} {basic_inv:<15} {pro_inv:<15} {ent_inv:<15}")
    
    # WhatsApp
    free_wa = "❌ No"
    basic_wa = "❌ No"
    pro_wa = "✅ Sí"
    ent_wa = "✅ Premium"
    print(f"{'💬 WhatsApp':<30} {free_wa:<15} {basic_wa:<15} {pro_wa:<15} {ent_wa:<15}")
    
    # Facturación DIAN
    free_dian = "❌ No"
    basic_dian = "❌ No"
    pro_dian = "✅ 50/mes"
    ent_dian = "✅ Ilimitadas"
    print(f"{'📄 Facturación DIAN':<30} {free_dian:<15} {basic_dian:<15} {pro_dian:<15} {ent_dian:<15}")
    
    # API
    free_api = "❌ No"
    basic_api = "❌ No"
    pro_api = "❌ No"
    ent_api = "✅ Sí"
    print(f"{'🔌 API Access':<30} {free_api:<15} {basic_api:<15} {pro_api:<15} {ent_api:<15}")
    
    print()

def main():
    """Función principal"""
    
    display_plan_modules()
    verify_plan_limits()
    compare_plans()
    
    print("\n" + "="*80)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("="*80)
    print("\nResumen de cambios recientes:")
    print("  • Plan Básico ahora incluye 'team_management' (Gestión de Equipo)")
    print("  • Permite crear hasta 3 usuarios en el Plan Básico")
    print("  • El sidebar ya no mostrará el badge 'Premium' para Gestión de Equipo")
    print()

if __name__ == '__main__':
    main()
