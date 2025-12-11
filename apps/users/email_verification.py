"""
Modelo para tokens de verificación de email
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from datetime import timedelta


class EmailVerificationToken(models.Model):
    """Token para verificar email del usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification_token')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Token de Verificación de Email'
        verbose_name_plural = 'Tokens de Verificación de Email'
    
    def __str__(self):
        return f"{self.user.username} - {'Verificado' if self.is_verified else 'Pendiente'}"
    
    @property
    def is_expired(self):
        """Verifica si el token ha expirado (24 horas)"""
        if self.is_verified:
            return False
        expiry_time = self.created_at + timedelta(hours=24)
        return timezone.now() > expiry_time
    
    def verify(self):
        """Marca el email como verificado"""
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save()
        
        # Actualizar el usuario
        self.user.is_active = True
        self.user.save()
