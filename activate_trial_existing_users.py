"""
Script para activar período de prueba en usuarios existentes con Plan Free
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import UserSubscription
from django.utils import timezone
from datetime import timedelta

def activate_trial_for_existing_users():
    """Activa el período de prueba para usuarios existentes con Plan Free"""
    
    print("=" * 70)
    print("ACTIVAR PERÍODO DE PRUEBA PARA USUARIOS EXISTENTES")
    print("=" * 70)
    
    # Buscar suscripciones Free que no tienen trial activo
    free_subs = UserSubscription.objects.filter(
        plan__plan_type='free',
        is_trial=False
    ).select_related('user', 'plan')
    
    total = free_subs.count()
    
    if total == 0:
        print("\n✅ No hay usuarios con Plan Free sin trial activo")
        print("   Todos los usuarios ya tienen trial configurado")
        return
    
    print(f"\n📊 Usuarios encontrados con Plan Free: {total}")
    print(f"\n{'Usuario':<20} {'Plan':<20} {'Fecha Inicio':<20} {'Acción'}")
    print("-" * 90)
    
    updated_count = 0
    
    for sub in free_subs:
        # Activar trial
        sub.is_trial = True
        # Trial de 3 meses desde la fecha de creación de la suscripción
        sub.trial_ends_at = sub.start_date + timedelta(days=90)
        sub.payment_status = 'paid'
        sub.amount_paid = 0
        sub.save()
        
        status = "✅ Trial activado"
        print(f"{sub.user.username:<20} {sub.plan.name:<20} {sub.start_date.strftime('%Y-%m-%d'):<20} {status}")
        
        updated_count += 1
    
    print("-" * 90)
    print(f"\n✅ Total actualizado: {updated_count} suscripciones")
    
    print(f"\n💡 RESUMEN:")
    print(f"   - Trial activado: 3 meses gratis")
    print(f"   - Precio post-trial: $12 USD/mes")
    print(f"   - Estado de pago: Pagado (durante trial)")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    activate_trial_for_existing_users()
