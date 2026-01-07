"""
Script para simular un registro completo de usuario y verificar el email
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.email_views import send_verification_email
from apps.users.email_verification_models import UserProfile
from apps.organizations.models import SubscriptionPlan
from apps.users.models import UserSubscription
from django.test import RequestFactory

User = get_user_model()

print('=' * 80)
print('SIMULACIÓN DE REGISTRO COMPLETO DE USUARIO')
print('=' * 80)

# Simular un request para construir URL absoluta
factory = RequestFactory()
request = factory.get('/')
request.META['HTTP_HOST'] = 'opticaapp-4e16.onrender.com'
request.META['wsgi.url_scheme'] = 'https'

# Datos del nuevo usuario
username = f'usuario_prueba_{int(os.urandom(4).hex(), 16)}'
email = 'danioso8@gmail.com'
password = 'Password123!'

print(f'\n1️⃣  CREANDO USUARIO')
print('-' * 80)
print(f'Username: {username}')
print(f'Email: {email}')

# Verificar si ya existe
if User.objects.filter(username=username).exists():
    print(f'⚠️  Usuario ya existe, usando uno existente')
    user = User.objects.get(username=username)
else:
    # Crear usuario inactivo (como en el registro real)
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name='Usuario',
        last_name='Prueba',
        is_active=False  # Inactivo hasta verificar email
    )
    print(f'✅ Usuario creado (ID: {user.id})')

print(f'\n2️⃣  CREANDO PERFIL DE USUARIO')
print('-' * 80)
profile, created = UserProfile.objects.get_or_create(
    user=user,
    defaults={'is_email_verified': False}
)
if created:
    print('✅ Perfil de usuario creado')
else:
    print('⚠️  Perfil ya existía')
print(f'Email verificado: {profile.is_email_verified}')

print(f'\n3️⃣  ASIGNANDO PLAN DE SUSCRIPCIÓN')
print('-' * 80)
try:
    # Buscar plan gratuito
    free_plan = SubscriptionPlan.objects.filter(plan_type='free', is_active=True).first()
    
    if free_plan:
        subscription, created = UserSubscription.objects.get_or_create(
            user=user,
            defaults={
                'plan': free_plan,
                'billing_cycle': 'monthly',
                'payment_status': 'paid'  # Plan gratuito ya está "pagado"
            }
        )
        if created:
            print(f'✅ Suscripción creada: {free_plan.name}')
        else:
            print(f'⚠️  Suscripción ya existía: {free_plan.name}')
    else:
        print('⚠️  No se encontró plan gratuito')
except Exception as e:
    print(f'❌ Error al crear suscripción: {e}')

print(f'\n4️⃣  ENVIANDO EMAIL DE VERIFICACIÓN')
print('-' * 80)

try:
    result = send_verification_email(user, request)
    
    if result:
        print('✅ Email de verificación enviado exitosamente')
        
        # Obtener el token generado
        from apps.users.email_verification_models import EmailVerificationToken
        latest_token = EmailVerificationToken.objects.filter(
            user=user, 
            is_used=False
        ).latest('created_at')
        
        print(f'\n📧 DETALLES:')
        print(f'   Para: {email}')
        print(f'   Token: {latest_token.token}')
        print(f'   Expira: {latest_token.expires_at}')
        
        # Construir URL
        from django.urls import reverse
        verification_path = reverse('users:verify_email', kwargs={'token': str(latest_token.token)})
        verification_url = f"https://opticaapp-4e16.onrender.com{verification_path}"
        
        print(f'\n🔗 URL DE VERIFICACIÓN:')
        print(f'   {verification_url}')
        
        print(f'\n📬 Revisa tu email en: {email}')
        print(f'   También revisa SPAM si no aparece en la bandeja principal')
        
        print(f'\n💡 ESTADO DEL USUARIO:')
        print(f'   is_active: {user.is_active} (debe ser False hasta verificar)')
        print(f'   is_email_verified: {profile.is_email_verified} (debe ser False)')
        
        print(f'\n✅ PROCESO COMPLETADO')
        print(f'   El usuario puede hacer clic en el enlace del email para activar su cuenta')
        
    else:
        print('❌ Error al enviar email de verificación')
        
except Exception as e:
    print(f'❌ ERROR:')
    print(f'   {type(e).__name__}: {str(e)}')
    import traceback
    traceback.print_exc()

print('\n' + '=' * 80)
print('FIN DE LA SIMULACIÓN')
print('=' * 80)
