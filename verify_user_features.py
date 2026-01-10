from django.contrib.auth import get_user_model
from apps.users.models import UserSubscription

User = get_user_model()

user = User.objects.get(username='danioso8329')
print(f'Usuario: {user.username}')

try:
    sub = UserSubscription.objects.get(user=user)
    print(f'Plan: {sub.plan.name}')
    print(f'Activa: {sub.is_active}')
    
    # Features que el usuario dice que NO tiene acceso
    features_to_check = [
        ('electronic_invoicing', 'Facturación Electrónica'),
        ('payroll_dian', 'Nómina Electrónica'),
        ('promotions', 'Promociones'),
        ('workflows', 'Workflows'),
        ('reports_basic', 'Reportes'),
        ('dashboard', 'Dashboard'),
    ]
    
    print(f'\n=== Verificación de Features ===')
    for code, name in features_to_check:
        # Verificar desde el plan
        has_it = sub.plan.has_feature(code)
        status = "✓ TIENE ACCESO" if has_it else "✗ SIN ACCESO"
        print(f'{name} ({code}): {status}')
        
except UserSubscription.DoesNotExist:
    print('❌ No tiene suscripción activa')
except Exception as e:
    print(f'❌ Error: {e}')
