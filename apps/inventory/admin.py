from django.contrib import admin
from apps.inventory.models import (
    InventoryMovement, ProductLot, StockAlert, InventoryAdjustment
)


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'product', 'movement_type', 'quantity', 
        'stock_before', 'stock_after', 'created_by', 'created_at'
    ]
    list_filter = ['movement_type', 'created_at', 'organization']
    search_fields = ['product__name', 'reference_document', 'reason']
    readonly_fields = ['total_cost', 'stock_before', 'stock_after', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información del Movimiento', {
            'fields': ('organization', 'product', 'movement_type', 'lot')
        }),
        ('Cantidades y Costos', {
            'fields': ('quantity', 'unit_cost', 'total_cost')
        }),
        ('Stock', {
            'fields': ('stock_before', 'stock_after')
        }),
        ('Referencia', {
            'fields': ('reference_document', 'reason')
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at')
        }),
    )


@admin.register(ProductLot)
class ProductLotAdmin(admin.ModelAdmin):
    list_display = [
        'lot_number', 'product', 'quantity', 'expiration_date', 
        'is_expired', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'expiration_date', 'organization']
    search_fields = ['lot_number', 'product__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'expiration_date'
    
    fieldsets = (
        ('Información del Lote', {
            'fields': ('organization', 'product', 'lot_number')
        }),
        ('Cantidades y Costos', {
            'fields': ('quantity', 'unit_cost')
        }),
        ('Fechas', {
            'fields': ('purchase_date', 'expiration_date')
        }),
        ('Proveedor', {
            'fields': ('supplier',)
        }),
        ('Estado', {
            'fields': ('is_active', 'created_at')
        }),
    )


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'product', 'alert_type', 'priority', 
        'is_resolved', 'created_at'
    ]
    list_filter = ['alert_type', 'priority', 'is_resolved', 'organization']
    search_fields = ['product__name', 'message']
    readonly_fields = ['created_at', 'resolved_at']
    date_hierarchy = 'created_at'
    
    actions = ['resolve_alerts']
    
    def resolve_alerts(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(
            is_resolved=True,
            resolved_at=timezone.now(),
            resolved_by=request.user
        )
        self.message_user(request, f'{count} alerta(s) resuelta(s).')
    resolve_alerts.short_description = "Resolver alertas seleccionadas"


@admin.register(InventoryAdjustment)
class InventoryAdjustmentAdmin(admin.ModelAdmin):
    list_display = [
        'adjustment_number', 'product', 'adjustment_type', 'difference',
        'status', 'created_by', 'created_at'
    ]
    list_filter = ['status', 'adjustment_type', 'organization']
    search_fields = ['adjustment_number', 'product__name', 'reason']
    readonly_fields = [
        'adjustment_number', 'difference', 'cost_impact', 
        'created_at', 'approved_at'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información del Ajuste', {
            'fields': ('organization', 'adjustment_number', 'product', 'adjustment_type')
        }),
        ('Cantidades', {
            'fields': ('quantity_before', 'quantity_after', 'difference')
        }),
        ('Impacto', {
            'fields': ('cost_impact', 'reason')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'approved_by', 'approved_at')
        }),
    )
