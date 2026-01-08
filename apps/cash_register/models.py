"""
Modelos para el módulo de Gestión de Caja/Tesorería
Incluye: CashRegister, CashMovement, CashClosure, CashCategory
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal


class CashCategory(models.Model):
    """
    Modelo para categorías personalizadas de movimientos de caja
    """
    CATEGORY_TYPE_CHOICES = [
        ('INCOME', 'Ingreso'),
        ('EXPENSE', 'Egreso'),
    ]

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='cash_categories',
        verbose_name='Organización'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    category_type = models.CharField(
        max_length=10,
        choices=CATEGORY_TYPE_CHOICES,
        verbose_name='Tipo'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    class Meta:
        verbose_name = 'Categoría de Caja'
        verbose_name_plural = 'Categorías de Caja'
        ordering = ['category_type', 'name']
        unique_together = [['organization', 'name', 'category_type']]

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class CashRegister(models.Model):
    """
    Modelo para representar una caja registradora
    Una caja puede estar abierta o cerrada
    """
    STATUS_CHOICES = [
        ('OPEN', 'Abierta'),
        ('CLOSED', 'Cerrada'),
    ]

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='cash_registers',
        verbose_name='Organización'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre de la Caja'
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Ubicación'
    )
    responsible = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_cash_registers',
        verbose_name='Responsable Actual'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='CLOSED',
        verbose_name='Estado'
    )
    current_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Saldo Actual'
    )
    opened_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha/Hora de Apertura'
    )
    opening_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Monto de Apertura'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )

    class Meta:
        verbose_name = 'Caja Registradora'
        verbose_name_plural = 'Cajas Registradoras'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['responsible']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"

    def can_open(self):
        """Verifica si la caja puede ser abierta"""
        return self.status == 'CLOSED' and self.is_active

    def can_close(self):
        """Verifica si la caja puede ser cerrada"""
        return self.status == 'OPEN'

    def open_register(self, user, opening_amount):
        """Abre la caja registradora"""
        if not self.can_open():
            raise ValueError("La caja no puede ser abierta en su estado actual")
        
        self.status = 'OPEN'
        self.responsible = user
        self.opened_at = timezone.now()
        self.opening_amount = opening_amount
        self.current_balance = opening_amount
        self.save()

    def close_register(self):
        """Cierra la caja registradora"""
        if not self.can_close():
            raise ValueError("La caja no puede ser cerrada en su estado actual")
        
        self.status = 'CLOSED'
        self.opened_at = None
        self.opening_amount = Decimal('0.00')
        self.current_balance = Decimal('0.00')  # Resetear el saldo a 0
        self.save()


class CashMovement(models.Model):
    """
    Modelo para registrar movimientos de efectivo en la caja
    Incluye ingresos y egresos
    """
    MOVEMENT_TYPE_CHOICES = [
        ('INCOME', 'Ingreso'),
        ('EXPENSE', 'Egreso'),
        ('OPENING', 'Apertura'),
        ('CLOSURE', 'Cierre'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Efectivo'),
        ('CARD', 'Tarjeta'),
        ('TRANSFER', 'Transferencia'),
        ('CHECK', 'Cheque'),
        ('OTHER', 'Otro'),
    ]

    CATEGORY_CHOICES = [
        # Ingresos
        ('SALE', 'Venta de Producto'),
        ('SALE_GLASSES', 'Venta de Lentes'),
        ('SALE_FRAMES', 'Venta de Monturas'),
        ('SALE_CONTACTS', 'Venta de Lentes de Contacto'),
        ('SALE_ACCESSORIES', 'Venta de Accesorios'),
        ('EXAM_PAYMENT', 'Pago de Examen Visual'),
        ('PAYMENT_RECEIVED', 'Cobro a Cliente'),
        ('ADVANCE_PAYMENT', 'Anticipo de Cliente'),
        ('REFUND', 'Devolución de Proveedor'),
        ('OTHER_INCOME', 'Otro Ingreso'),
        
        # Egresos
        ('PURCHASE', 'Compra de Mercancía'),
        ('PURCHASE_FRAMES', 'Compra de Monturas'),
        ('PURCHASE_LENSES', 'Compra de Lentes'),
        ('PURCHASE_CONTACTS', 'Compra de Lentes de Contacto'),
        ('PAYMENT_MADE', 'Pago a Proveedor'),
        ('SALARY', 'Pago de Nómina'),
        ('RENT', 'Pago de Arriendo'),
        ('UTILITIES', 'Servicios Públicos'),
        ('MAINTENANCE', 'Mantenimiento de Equipos'),
        ('MARKETING', 'Publicidad y Marketing'),
        ('OFFICE_SUPPLIES', 'Útiles de Oficina'),
        ('CLEANING', 'Artículos de Limpieza'),
        ('TRANSPORT', 'Transporte y Envíos'),
        ('TAXES', 'Impuestos'),
        ('BANK_FEES', 'Comisiones Bancarias'),
        ('EXPENSE', 'Gasto Operativo'),
        ('REFUND_CUSTOMER', 'Devolución a Cliente'),
        ('WITHDRAWAL', 'Retiro de Efectivo'),
        ('OTHER_EXPENSE', 'Otro Egreso'),
        
        # Sistema
        ('OPENING', 'Apertura de Caja'),
        ('CLOSURE', 'Cierre de Caja'),
    ]

    cash_register = models.ForeignKey(
        CashRegister,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name='Caja Registradora'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='cash_movements',
        verbose_name='Organización'
    )
    movement_type = models.CharField(
        max_length=10,
        choices=MOVEMENT_TYPE_CHOICES,
        verbose_name='Tipo de Movimiento'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name='Categoría'
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        default='CASH',
        verbose_name='Método de Pago'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Monto'
    )
    description = models.TextField(
        verbose_name='Descripción'
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Referencia (Nº Factura, Recibo, etc.)'
    )
    # Relaciones opcionales
    sale = models.ForeignKey(
        'sales.Sale',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cash_movements',
        verbose_name='Venta Relacionada'
    )
    # Balance tracking
    balance_before = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Saldo Anterior'
    )
    balance_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Saldo Posterior'
    )
    # Auditoría
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='cash_movements_created',
        verbose_name='Creado Por'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha/Hora'
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Eliminado'
    )

    class Meta:
        verbose_name = 'Movimiento de Caja'
        verbose_name_plural = 'Movimientos de Caja'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cash_register', '-created_at']),
            models.Index(fields=['organization', 'movement_type']),
            models.Index(fields=['category']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_movement_type_display()} - ${self.amount} - {self.created_at.strftime('%d/%m/%Y')}"

    def save(self, *args, **kwargs):
        """Override save para actualizar balance de la caja"""
        if not self.pk:  # Solo en creación
            # Registrar balance antes del movimiento
            self.balance_before = self.cash_register.current_balance
            
            # Calcular nuevo balance
            # IMPORTANTE: No actualizar balance para OPENING porque ya se hizo en open_register()
            if self.movement_type == 'INCOME':
                self.balance_after = self.balance_before + self.amount
                self.cash_register.current_balance = self.balance_after
                self.cash_register.save()
            elif self.movement_type == 'EXPENSE':
                self.balance_after = self.balance_before - self.amount
                self.cash_register.current_balance = self.balance_after
                self.cash_register.save()
            elif self.movement_type == 'OPENING':
                # El balance ya fue establecido en open_register()
                self.balance_after = self.cash_register.current_balance
            elif self.movement_type == 'CLOSURE':
                self.balance_after = self.balance_before - self.amount
                self.cash_register.current_balance = self.balance_after
                self.cash_register.save()
        
        super().save(*args, **kwargs)


class CashClosure(models.Model):
    """
    Modelo para registrar el cierre de caja diario
    Incluye cuadre y diferencias
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('REVIEWED', 'Revisado'),
        ('APPROVED', 'Aprobado'),
        ('REJECTED', 'Rechazado'),
    ]

    cash_register = models.ForeignKey(
        CashRegister,
        on_delete=models.CASCADE,
        related_name='closures',
        verbose_name='Caja Registradora'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='cash_closures',
        verbose_name='Organización'
    )
    closure_date = models.DateField(
        verbose_name='Fecha de Cierre'
    )
    # Montos del sistema
    opening_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto de Apertura'
    )
    total_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Ingresos'
    )
    total_expenses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Egresos'
    )
    expected_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto Esperado (Sistema)'
    )
    # Montos físicos contados
    counted_cash = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Efectivo Contado'
    )
    counted_cards = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Tarjetas'
    )
    counted_transfers = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Transferencias'
    )
    counted_checks = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Cheques'
    )
    counted_other = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Otros Métodos'
    )
    total_counted = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Contado'
    )
    # Diferencia
    difference = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Diferencia (Contado - Esperado)'
    )
    # Desglose de billetes/monedas (TextField para compatibilidad con SQLite)
    denomination_breakdown = models.TextField(
        default='{}',
        blank=True,
        verbose_name='Desglose de Denominaciones'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notas/Observaciones'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name='Estado'
    )
    # Auditoría
    closed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='closures_created',
        verbose_name='Cerrado Por'
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='closures_reviewed',
        verbose_name='Revisado Por'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha/Hora de Creación'
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha/Hora de Revisión'
    )

    class Meta:
        verbose_name = 'Cierre de Caja'
        verbose_name_plural = 'Cierres de Caja'
        ordering = ['-closure_date', '-created_at']
        # Removido unique_together para permitir múltiples cierres por día
        indexes = [
            models.Index(fields=['cash_register', '-closure_date']),
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Cierre {self.cash_register.name} - {self.closure_date.strftime('%d/%m/%Y')}"

    def get_denomination_breakdown(self):
        """Obtiene el desglose de denominaciones como diccionario"""
        import json
        try:
            if isinstance(self.denomination_breakdown, str):
                return json.loads(self.denomination_breakdown) if self.denomination_breakdown else {}
            return self.denomination_breakdown or {}
        except (json.JSONDecodeError, ValueError):
            return {}

    def set_denomination_breakdown(self, data):
        """Establece el desglose de denominaciones desde un diccionario"""
        import json
        self.denomination_breakdown = json.dumps(data) if data else '{}'

    def calculate_totals(self):
        """Calcula totales automáticamente"""
        self.total_counted = (
            self.counted_cash +
            self.counted_cards +
            self.counted_transfers +
            self.counted_checks +
            self.counted_other
        )
        self.difference = self.total_counted - self.expected_amount

    def save(self, *args, **kwargs):
        """Override save para calcular totales"""
        self.calculate_totals()
        super().save(*args, **kwargs)

    def approve(self, user):
        """Aprobar cierre de caja"""
        self.status = 'APPROVED'
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.save()

    def reject(self, user):
        """Rechazar cierre de caja"""
        self.status = 'REJECTED'
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.save()
