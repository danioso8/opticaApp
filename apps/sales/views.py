from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q, Avg, F
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import Sale, SaleItem, Product, Category
from apps.billing.models import Invoice, Payment  # Importar modelos de facturación


@login_required
def sales_dashboard(request):
    """Dashboard principal de ventas con estadísticas y gráficos - SINCRONIZADO con facturas"""
    today = timezone.now().date()
    
    # Filtros de fecha
    period = request.GET.get('period', 'today')
    
    if period == 'today':
        start_date = today
        end_date = today
    elif period == 'week':
        start_date = today - timedelta(days=7)
        end_date = today
    elif period == 'month':
        start_date = today.replace(day=1)
        end_date = today
    elif period == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:
        start_date = today
        end_date = today
    
    # Filtrar por organización
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    
    # ==================== VENTAS DEL MÓDULO DE VENTAS ====================
    # Solo ventas completadas (excluye canceladas y pendientes)
    sales = Sale.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status='completed',  # Excluye las canceladas automáticamente
        **org_filter
    )
    
    sales_revenue = sales.aggregate(Sum('total'))['total__sum'] or Decimal('0')
    sales_count = sales.count()
    
    # ==================== FACTURAS DEL MÓDULO DE FACTURACIÓN ====================
    # Solo facturas activas (excluye las que tienen ventas canceladas)
    invoices = Invoice.objects.filter(
        fecha_emision__gte=start_date,
        fecha_emision__lte=end_date,
        estado_pago__in=['unpaid', 'partial', 'paid'],  # Todos los estados activos
        **org_filter
    ).exclude(
        sale__status='cancelled'  # Excluir facturas con ventas canceladas
    )
    
    invoices_revenue = invoices.aggregate(Sum('total'))['total__sum'] or Decimal('0')
    invoices_count = invoices.count()
    
    # ==================== ESTADÍSTICAS COMBINADAS ====================
    total_revenue = sales_revenue + invoices_revenue
    total_transactions = sales_count + invoices_count
    avg_sale = total_revenue / total_transactions if total_transactions > 0 else Decimal('0')
    
    # ==================== MÉTODOS DE PAGO COMBINADOS ====================
    # Pagos de ventas
    sales_payment_methods = sales.values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total')
    )
    
    # Pagos de facturas
    invoice_payments = Payment.objects.filter(
        invoice__fecha_emision__gte=start_date,
        invoice__fecha_emision__lte=end_date,
        status='approved',
        **{f'invoice__{k}': v for k, v in org_filter.items()}
    ).values('payment_method').annotate(
        count=Count('id'),
        total=Sum('amount')
    )
    
    # Combinar y normalizar métodos de pago
    payment_methods_dict = {}
    
    # Mapeo de métodos de pago para normalizar
    method_mapping = {
        'cash': 'Efectivo',
        'card': 'Tarjeta',
        'card_credit': 'Tarjeta de Crédito',
        'card_debit': 'Tarjeta Débito',
        'transfer': 'Transferencia',
        'mixed': 'Mixto',
        'check': 'Cheque',
        'other': 'Otro',
    }
    
    # Agregar ventas
    for pm in sales_payment_methods:
        method = pm['payment_method']
        display_name = method_mapping.get(method, method.title())
        if display_name not in payment_methods_dict:
            payment_methods_dict[display_name] = {'count': 0, 'total': Decimal('0')}
        payment_methods_dict[display_name]['count'] += pm['count']
        payment_methods_dict[display_name]['total'] += pm['total']
    
    # Agregar pagos de facturas
    for pm in invoice_payments:
        method = pm['payment_method']
        display_name = method_mapping.get(method, method.title())
        if display_name not in payment_methods_dict:
            payment_methods_dict[display_name] = {'count': 0, 'total': Decimal('0')}
        payment_methods_dict[display_name]['count'] += pm['count']
        payment_methods_dict[display_name]['total'] += pm['total']
    
    # Convertir a lista para JSON
    payment_methods_json = []
    for method_name, data in sorted(payment_methods_dict.items(), key=lambda x: x[1]['total'], reverse=True):
        payment_methods_json.append({
            'payment_method': method_name,
            'count': data['count'],
            'total': float(data['total'])
        })
    
    # ==================== PRODUCTOS MÁS VENDIDOS ====================
    # Solo del módulo de ventas completadas (excluye canceladas)
    top_products = SaleItem.objects.filter(
        sale__created_at__date__gte=start_date,
        sale__created_at__date__lte=end_date,
        sale__status='completed'  # Excluye items de ventas canceladas
    ).values('product__name').annotate(
        quantity=Sum('quantity'),
        revenue=Sum('subtotal')
    ).order_by('-quantity')[:10]
    
    # ==================== ÚLTIMAS TRANSACCIONES (SOLO FACTURAS) ====================
    # Mostrar solo facturas para evitar duplicados (las facturas ya tienen ventas asociadas)
    recent_transactions = []
    
    # Facturas recientes (solo activas, no asociadas a ventas canceladas)
    for invoice in Invoice.objects.filter(
        **org_filter, 
        estado_pago__in=['unpaid', 'partial', 'paid']
    ).exclude(
        sale__status='cancelled'  # Excluir facturas con ventas canceladas
    ).order_by('-fecha_emision')[:10]:
        # Obtener método de pago de los pagos asociados
        first_payment = invoice.payments.filter(status='approved').first()
        payment_method = 'Pendiente'
        if first_payment:
            payment_method = method_mapping.get(first_payment.payment_method, first_payment.payment_method.title())
        
        recent_transactions.append({
            'type': 'invoice',
            'id': invoice.id,
            'number': invoice.numero_completo or f"#{invoice.id}",
            'customer': invoice.cliente_nombre or (invoice.patient.full_name if invoice.patient else 'N/A'),
            'total': invoice.total,
            'payment_method': payment_method,
            'date': invoice.fecha_emision,
            'tipo_factura': 'Electrónica' if invoice.es_factura_electronica else 'Normal',
        })
    
    # ==================== PRODUCTOS CON BAJO STOCK ====================
    low_stock_products = Product.objects.filter(
        is_active=True,
        stock__lte=F('min_stock'),
        **org_filter
    ).order_by('stock')[:5]
    
    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'total_revenue': total_revenue,
        'total_sales': total_transactions,
        'avg_sale': avg_sale,
        'payment_methods': payment_methods_json,
        'payment_methods_json': json.dumps(payment_methods_json),
        'top_products': top_products,
        'recent_transactions': recent_transactions,  # Cambiado de recent_sales
        'low_stock_products': low_stock_products,
        'today': today,
        # Estadísticas separadas
        'sales_count': sales_count,
        'invoices_count': invoices_count,
        'sales_revenue': sales_revenue,
        'invoices_revenue': invoices_revenue,
    }
    
    return render(request, 'sales/dashboard.html', context)


@login_required
def new_sale(request):
    """Crear nueva venta"""
    # TODO: Implementar formulario de venta
    return render(request, 'sales/new_sale.html')


@login_required
def sale_detail(request, pk):
    """Detalle de una venta"""
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'sales/detail.html', {'sale': sale})


# ==================== API ENDPOINTS PARA GRÁFICOS ====================

@login_required
def daily_stats_api(request):
    """Estadísticas de ventas diarias de los últimos 30 días"""
    today = timezone.now().date()
    start_date = today - timedelta(days=29)
    
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    
    # Ventas por día
    daily_sales = []
    for i in range(30):
        date = start_date + timedelta(days=i)
        sales = Sale.objects.filter(
            created_at__date=date,
            status='completed',
            **org_filter
        )
        total = sales.aggregate(Sum('total'))['total__sum'] or 0
        count = sales.count()
        
        daily_sales.append({
            'date': date.strftime('%Y-%m-%d'),
            'label': date.strftime('%d/%m'),
            'total': float(total),
            'count': count
        })
    
    return JsonResponse({'data': daily_sales})


@login_required
def weekly_stats_api(request):
    """Estadísticas de ventas semanales de las últimas 12 semanas"""
    today = timezone.now().date()
    
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    
    weekly_sales = []
    for i in range(12):
        week_end = today - timedelta(days=i*7)
        week_start = week_end - timedelta(days=6)
        
        sales = Sale.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=week_end,
            status='completed',
            **org_filter
        )
        total = sales.aggregate(Sum('total'))['total__sum'] or 0
        count = sales.count()
        
        weekly_sales.insert(0, {
            'week': f'Semana {week_start.strftime("%d/%m")}',
            'total': float(total),
            'count': count
        })
    
    return JsonResponse({'data': weekly_sales})


@login_required
def monthly_stats_api(request):
    """Estadísticas de ventas mensuales del año actual"""
    today = timezone.now().date()
    year = today.year
    
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    
    monthly_sales = []
    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    for month in range(1, 13):
        sales = Sale.objects.filter(
            created_at__date__year=year,
            created_at__date__month=month,
            status='completed',
            **org_filter
        )
        total = sales.aggregate(Sum('total'))['total__sum'] or 0
        count = sales.count()
        
        monthly_sales.append({
            'month': months[month-1],
            'total': float(total),
            'count': count
        })
    
    return JsonResponse({'data': monthly_sales})


@login_required
def top_products_api(request):
    """Productos más vendidos"""
    period = request.GET.get('period', 'month')
    today = timezone.now().date()
    
    if period == 'week':
        start_date = today - timedelta(days=7)
    elif period == 'month':
        start_date = today.replace(day=1)
    else:
        start_date = today.replace(month=1, day=1)
    
    top_products = SaleItem.objects.filter(
        sale__created_at__date__gte=start_date,
        sale__status='completed'
    ).values('product__name').annotate(
        quantity=Sum('quantity'),
        revenue=Sum('subtotal')
    ).order_by('-quantity')[:10]
    
    data = list(top_products)
    for item in data:
        item['revenue'] = float(item['revenue'])
    
    return JsonResponse({'data': data})


# Importar models para usar F
from django.db import models
