"""
Ejemplo de modelo usando módulos compartidos
Este archivo demuestra cómo usar los módulos compartidos en cualquier app
"""
from django.db import models
from shared.core import TimeStampedMixin, OrganizationMixin, SoftDeleteMixin, ActiveMixin
from shared.core import validate_phone, validate_email_custom, validate_nit


class Cliente(TimeStampedMixin, OrganizationMixin, SoftDeleteMixin, ActiveMixin, models.Model):
    """
    Modelo de Cliente usando TODOS los mixins compartidos
    
    Hereda automáticamente:
    - created_at, updated_at (TimeStampedMixin)
    - organization (OrganizationMixin)
    - is_deleted, deleted_at, deleted_by (SoftDeleteMixin)
    - is_active (ActiveMixin)
    """
    
    # Campos básicos
    nombre = models.CharField('Nombre completo', max_length=200)
    email = models.EmailField('Email', validators=[validate_email_custom])
    telefono = models.CharField('Teléfono', max_length=20, validators=[validate_phone])
    
    # Documentos
    tipo_documento = models.CharField(
        'Tipo de documento',
        max_length=20,
        choices=[('CC', 'Cédula'), ('NIT', 'NIT'), ('CE', 'Cédula Extranjera')],
        default='CC'
    )
    numero_documento = models.CharField('Número de documento', max_length=20)
    
    # Dirección
    direccion = models.CharField('Dirección', max_length=300, blank=True)
    ciudad = models.CharField('Ciudad', max_length=100, blank=True)
    
    # Información adicional
    notas = models.TextField('Notas', blank=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'numero_documento']),
            models.Index(fields=['organization', 'email']),
        ]
    
    def __str__(self):
        return f"{self.nombre} - {self.numero_documento}"
    
    def eliminar(self, usuario):
        """Elimina el cliente de forma suave usando el mixin"""
        self.soft_delete(user=usuario)
    
    def restaurar(self):
        """Restaura un cliente eliminado"""
        self.restore()


class Producto(TimeStampedMixin, OrganizationMixin, ActiveMixin, models.Model):
    """
    Modelo de Producto usando mixins selectivos
    """
    
    # Campos básicos
    codigo = models.CharField('Código', max_length=50, unique=True)
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True)
    
    # Precios
    precio_compra = models.DecimalField('Precio de compra', max_digits=12, decimal_places=2, default=0)
    precio_venta = models.DecimalField('Precio de venta', max_digits=12, decimal_places=2, default=0)
    
    # Inventario
    stock = models.IntegerField('Stock actual', default=0)
    stock_minimo = models.IntegerField('Stock mínimo', default=5)
    
    # Categoría
    categoria = models.CharField('Categoría', max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def margen_ganancia(self):
        """Calcula el margen de ganancia"""
        if self.precio_compra == 0:
            return 0
        return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
    
    @property
    def requiere_reorden(self):
        """Verifica si el stock está bajo"""
        return self.stock <= self.stock_minimo


class Factura(TimeStampedMixin, OrganizationMixin, models.Model):
    """
    Modelo de Factura
    """
    
    # Relaciones
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='facturas',
        verbose_name='Cliente'
    )
    
    # Datos de factura
    numero_factura = models.CharField('Número de factura', max_length=50, unique=True)
    fecha = models.DateField('Fecha')
    
    # Montos
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2, default=0)
    impuestos = models.DecimalField('Impuestos', max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2, default=0)
    
    # Estado
    estado = models.CharField(
        'Estado',
        max_length=20,
        choices=[
            ('borrador', 'Borrador'),
            ('emitida', 'Emitida'),
            ('pagada', 'Pagada'),
            ('anulada', 'Anulada'),
        ],
        default='borrador'
    )
    
    # Notas
    notas = models.TextField('Notas', blank=True)
    
    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-fecha', '-created_at']
    
    def __str__(self):
        return f"{self.numero_factura} - {self.cliente.nombre}"
    
    def calcular_total(self):
        """Calcula el total de la factura"""
        self.total = self.subtotal + self.impuestos
        self.save(update_fields=['total'])


class DetalleFactura(models.Model):
    """
    Detalle de factura (items)
    """
    
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Factura'
    )
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='detalles_factura',
        verbose_name='Producto'
    )
    
    cantidad = models.IntegerField('Cantidad', default=1)
    precio_unitario = models.DecimalField('Precio unitario', max_digits=12, decimal_places=2)
    descuento = models.DecimalField('Descuento', max_digits=12, decimal_places=2, default=0)
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2)
    
    class Meta:
        verbose_name = 'Detalle de factura'
        verbose_name_plural = 'Detalles de factura'
    
    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
    
    def calcular_subtotal(self):
        """Calcula el subtotal del item"""
        self.subtotal = (self.cantidad * self.precio_unitario) - self.descuento
        self.save(update_fields=['subtotal'])
