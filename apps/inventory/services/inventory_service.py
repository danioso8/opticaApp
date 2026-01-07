from django.db import transaction
from django.db.models import F, Sum, Q
from django.utils import timezone
from decimal import Decimal
from apps.inventory.models import (
    InventoryMovement, ProductLot, StockAlert, InventoryAdjustment
)
from apps.sales.models import Product


class InventoryService:
    """Servicio para gestión de inventario con trazabilidad completa"""
    
    def __init__(self, organization):
        self.organization = organization
    
    @transaction.atomic
    def register_movement(self, product, movement_type, quantity, unit_cost, 
                         created_by, reference_document='', reason='', lot=None):
        """
        Registra un movimiento de inventario y actualiza el stock
        
        Args:
            product: Producto
            movement_type: Tipo de movimiento (IN_*/OUT_*)
            quantity: Cantidad del movimiento
            unit_cost: Costo unitario
            created_by: Usuario que crea el movimiento
            reference_document: Documento de referencia (opcional)
            reason: Razón del movimiento (opcional)
            lot: Lote asociado (opcional)
        
        Returns:
            InventoryMovement instance
        """
        # Guardar stock anterior
        stock_before = product.stock
        
        # Calcular nuevo stock
        if movement_type.startswith('IN_'):
            stock_after = stock_before + quantity
        elif movement_type.startswith('OUT_'):
            stock_after = stock_before - quantity
            if stock_after < 0:
                raise ValueError(f"Stock insuficiente. Disponible: {stock_before}, Solicitado: {quantity}")
        else:
            raise ValueError(f"Tipo de movimiento inválido: {movement_type}")
        
        # Crear movimiento
        movement = InventoryMovement.objects.create(
            organization=self.organization,
            product=product,
            movement_type=movement_type,
            quantity=quantity,
            unit_cost=unit_cost,
            reference_document=reference_document,
            reason=reason,
            lot=lot,
            created_by=created_by,
            stock_before=stock_before,
            stock_after=stock_after
        )
        
        # Actualizar stock del producto
        product.stock = stock_after
        
        # Actualizar costo si es entrada
        if movement_type.startswith('IN_'):
            # Calcular costo promedio ponderado
            total_value_before = stock_before * product.cost
            total_value_new = quantity * unit_cost
            total_value_after = total_value_before + total_value_new
            
            if stock_after > 0:
                product.cost = total_value_after / stock_after
        
        product.save()
        
        # Actualizar lote si existe
        if lot:
            if movement_type.startswith('IN_'):
                lot.quantity += quantity
            else:
                lot.quantity -= quantity
            lot.save()
        
        # Verificar y crear alertas si es necesario
        self._check_and_create_alerts(product)
        
        return movement
    
    def get_kardex(self, product, start_date=None, end_date=None):
        """
        Obtiene el kardex (historial de movimientos) de un producto
        
        Args:
            product: Producto
            start_date: Fecha inicial (opcional)
            end_date: Fecha final (opcional)
        
        Returns:
            QuerySet de movimientos
        """
        movements = InventoryMovement.objects.filter(
            organization=self.organization,
            product=product
        )
        
        if start_date:
            movements = movements.filter(created_at__gte=start_date)
        if end_date:
            movements = movements.filter(created_at__lte=end_date)
        
        return movements.order_by('created_at')
    
    def get_stock_valuation(self):
        """
        Calcula la valorización total del inventario
        
        Returns:
            dict con totales y detalles
        """
        products = Product.objects.filter(
            organization=self.organization,
            is_active=True
        )
        
        total_value = Decimal('0.00')
        total_items = 0
        details = []
        
        for product in products:
            value = product.stock * product.cost
            total_value += value
            total_items += product.stock
            
            details.append({
                'product': product,
                'stock': product.stock,
                'cost': product.cost,
                'value': value
            })
        
        return {
            'total_value': total_value,
            'total_items': total_items,
            'total_products': products.count(),
            'details': details
        }
    
    def get_low_stock_products(self):
        """
        Obtiene productos con stock bajo
        
        Returns:
            QuerySet de productos
        """
        return Product.objects.filter(
            organization=self.organization,
            is_active=True,
            stock__lte=F('min_stock')
        )
    
    def get_out_of_stock_products(self):
        """
        Obtiene productos sin stock
        
        Returns:
            QuerySet de productos
        """
        return Product.objects.filter(
            organization=self.organization,
            is_active=True,
            stock=0
        )
    
    def _check_and_create_alerts(self, product):
        """
        Verifica y crea alertas de stock si es necesario
        
        Args:
            product: Producto a verificar
        """
        from apps.inventory.services.alert_service import AlertService
        alert_service = AlertService(self.organization)
        
        # Verificar stock bajo
        if product.stock <= product.min_stock:
            if product.stock == 0:
                alert_service.create_alert(
                    product=product,
                    alert_type='OUT_OF_STOCK',
                    priority='CRITICAL',
                    message=f'Producto sin stock: {product.name}'
                )
            else:
                alert_service.create_alert(
                    product=product,
                    alert_type='LOW_STOCK',
                    priority='HIGH',
                    message=f'Stock bajo: {product.stock} unidades (Mínimo: {product.min_stock})'
                )
    
    @transaction.atomic
    def create_adjustment(self, product, quantity_after, adjustment_type, 
                         reason, created_by):
        """
        Crea un ajuste de inventario pendiente de aprobación
        
        Args:
            product: Producto
            quantity_after: Cantidad después del ajuste
            adjustment_type: Tipo de ajuste
            reason: Razón del ajuste
            created_by: Usuario que crea
        
        Returns:
            InventoryAdjustment instance
        """
        adjustment = InventoryAdjustment.objects.create(
            organization=self.organization,
            product=product,
            adjustment_type=adjustment_type,
            quantity_before=product.stock,
            quantity_after=quantity_after,
            reason=reason,
            created_by=created_by
        )
        
        return adjustment
    
    @transaction.atomic
    def approve_adjustment(self, adjustment, approved_by):
        """
        Aprueba un ajuste y ejecuta el movimiento de inventario
        
        Args:
            adjustment: Ajuste a aprobar
            approved_by: Usuario que aprueba
        """
        # Aprobar ajuste
        adjustment.approve(approved_by)
        
        # Determinar tipo de movimiento
        if adjustment.difference > 0:
            movement_type = 'IN_ADJUSTMENT'
            quantity = adjustment.difference
        else:
            movement_type = 'OUT_ADJUSTMENT'
            quantity = abs(adjustment.difference)
        
        # Registrar movimiento
        if quantity > 0:
            self.register_movement(
                product=adjustment.product,
                movement_type=movement_type,
                quantity=quantity,
                unit_cost=adjustment.product.cost,
                created_by=approved_by,
                reference_document=adjustment.adjustment_number,
                reason=f"Ajuste aprobado: {adjustment.reason}"
            )
