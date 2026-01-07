from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, F, Count
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from apps.inventory.models import (
    InventoryMovement, ProductLot, StockAlert, InventoryAdjustment
)
from apps.inventory.services.inventory_service import InventoryService
from apps.inventory.services.alert_service import AlertService
from apps.sales.models import Product, Category


@login_required
def inventory_dashboard(request):
    """Dashboard principal de inventario"""
    organization = request.organization
    inventory_service = InventoryService(organization)
    alert_service = AlertService(organization)
    
    # Obtener estadísticas
    valuation = inventory_service.get_stock_valuation()
    alert_summary = alert_service.get_alert_summary()
    
    # Productos con stock bajo
    low_stock_products = inventory_service.get_low_stock_products()[:10]
    
    # Productos sin stock
    out_of_stock_products = inventory_service.get_out_of_stock_products()[:10]
    
    # Movimientos recientes
    recent_movements = InventoryMovement.objects.filter(
        organization=organization
    ).select_related('product', 'created_by').order_by('-created_at')[:10]
    
    # Alertas críticas
    critical_alerts = alert_service.get_active_alerts(priority='CRITICAL')[:10]
    
    context = {
        'valuation': valuation,
        'alert_summary': alert_summary,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'recent_movements': recent_movements,
        'critical_alerts': critical_alerts,
    }
    
    return render(request, 'inventory/dashboard.html', context)


@login_required
def movement_list(request):
    """Lista de movimientos de inventario"""
    organization = request.organization
    
    # Filtros
    movement_type = request.GET.get('type', '')
    product_id = request.GET.get('product', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    movements = InventoryMovement.objects.filter(
        organization=organization
    ).select_related('product', 'created_by', 'lot')
    
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    if product_id:
        movements = movements.filter(product_id=product_id)
    if start_date:
        movements = movements.filter(created_at__gte=start_date)
    if end_date:
        movements = movements.filter(created_at__lte=end_date)
    
    movements = movements.order_by('-created_at')
    
    # Productos para filtro
    products = Product.objects.filter(
        organization=organization,
        is_active=True
    ).order_by('name')
    
    context = {
        'movements': movements,
        'products': products,
        'movement_types': InventoryMovement.MOVEMENT_TYPES,
        'filters': {
            'type': movement_type,
            'product': product_id,
            'start_date': start_date,
            'end_date': end_date,
        }
    }
    
    return render(request, 'inventory/movement_list.html', context)


@login_required
def movement_create(request):
    """Crear movimiento de inventario"""
    organization = request.organization
    
    if request.method == 'POST':
        try:
            inventory_service = InventoryService(organization)
            
            product = get_object_or_404(
                Product,
                id=request.POST.get('product'),
                organization=organization
            )
            
            movement_type = request.POST.get('movement_type')
            quantity = int(request.POST.get('quantity'))
            unit_cost = float(request.POST.get('unit_cost'))
            reference_document = request.POST.get('reference_document', '')
            reason = request.POST.get('reason', '')
            
            # Lote opcional
            lot_id = request.POST.get('lot')
            lot = None
            if lot_id:
                lot = get_object_or_404(
                    ProductLot,
                    id=lot_id,
                    organization=organization
                )
            
            movement = inventory_service.register_movement(
                product=product,
                movement_type=movement_type,
                quantity=quantity,
                unit_cost=unit_cost,
                created_by=request.user,
                reference_document=reference_document,
                reason=reason,
                lot=lot
            )
            
            messages.success(request, f'Movimiento registrado exitosamente: {movement.get_movement_type_display()}')
            return redirect('inventory:movement_list')
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al crear movimiento: {str(e)}')
    
    # Obtener productos y lotes
    products = Product.objects.filter(
        organization=organization,
        is_active=True
    ).order_by('name')
    
    context = {
        'products': products,
        'movement_types': InventoryMovement.MOVEMENT_TYPES,
    }
    
    return render(request, 'inventory/movement_create.html', context)


@login_required
def product_kardex(request, product_id):
    """Kardex de un producto"""
    organization = request.organization
    product = get_object_or_404(Product, id=product_id, organization=organization)
    
    inventory_service = InventoryService(organization)
    
    # Fechas
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    movements = inventory_service.get_kardex(
        product=product,
        start_date=start_date,
        end_date=end_date
    )
    
    context = {
        'product': product,
        'movements': movements,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'inventory/kardex.html', context)


@login_required
def lot_list(request):
    """Lista de lotes"""
    organization = request.organization
    
    # Filtros
    product_id = request.GET.get('product', '')
    status = request.GET.get('status', 'active')
    
    lots = ProductLot.objects.filter(
        organization=organization
    ).select_related('product', 'supplier')
    
    if product_id:
        lots = lots.filter(product_id=product_id)
    
    if status == 'active':
        lots = lots.filter(is_active=True, quantity__gt=0)
    elif status == 'expired':
        lots = lots.filter(expiration_date__lt=timezone.now().date())
    elif status == 'near_expiry':
        future_date = timezone.now().date() + timedelta(days=30)
        lots = lots.filter(
            expiration_date__lte=future_date,
            expiration_date__gte=timezone.now().date()
        )
    
    lots = lots.order_by('-created_at')
    
    products = Product.objects.filter(
        organization=organization,
        is_active=True
    ).order_by('name')
    
    context = {
        'lots': lots,
        'products': products,
        'filters': {
            'product': product_id,
            'status': status,
        }
    }
    
    return render(request, 'inventory/lot_list.html', context)


@login_required
def lot_create(request):
    """Crear lote"""
    organization = request.organization
    
    if request.method == 'POST':
        try:
            product = get_object_or_404(
                Product,
                id=request.POST.get('product'),
                organization=organization
            )
            
            lot = ProductLot.objects.create(
                organization=organization,
                product=product,
                lot_number=request.POST.get('lot_number'),
                expiration_date=request.POST.get('expiration_date') or None,
                quantity=int(request.POST.get('quantity', 0)),
                unit_cost=float(request.POST.get('unit_cost')),
                purchase_date=request.POST.get('purchase_date')
            )
            
            messages.success(request, f'Lote creado exitosamente: {lot.lot_number}')
            return redirect('inventory:lot_list')
            
        except Exception as e:
            messages.error(request, f'Error al crear lote: {str(e)}')
    
    products = Product.objects.filter(
        organization=organization,
        is_active=True
    ).order_by('name')
    
    context = {
        'products': products,
    }
    
    return render(request, 'inventory/lot_create.html', context)


@login_required
def alert_list(request):
    """Lista de alertas"""
    organization = request.organization
    alert_service = AlertService(organization)
    
    # Filtros
    alert_type = request.GET.get('type', '')
    priority = request.GET.get('priority', '')
    status = request.GET.get('status', 'active')
    
    alerts = StockAlert.objects.filter(
        organization=organization
    ).select_related('product', 'lot', 'resolved_by')
    
    if status == 'active':
        alerts = alerts.filter(is_resolved=False)
    elif status == 'resolved':
        alerts = alerts.filter(is_resolved=True)
    
    if alert_type:
        alerts = alerts.filter(alert_type=alert_type)
    if priority:
        alerts = alerts.filter(priority=priority)
    
    alerts = alerts.order_by('-priority', '-created_at')
    
    # Resumen
    summary = alert_service.get_alert_summary()
    
    context = {
        'alerts': alerts,
        'summary': summary,
        'alert_types': StockAlert.ALERT_TYPES,
        'priority_choices': StockAlert.PRIORITY_CHOICES,
        'filters': {
            'type': alert_type,
            'priority': priority,
            'status': status,
        }
    }
    
    return render(request, 'inventory/alert_list.html', context)


@login_required
def alert_resolve(request, alert_id):
    """Resolver alerta"""
    organization = request.organization
    alert_service = AlertService(organization)
    
    try:
        alert = alert_service.resolve_alert(alert_id, request.user)
        messages.success(request, f'Alerta resuelta: {alert.get_alert_type_display()}')
    except Exception as e:
        messages.error(request, f'Error al resolver alerta: {str(e)}')
    
    return redirect('inventory:alert_list')


@login_required
def adjustment_list(request):
    """Lista de ajustes"""
    organization = request.organization
    
    # Filtros
    status = request.GET.get('status', '')
    
    adjustments = InventoryAdjustment.objects.filter(
        organization=organization
    ).select_related('product', 'created_by', 'approved_by')
    
    if status:
        adjustments = adjustments.filter(status=status)
    
    adjustments = adjustments.order_by('-created_at')
    
    # Estadísticas
    pending_count = adjustments.filter(status='PENDING').count()
    approved_count = adjustments.filter(status='APPROVED').count()
    
    context = {
        'adjustments': adjustments,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'status_choices': InventoryAdjustment.STATUS_CHOICES,
        'filters': {
            'status': status,
        }
    }
    
    return render(request, 'inventory/adjustment_list.html', context)


@login_required
def adjustment_create(request):
    """Crear ajuste"""
    organization = request.organization
    
    if request.method == 'POST':
        try:
            inventory_service = InventoryService(organization)
            
            product = get_object_or_404(
                Product,
                id=request.POST.get('product'),
                organization=organization
            )
            
            adjustment = inventory_service.create_adjustment(
                product=product,
                quantity_after=int(request.POST.get('quantity_after')),
                adjustment_type=request.POST.get('adjustment_type'),
                reason=request.POST.get('reason'),
                created_by=request.user
            )
            
            messages.success(request, f'Ajuste creado: {adjustment.adjustment_number}. Pendiente de aprobación.')
            return redirect('inventory:adjustment_list')
            
        except Exception as e:
            messages.error(request, f'Error al crear ajuste: {str(e)}')
    
    products = Product.objects.filter(
        organization=organization,
        is_active=True
    ).order_by('name')
    
    context = {
        'products': products,
        'adjustment_types': InventoryAdjustment.ADJUSTMENT_TYPES,
    }
    
    return render(request, 'inventory/adjustment_create.html', context)


@login_required
def adjustment_approve(request, adjustment_id):
    """Aprobar ajuste"""
    organization = request.organization
    inventory_service = InventoryService(organization)
    
    try:
        adjustment = get_object_or_404(
            InventoryAdjustment,
            id=adjustment_id,
            organization=organization,
            status='PENDING'
        )
        
        inventory_service.approve_adjustment(adjustment, request.user)
        messages.success(request, f'Ajuste aprobado: {adjustment.adjustment_number}')
        
    except Exception as e:
        messages.error(request, f'Error al aprobar ajuste: {str(e)}')
    
    return redirect('inventory:adjustment_list')


@login_required
def adjustment_reject(request, adjustment_id):
    """Rechazar ajuste"""
    organization = request.organization
    
    try:
        adjustment = get_object_or_404(
            InventoryAdjustment,
            id=adjustment_id,
            organization=organization,
            status='PENDING'
        )
        
        adjustment.reject(request.user)
        messages.warning(request, f'Ajuste rechazado: {adjustment.adjustment_number}')
        
    except Exception as e:
        messages.error(request, f'Error al rechazar ajuste: {str(e)}')
    
    return redirect('inventory:adjustment_list')


# API endpoints para AJAX
@login_required
def get_product_info(request, product_id):
    """Obtener información de un producto (AJAX)"""
    organization = request.organization
    
    try:
        product = Product.objects.get(id=product_id, organization=organization)
        data = {
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'stock': product.stock,
            'cost': float(product.cost),
            'price': float(product.price),
            'min_stock': product.min_stock,
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)


@login_required
def get_product_lots(request, product_id):
    """Obtener lotes de un producto (AJAX)"""
    organization = request.organization
    
    lots = ProductLot.objects.filter(
        organization=organization,
        product_id=product_id,
        is_active=True,
        quantity__gt=0
    ).values('id', 'lot_number', 'quantity', 'expiration_date')
    
    return JsonResponse(list(lots), safe=False)

