from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid

# Importar modelos de verificación de email
from .email_verification_models import EmailVerificationToken, UserProfile


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


class PaymentMethod(models.Model):
    """Método de pago del usuario (tarjetas tokenizadas)"""
    CARD_TYPES = [
        ('CREDIT', 'Crédito'),
        ('DEBIT', 'Débito'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    
    # Token de Wompi (no guardamos datos sensibles de la tarjeta)
    wompi_token_id = models.CharField(max_length=255, unique=True)
    
    # Información de la tarjeta (solo últimos 4 dígitos y tipo)
    card_last_four = models.CharField(max_length=4)
    card_brand = models.CharField(max_length=50)  # VISA, MASTERCARD, etc.
    card_type = models.CharField(max_length=10, choices=CARD_TYPES, default='CREDIT')
    card_holder_name = models.CharField(max_length=255)
    
    # Información adicional
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.card_brand} **** {self.card_last_four} ({self.user.username})"
    
    def save(self, *args, **kwargs):
        # Si es el método por defecto, desactivar otros
        if self.is_default:
            PaymentMethod.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Transaction(models.Model):
    """Registro de transacciones de pago"""
    TRANSACTION_STATUS = [
        ('PENDING', 'Pendiente'),
        ('APPROVED', 'Aprobada'),
        ('DECLINED', 'Rechazada'),
        ('VOIDED', 'Anulada'),
        ('ERROR', 'Error'),
    ]
    
    TRANSACTION_TYPES = [
        ('subscription_payment', 'Pago de Suscripción'),
        ('subscription_renewal', 'Renovación de Suscripción'),
        ('refund', 'Reembolso'),
    ]
    
    # Identificadores
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wompi_transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    
    # Relaciones
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Información de la transacción
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES, default='subscription_payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='COP')
    
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='PENDING')
    status_message = models.TextField(blank=True)
    
    # Información de Wompi
    wompi_reference = models.CharField(max_length=255, blank=True)
    wompi_payment_method_type = models.CharField(max_length=50, blank=True)
    wompi_payment_link_id = models.CharField(max_length=255, blank=True)
    
    # Metadatos (TextField - se guarda como JSON string para compatibilidad SQLite/PostgreSQL)
    metadata = models.TextField(blank=True, default='')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['wompi_transaction_id']),
        ]
    
    def __str__(self):
        return f"Transaction {self.id} - {self.user.username} - {self.amount} {self.currency}"
    
    def mark_as_approved(self, wompi_transaction_id=None, processed_at=None):
        """Marca la transacción como aprobada"""
        self.status = 'APPROVED'
        if wompi_transaction_id:
            self.wompi_transaction_id = wompi_transaction_id
        self.processed_at = processed_at or timezone.now()
        self.save()
    
    def mark_as_declined(self, reason=''):
        """Marca la transacción como rechazada"""
        self.status = 'DECLINED'
        self.status_message = reason
        self.processed_at = timezone.now()
        self.save()


class SubscriptionRenewalLog(models.Model):
    """Log de intentos de renovación automática"""
    STATUS_CHOICES = [
        ('success', 'Exitoso'),
        ('failed', 'Fallido'),
        ('pending', 'Pendiente'),
        ('skipped', 'Omitido'),
    ]
    
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, related_name='renewal_logs')
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount_attempted = models.DecimalField(max_digits=10, decimal_places=2)
    
    error_message = models.TextField(blank=True)
    email_sent = models.BooleanField(default=False)
    
    attempted_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Log de Renovación'
        verbose_name_plural = 'Logs de Renovación'
        ordering = ['-attempted_at']
    
    def __str__(self):
        return f"Renewal {self.subscription} - {self.status} - {self.attempted_at}"
