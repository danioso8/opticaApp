from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from apps.organizations.base_models import TenantModel


class InventoryMovement(TenantModel):
    """Movimientos de inventario con trazabilidad completa"""
    
    MOVEMENT_TYPES = [
        ('IN_PURCHASE', 'Entrada por compra'),
        ('IN_RETURN', 'Entrada por devolución'),
        ('IN_ADJUSTMENT', 'Entrada por ajuste'),
        ('IN_TRANSFER', 'Entrada por transferencia'),
        ('OUT_SALE', 'Salida por venta'),
        ('OUT_LOSS', 'Salida por pérdida'),
        ('OUT_DAMAGE', 'Salida por daño'),
        ('OUT_ADJUSTMENT', 'Salida por ajuste'),
        ('OUT_TRANSFER', 'Salida por transferencia'),
    ]
    
    product = models.ForeignKey(
        'sales.Product',
        on_delete=models.PROTECT,
        verbose_name='Producto',
        related_name='inventory_movements'
    )
    movement_type = models.CharField(
        'Tipo de Movimiento',
        max_length=20,
        choices=MOVEMENT_TYPES
    )
    quantity = models.IntegerField(
        'Cantidad',
        validators=[MinValueValidator(1)]
    )
    unit_cost = models.DecimalField(
        'Costo Unitario',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_cost = models.DecimalField(
        'Costo Total',
        max_digits=12,
        decimal_places=2,
        default=0
    )
    reference_document = models.CharField(
        'Documento de Referencia',
        max_length=100,
        blank=True,
        help_text='Factura, OC, Guía, etc.'
    )
    reason = models.TextField(
        'Razón/Motivo',
        blank=True,
        help_text='Motivo del movimiento'
    )
    lot = models.ForeignKey(
        'ProductLot',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Lote',
        related_name='movements'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Creado por',
        related_name='inventory_movements_created'
    )
    created_at = models.DateTimeField(
        'Fecha de Creación',
        auto_now_add=True
    )
    
    # Control de stock
    stock_before = models.IntegerField(
        'Stock Anterior',
        default=0
    )
    stock_after = models.IntegerField(
        'Stock Posterior',
        default=0
    )
    
    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'product', '-created_at']),
            models.Index(fields=['organization', 'movement_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        # Calcular costo total
        self.total_cost = self.unit_cost * self.quantity
        super().save(*args, **kwargs)
    
    @property
    def is_incoming(self):
        """Verifica si es un movimiento de entrada"""
        return self.movement_type.startswith('IN_')
    
    @property
    def is_outgoing(self):
        """Verifica si es un movimiento de salida"""
        return self.movement_type.startswith('OUT_')


class ProductLot(TenantModel):
    """Lotes de productos con control de vencimiento"""
    
    product = models.ForeignKey(
        'sales.Product',
        on_delete=models.PROTECT,
        verbose_name='Producto',
        related_name='lots'
    )
    lot_number = models.CharField(
        'Número de Lote',
        max_length=50
    )
    expiration_date = models.DateField(
        'Fecha de Vencimiento',
        null=True,
        blank=True,
        help_text='Opcional para productos no perecederos'
    )
    quantity = models.IntegerField(
        'Cantidad',
        default=0,
        validators=[MinValueValidator(0)]
    )
    unit_cost = models.DecimalField(
        'Costo Unitario',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    supplier = models.ForeignKey(
        'billing.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Proveedor'
    )
    purchase_date = models.DateField(
        'Fecha de Compra',
        default=timezone.now
    )
    is_active = models.BooleanField(
        'Activo',
        default=True
    )
    created_at = models.DateTimeField(
        'Creado',
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = 'Lote de Producto'
        verbose_name_plural = 'Lotes de Productos'
        ordering = ['-created_at']
        unique_together = [['organization', 'product', 'lot_number']]
        indexes = [
            models.Index(fields=['organization', 'product', 'is_active']),
            models.Index(fields=['expiration_date']),
        ]
    
    def __str__(self):
        return f"Lote {self.lot_number} - {self.product.name}"
    
    @property
    def is_expired(self):
        """Verifica si el lote está vencido"""
        if not self.expiration_date:
            return False
        return self.expiration_date < timezone.now().date()
    
    @property
    def days_to_expiration(self):
        """Días hasta el vencimiento"""
        if not self.expiration_date:
            return None
        delta = self.expiration_date - timezone.now().date()
        return delta.days
    
    @property
    def is_near_expiration(self):
        """Verifica si está próximo a vencer (30 días)"""
        days = self.days_to_expiration
        if days is None:
            return False
        return 0 <= days <= 30


class StockAlert(TenantModel):
    """Alertas de stock bajo y otras notificaciones de inventario"""
    
    ALERT_TYPES = [
        ('LOW_STOCK', 'Stock Bajo'),
        ('OUT_OF_STOCK', 'Sin Stock'),
        ('NEAR_EXPIRY', 'Próximo a Vencer'),
        ('EXPIRED', 'Vencido'),
        ('OVERSTOCK', 'Sobrestock'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Baja'),
        ('MEDIUM', 'Media'),
        ('HIGH', 'Alta'),
        ('CRITICAL', 'Crítica'),
    ]
    
    product = models.ForeignKey(
        'sales.Product',
        on_delete=models.CASCADE,
        verbose_name='Producto',
        related_name='stock_alerts'
    )
    alert_type = models.CharField(
        'Tipo de Alerta',
        max_length=20,
        choices=ALERT_TYPES
    )
    priority = models.CharField(
        'Prioridad',
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    lot = models.ForeignKey(
        ProductLot,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Lote',
        related_name='alerts'
    )
    message = models.TextField(
        'Mensaje',
        blank=True
    )
    is_resolved = models.BooleanField(
        'Resuelto',
        default=False
    )
    resolved_at = models.DateTimeField(
        'Resuelto el',
        null=True,
        blank=True
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Resuelto por',
        related_name='resolved_alerts'
    )
    created_at = models.DateTimeField(
        'Creado',
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = 'Alerta de Stock'
        verbose_name_plural = 'Alertas de Stock'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['organization', 'is_resolved', '-created_at']),
            models.Index(fields=['alert_type', 'is_resolved']),
        ]
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.product.name}"
    
    def resolve(self, user):
        """Marca la alerta como resuelta"""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.save()


class InventoryAdjustment(TenantModel):
    """Ajustes de inventario con aprobaciones y auditoría"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('APPROVED', 'Aprobado'),
        ('REJECTED', 'Rechazado'),
    ]
    
    ADJUSTMENT_TYPES = [
        ('COUNT', 'Conteo Físico'),
        ('DAMAGE', 'Daño/Pérdida'),
        ('CORRECTION', 'Corrección'),
        ('OTHER', 'Otro'),
    ]
    
    adjustment_number = models.CharField(
        'Número de Ajuste',
        max_length=20,
        unique=True
    )
    product = models.ForeignKey(
        'sales.Product',
        on_delete=models.PROTECT,
        verbose_name='Producto',
        related_name='adjustments'
    )
    adjustment_type = models.CharField(
        'Tipo de Ajuste',
        max_length=20,
        choices=ADJUSTMENT_TYPES
    )
    quantity_before = models.IntegerField(
        'Cantidad Anterior',
        validators=[MinValueValidator(0)]
    )
    quantity_after = models.IntegerField(
        'Cantidad Después',
        validators=[MinValueValidator(0)]
    )
    difference = models.IntegerField(
        'Diferencia',
        default=0
    )
    reason = models.TextField(
        'Razón del Ajuste'
    )
    cost_impact = models.DecimalField(
        'Impacto en Costo',
        max_digits=12,
        decimal_places=2,
        default=0
    )
    status = models.CharField(
        'Estado',
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Creado por',
        related_name='adjustments_created'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Aprobado por',
        related_name='adjustments_approved'
    )
    created_at = models.DateTimeField(
        'Creado',
        auto_now_add=True
    )
    approved_at = models.DateTimeField(
        'Aprobado el',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Ajuste de Inventario'
        verbose_name_plural = 'Ajustes de Inventario'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Ajuste {self.adjustment_number} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Calcular diferencia
        self.difference = self.quantity_after - self.quantity_before
        
        # Calcular impacto en costo
        if self.difference != 0:
            self.cost_impact = abs(self.difference) * self.product.cost
            if self.difference < 0:
                self.cost_impact = -self.cost_impact
        
        # Generar número de ajuste si no existe
        if not self.adjustment_number:
            from datetime import datetime
            prefix = f"ADJ-{datetime.now().strftime('%Y%m')}"
            last_adjustment = InventoryAdjustment.objects.filter(
                organization=self.organization,
                adjustment_number__startswith=prefix
            ).order_by('-adjustment_number').first()
            
            if last_adjustment:
                last_num = int(last_adjustment.adjustment_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.adjustment_number = f"{prefix}-{new_num:04d}"
        
        super().save(*args, **kwargs)
    
    def approve(self, user):
        """Aprobar el ajuste"""
        self.status = 'APPROVED'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()
    
    def reject(self, user):
        """Rechazar el ajuste"""
        self.status = 'REJECTED'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()
