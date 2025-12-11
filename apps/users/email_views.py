"""
Vistas para verificación de email
"""
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .email_verification_models import EmailVerificationToken, UserProfile
from django.utils import timezone


def send_verification_email(user, request):
    """Envía email de verificación al usuario"""
    # Crear token de verificación
    token = EmailVerificationToken.objects.create(user=user)
    
    # Construir URL de verificación
    verification_url = request.build_absolute_uri(
        reverse('users:verify_email', kwargs={'token': str(token.token)})
    )
    
    # Contexto para el template
    context = {
        'user': user,
        'verification_url': verification_url,
        'site_name': 'OpticaApp',
    }
    
    # Renderizar template HTML
    html_message = render_to_string('users/emails/verify_email.html', context)
    plain_message = strip_tags(html_message)
    
    # Enviar email
    try:
        send_mail(
            subject='Verifica tu correo electrónico - OpticaApp',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email de verificación: {e}")
        return False


def verify_email(request, token):
    """Verifica el email del usuario con el token"""
    try:
        verification_token = EmailVerificationToken.objects.get(token=token)
        
        # Verificar si el token es válido
        if verification_token.is_used:
            messages.warning(request, 'Este enlace de verificación ya fue utilizado.')
            return redirect('organizations:login')
        
        if verification_token.is_expired:
            messages.error(request, 'Este enlace de verificación ha expirado. Por favor solicita uno nuevo.')
            return redirect('organizations:login')
        
        # Marcar token como usado
        verification_token.is_used = True
        verification_token.save()
        
        # Activar usuario y marcar email como verificado
        user = verification_token.user
        user.is_active = True
        user.save()
        
        # Actualizar perfil
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.is_email_verified = True
        profile.email_verified_at = timezone.now()
        profile.save()
        
        # Verificar si el usuario tiene una suscripción pendiente de pago
        from apps.users.models import UserSubscription
        from django.contrib.auth import login
        
        pending_subscription = UserSubscription.objects.filter(
            user=user,
            payment_status='pending'
        ).first()
        
        if pending_subscription:
            # Login automático para redirigir al checkout
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            messages.success(request, '¡Email verificado! Ahora completa el pago de tu suscripción.')
            return redirect('users:subscription_checkout', plan_id=pending_subscription.plan.id)
        else:
            messages.success(request, '¡Tu correo electrónico ha sido verificado exitosamente! Ahora puedes iniciar sesión.')
            return redirect('dashboard:login')
        
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'El enlace de verificación no es válido.')
        return redirect('dashboard:login')


def resend_verification_email(request):
    """Reenvía el email de verificación"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Verificar si ya está verificado
            profile = UserProfile.objects.filter(user=user).first()
            if profile and profile.is_email_verified:
                messages.info(request, 'Tu correo electrónico ya está verificado. Puedes iniciar sesión.')
                return redirect('dashboard:login')
            
            # Invalidar tokens anteriores
            EmailVerificationToken.objects.filter(user=user, is_used=False).update(is_used=True)
            
            # Enviar nuevo email
            if send_verification_email(user, request):
                messages.success(request, 'Se ha enviado un nuevo correo de verificación. Por favor revisa tu bandeja de entrada.')
            else:
                messages.error(request, 'Hubo un error al enviar el correo. Por favor intenta más tarde.')
                
        except User.DoesNotExist:
            # Por seguridad, no revelamos si el email existe o no
            messages.info(request, 'Si el correo existe en nuestro sistema, recibirás un email de verificación.')
        
        return redirect('dashboard:login')
    
    return render(request, 'users/resend_verification.html')


def verification_pending(request):
    """Vista que muestra mensaje de verificación pendiente"""
    return render(request, 'users/verification_pending.html')
