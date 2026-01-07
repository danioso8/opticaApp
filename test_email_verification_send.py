"""
Script para probar el envío de email de verificación
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from apps.users.email_verification_service import send_verification_email
from apps.users.email_verification_models import UserProfile, EmailVerificationToken
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

User = get_user_model()

print('=' * 80)
print('PRUEBA DE ENVÍO DE EMAIL DE VERIFICACIÓN')
print('=' * 80)

# 1. Verificar configuración
print('\n1️⃣  CONFIGURACIÓN DE EMAIL')
print('-' * 80)
print(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
print(f'EMAIL_HOST: {settings.EMAIL_HOST}')
print(f'EMAIL_PORT: {settings.EMAIL_PORT}')
print(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
print(f'EMAIL_HOST_PASSWORD: {"✅ Configurado" if settings.EMAIL_HOST_PASSWORD else "❌ NO CONFIGURADO"}')
print(f'DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
print(f'WEBSITE_URL: {getattr(settings, "WEBSITE_URL", "NO CONFIGURADO")}')

# 2. Verificar si existe un usuario de prueba
print('\n2️⃣  VERIFICANDO USUARIO DE PRUEBA')
print('-' * 80)

test_email = 'danioso8@gmail.com'
test_users = User.objects.filter(email=test_email)

if test_users.exists():
    user = test_users.first()
    print(f'✅ Usuario de prueba encontrado:')
    print(f'   Username: {user.username}')
    print(f'   Email: {user.email}')
    print(f'   Activo: {user.is_active}')
    
    # Verificar perfil
    try:
        profile = UserProfile.objects.get(user=user)
        print(f'   Email verificado: {profile.is_email_verified}')
    except UserProfile.DoesNotExist:
        print('   ⚠️  No tiene perfil de usuario - creando...')
        profile = UserProfile.objects.create(user=user, is_email_verified=False)
        print('   ✅ Perfil creado')
else:
    print(f'⚠️  No existe usuario con email {test_email}')
    print('   Creando usuario de prueba...')
    
    user = User.objects.create_user(
        username='test_verification',
        email=test_email,
        password='Test1234!',
        first_name='Test',
        last_name='Verification',
        is_active=False
    )
    
    profile = UserProfile.objects.create(
        user=user,
        is_email_verified=False
    )
    
    print(f'✅ Usuario de prueba creado:')
    print(f'   Username: {user.username}')
    print(f'   Email: {user.email}')

# 3. Invalidar tokens anteriores
print('\n3️⃣  INVALIDANDO TOKENS ANTERIORES')
print('-' * 80)
old_tokens = EmailVerificationToken.objects.filter(user=user, is_used=False)
count = old_tokens.count()
if count > 0:
    old_tokens.update(is_used=True)
    print(f'✅ {count} token(s) anterior(es) invalidado(s)')
else:
    print('   No hay tokens anteriores')

# 4. Enviar email de verificación
print('\n4️⃣  ENVIANDO EMAIL DE VERIFICACIÓN')
print('-' * 80)

try:
    result = send_verification_email(user, request=None)
    
    if result:
        print('✅ Email de verificación enviado exitosamente')
        
        # Mostrar el token generado
        latest_token = EmailVerificationToken.objects.filter(user=user, is_used=False).latest('created_at')
        print(f'\n📧 DETALLES DEL TOKEN:')
        print(f'   Token: {latest_token.token}')
        print(f'   Expira: {latest_token.expires_at}')
        
        # Construir URL de verificación
        from django.urls import reverse
        verification_path = reverse('users:verify_email', kwargs={'token': str(latest_token.token)})
        base_url = getattr(settings, 'WEBSITE_URL', 'http://localhost:8000').rstrip('/')
        verification_url = f"{base_url}{verification_path}"
        
        print(f'\n🔗 URL DE VERIFICACIÓN:')
        print(f'   {verification_url}')
        
        print(f'\n📬 Revisa tu bandeja de entrada en: {test_email}')
        print(f'   También revisa la carpeta de SPAM/Correo no deseado')
        
    else:
        print('❌ Error al enviar el email de verificación')
        
except Exception as e:
    print(f'❌ ERROR:')
    print(f'   Tipo: {type(e).__name__}')
    print(f'   Mensaje: {str(e)}')
    import traceback
    traceback.print_exc()

# 5. Verificar que el template existe
print('\n5️⃣  VERIFICANDO TEMPLATE')
print('-' * 80)
import os
template_path = os.path.join('apps', 'users', 'templates', 'users', 'emails', 'email_verification.html')
if os.path.exists(template_path):
    print(f'✅ Template existe: {template_path}')
else:
    print(f'⚠️  Template NO encontrado: {template_path}')
    # Buscar templates alternativos
    alt_path = os.path.join('apps', 'users', 'templates', 'users', 'emails', 'verify_email.html')
    if os.path.exists(alt_path):
        print(f'✅ Template alternativo encontrado: {alt_path}')
    else:
        print('❌ No se encontró ningún template de email')

print('\n' + '=' * 80)
print('FIN DE LA PRUEBA')
print('=' * 80)
