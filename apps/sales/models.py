from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """Categorías de productos"""
    name = models.CharField('Nombre', max_length=100)
    description = models.TextField('Descripción', blank=True)
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Productos e inventario"""
    name = models.CharField('Nombre', max_length=200)
    sku = models.CharField('SKU', max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Categoría')
    description = models.TextField('Descripción', blank=True)
    price = models.DecimalField('Precio', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    cost = models.DecimalField('Costo', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], default=0)
    stock = models.IntegerField('Stock', default=0, validators=[MinValueValidator(0)])
    min_stock = models.IntegerField('Stock Mínimo', default=5, validators=[MinValueValidator(0)])
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    @property
    def needs_restock(self):
        """Verifica si necesita reabastecimiento"""
        return self.stock <= self.min_stock
    
    @property
    def profit_margin(self):
        """Calcula el margen de ganancia"""
        if self.cost > 0:
            return ((self.price - self.cost) / self.cost) * 100
        return 0


class Sale(models.Model):
    """Ventas realizadas"""
    PAYMENT_METHODS = [
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
        ('mixed', 'Mixto'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]
    
    sale_number = models.CharField('Número de Venta', max_length=20, unique=True)
    patient = models.ForeignKey('patients.Patient', on_delete=models.PROTECT, verbose_name='Paciente', null=True, blank=True)
    customer_name = models.CharField('Nombre del Cliente', max_length=200, blank=True, help_text='Usar si no es un paciente registrado')
    sold_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Vendido por')
    payment_method = models.CharField('Método de Pago', max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField('Estado', max_length=20, choices=STATUS_CHOICES, default='completed')
    subtotal = models.DecimalField('Subtotal', max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField('Descuento', max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    tax = models.DecimalField('Impuesto', max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0.00'))])
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, default=0)
    notes = models.TextField('Notas', blank=True)
    created_at = models.DateTimeField('Fecha de Venta', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Venta {self.sale_number} - {self.get_customer_display()}"
    
    def get_customer_display(self):
        """Retorna el nombre del cliente o paciente"""
        if self.patient:
            return self.patient.full_name
        return self.customer_name or 'Cliente sin nombre'
    
    def calculate_totals(self):
        """Calcula los totales de la venta"""
        self.subtotal = sum(item.subtotal for item in self.items.all())
        self.total = self.subtotal - self.discount + self.tax
        self.save()


class SaleItem(models.Model):
    """Items de una venta"""
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items', verbose_name='Venta')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Producto')
    quantity = models.IntegerField('Cantidad', validators=[MinValueValidator(1)])
    price = models.DecimalField('Precio Unitario', max_digits=10, decimal_places=2)
    discount = models.DecimalField('Descuento', max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField('Subtotal', max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Item de Venta'
        verbose_name_plural = 'Items de Venta'
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Calcula el subtotal automáticamente"""
        self.subtotal = (self.price * self.quantity) - self.discount
        super().save(*args, **kwargs)
