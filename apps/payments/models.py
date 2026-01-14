# -*- coding: utf-8 -*-
"""
Modelos para gestión de pagos y facturación
"""
from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid


class PaymentMethod(models.Model):
    """
    Métodos de pago guardados por una organización
    """
    PAYMENT_TYPES = [
        ('card', 'Tarjeta de Crédito/Débito'),
        ('pse', 'PSE'),
        ('nequi', 'Nequi'),
        ('daviplata', 'Daviplata'),
        ('paypal', 'PayPal'),
    ]
    
    CARD_BRANDS = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
        ('diners', 'Diners Club'),
    ]
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    
    # Para tarjetas
    card_brand = models.CharField(max_length=20, choices=CARD_BRANDS, null=True, blank=True)
    last_four = models.CharField(max_length=4, null=True, blank=True)
    expiry_month = models.IntegerField(null=True, blank=True)
    expiry_year = models.IntegerField(null=True, blank=True)
    cardholder_name = models.CharField(max_length=200, null=True, blank=True)
    
    # IDs de pasarelas de pago
    stripe_payment_method_id = models.CharField(max_length=200, null=True, blank=True)
    wompi_token_id = models.CharField(max_length=200, null=True, blank=True)
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'
    
    def __str__(self):
        if self.payment_type == 'card':
            return f"{self.get_card_brand_display()} •••• {self.last_four}"
        return self.get_payment_type_display()
    
    def save(self, *args, **kwargs):
        # Si es el único método, hacerlo default
        if not self.organization.payment_methods.exists():
            self.is_default = True
        
        # Si se marca como default, desmarcar los demás
        if self.is_default:
            PaymentMethod.objects.filter(
                organization=self.organization,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)


class Transaction(models.Model):
    """
    Registro de todas las transacciones de pago
    """
    TRANSACTION_TYPES = [
        ('module_purchase', 'Compra de Módulo'),
        ('subscription_renewal', 'Renovación de Suscripción'),
        ('addon_purchase', 'Compra de Add-on'),
        ('refund', 'Reembolso'),
    ]
    
    TRANSACTION_STATUS = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completada'),
        ('failed', 'Fallida'),
        ('refunded', 'Reembolsada'),
        ('cancelled', 'Cancelada'),
    ]
    
    PAYMENT_GATEWAYS = [
        ('stripe', 'Stripe'),
        ('wompi', 'Wompi'),
        ('paypal', 'PayPal'),
        ('payu', 'PayU'),
        ('mercadopago', 'Mercado Pago'),
    ]
    
    # Identificador único
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    
    # Montos
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Información de la pasarela
    payment_gateway = models.CharField(max_length=20, choices=PAYMENT_GATEWAYS)
    gateway_transaction_id = models.CharField(max_length=200, null=True, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)
    
    # Módulos relacionados (para compras de módulos)
    modules = models.ManyToManyField(
        'organizations.PlanFeature',
        blank=True,
        related_name='transactions'
    )
    
    # Metadata
    metadata = models.JSONField(null=True, blank=True)
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Información de facturación
    invoice = models.ForeignKey(
        'Invoice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.transaction_number} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_number:
            # Generar número de transacción único
            prefix = 'TRX'
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            random_suffix = str(uuid.uuid4())[:6].upper()
            self.transaction_number = f"{prefix}-{timestamp}-{random_suffix}"
        
        super().save(*args, **kwargs)
    
    def mark_as_completed(self):
        """Marcar transacción como completada"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, reason=None):
        """Marcar transacción como fallida"""
        self.status = 'failed'
        if reason and self.metadata:
            self.metadata['failure_reason'] = reason
        elif reason:
            self.metadata = {'failure_reason': reason}
        self.save()


class Invoice(models.Model):
    """
    Facturas generadas para las organizaciones
    """
    INVOICE_STATUS = [
        ('draft', 'Borrador'),
        ('pending', 'Pendiente'),
        ('paid', 'Pagada'),
        ('overdue', 'Vencida'),
        ('cancelled', 'Cancelada'),
    ]
    
    # Identificador
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='draft')
    
    # Montos
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Período de facturación
    billing_period_start = models.DateField()
    billing_period_end = models.DateField()
    
    # Fechas
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Notas
    notes = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['status', 'due_date']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.organization.name}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generar número de factura único
            prefix = 'INV'
            timestamp = timezone.now().strftime('%Y%m')
            count = Invoice.objects.filter(
                created_at__year=timezone.now().year,
                created_at__month=timezone.now().month
            ).count() + 1
            self.invoice_number = f"{prefix}-{timestamp}-{count:04d}"
        
        super().save(*args, **kwargs)
    
    def mark_as_paid(self):
        """Marcar factura como pagada"""
        self.status = 'paid'
        self.paid_at = timezone.now()
        self.save()
    
    def is_overdue(self):
        """Verificar si la factura está vencida"""
        if self.status in ['paid', 'cancelled']:
            return False
        return timezone.now().date() > self.due_date


class InvoiceItem(models.Model):
    """
    Items/líneas de una factura
    """
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    module = models.ForeignKey(
        'organizations.PlanFeature',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    description = models.CharField(max_length=300)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Item de Factura'
        verbose_name_plural = 'Items de Factura'
    
    def __str__(self):
        return f"{self.description} - ${self.total_price}"
    
    def save(self, *args, **kwargs):
        # Calcular total automáticamente
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class PaymentPlan(models.Model):
    """
    Planes de pago recurrentes para organizaciones
    """
    PLAN_STATUS = [
        ('active', 'Activo'),
        ('paused', 'Pausado'),
        ('cancelled', 'Cancelado'),
    ]
    
    BILLING_CYCLES = [
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
    ]
    
    organization = models.OneToOneField(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='payment_plan'
    )
    
    status = models.CharField(max_length=20, choices=PLAN_STATUS, default='active')
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, default='monthly')
    
    # Próxima fecha de facturación
    next_billing_date = models.DateField()
    
    # Monto mensual estimado
    estimated_monthly_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Auto-renovación
    auto_renew = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Plan de Pago'
        verbose_name_plural = 'Planes de Pago'
    
    def __str__(self):
        return f"Plan de {self.organization.name} - {self.get_billing_cycle_display()}"
