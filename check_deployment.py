"""
Script de verificación pre-despliegue
Verifica que todos los sistemas estén listos para producción
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from apps.users.email_verification_models import UserProfile, EmailVerificationToken
from apps.users.models import UserSubscription, PaymentMethod, Transaction
from apps.organizations.models import SubscriptionPlan


def check_deployment_readiness():
    """Verifica que todo esté listo para despliegue"""
    
    print("=" * 70)
    print("VERIFICACIÓN PRE-DESPLIEGUE A RENDER")
    print("=" * 70)
    
    issues = []
    warnings = []
    success = []
    
    # 1. Base de Datos
    print("\n📊 1. VERIFICACIÓN DE BASE DE DATOS")
    print("-" * 70)
    
    try:
        # Verificar tablas de pagos
        payment_count = PaymentMethod.objects.count()
        transaction_count = Transaction.objects.count()
        subscription_count = UserSubscription.objects.count()
        print(f"   ✓ Tabla PaymentMethod: {payment_count} registros")
        print(f"   ✓ Tabla Transaction: {transaction_count} registros")
        print(f"   ✓ Tabla UserSubscription: {subscription_count} registros")
        success.append("Tablas de pagos Wompi")
        
        # Verificar tablas de verificación
        profile_count = UserProfile.objects.count()
        token_count = EmailVerificationToken.objects.count()
        print(f"   ✓ Tabla UserProfile: {profile_count} registros")
        print(f"   ✓ Tabla EmailVerificationToken: {token_count} registros")
        success.append("Tablas de verificación de email")
        
    except Exception as e:
        issues.append(f"Error en base de datos: {e}")
        print(f"   ✗ Error: {e}")
    
    # 2. Usuarios
    print("\n👥 2. VERIFICACIÓN DE USUARIOS")
    print("-" * 70)
    
    total_users = User.objects.count()
    users_with_profile = UserProfile.objects.count()
    verified_users = UserProfile.objects.filter(is_email_verified=True).count()
    
    print(f"   Total usuarios: {total_users}")
    print(f"   Con perfil: {users_with_profile}")
    print(f"   Verificados: {verified_users}")
    
    if total_users != users_with_profile:
        warnings.append(f"{total_users - users_with_profile} usuarios sin perfil")
        print(f"   ⚠ {total_users - users_with_profile} usuarios sin perfil (se crearán automáticamente)")
    else:
        print("   ✓ Todos los usuarios tienen perfil")
        success.append("Todos los usuarios tienen perfil")
    
    # 3. Planes de Suscripción
    print("\n💳 3. VERIFICACIÓN DE PLANES")
    print("-" * 70)
    
    try:
        plans = SubscriptionPlan.objects.filter(is_active=True)
        plan_count = plans.count()
        
        if plan_count == 0:
            issues.append("No hay planes de suscripción activos")
            print("   ✗ No hay planes de suscripción activos")
        else:
            print(f"   ✓ {plan_count} planes activos:")
            for plan in plans:
                print(f"      - {plan.name}: ${plan.price_monthly}/mes")
            success.append(f"{plan_count} planes de suscripción activos")
    except Exception as e:
        issues.append(f"Error al verificar planes: {e}")
        print(f"   ✗ Error: {e}")
    
    # 4. Configuración de Wompi
    print("\n💰 4. CONFIGURACIÓN DE WOMPI")
    print("-" * 70)
    
    wompi_test_mode = getattr(settings, 'WOMPI_TEST_MODE', True)
    wompi_public_test = getattr(settings, 'WOMPI_PUBLIC_KEY_TEST', '')
    wompi_private_test = getattr(settings, 'WOMPI_PRIVATE_KEY_TEST', '')
    wompi_public_prod = getattr(settings, 'WOMPI_PUBLIC_KEY', '')
    wompi_private_prod = getattr(settings, 'WOMPI_PRIVATE_KEY', '')
    
    print(f"   Modo: {'PRUEBA' if wompi_test_mode else 'PRODUCCIÓN'}")
    
    if wompi_test_mode:
        if wompi_public_test and wompi_public_test != 'pub_test_tu_llave_aqui':
            print(f"   ✓ Public Key Test: Configurada")
            success.append("Wompi Public Key Test")
        else:
            warnings.append("Wompi Public Key Test no configurada")
            print(f"   ⚠ Public Key Test: NO CONFIGURADA")
        
        if wompi_private_test and wompi_private_test != 'prv_test_tu_llave_aqui':
            print(f"   ✓ Private Key Test: Configurada")
            success.append("Wompi Private Key Test")
        else:
            warnings.append("Wompi Private Key Test no configurada")
            print(f"   ⚠ Private Key Test: NO CONFIGURADA")
    else:
        if wompi_public_prod and wompi_public_prod != 'pub_prod_tu_llave_aqui':
            print(f"   ✓ Public Key Prod: Configurada")
            success.append("Wompi Public Key Producción")
        else:
            issues.append("Wompi Public Key Producción no configurada")
            print(f"   ✗ Public Key Prod: NO CONFIGURADA")
        
        if wompi_private_prod and wompi_private_prod != 'prv_prod_tu_llave_aqui':
            print(f"   ✓ Private Key Prod: Configurada")
            success.append("Wompi Private Key Producción")
        else:
            issues.append("Wompi Private Key Producción no configurada")
            print(f"   ✗ Private Key Prod: NO CONFIGURADA")
    
    # 5. Configuración de Email
    print("\n📧 5. CONFIGURACIÓN DE EMAIL")
    print("-" * 70)
    
    email_backend = settings.EMAIL_BACKEND
    email_host = settings.EMAIL_HOST
    email_port = settings.EMAIL_PORT
    email_user = settings.EMAIL_HOST_USER
    email_password = settings.EMAIL_HOST_PASSWORD
    default_from = settings.DEFAULT_FROM_EMAIL
    
    print(f"   Backend: {email_backend}")
    print(f"   Host: {email_host}:{email_port}")
    print(f"   From: {default_from}")
    
    if email_user and email_user != 'tu_email@gmail.com':
        print(f"   ✓ Email User: {email_user}")
        success.append("Email User configurado")
    else:
        issues.append("EMAIL_HOST_USER no configurado")
        print(f"   ✗ Email User: NO CONFIGURADO")
    
    if email_password and email_password != 'tu_app_password_gmail':
        print(f"   ✓ Email Password: Configurada")
        success.append("Email Password configurada")
    else:
        issues.append("EMAIL_HOST_PASSWORD no configurado")
        print(f"   ✗ Email Password: NO CONFIGURADA")
    
    # 6. Middleware
    print("\n🔧 6. VERIFICACIÓN DE MIDDLEWARE")
    print("-" * 70)
    
    middleware = settings.MIDDLEWARE
    
    required_middleware = [
        ('apps.organizations.middleware.TenantMiddleware', 'Tenant'),
        ('apps.users.email_verification_middleware.EmailVerificationMiddleware', 'Email Verification'),
        ('apps.organizations.middleware.SubscriptionMiddleware', 'Subscription'),
    ]
    
    for mw_path, mw_name in required_middleware:
        if mw_path in middleware:
            position = middleware.index(mw_path) + 1
            print(f"   ✓ {mw_name}: Activo (posición {position}/{len(middleware)})")
            success.append(f"Middleware {mw_name}")
        else:
            issues.append(f"Middleware {mw_name} no está configurado")
            print(f"   ✗ {mw_name}: NO CONFIGURADO")
    
    # 7. URLs
    print("\n🔗 7. VERIFICACIÓN DE URLS")
    print("-" * 70)
    
    try:
        from django.urls import get_resolver
        resolver = get_resolver()
        
        required_urls = [
            ('users:verify_email', 'Verificación de email'),
            ('users:resend_verification', 'Reenvío de verificación'),
            ('users:subscription_checkout', 'Checkout de suscripción'),
            ('users:wompi_webhook', 'Webhook de Wompi'),
        ]
        
        for url_name, description in required_urls:
            try:
                resolver.reverse(url_name, args=['test'] if 'verify_email' in url_name or 'checkout' in url_name else [])
                print(f"   ✓ {description}: Configurada")
                success.append(f"URL {description}")
            except:
                issues.append(f"URL {description} no está configurada")
                print(f"   ✗ {description}: NO CONFIGURADA")
    except Exception as e:
        warnings.append(f"No se pudieron verificar las URLs: {e}")
        print(f"   ⚠ No se pudieron verificar: {e}")
    
    # 8. Configuración de Seguridad
    print("\n🔐 8. CONFIGURACIÓN DE SEGURIDAD")
    print("-" * 70)
    
    debug = settings.DEBUG
    secret_key = settings.SECRET_KEY
    allowed_hosts = settings.ALLOWED_HOSTS
    
    if debug:
        warnings.append("DEBUG está activado (debe ser False en producción)")
        print(f"   ⚠ DEBUG: True (debe ser False en producción)")
    else:
        print(f"   ✓ DEBUG: False")
        success.append("DEBUG desactivado")
    
    if 'django-insecure' in secret_key:
        issues.append("SECRET_KEY usando valor por defecto inseguro")
        print(f"   ✗ SECRET_KEY: Usando valor por defecto (INSEGURO)")
    else:
        print(f"   ✓ SECRET_KEY: Configurada")
        success.append("SECRET_KEY segura")
    
    if allowed_hosts and allowed_hosts != ['*']:
        print(f"   ✓ ALLOWED_HOSTS: {len(allowed_hosts)} hosts configurados")
        success.append("ALLOWED_HOSTS configurado")
    else:
        warnings.append("ALLOWED_HOSTS muy permisivo")
        print(f"   ⚠ ALLOWED_HOSTS: Muy permisivo")
    
    # RESUMEN FINAL
    print("\n" + "=" * 70)
    print("RESUMEN DE VERIFICACIÓN")
    print("=" * 70)
    
    print(f"\n✅ ÉXITOS: {len(success)}")
    for item in success[:5]:
        print(f"   • {item}")
    if len(success) > 5:
        print(f"   ... y {len(success) - 5} más")
    
    if warnings:
        print(f"\n⚠️  ADVERTENCIAS: {len(warnings)}")
        for warning in warnings:
            print(f"   • {warning}")
    
    if issues:
        print(f"\n❌ PROBLEMAS CRÍTICOS: {len(issues)}")
        for issue in issues:
            print(f"   • {issue}")
    
    # Veredicto final
    print("\n" + "=" * 70)
    if not issues:
        if warnings:
            print("🟡 ESTADO: LISTO CON ADVERTENCIAS")
            print("El sistema puede desplegarse, pero revisa las advertencias.")
        else:
            print("🟢 ESTADO: LISTO PARA DESPLIEGUE")
            print("¡Todo está configurado correctamente!")
    else:
        print("🔴 ESTADO: NO LISTO PARA DESPLIEGUE")
        print("Debes resolver los problemas críticos antes de desplegar.")
    
    print("=" * 70)
    
    return len(issues) == 0


if __name__ == '__main__':
    ready = check_deployment_readiness()
    exit(0 if ready else 1)
