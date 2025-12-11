"""
Script para actualizar suscripciones de planes Free que tengan payment_status='pending'
Este script corrige cualquier suscripción existente para que los usuarios con plan Free
no sean redirigidos al checkout de pago.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import UserSubscription
from apps.organizations.models import SubscriptionPlan


def fix_free_subscriptions():
    """Actualizar todas las suscripciones de planes Free con payment_status pendiente"""
    
    print("🔍 Buscando suscripciones de planes Free con payment_status='pending'...")
    
    # Buscar todas las suscripciones con plan Free que tengan payment_status='pending'
    free_plans = SubscriptionPlan.objects.filter(plan_type='free')
    
    if not free_plans.exists():
        print("⚠️ No se encontraron planes Free en el sistema.")
        return
    
    print(f"✓ Encontrados {free_plans.count()} planes Free:")
    for plan in free_plans:
        print(f"  - {plan.name} (ID: {plan.id})")
    
    # Obtener suscripciones con planes Free que estén pendientes
    pending_free_subs = UserSubscription.objects.filter(
        plan__plan_type='free',
        payment_status='pending'
    )
    
    count = pending_free_subs.count()
    
    if count == 0:
        print("\n✓ No hay suscripciones de planes Free con payment_status='pending'.")
        print("  Todas las suscripciones Free ya están correctamente configuradas.")
        return
    
    print(f"\n📝 Encontradas {count} suscripciones de planes Free con payment_status='pending'")
    print("\nActualizando...")
    
    updated = 0
    for subscription in pending_free_subs:
        print(f"\n  Usuario: {subscription.user.username}")
        print(f"  Plan: {subscription.plan.name}")
        print(f"  Estado anterior: {subscription.payment_status}")
        
        subscription.payment_status = 'paid'
        subscription.amount_paid = 0  # Planes gratuitos no tienen costo
        subscription.save()
        
        print(f"  ✓ Estado actualizado a: paid")
        updated += 1
    
    print(f"\n✅ Proceso completado: {updated} suscripciones actualizadas")
    print("\n📋 Resumen:")
    print(f"  - Planes Free en el sistema: {free_plans.count()}")
    print(f"  - Suscripciones corregidas: {updated}")
    
    # Verificar que no queden suscripciones pendientes
    remaining = UserSubscription.objects.filter(
        plan__plan_type='free',
        payment_status='pending'
    ).count()
    
    if remaining > 0:
        print(f"\n⚠️ ADVERTENCIA: Aún quedan {remaining} suscripciones Free pendientes.")
    else:
        print("\n✓ Todas las suscripciones Free ahora tienen payment_status='paid'")
        print("  Los usuarios con plan Free ya no serán redirigidos al checkout de pago.")


def verify_subscriptions():
    """Verificar el estado de todas las suscripciones"""
    print("\n\n" + "="*60)
    print("VERIFICACIÓN DE TODAS LAS SUSCRIPCIONES")
    print("="*60)
    
    all_subs = UserSubscription.objects.select_related('user', 'plan').all()
    
    if not all_subs.exists():
        print("\n⚠️ No hay suscripciones en el sistema.")
        return
    
    print(f"\nTotal de suscripciones: {all_subs.count()}\n")
    
    # Agrupar por tipo de plan y estado de pago
    by_plan = {}
    for sub in all_subs:
        plan_type = sub.plan.plan_type
        if plan_type not in by_plan:
            by_plan[plan_type] = {'pending': 0, 'paid': 0, 'failed': 0, 'cancelled': 0, 'total': 0}
        
        by_plan[plan_type][sub.payment_status] += 1
        by_plan[plan_type]['total'] += 1
    
    # Mostrar resumen
    for plan_type, stats in by_plan.items():
        print(f"\n{plan_type.upper()}:")
        print(f"  Total: {stats['total']}")
        print(f"  Pagadas: {stats['paid']}")
        print(f"  Pendientes: {stats['pending']}")
        print(f"  Fallidas: {stats['failed']}")
        print(f"  Canceladas: {stats['cancelled']}")
    
    # Advertencias
    free_pending = UserSubscription.objects.filter(
        plan__plan_type='free',
        payment_status='pending'
    ).count()
    
    if free_pending > 0:
        print(f"\n⚠️ PROBLEMA: {free_pending} suscripciones Free tienen payment_status='pending'")
        print("   Estos usuarios serán redirigidos al checkout de pago.")
    else:
        print("\n✓ Todas las suscripciones Free tienen payment_status='paid'")


if __name__ == '__main__':
    print("="*60)
    print("CORRECCIÓN DE SUSCRIPCIONES DE PLANES FREE")
    print("="*60)
    print()
    
    try:
        fix_free_subscriptions()
        verify_subscriptions()
        
        print("\n" + "="*60)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error durante el proceso: {str(e)}")
        import traceback
        traceback.print_exc()
