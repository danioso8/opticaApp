"""
Script para verificar el sistema de control de acceso a módulos por plan
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserSubscription
from apps.organizations.models import SubscriptionPlan
from apps.organizations.plan_features import (
    has_module_access,
    get_user_modules,
    get_required_plan_for_module,
    MODULES,
    PLAN_MODULES
)

def print_section(title):
    """Imprime un título de sección"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def verify_module_definitions():
    """Verifica que todos los módulos están correctamente definidos"""
    print_section("1. VERIFICACIÓN DE DEFINICIONES DE MÓDULOS")
    
    print(f"\n📦 Total de módulos definidos: {len(MODULES)}")
    print("\nMódulos:")
    for code, info in MODULES.items():
        print(f"  • {code:20s} → {info['name']}")
    
    print(f"\n📋 Total de planes con módulos: {len(PLAN_MODULES)}")
    print("\nMódulos por plan:")
    for plan_type, modules in PLAN_MODULES.items():
        print(f"  • {plan_type.upper():15s} → {len(modules)} módulos")

def verify_plan_hierarchy():
    """Verifica la jerarquía de módulos entre planes"""
    print_section("2. VERIFICACIÓN DE JERARQUÍA DE PLANES")
    
    plans_order = ['free', 'basic', 'professional', 'premium', 'enterprise']
    
    print("\nMódulos acumulados por plan:")
    for i, plan_type in enumerate(plans_order):
        modules = PLAN_MODULES.get(plan_type, [])
        print(f"\n{plan_type.upper()}:")
        print(f"  Total: {len(modules)} módulos")
        
        # Verificar herencia (planes superiores tienen más o igual cantidad)
        if i > 0:
            prev_plan = plans_order[i-1]
            prev_modules = set(PLAN_MODULES.get(prev_plan, []))
            curr_modules = set(modules)
            
            # Los módulos del plan anterior deben estar en el actual
            missing = prev_modules - curr_modules
            if missing:
                print(f"  ⚠️  ADVERTENCIA: Faltan módulos del plan anterior: {missing}")
            else:
                print(f"  ✅ Hereda todos los módulos de {prev_plan.upper()}")

def verify_user_access(username='danioso8'):
    """Verifica el acceso del usuario a los módulos"""
    print_section(f"3. VERIFICACIÓN DE ACCESO DEL USUARIO: {username}")
    
    try:
        user = User.objects.get(username=username)
        subscription = UserSubscription.objects.get(user=user)
        
        print(f"\n👤 Usuario: {user.username}")
        print(f"� Superusuario: {'Sí' if user.is_superuser else 'No'}")
        
        if user.is_superuser:
            print(f"⚠️  NOTA: Los superusuarios tienen acceso ilimitado a TODOS los módulos")
        
        print(f"📊 Plan: {subscription.plan.name} ({subscription.plan.plan_type})")
        print(f"⏰ Estado: {'Activo' if subscription.is_active else 'Inactivo'}")
        
        if subscription.is_trial:
            print(f"🎁 Trial: Sí (expira: {subscription.trial_ends_at})")
        
        # Obtener módulos del plan del usuario
        plan_type = subscription.plan.plan_type
        user_modules_codes = PLAN_MODULES.get(plan_type, [])
        
        print(f"\n✅ Módulos incluidos en el plan {plan_type.upper()} ({len(user_modules_codes)}):")
        for module_code in user_modules_codes:
            module_info = MODULES.get(module_code, {})
            print(f"  • {module_code:20s} → {module_info.get('name', 'N/A')}")
        
        # Verificar módulos bloqueados (solo si no es superuser)
        if not user.is_superuser:
            all_modules = set(MODULES.keys())
            blocked_modules = all_modules - set(user_modules_codes)
            
            if blocked_modules:
                print(f"\n🔒 Módulos bloqueados ({len(blocked_modules)}):")
                for module_code in sorted(blocked_modules):
                    module_info = MODULES.get(module_code, {})
                    required_plan = get_required_plan_for_module(module_code)
                    print(f"  • {module_code:20s} → Requiere: {required_plan.upper()}")
        else:
            print(f"\n✨ Como superusuario, tiene acceso a TODOS los módulos sin restricciones")
        
    except User.DoesNotExist:
        print(f"\n❌ Usuario '{username}' no encontrado")
    except UserSubscription.DoesNotExist:
        print(f"\n❌ El usuario '{username}' no tiene suscripción")

def test_specific_modules():
    """Prueba el acceso a módulos específicos"""
    print_section("4. PRUEBAS DE MÓDULOS ESPECÍFICOS")
    
    # Nota sobre superusuarios
    print("\n⚠️  NOTA: El usuario 'danioso8' es superusuario, por lo que tendrá acceso a todo.")
    print("    Estas pruebas verifican la LÓGICA del sistema, no las restricciones reales.")
    
    test_cases = [
        ('danioso8', 'products', False, 'Plan FREE NO debería tener acceso a Productos (sin superuser)'),
        ('danioso8', 'patients', True, 'Plan FREE SÍ debería tener acceso a Pacientes'),
        ('danioso8', 'whatsapp', False, 'Plan FREE NO debería tener acceso a WhatsApp (sin superuser)'),
        ('danioso8', 'invoices_dian', False, 'Plan FREE NO debería tener acceso a Facturación DIAN (sin superuser)'),
        ('danioso8', 'dashboard', True, 'Plan FREE SÍ debería tener acceso a Dashboard'),
        ('danioso8', 'clinical_history', True, 'Plan FREE SÍ debería tener acceso a Historia Clínica'),
    ]
    
    print("\nCasos de prueba (lógica del plan, ignorando superuser):")
    passed = 0
    failed = 0
    
    for username, module_code, expected_access, description in test_cases:
        try:
            user = User.objects.get(username=username)
            
            # Obtener módulos del PLAN, sin considerar superuser
            subscription = UserSubscription.objects.get(user=user)
            plan_modules = PLAN_MODULES.get(subscription.plan.plan_type, [])
            actual_access_by_plan = module_code in plan_modules
            
            # Acceso real (con superuser)
            actual_access_real = has_module_access(user, module_code)
            
            if actual_access_by_plan == expected_access:
                status = "✅ PASS"
                passed += 1
            else:
                status = "❌ FAIL"
                failed += 1
                
            access_plan = "SÍ" if actual_access_by_plan else "NO"
            access_real = "SÍ" if actual_access_real else "NO"
            print(f"\n  {description}")
            print(f"  → {status} - Por plan: {access_plan} | Acceso real (superuser): {access_real}")
            
        except User.DoesNotExist:
            print(f"\n  {description}")
            print(f"  → ❌ Usuario no encontrado")
            failed += 1
        except UserSubscription.DoesNotExist:
            print(f"\n  {description}")
            print(f"  → ❌ Sin suscripción")
            failed += 1
    
    print(f"\n📊 Resumen de lógica del plan: {passed} exitosas, {failed} fallidas")

def main():
    """Función principal"""
    print_section("VERIFICACIÓN DEL SISTEMA DE CONTROL DE ACCESO A MÓDULOS")
    print("\nEste script verifica que el sistema de módulos por plan esté configurado correctamente.\n")
    
    verify_module_definitions()
    verify_plan_hierarchy()
    verify_user_access()
    test_specific_modules()
    
    print("\n" + "=" * 80)
    print("  ✅ VERIFICACIÓN COMPLETADA")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
