from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from apps.inventory.models import StockAlert, ProductLot
from apps.sales.models import Product


class AlertService:
    """Servicio para gestión de alertas de inventario"""
    
    def __init__(self, organization):
        self.organization = organization
    
    def create_alert(self, product, alert_type, priority, message, lot=None):
        """
        Crea una alerta de inventario si no existe una activa del mismo tipo
        
        Args:
            product: Producto
            alert_type: Tipo de alerta
            priority: Prioridad
            message: Mensaje
            lot: Lote (opcional)
        
        Returns:
            StockAlert instance o None si ya existe
        """
        # Verificar si ya existe una alerta activa del mismo tipo
        existing_alert = StockAlert.objects.filter(
            organization=self.organization,
            product=product,
            alert_type=alert_type,
            is_resolved=False,
            lot=lot
        ).first()
        
        if existing_alert:
            # Actualizar mensaje si cambió
            if existing_alert.message != message:
                existing_alert.message = message
                existing_alert.save()
            return existing_alert
        
        # Crear nueva alerta
        alert = StockAlert.objects.create(
            organization=self.organization,
            product=product,
            alert_type=alert_type,
            priority=priority,
            message=message,
            lot=lot
        )
        
        return alert
    
    def check_all_products(self):
        """
        Verifica todos los productos y crea alertas según sea necesario
        
        Returns:
            dict con estadísticas de alertas creadas
        """
        products = Product.objects.filter(
            organization=self.organization,
            is_active=True
        )
        
        stats = {
            'low_stock': 0,
            'out_of_stock': 0,
            'near_expiry': 0,
            'expired': 0,
            'total': 0
        }
        
        for product in products:
            # Verificar stock bajo
            if product.stock == 0:
                self.create_alert(
                    product=product,
                    alert_type='OUT_OF_STOCK',
                    priority='CRITICAL',
                    message=f'Producto sin stock'
                )
                stats['out_of_stock'] += 1
            elif product.stock <= product.min_stock:
                self.create_alert(
                    product=product,
                    alert_type='LOW_STOCK',
                    priority='HIGH',
                    message=f'Stock bajo: {product.stock} unidades (Mínimo: {product.min_stock})'
                )
                stats['low_stock'] += 1
            else:
                # Resolver alertas de stock si ya no aplican
                StockAlert.objects.filter(
                    organization=self.organization,
                    product=product,
                    alert_type__in=['LOW_STOCK', 'OUT_OF_STOCK'],
                    is_resolved=False
                ).update(is_resolved=True, resolved_at=timezone.now())
        
        # Verificar lotes próximos a vencer o vencidos
        lots = ProductLot.objects.filter(
            organization=self.organization,
            is_active=True,
            expiration_date__isnull=False
        )
        
        for lot in lots:
            if lot.is_expired:
                self.create_alert(
                    product=lot.product,
                    alert_type='EXPIRED',
                    priority='CRITICAL',
                    message=f'Lote {lot.lot_number} vencido ({lot.expiration_date})',
                    lot=lot
                )
                stats['expired'] += 1
            elif lot.is_near_expiration:
                self.create_alert(
                    product=lot.product,
                    alert_type='NEAR_EXPIRY',
                    priority='HIGH',
                    message=f'Lote {lot.lot_number} próximo a vencer en {lot.days_to_expiration} días',
                    lot=lot
                )
                stats['near_expiry'] += 1
        
        stats['total'] = sum(stats.values()) - stats['total']
        return stats
    
    def get_active_alerts(self, priority=None):
        """
        Obtiene alertas activas
        
        Args:
            priority: Filtrar por prioridad (opcional)
        
        Returns:
            QuerySet de alertas
        """
        alerts = StockAlert.objects.filter(
            organization=self.organization,
            is_resolved=False
        )
        
        if priority:
            alerts = alerts.filter(priority=priority)
        
        return alerts.select_related('product', 'lot').order_by('-priority', '-created_at')
    
    def get_alert_summary(self):
        """
        Obtiene un resumen de alertas activas
        
        Returns:
            dict con conteos por tipo y prioridad
        """
        alerts = StockAlert.objects.filter(
            organization=self.organization,
            is_resolved=False
        )
        
        summary = {
            'total': alerts.count(),
            'by_type': {},
            'by_priority': {},
            'critical_count': 0
        }
        
        # Contar por tipo
        for choice in StockAlert.ALERT_TYPES:
            alert_type = choice[0]
            count = alerts.filter(alert_type=alert_type).count()
            summary['by_type'][alert_type] = count
        
        # Contar por prioridad
        for choice in StockAlert.PRIORITY_CHOICES:
            priority = choice[0]
            count = alerts.filter(priority=priority).count()
            summary['by_priority'][priority] = count
        
        summary['critical_count'] = summary['by_priority'].get('CRITICAL', 0)
        
        return summary
    
    @transaction.atomic
    def resolve_alert(self, alert_id, user):
        """
        Resuelve una alerta
        
        Args:
            alert_id: ID de la alerta
            user: Usuario que resuelve
        
        Returns:
            StockAlert instance
        """
        alert = StockAlert.objects.get(
            id=alert_id,
            organization=self.organization
        )
        alert.resolve(user)
        return alert
    
    @transaction.atomic
    def resolve_product_alerts(self, product, alert_types=None):
        """
        Resuelve todas las alertas de un producto
        
        Args:
            product: Producto
            alert_types: Lista de tipos de alerta a resolver (opcional)
        """
        alerts = StockAlert.objects.filter(
            organization=self.organization,
            product=product,
            is_resolved=False
        )
        
        if alert_types:
            alerts = alerts.filter(alert_type__in=alert_types)
        
        alerts.update(
            is_resolved=True,
            resolved_at=timezone.now()
        )
