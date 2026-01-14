# -*- coding: utf-8 -*-
"""
Vistas para el selector de módulos À la Carte
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Q, F
from django.utils import timezone
from django.contrib import messages
from decimal import Decimal
from datetime import timedelta

from apps.organizations.models import (
    PlanFeature, 
    ModulePricing, 
    OrganizationModule,
    TrialStatus,
    Organization
)


@login_required
def module_marketplace(request):
    """
    Marketplace de módulos disponibles - Vista pública para todos
    Muestra todos los módulos agrupados por categoría con precios
    """
    organization = request.organization
    
    # Obtener trial status si existe
    try:
        trial = TrialStatus.objects.get(organization=organization)
    except TrialStatus.DoesNotExist:
        trial = None
    
    # Obtener configuración de precios
    try:
        pricing_config = ModulePricing.objects.first()
    except ModulePricing.DoesNotExist:
        pricing_config = None
    
    # Obtener todos los módulos activos disponibles para compra À la Carte
    all_modules = PlanFeature.objects.filter(
        is_active=True,
        can_purchase_separately=True
    ).exclude(
        # Excluir módulos empresariales antiguos
        code__in=['ENTERPRISE_ANALYTICS', 'DIAN_INVOICING', 'DIAN_PAYROLL']
    ).order_by('category', 'name')
    
    # Obtener módulos ya comprados por la organización
    purchased_module_ids = OrganizationModule.objects.filter(
        organization=organization,
        is_active=True
    ).values_list('module_id', flat=True)
    
    # Agrupar módulos por categoría
    categories = {}
    total_if_all = Decimal('0.00')
    
    for module in all_modules:
        category = module.get_category_display() if hasattr(module, 'get_category_display') else 'Otros'
        
        if category not in categories:
            categories[category] = {
                'modules': [],
                'total': Decimal('0.00')
            }
        
        # Agregar info de si ya está comprado
        module.is_purchased = module.id in purchased_module_ids
        module.price = module.price_monthly or Decimal('0.00')
        
        categories[category]['modules'].append(module)
        categories[category]['total'] += module.price
        total_if_all += module.price
    
    # Calcular descuentos
    discount_10 = total_if_all * Decimal('0.10') if pricing_config else Decimal('0.00')
    discount_20 = total_if_all * Decimal('0.20') if pricing_config else Decimal('0.00')
    
    context = {
        'categories': categories,
        'trial': trial,
        'pricing_config': pricing_config,
        'total_if_all': total_if_all,
        'total_with_10_discount': total_if_all - discount_10,
        'total_with_20_discount': total_if_all - discount_20,
        'purchased_count': len(purchased_module_ids),
    }
    
    return render(request, 'dashboard/modules/marketplace.html', context)


@login_required
def my_plan(request):
    """
    Vista del plan actual del usuario
    Muestra módulos activos, gastos mensuales, y opciones de gestión
    """
    organization = request.organization
    
    # Obtener trial status
    try:
        trial = TrialStatus.objects.get(organization=organization)
        is_trial = trial.state == 'active'
        days_remaining = trial.days_remaining
    except TrialStatus.DoesNotExist:
        trial = None
        is_trial = False
        days_remaining = 0
    
    # Obtener módulos activos
    active_modules = OrganizationModule.objects.filter(
        organization=organization,
        is_active=True
    ).select_related('module').order_by('module__category', 'module__name')
    
    # Calcular totales
    monthly_cost = active_modules.aggregate(
        total=Sum('price_paid')
    )['total'] or Decimal('0.00')
    
    # Estadísticas de uso si están disponibles
    module_usage = {}
    if trial and trial.most_used_modules:
        module_usage = trial.most_used_modules
    
    # Próxima fecha de facturación (primer día del próximo mes)
    today = timezone.now()
    if today.month == 12:
        next_billing_date = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_billing_date = today.replace(month=today.month + 1, day=1)
    
    context = {
        'organization': organization,
        'trial': trial,
        'is_trial': is_trial,
        'days_remaining': days_remaining,
        'active_modules': active_modules,
        'monthly_cost': monthly_cost,
        'module_count': active_modules.count(),
        'module_usage': module_usage,
        'next_billing_date': next_billing_date,
    }
    
    return render(request, 'dashboard/modules/my_plan.html', context)


@login_required
def module_selector(request):
    """
    Selector interactivo de módulos (usado post-trial)
    Permite elegir módulos con calculadora de precio en tiempo real
    """
    organization = request.organization
    
    # Verificar estado del trial
    try:
        trial = TrialStatus.objects.get(organization=organization)
        if trial.state == 'active':
            messages.info(request, 'Tu trial está activo. Puedes elegir módulos cuando expire.')
            return redirect('dashboard:my_plan')
    except TrialStatus.DoesNotExist:
        trial = None
    
    # Obtener configuración de precios
    try:
        pricing_config = ModulePricing.objects.first()
    except ModulePricing.DoesNotExist:
        pricing_config = None
    
    # Obtener todos los módulos disponibles
    all_modules = PlanFeature.objects.filter(
        is_active=True,
        can_purchase_separately=True
    ).exclude(
        code__in=['ENTERPRISE_ANALYTICS', 'DIAN_INVOICING', 'DIAN_PAYROLL']
    ).order_by('category', 'name')
    
    # Módulos ya comprados
    purchased_module_ids = OrganizationModule.objects.filter(
        organization=organization,
        is_active=True
    ).values_list('module_id', flat=True)
    
    # Agrupar por categoría
    categories = {}
    for module in all_modules:
        category = module.get_category_display() if hasattr(module, 'get_category_display') else 'Otros'
        
        if category not in categories:
            categories[category] = []
        
        module.is_purchased = module.id in purchased_module_ids
        module.price = module.price_monthly or Decimal('0.00')
        categories[category].append(module)
    
    # Estadísticas de uso durante el trial
    most_used = []
    if trial and trial.most_used_modules:
        # Convertir a lista ordenada por uso
        most_used = sorted(
            trial.most_used_modules.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Top 5
    
    context = {
        'categories': categories,
        'trial': trial,
        'pricing_config': pricing_config,
        'purchased_module_ids': list(purchased_module_ids),
        'most_used': most_used,
    }
    
    return render(request, 'dashboard/modules/selector.html', context)


@login_required
def calculate_price(request):
    """
    API endpoint para calcular precio en tiempo real
    Recibe lista de IDs de módulos y retorna precio con descuentos
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    import json
    try:
        data = json.loads(request.body)
        module_ids = data.get('module_ids', [])
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    
    # Obtener módulos seleccionados
    modules = PlanFeature.objects.filter(
        id__in=module_ids,
        is_active=True
    )
    
    # Calcular subtotal
    subtotal = sum(m.price_monthly or Decimal('0.00') for m in modules)
    
    # Obtener configuración de descuentos
    try:
        pricing = ModulePricing.objects.first()
        discount_4 = pricing.discount_4_modules if pricing else 10
        discount_7 = pricing.discount_7_modules if pricing else 20
    except:
        discount_4 = 10
        discount_7 = 20
    
    # Aplicar descuentos
    module_count = len(module_ids)
    discount_percent = 0
    discount_amount = Decimal('0.00')
    
    if module_count >= 7:
        discount_percent = discount_7
        discount_amount = subtotal * Decimal(str(discount_7)) / Decimal('100')
    elif module_count >= 4:
        discount_percent = discount_4
        discount_amount = subtotal * Decimal(str(discount_4)) / Decimal('100')
    
    total = subtotal - discount_amount
    
    return JsonResponse({
        'module_count': module_count,
        'subtotal': float(subtotal),
        'discount_percent': discount_percent,
        'discount_amount': float(discount_amount),
        'total': float(total),
    })


@login_required
def add_module(request, module_id):
    """
    Agregar un módulo individual al plan
    Redirige a checkout para pago
    """
    organization = request.organization
    module = get_object_or_404(PlanFeature, id=module_id, is_active=True)
    
    # Verificar si ya está comprado
    existing = OrganizationModule.objects.filter(
        organization=organization,
        module=module,
        is_active=True
    ).exists()
    
    if existing:
        messages.warning(request, f'Ya tienes el módulo "{module.name}" activo.')
        return redirect('dashboard:my_plan')
    
    # Guardar en sesión para checkout
    request.session['checkout_modules'] = [module_id]
    
    return redirect('dashboard:module_checkout')


@login_required
def remove_module(request, module_id):
    """
    Desactivar un módulo del plan
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    organization = request.organization
    
    try:
        org_module = OrganizationModule.objects.get(
            organization=organization,
            module_id=module_id,
            is_active=True
        )
        
        # Desactivar (no eliminar)
        org_module.is_active = False
        org_module.auto_renew = False
        org_module.save()
        
        messages.success(
            request,
            f'Módulo "{org_module.module.name}" desactivado. '
            f'No se cobrará en el próximo ciclo.'
        )
        
        return JsonResponse({'success': True})
        
    except OrganizationModule.DoesNotExist:
        return JsonResponse({'error': 'Módulo no encontrado'}, status=404)


@login_required
def module_checkout(request):
    """
    Página de checkout para pagar módulos seleccionados
    """
    organization = request.organization
    
    # Obtener módulos desde sesión
    module_ids = request.session.get('checkout_modules', [])
    
    if not module_ids:
        messages.warning(request, 'No hay módulos seleccionados.')
        return redirect('dashboard:module_selector')
    
    # Obtener módulos
    modules = PlanFeature.objects.filter(
        id__in=module_ids,
        is_active=True
    )
    
    # Calcular precios
    subtotal = sum(m.price_monthly or Decimal('0.00') for m in modules)
    
    # Descuentos
    try:
        pricing = ModulePricing.objects.first()
        discount_4 = pricing.discount_4_modules if pricing else 10
        discount_7 = pricing.discount_7_modules if pricing else 20
    except:
        discount_4 = 10
        discount_7 = 20
    
    module_count = len(module_ids)
    discount_percent = 0
    discount_amount = Decimal('0.00')
    
    if module_count >= 7:
        discount_percent = discount_7
        discount_amount = subtotal * Decimal(str(discount_7)) / Decimal('100')
    elif module_count >= 4:
        discount_percent = discount_4
        discount_amount = subtotal * Decimal(str(discount_4)) / Decimal('100')
    
    total = subtotal - discount_amount
    
    context = {
        'organization': organization,
        'modules': modules,
        'module_count': module_count,
        'subtotal': subtotal,
        'discount_percent': discount_percent,
        'discount_amount': discount_amount,
        'total': total,
    }
    
    return render(request, 'dashboard/modules/checkout.html', context)
