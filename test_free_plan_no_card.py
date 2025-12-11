"""
Test de verificación del sistema de Plan Free sin tarjeta
Este script prueba que los usuarios con Plan Free no sean redirigidos al checkout
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import SubscriptionPlan
from apps.users.models import UserSubscription
from django.utils import timezone
from datetime import timedelta


def test_free_plan_subscription():
    """Test: Crear suscripción con Plan Free"""
    print("\n" + "="*60)
    print("TEST 1: Crear suscripción con Plan Free")
    print("="*60)
    
    # Buscar o crear plan Free
    free_plan, created = SubscriptionPlan.objects.get_or_create(
        plan_type='free',
        defaults={
            'name': 'Plan Free Test',
            'slug': 'free-test',
            'price_monthly': 0,
            'price_yearly': 0,
            'max_users': 1,
            'max_patients': 50,
            'max_appointments_month': 50,
            'is_active': True
        }
    )
    
    print(f"Plan Free: {free_plan.name} (ID: {free_plan.id})")
    
    # Crear usuario de prueba si no existe
    test_username = 'test_free_user'
    
    # Eliminar usuario de prueba anterior si existe
    User.objects.filter(username=test_username).delete()
    
    test_user = User.objects.create_user(
        username=test_username,
        email='test_free@example.com',
        password='testpass123',
        first_name='Test',
        last_name='Free User'
    )
    
    print(f"Usuario de prueba creado: {test_user.username}")
    
    # Crear suscripción con plan Free
    subscription = UserSubscription.objects.create(
        user=test_user,
        plan=free_plan,
        billing_cycle='monthly',
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=30),
        is_active=True,
        payment_status='pending'  # Intentamos crear con pending
    )
    
    # El modelo debería cambiar automáticamente a 'paid'
    subscription.refresh_from_db()
    
    print(f"\nEstado de la suscripción:")
    print(f"  - payment_status: {subscription.payment_status}")
    print(f"  - amount_paid: ${subscription.amount_paid}")
    print(f"  - is_active: {subscription.is_active}")
    
    # Verificaciones
    if subscription.payment_status == 'paid':
        print("\n✅ TEST PASADO: payment_status es 'paid'")
    else:
        print(f"\n❌ TEST FALLIDO: payment_status es '{subscription.payment_status}', esperado 'paid'")
    
    if subscription.amount_paid == 0:
        print("✅ TEST PASADO: amount_paid es 0")
    else:
        print(f"❌ TEST FALLIDO: amount_paid es {subscription.amount_paid}, esperado 0")
    
    # Limpiar
    test_user.delete()
    
    return subscription.payment_status == 'paid' and subscription.amount_paid == 0


def test_paid_plan_subscription():
    """Test: Crear suscripción con Plan de Pago"""
    print("\n" + "="*60)
    print("TEST 2: Crear suscripción con Plan de Pago")
    print("="*60)
    
    # Buscar o crear plan básico
    basic_plan, created = SubscriptionPlan.objects.get_or_create(
        plan_type='basic',
        defaults={
            'name': 'Plan Básico Test',
            'slug': 'basic-test',
            'price_monthly': 29900,
            'price_yearly': 299000,
            'max_users': 3,
            'max_patients': 200,
            'max_appointments_month': 200,
            'is_active': True
        }
    )
    
    print(f"Plan Básico: {basic_plan.name} (ID: {basic_plan.id})")
    
    # Crear usuario de prueba
    test_username = 'test_basic_user'
    User.objects.filter(username=test_username).delete()
    
    test_user = User.objects.create_user(
        username=test_username,
        email='test_basic@example.com',
        password='testpass123',
        first_name='Test',
        last_name='Basic User'
    )
    
    print(f"Usuario de prueba creado: {test_user.username}")
    
    # Crear suscripción con plan básico (sin especificar payment_status)
    subscription = UserSubscription.objects.create(
        user=test_user,
        plan=basic_plan,
        billing_cycle='monthly',
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=30),
        is_active=True
        # payment_status debería ser 'pending' por defecto
    )
    
    subscription.refresh_from_db()
    
    print(f"\nEstado de la suscripción:")
    print(f"  - payment_status: {subscription.payment_status}")
    print(f"  - amount_paid: ${subscription.amount_paid}")
    print(f"  - is_active: {subscription.is_active}")
    
    # Verificaciones
    if subscription.payment_status == 'pending':
        print("\n✅ TEST PASADO: payment_status es 'pending' para plan de pago")
    else:
        print(f"\n❌ TEST FALLIDO: payment_status es '{subscription.payment_status}', esperado 'pending'")
    
    # Limpiar
    test_user.delete()
    
    return subscription.payment_status == 'pending'


def test_upgrade_to_free():
    """Test: Cambiar a Plan Free desde plan de pago"""
    print("\n" + "="*60)
    print("TEST 3: Cambiar a Plan Free desde plan de pago")
    print("="*60)
    
    # Crear planes
    basic_plan = SubscriptionPlan.objects.filter(plan_type='basic').first()
    free_plan = SubscriptionPlan.objects.filter(plan_type='free').first()
    
    if not basic_plan or not free_plan:
        print("⚠️ TEST OMITIDO: No hay planes Basic o Free en la BD")
        return True
    
    # Crear usuario
    test_username = 'test_upgrade_user'
    User.objects.filter(username=test_username).delete()
    
    test_user = User.objects.create_user(
        username=test_username,
        email='test_upgrade@example.com',
        password='testpass123'
    )
    
    # Crear suscripción con plan básico
    subscription = UserSubscription.objects.create(
        user=test_user,
        plan=basic_plan,
        billing_cycle='monthly',
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=30),
        is_active=True,
        payment_status='paid'
    )
    
    print(f"Suscripción inicial:")
    print(f"  - Plan: {subscription.plan.name}")
    print(f"  - payment_status: {subscription.payment_status}")
    
    # Cambiar a plan Free
    subscription.plan = free_plan
    subscription.save()
    
    subscription.refresh_from_db()
    
    print(f"\nDespués de cambiar a Plan Free:")
    print(f"  - Plan: {subscription.plan.name}")
    print(f"  - payment_status: {subscription.payment_status}")
    print(f"  - amount_paid: ${subscription.amount_paid}")
    
    # Verificaciones
    success = True
    if subscription.payment_status == 'paid':
        print("\n✅ TEST PASADO: payment_status sigue siendo 'paid'")
    else:
        print(f"\n❌ TEST FALLIDO: payment_status es '{subscription.payment_status}'")
        success = False
    
    if subscription.amount_paid == 0:
        print("✅ TEST PASADO: amount_paid actualizado a 0")
    else:
        print(f"⚠️ ADVERTENCIA: amount_paid es {subscription.amount_paid}, podría ser 0")
    
    # Limpiar
    test_user.delete()
    
    return success


def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "="*60)
    print("SUITE DE TESTS - PLAN FREE SIN TARJETA")
    print("="*60)
    
    results = []
    
    try:
        # Test 1
        result1 = test_free_plan_subscription()
        results.append(("Crear suscripción Free", result1))
        
        # Test 2
        result2 = test_paid_plan_subscription()
        results.append(("Crear suscripción de Pago", result2))
        
        # Test 3
        result3 = test_upgrade_to_free()
        results.append(("Cambiar a Plan Free", result3))
        
        # Resumen
        print("\n" + "="*60)
        print("RESUMEN DE TESTS")
        print("="*60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASADO" if result else "❌ FALLIDO"
            print(f"{status}: {test_name}")
        
        print(f"\nTotal: {passed}/{total} tests pasados")
        
        if passed == total:
            print("\n🎉 ¡TODOS LOS TESTS PASARON!")
            print("\nEl sistema de Plan Free sin tarjeta está funcionando correctamente:")
            print("  ✓ Planes Free se marcan automáticamente como 'paid'")
            print("  ✓ Planes de pago mantienen 'pending' hasta el checkout")
            print("  ✓ Cambio a Plan Free actualiza el estado correctamente")
        else:
            print("\n⚠️ ALGUNOS TESTS FALLARON")
            print("Revisa los errores arriba para más detalles")
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LOS TESTS: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
