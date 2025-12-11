"""
Script para probar el sistema de verificación de email
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.email_verification_models import EmailVerificationToken, UserProfile
from django.utils import timezone


def test_email_verification_system():
    """Prueba el sistema de verificación de email"""
    
    print("=" * 60)
    print("PRUEBA DEL SISTEMA DE VERIFICACIÓN DE EMAIL")
    print("=" * 60)
    
    # 1. Verificar que los modelos existan
    print("\n1. Verificando modelos...")
    try:
        token_count = EmailVerificationToken.objects.count()
        profile_count = UserProfile.objects.count()
        print(f"   ✓ EmailVerificationToken: {token_count} registros")
        print(f"   ✓ UserProfile: {profile_count} registros")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return
    
    # 2. Verificar usuarios sin verificar
    print("\n2. Usuarios sin verificar email...")
    unverified_users = User.objects.filter(
        profile__is_email_verified=False
    )
    print(f"   Total: {unverified_users.count()}")
    for user in unverified_users[:5]:
        print(f"   - {user.username} ({user.email})")
    
    # 3. Verificar tokens pendientes
    print("\n3. Tokens de verificación pendientes...")
    pending_tokens = EmailVerificationToken.objects.filter(
        is_used=False
    )
    print(f"   Total: {pending_tokens.count()}")
    for token in pending_tokens[:5]:
        expired_status = "EXPIRADO" if token.is_expired else "VÁLIDO"
        valid_status = "SÍ" if token.is_valid else "NO"
        print(f"   - {token.user.username}: {expired_status}, Válido: {valid_status}")
    
    # 4. Verificar usuarios verificados
    print("\n4. Usuarios con email verificado...")
    verified_users = User.objects.filter(
        profile__is_email_verified=True
    )
    print(f"   Total: {verified_users.count()}")
    for user in verified_users[:5]:
        profile = user.profile
        verified_date = profile.email_verified_at.strftime('%Y-%m-%d %H:%M') if profile.email_verified_at else 'N/A'
        print(f"   - {user.username}: Verificado el {verified_date}")
    
    # 5. Verificar usuarios sin perfil
    print("\n5. Usuarios sin perfil (deberían ser pocos)...")
    users_without_profile = User.objects.exclude(
        id__in=UserProfile.objects.values_list('user_id', flat=True)
    )
    print(f"   Total: {users_without_profile.count()}")
    if users_without_profile.count() > 0:
        print("   ⚠ ADVERTENCIA: Hay usuarios sin perfil. El middleware los creará automáticamente.")
        for user in users_without_profile[:5]:
            print(f"   - {user.username} ({user.email})")
    
    # 6. Estadísticas generales
    print("\n6. Estadísticas generales...")
    total_users = User.objects.count()
    verified_count = verified_users.count()
    unverified_count = unverified_users.count()
    verification_rate = (verified_count / total_users * 100) if total_users > 0 else 0
    
    print(f"   Total usuarios: {total_users}")
    print(f"   Verificados: {verified_count} ({verification_rate:.1f}%)")
    print(f"   No verificados: {unverified_count}")
    print(f"   Tokens activos: {pending_tokens.count()}")
    
    # 7. Verificar configuración de email
    print("\n7. Configuración de email...")
    from django.conf import settings
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER or '(no configurado)'}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    if not settings.EMAIL_HOST_USER:
        print("   ⚠ ADVERTENCIA: EMAIL_HOST_USER no está configurado")
        print("   Los emails NO se enviarán hasta configurar las credenciales SMTP")
    
    # 8. Verificar middleware
    print("\n8. Verificando middleware...")
    middleware = settings.MIDDLEWARE
    email_middleware = 'apps.users.email_verification_middleware.EmailVerificationMiddleware'
    if email_middleware in middleware:
        print(f"   ✓ EmailVerificationMiddleware está activo")
        print(f"   Posición: {middleware.index(email_middleware) + 1} de {len(middleware)}")
    else:
        print(f"   ✗ EmailVerificationMiddleware NO está configurado")
    
    print("\n" + "=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)


if __name__ == '__main__':
    test_email_verification_system()
