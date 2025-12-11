"""
Script para verificación final completa del sistema
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


def final_check():
    """Verificación final de todos los sistemas"""
    
    print("=" * 70)
    print("VERIFICACIÓN FINAL DEL SISTEMA")
    print("=" * 70)
    
    all_ok = True
    
    # 1. Base de Datos
    print("\n✅ 1. BASE DE DATOS")
    try:
        print(f"   - Usuarios: {User.objects.count()}")
        print(f"   - Perfiles: {UserProfile.objects.count()}")
        print(f"   - Planes: {SubscriptionPlan.objects.filter(is_active=True).count()}")
        print(f"   - Suscripciones: {UserSubscription.objects.count()}")
        print(f"   - Transacciones: {Transaction.objects.count()}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        all_ok = False
    
    # 2. Configuración Email
    print("\n✅ 2. CONFIGURACIÓN DE EMAIL")
    print(f"   - Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    print(f"   - Usuario: {settings.EMAIL_HOST_USER}")
    print(f"   - TLS: {settings.EMAIL_USE_TLS}")
    
    if settings.EMAIL_HOST_USER == 'compueasys@gmail.com':
        print(f"   ✓ Credenciales configuradas correctamente")
    else:
        print(f"   ⚠ Credenciales por defecto")
    
    # 3. Configuración Wompi
    print("\n✅ 3. CONFIGURACIÓN DE WOMPI")
    print(f"   - Modo: {'SANDBOX' if settings.WOMPI_TEST_MODE else 'PRODUCCIÓN'}")
    print(f"   - Base URL: {settings.WOMPI_BASE_URL}")
    
    if settings.WOMPI_PUBLIC_KEY.startswith('pub_test_'):
        print(f"   ✓ Llaves de sandbox configuradas")
    else:
        print(f"   ⚠ Llaves no configuradas o producción")
    
    # 4. Middleware
    print("\n✅ 4. MIDDLEWARE")
    middlewares_check = {
        'TenantMiddleware': 'apps.organizations.middleware.TenantMiddleware',
        'EmailVerificationMiddleware': 'apps.users.email_verification_middleware.EmailVerificationMiddleware',
        'SubscriptionMiddleware': 'apps.organizations.middleware.SubscriptionMiddleware',
    }
    
    for name, path in middlewares_check.items():
        if path in settings.MIDDLEWARE:
            print(f"   ✓ {name}")
        else:
            print(f"   ✗ {name} NO configurado")
            all_ok = False
    
    # 5. URLs
    print("\n✅ 5. URLS REGISTRADAS")
    from django.urls import get_resolver
    resolver = get_resolver()
    
    urls_check = {
        'Verificación Email': 'users:verify_email',
        'Reenvío Verificación': 'users:resend_verification',
        'Pending Verificación': 'users:verification_pending',
        'Checkout Wompi': 'users:subscription_checkout',
        'Webhook Wompi': 'users:wompi_webhook',
    }
    
    for name, url_name in urls_check.items():
        try:
            # Intentar resolver con argumentos dummy
            if 'verify_email' in url_name or 'checkout' in url_name:
                resolver.reverse(url_name, args=['00000000-0000-0000-0000-000000000000'] if 'verify' in url_name else ['1'])
            else:
                resolver.reverse(url_name)
            print(f"   ✓ {name}")
        except:
            print(f"   ✗ {name} NO configurada")
            all_ok = False
    
    # 6. Templates
    print("\n✅ 6. TEMPLATES")
    from django.template.loader import get_template
    
    templates_check = [
        'users/verification_pending.html',
        'users/resend_verification.html',
        'users/emails/verify_email.html',
        'users/subscription_checkout.html',
    ]
    
    for template_name in templates_check:
        try:
            get_template(template_name)
            print(f"   ✓ {template_name}")
        except:
            print(f"   ✗ {template_name} NO encontrado")
            all_ok = False
    
    # 7. Usuarios Verificados
    print("\n✅ 7. ESTADO DE USUARIOS")
    total_users = User.objects.count()
    verified_users = UserProfile.objects.filter(is_email_verified=True).count()
    percentage = (verified_users / total_users * 100) if total_users > 0 else 0
    
    print(f"   - Total: {total_users}")
    print(f"   - Verificados: {verified_users} ({percentage:.0f}%)")
    
    if percentage == 100:
        print(f"   ✓ Todos los usuarios están verificados")
    
    # Resumen Final
    print("\n" + "=" * 70)
    if all_ok:
        print("🎉 SISTEMA COMPLETAMENTE LISTO")
        print("=" * 70)
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Probar registro: http://localhost:8000/organizations/register/")
        print("   2. Verificar email recibido")
        print("   3. Hacer clic en enlace de verificación")
        print("   4. Iniciar sesión y probar checkout de plan")
        print("\n💡 Scripts disponibles:")
        print("   - python test_send_email.py - Probar envío de email")
        print("   - python test_wompi_config.py - Verificar Wompi")
        print("   - python test_email_verification.py - Verificar sistema email")
    else:
        print("⚠️ ALGUNOS CHECKS FALLARON")
        print("=" * 70)
        print("Revisa los errores marcados con ✗")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    final_check()
