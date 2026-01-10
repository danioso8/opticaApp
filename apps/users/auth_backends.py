"""
Backend de autenticación personalizado que permite login con email o username
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Autenticación usando email o username
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        try:
            # Buscar usuario por username o email
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
            
            # Verificar contraseña
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Ejecutar el hasher de passwords para prevenir timing attacks
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Si hay múltiples usuarios con el mismo email, usar el primero
            user = User.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).first()
            
            if user and user.check_password(password):
                return user
        
        return None
