from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q, Avg
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import Sale, SaleItem, Product, Category


@login_required
def sales_dashboard(request):
    """Dashboard principal de ventas con estadísticas y gráficos"""
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
    
    # Ventas del período
    sales = Sale.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status='completed'
    )
    
    # Estadísticas principales
    total_revenue = sales.aggregate(Sum('total'))['total__sum'] or Decimal('0')
    total_sales = sales.count()
    avg_sale = sales.aggregate(Avg('total'))['total__avg'] or Decimal('0')
    
    # Ventas por método de pago
    payment_methods = sales.values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total')
    ).order_by('-total')
    
    # Convertir a lista para JSON
    payment_methods_json = []
    for pm in payment_methods:
        payment_methods_json.append({
            'payment_method': pm['payment_method'],
            'count': pm['count'],
            'total': float(pm['total'])
        })
    
    # Productos más vendidos
    top_products = SaleItem.objects.filter(
        sale__created_at__date__gte=start_date,
        sale__created_at__date__lte=end_date,
        sale__status='completed'
    ).values('product__name').annotate(
        quantity=Sum('quantity'),
        revenue=Sum('subtotal')
    ).order_by('-quantity')[:10]
    
    # Últimas ventas
    recent_sales = Sale.objects.filter(status='completed').order_by('-created_at')[:10]
    
    # Productos con bajo stock
    low_stock_products = Product.objects.filter(
        is_active=True,
        stock__lte=models.F('min_stock')
    ).order_by('stock')[:5]
    
    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'avg_sale': avg_sale,
        'payment_methods': payment_methods,
        'payment_methods_json': json.dumps(payment_methods_json),
        'top_products': top_products,
        'recent_sales': recent_sales,
        'low_stock_products': low_stock_products,
        'today': today,
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
    
    # Ventas por día
    daily_sales = []
    for i in range(30):
        date = start_date + timedelta(days=i)
        sales = Sale.objects.filter(
            created_at__date=date,
            status='completed'
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
    
    weekly_sales = []
    for i in range(12):
        week_end = today - timedelta(days=i*7)
        week_start = week_end - timedelta(days=6)
        
        sales = Sale.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=week_end,
            status='completed'
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
    
    monthly_sales = []
    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    
    for month in range(1, 13):
        sales = Sale.objects.filter(
            created_at__date__year=year,
            created_at__date__month=month,
            status='completed'
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
