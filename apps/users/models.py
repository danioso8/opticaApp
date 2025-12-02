from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class UserSubscription(models.Model):
    """Suscripción del usuario (no de la organización)"""
    BILLING_CYCLES = [
        ('monthly', 'Mensual'),
        ('yearly', 'Anual'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey('organizations.SubscriptionPlan', on_delete=models.PROTECT)
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLES, default='monthly')
    
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=True, verbose_name='Renovación Automática')
    
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Suscripción de Usuario'
        verbose_name_plural = 'Suscripciones de Usuarios'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.billing_cycle})"
    
    def save(self, *args, **kwargs):
        # Calcular end_date si no está establecida
        if not self.end_date:
            if self.billing_cycle == 'monthly':
                self.end_date = self.start_date + timedelta(days=30)
            else:  # yearly
                self.end_date = self.start_date + timedelta(days=365)
        
        # Establecer el monto pagado según el plan
        if not self.amount_paid:
            if self.billing_cycle == 'monthly':
                self.amount_paid = self.plan.price_monthly
            else:
                self.amount_paid = self.plan.price_yearly
        
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Verifica si la suscripción ha expirado"""
        return timezone.now() > self.end_date
    
    @property
    def days_remaining(self):
        """Calcula los días restantes de la suscripción"""
        if self.is_expired:
            return 0
        delta = self.end_date - timezone.now()
        return delta.days
    
    def can_create_organizations(self):
        """Verifica si puede crear más organizaciones según su plan"""
        if not self.is_active or self.is_expired:
            return False
        
        current_orgs = self.user.owned_organizations.filter(is_active=True).count()
        max_orgs = self.plan.max_users  # Usaremos max_users como max_organizations por ahora
        
        return current_orgs < max_orgs
