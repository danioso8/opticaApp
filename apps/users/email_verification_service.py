"""
Servicio para verificación de email
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from .email_verification_models import EmailVerificationToken, UserProfile
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def create_user_profile(user):
    """Crea el perfil de usuario si no existe"""
    profile, created = UserProfile.objects.get_or_create(user=user)
    return profile


def send_verification_email(user, request=None):
    """
    Envía email de verificación al usuario
    
    Args:
        user: Usuario a verificar
        request: Request object para construir URL absoluta
        
    Returns:
        bool: True si el email se envió correctamente
    """
    try:
        # Crear token de verificación
        token = EmailVerificationToken.objects.create(user=user)
        
        # Construir URL de verificación
        verification_path = reverse('users:verify_email', kwargs={'token': str(token.token)})
        
        if request:
            verification_url = request.build_absolute_uri(verification_path)
        else:
            base_url = settings.WEBSITE_URL.rstrip('/')
            verification_url = f"{base_url}{verification_path}"
        
        # Renderizar email
        html_message = render_to_string('users/emails/email_verification.html', {
            'user': user,
            'verification_url': verification_url,
            'expires_hours': 24,
        })
        
        # Enviar email
        send_mail(
            subject='Verifica tu cuenta - OpticaApp',
            message=f'Por favor verifica tu cuenta haciendo clic en el siguiente enlace: {verification_url}',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Email de verificación enviado a {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Error al enviar email de verificación a {user.email}: {str(e)}")
        return False


def verify_email_token(token_str):
    """
    Verifica un token de email
    
    Args:
        token_str: Token UUID como string
        
    Returns:
        tuple: (success: bool, message: str, user: User|None)
    """
    try:
        token = EmailVerificationToken.objects.get(token=token_str)
        
        if token.is_used:
            return False, "Este link de verificación ya ha sido usado.", None
        
        if token.is_expired:
            return False, "Este link de verificación ha expirado. Por favor solicita uno nuevo.", None
        
        # Marcar token como usado
        token.is_used = True
        token.save()
        
        # Actualizar perfil del usuario
        profile, created = UserProfile.objects.get_or_create(user=token.user)
        profile.is_email_verified = True
        profile.email_verified_at = timezone.now()
        profile.save()
        
        logger.info(f"Email verificado para usuario: {token.user.username}")
        return True, "¡Email verificado exitosamente! Ya puedes acceder a tu cuenta.", token.user
        
    except EmailVerificationToken.DoesNotExist:
        return False, "Link de verificación inválido.", None
    except Exception as e:
        logger.error(f"Error al verificar token: {str(e)}")
        return False, f"Error al verificar el email: {str(e)}", None


def resend_verification_email(user, request=None):
    """
    Reenvía email de verificación
    
    Args:
        user: Usuario
        request: Request object
        
    Returns:
        bool: True si se envió correctamente
    """
    # Invalidar tokens anteriores no usados
    EmailVerificationToken.objects.filter(
        user=user,
        is_used=False
    ).update(is_used=True)
    
    # Enviar nuevo email
    return send_verification_email(user, request)


def is_email_verified(user):
    """
    Verifica si el email del usuario está verificado
    
    Args:
        user: Usuario a verificar
        
    Returns:
        bool: True si está verificado
    """
    try:
        return user.profile.is_email_verified
    except UserProfile.DoesNotExist:
        return False
