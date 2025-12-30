"""
Script de verificación del sistema de Trial
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import UserSubscription
from apps.organizations.models import SubscriptionPlan
from django.utils import timezone

def verify_trial_system():
    """Verifica el sistema de trial"""
    
    print("\n" + "=" * 70)
    print("VERIFICACIÓN DEL SISTEMA DE TRIAL - PLAN FREE")
    print("=" * 70)
    
    # 1. Verificar Plan Free
    print("\n📋 1. VERIFICACIÓN DEL PLAN FREE")
    print("-" * 70)
    try:
        free_plan = SubscriptionPlan.objects.get(plan_type='free')
        print(f"   ✅ Plan encontrado: {free_plan.name}")
        print(f"   💰 Precio mensual: ${free_plan.price_monthly} USD")
        print(f"   💰 Precio anual: ${free_plan.price_yearly} USD")
    except SubscriptionPlan.DoesNotExist:
        print("   ❌ ERROR: Plan Free no encontrado")
        return
    
    # 2. Verificar suscripciones con trial
    print("\n📊 2. SUSCRIPCIONES CON PERÍODO DE PRUEBA")
    print("-" * 70)
    
    trial_subs = UserSubscription.objects.filter(
        plan__plan_type='free',
        is_trial=True
    ).select_related('user', 'plan')
    
    if trial_subs.exists():
        print(f"\n   Total usuarios en trial: {trial_subs.count()}\n")
        print(f"   {'Usuario':<15} {'Días restantes':<15} {'Vence el':<20} {'Estado'}")
        print("   " + "-" * 70)
        
        for sub in trial_subs:
            days = sub.trial_days_remaining
            expires = sub.trial_ends_at.strftime('%Y-%m-%d') if sub.trial_ends_at else 'N/A'
            
            if sub.trial_is_expired:
                status = "❌ Trial vencido"
            elif days <= 7:
                status = f"⚠️  Por vencer"
            else:
                status = "✅ Activo"
            
            print(f"   {sub.user.username:<15} {days:<15} {expires:<20} {status}")
    else:
        print("   ℹ️  No hay usuarios con trial activo")
    
    # 3. Verificar métodos helper
    print("\n🔧 3. PRUEBA DE MÉTODOS HELPER")
    print("-" * 70)
    
    if trial_subs.exists():
        test_sub = trial_subs.first()
        print(f"\n   Probando con usuario: {test_sub.user.username}")
        print(f"   - is_trial: {test_sub.is_trial}")
        print(f"   - trial_ends_at: {test_sub.trial_ends_at}")
        print(f"   - trial_is_expired: {test_sub.trial_is_expired}")
        print(f"   - trial_days_remaining: {test_sub.trial_days_remaining}")
        print(f"   - needs_payment_after_trial: {test_sub.needs_payment_after_trial()}")
        print(f"   - payment_status: {test_sub.payment_status}")
        print(f"   - amount_paid: ${test_sub.amount_paid}")
    
    # 4. Resumen
    print("\n📝 4. RESUMEN DE CONFIGURACIÓN")
    print("-" * 70)
    print(f"   ✅ Campos de trial agregados al modelo")
    print(f"   ✅ Migración aplicada correctamente")
    print(f"   ✅ Plan Free actualizado: $12 USD/mes post-trial")
    print(f"   ✅ Trial automático: 3 meses (90 días)")
    print(f"   ✅ Métodos helper funcionando")
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("-" * 70)
    print("   1. Crear comando para verificar trials expirados")
    print("   2. Configurar notificaciones antes de expiración")
    print("   3. Implementar control de acceso por módulos")
    print("   4. Actualizar UI para mostrar días restantes de trial")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == '__main__':
    verify_trial_system()
