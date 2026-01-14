# -*- coding: utf-8 -*-
"""
Vistas del Panel Admin SAAS - Gestión de Módulos y Trials
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.organizations.models import (
    Organization,
    PlanFeature,
    ModulePricing,
    OrganizationModule,
    TrialStatus,
    SubscriptionNotification
)
from apps.payments.models import Transaction, Invoice
from apps.admin_dashboard.views import superuser_required


@superuser_required
def modules_dashboard(request):
    """
    Dashboard principal de módulos À la Carte
    Métricas y estadísticas de uso
    """
    # Estadísticas generales
    total_modules = PlanFeature.objects.filter(
        is_active=True,
        available_alacarte=True
    ).count()
    
    total_active_subscriptions = OrganizationModule.objects.filter(
        is_active=True
    ).values('organization').distinct().count()
    
    # MRR (Monthly Recurring Revenue)
    mrr = OrganizationModule.objects.filter(
        is_active=True
    ).aggregate(total=Sum('price_paid'))['total'] or Decimal('0.00')
    
    # Módulos más populares
    popular_modules = OrganizationModule.objects.filter(
        is_active=True
    ).values(
        'module__name',
        'module__id'
    ).annotate(
        subscription_count=Count('id')
    ).order_by('-subscription_count')[:10]
    
    # Trials activos
    active_trials = TrialStatus.objects.filter(
        state='active'
    ).count()
    
    # Conversión trial to paid
    total_trials = TrialStatus.objects.count()
    converted_trials = TrialStatus.objects.filter(
        state='converted'
    ).count()
    
    conversion_rate = (converted_trials / total_trials * 100) if total_trials > 0 else 0
    
    # Ingresos del último mes
    last_month = timezone.now() - timedelta(days=30)
    monthly_revenue = Transaction.objects.filter(
        status='completed',
        created_at__gte=last_month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Distribución de módulos por organización
    module_distribution = OrganizationModule.objects.filter(
        is_active=True
    ).values('organization').annotate(
        module_count=Count('id')
    ).values_list('module_count', flat=True)
    
    # Calcular promedio de módulos por cliente
    avg_modules = sum(module_distribution) / len(module_distribution) if module_distribution else 0
    
    context = {
        'total_modules': total_modules,
        'total_active_subscriptions': total_active_subscriptions,
        'mrr': mrr,
        'popular_modules': popular_modules,
        'active_trials': active_trials,
        'conversion_rate': round(conversion_rate, 2),
        'monthly_revenue': monthly_revenue,
        'avg_modules_per_customer': round(avg_modules, 2),
    }
    
    return render(request, 'admin_dashboard/modules/dashboard.html', context)


@superuser_required
def modules_management(request):
    """
    Gestión de módulos - CRUD
    """
    modules = PlanFeature.objects.all().order_by('category', 'name')
    
    # Agregar estadísticas de uso a cada módulo
    for module in modules:
        module.active_subscriptions = OrganizationModule.objects.filter(
            module=module,
            is_active=True
        ).count()
        
        module.monthly_revenue = OrganizationModule.objects.filter(
            module=module,
            is_active=True
        ).aggregate(total=Sum('price_paid'))['total'] or Decimal('0.00')
    
    context = {
        'modules': modules,
    }
    
    return render(request, 'admin_dashboard/modules/management.html', context)


@superuser_required
def module_pricing_config(request):
    """
    Configuración de precios de módulos
    """
    if request.method == 'POST':
        try:
            pricing, created = ModulePricing.objects.get_or_create(
                id=1,
                defaults={
                    'base_price_monthly': Decimal('5.00'),
                    'discount_4_modules': 10,
                    'discount_7_modules': 20,
                }
            )
            
            # Actualizar valores
            pricing.base_price_monthly = Decimal(request.POST.get('base_price', '5.00'))
            pricing.discount_4_modules = int(request.POST.get('discount_4', 10))
            pricing.discount_7_modules = int(request.POST.get('discount_7', 20))
            
            # Precios promocionales
            promo_price = request.POST.get('promo_price')
            if promo_price:
                pricing.promo_price = Decimal(promo_price)
                pricing.promo_start = request.POST.get('promo_start')
                pricing.promo_end = request.POST.get('promo_end')
            else:
                pricing.promo_price = None
                pricing.promo_start = None
                pricing.promo_end = None
            
            pricing.save()
            
            messages.success(request, 'Configuración de precios actualizada exitosamente.')
            return redirect('admin_dashboard:module_pricing_config')
        
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
    
    try:
        pricing = ModulePricing.objects.first()
    except:
        pricing = None
    
    context = {
        'pricing': pricing,
    }
    
    return render(request, 'admin_dashboard/modules/pricing_config.html', context)


@superuser_required
def trials_dashboard(request):
    """
    Dashboard de trials - monitoreo y conversión
    """
    # Trials por estado
    trials_by_state = TrialStatus.objects.values('state').annotate(
        count=Count('id')
    )
    
    # Trials que expiran pronto (próximos 7 días)
    today = timezone.now().date()
    expiring_soon = TrialStatus.objects.filter(
        state='active',
        trial_end__lte=today + timedelta(days=7),
        trial_end__gte=today
    ).select_related('organization')
    
    # Trials expirados sin conversión (periodo de gracia)
    in_grace_period = TrialStatus.objects.filter(
        state='expired_grace'
    ).select_related('organization')
    
    # Análisis de conversión por día de trial
    conversion_by_day = []
    for day in [20, 25, 28, 30]:
        trials_at_day = TrialStatus.objects.filter(
            trial_start__lte=today - timedelta(days=day)
        ).count()
        
        converted_at_day = TrialStatus.objects.filter(
            trial_start__lte=today - timedelta(days=day),
            state='converted'
        ).count()
        
        rate = (converted_at_day / trials_at_day * 100) if trials_at_day > 0 else 0
        
        conversion_by_day.append({
            'day': day,
            'total': trials_at_day,
            'converted': converted_at_day,
            'rate': round(rate, 2)
        })
    
    # Módulos más usados durante trials
    all_most_used = []
    for trial in TrialStatus.objects.filter(most_used_modules__isnull=False):
        if trial.most_used_modules:
            all_most_used.extend(trial.most_used_modules.keys())
    
    from collections import Counter
    module_popularity = Counter(all_most_used).most_common(10)
    
    context = {
        'trials_by_state': trials_by_state,
        'expiring_soon': expiring_soon,
        'in_grace_period': in_grace_period,
        'conversion_by_day': conversion_by_day,
        'module_popularity': module_popularity,
    }
    
    return render(request, 'admin_dashboard/modules/trials_dashboard.html', context)


@superuser_required
def trial_detail(request, trial_id):
    """
    Detalle de un trial específico
    """
    trial = get_object_or_404(TrialStatus, id=trial_id)
    
    # Módulos activos de la organización
    active_modules = OrganizationModule.objects.filter(
        organization=trial.organization,
        is_active=True
    ).select_related('module')
    
    # Notificaciones enviadas
    notifications = SubscriptionNotification.objects.filter(
        organization=trial.organization
    ).order_by('-sent_at')[:20]
    
    # Transacciones
    transactions = Transaction.objects.filter(
        organization=trial.organization
    ).order_by('-created_at')[:10]
    
    context = {
        'trial': trial,
        'organization': trial.organization,
        'active_modules': active_modules,
        'notifications': notifications,
        'transactions': transactions,
    }
    
    return render(request, 'admin_dashboard/modules/trial_detail.html', context)


@superuser_required
def conversion_analytics(request):
    """
    Analytics avanzados de conversión
    """
    # Conversión por mes
    from django.db.models.functions import TruncMonth
    
    conversions_by_month = TrialStatus.objects.filter(
        state='converted'
    ).annotate(
        month=TruncMonth('trial_start')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Tiempo promedio hasta conversión
    converted_trials = TrialStatus.objects.filter(state='converted')
    
    avg_days_to_convert = 0
    if converted_trials.exists():
        total_days = 0
        for trial in converted_trials:
            if trial.trial_end:
                days = (trial.trial_end - trial.trial_start).days
                total_days += days
        avg_days_to_convert = total_days / converted_trials.count() if converted_trials.count() > 0 else 0
    
    # Revenue por fuente de conversión
    revenue_by_source = Transaction.objects.filter(
        status='completed',
        transaction_type='module_purchase'
    ).values('payment_gateway').annotate(
        total_revenue=Sum('amount'),
        transaction_count=Count('id')
    )
    
    # Tasa de abandono (churn)
    total_orgs = Organization.objects.count()
    active_orgs = OrganizationModule.objects.filter(
        is_active=True
    ).values('organization').distinct().count()
    
    churn_rate = ((total_orgs - active_orgs) / total_orgs * 100) if total_orgs > 0 else 0
    
    # LTV (Lifetime Value) estimado
    avg_monthly_per_customer = OrganizationModule.objects.filter(
        is_active=True
    ).values('organization').annotate(
        monthly=Sum('price_paid')
    ).aggregate(avg=Avg('monthly'))['avg'] or Decimal('0.00')
    
    avg_lifetime_months = 12  # Estimado
    ltv = avg_monthly_per_customer * avg_lifetime_months
    
    context = {
        'conversions_by_month': list(conversions_by_month),
        'avg_days_to_convert': round(avg_days_to_convert, 1),
        'revenue_by_source': revenue_by_source,
        'churn_rate': round(churn_rate, 2),
        'ltv': ltv,
    }
    
    return render(request, 'admin_dashboard/modules/conversion_analytics.html', context)


@superuser_required
def notifications_log(request):
    """
    Log de todas las notificaciones enviadas
    """
    notifications = SubscriptionNotification.objects.all().order_by('-sent_at')[:200]
    
    # Estadísticas
    total_sent = SubscriptionNotification.objects.count()
    delivered = SubscriptionNotification.objects.filter(delivered=True).count()
    opened = SubscriptionNotification.objects.filter(opened=True).count()
    clicked = SubscriptionNotification.objects.filter(clicked=True).count()
    
    delivery_rate = (delivered / total_sent * 100) if total_sent > 0 else 0
    open_rate = (opened / delivered * 100) if delivered > 0 else 0
    click_rate = (clicked / opened * 100) if opened > 0 else 0
    
    context = {
        'notifications': notifications,
        'total_sent': total_sent,
        'delivery_rate': round(delivery_rate, 2),
        'open_rate': round(open_rate, 2),
        'click_rate': round(click_rate, 2),
    }
    
    return render(request, 'admin_dashboard/modules/notifications_log.html', context)


@superuser_required
def update_module_price(request, module_id):
    """
    Actualizar precio de un módulo (AJAX)
    """
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            
            module = PlanFeature.objects.get(id=module_id)
            new_price = Decimal(data.get('price', '0.00'))
            
            module.price_monthly = new_price
            module.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Precio de "{module.name}" actualizado a ${new_price}'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


@superuser_required
def toggle_module_status(request, module_id):
    """
    Activar/desactivar un módulo (AJAX)
    """
    if request.method == 'POST':
        try:
            module = PlanFeature.objects.get(id=module_id)
            module.is_active = not module.is_active
            module.save()
            
            return JsonResponse({
                'success': True,
                'is_active': module.is_active,
                'message': f'Módulo {"activado" if module.is_active else "desactivado"}'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
