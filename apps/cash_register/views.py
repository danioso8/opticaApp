"""
Vistas para el módulo de Gestión de Caja
"""

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from datetime import datetime, timedelta

from .models import CashRegister, CashMovement, CashClosure, CashCategory
from .services.cash_service import CashService
from .services.report_service import ReportService


@login_required
def dashboard(request):
    """Dashboard principal de caja"""
    organization = request.organization
    
    # Obtener cajas activas
    cash_registers = CashRegister.objects.filter(
        organization=organization,
        is_active=True
    )
    
    # Resumen del día
    today = timezone.now().date()
    daily_summary = CashService.get_daily_summary(organization, today)
    
    # Últimos movimientos
    recent_movements = CashMovement.objects.filter(
        organization=organization,
        is_deleted=False
    ).select_related('cash_register', 'created_by')[:10]
    
    # Cierres pendientes
    pending_closures = CashClosure.objects.filter(
        organization=organization,
        status='PENDING'
    ).count()
    
    context = {
        'cash_registers': cash_registers,
        'daily_summary': daily_summary,
        'recent_movements': recent_movements,
        'pending_closures': pending_closures,
    }
    
    return render(request, 'cash_register/dashboard.html', context)


@login_required
def cash_register_list(request):
    """Lista de cajas registradoras"""
    organization = request.organization
    
    cash_registers = CashRegister.objects.filter(
        organization=organization
    ).select_related('responsible')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        cash_registers = cash_registers.filter(status=status_filter)
    
    context = {
        'cash_registers': cash_registers,
        'status_filter': status_filter,
    }
    
    return render(request, 'cash_register/cash_register_list.html', context)


@login_required
def create_cash_register(request):
    """Crear una nueva caja registradora"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            location = request.POST.get('location', '')
            
            if not name:
                messages.error(request, 'El nombre de la caja es obligatorio')
                return redirect('cash_register:create_register')
            
            cash_register = CashRegister.objects.create(
                organization=request.organization,
                name=name,
                location=location,
                status='CLOSED',
                is_active=True
            )
            
            messages.success(request, f'Caja "{cash_register.name}" creada exitosamente')
            return redirect('cash_register:detail', pk=cash_register.pk)
            
        except Exception as e:
            messages.error(request, f'Error al crear la caja: {str(e)}')
    
    return render(request, 'cash_register/cash_register_create.html')


@login_required
def cash_register_detail(request, pk):
    """Detalle de una caja registradora"""
    cash_register = get_object_or_404(
        CashRegister,
        pk=pk,
        organization=request.organization
    )
    
    # Resumen actual
    summary = CashService.get_cash_register_summary(cash_register)
    
    # Movimientos del día
    today = timezone.now().date()
    movements = cash_register.movements.filter(
        created_at__date=today,
        is_deleted=False
    ).select_related('created_by')
    
    context = {
        'cash_register': cash_register,
        'summary': summary,
        'movements': movements,
    }
    
    return render(request, 'cash_register/cash_register_detail.html', context)


@login_required
def open_cash_register(request, pk):
    """Abrir una caja registradora"""
    cash_register = get_object_or_404(
        CashRegister,
        pk=pk,
        organization=request.organization
    )
    
    if request.method == 'POST':
        try:
            opening_amount = Decimal(request.POST.get('opening_amount', '0'))
            
            if opening_amount < 0:
                messages.error(request, 'El monto de apertura no puede ser negativo')
                return redirect('cash_register:detail', pk=pk)
            
            cash_register, movement = CashService.open_cash_register(
                cash_register,
                request.user,
                opening_amount
            )
            
            messages.success(request, f'Caja {cash_register.name} abierta exitosamente')
            return redirect('cash_register:detail', pk=pk)
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al abrir la caja: {str(e)}')
    
    context = {
        'cash_register': cash_register,
    }
    
    return render(request, 'cash_register/open_cash_register.html', context)


@login_required
def movement_list(request):
    """Lista de movimientos de caja"""
    organization = request.organization
    
    # Filtros
    cash_register_id = request.GET.get('cash_register')
    movement_type = request.GET.get('movement_type')
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Query base
    movements = CashMovement.objects.filter(
        organization=organization,
        is_deleted=False
    ).select_related('cash_register', 'created_by', 'sale')
    
    # Aplicar filtros
    if cash_register_id:
        movements = movements.filter(cash_register_id=cash_register_id)
    
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    
    if category:
        movements = movements.filter(category=category)
    
    if start_date:
        movements = movements.filter(created_at__date__gte=start_date)
    
    if end_date:
        movements = movements.filter(created_at__date__lte=end_date)
    
    # Paginación
    paginator = Paginator(movements, 25)
    page = request.GET.get('page')
    movements = paginator.get_page(page)
    
    # Totales
    total_income = CashMovement.objects.filter(
        organization=organization,
        movement_type='INCOME',
        is_deleted=False
    )
    if start_date:
        total_income = total_income.filter(created_at__date__gte=start_date)
    if end_date:
        total_income = total_income.filter(created_at__date__lte=end_date)
    total_income = total_income.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    total_expense = CashMovement.objects.filter(
        organization=organization,
        movement_type='EXPENSE',
        is_deleted=False
    )
    if start_date:
        total_expense = total_expense.filter(created_at__date__gte=start_date)
    if end_date:
        total_expense = total_expense.filter(created_at__date__lte=end_date)
    total_expense = total_expense.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Cajas para filtro
    cash_registers = CashRegister.objects.filter(
        organization=organization,
        is_active=True
    )
    
    context = {
        'movements': movements,
        'cash_registers': cash_registers,
        'total_income': total_income,
        'total_expense': total_expense,
        'filters': {
            'cash_register': cash_register_id,
            'movement_type': movement_type,
            'category': category,
            'start_date': start_date,
            'end_date': end_date,
        }
    }
    
    return render(request, 'cash_register/movement_list.html', context)


@login_required
def create_movement(request):
    """Crear un nuevo movimiento de caja"""
    organization = request.organization
    
    # Solo cajas abiertas
    cash_registers = CashRegister.objects.filter(
        organization=organization,
        status='OPEN',
        is_active=True
    )
    
    if request.method == 'POST':
        try:
            cash_register_id = request.POST.get('cash_register')
            movement_type = request.POST.get('movement_type')
            category = request.POST.get('category')
            payment_method = request.POST.get('payment_method', 'CASH')
            amount = Decimal(request.POST.get('amount', '0'))
            description = request.POST.get('description')
            reference = request.POST.get('reference', '')
            
            cash_register = get_object_or_404(CashRegister, pk=cash_register_id)
            
            movement = CashService.create_movement(
                cash_register=cash_register,
                movement_type=movement_type,
                category=category,
                amount=amount,
                description=description,
                payment_method=payment_method,
                reference=reference if reference else None,
                user=request.user
            )
            
            messages.success(request, 'Movimiento registrado exitosamente')
            return redirect('cash_register:movement_list')
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al crear movimiento: {str(e)}')
    
    context = {
        'cash_registers': cash_registers,
    }
    
    return render(request, 'cash_register/movement_create.html', context)


@login_required
def close_cash_register(request, pk):
    """Cerrar una caja registradora"""
    cash_register = get_object_or_404(
        CashRegister,
        pk=pk,
        organization=request.organization
    )
    
    # Resumen del día
    summary = CashService.get_cash_register_summary(cash_register)
    
    if request.method == 'POST':
        try:
            counted_amounts = {
                'cash': Decimal(request.POST.get('counted_cash', '0')),
                'cards': Decimal(request.POST.get('counted_cards', '0')),
                'transfers': Decimal(request.POST.get('counted_transfers', '0')),
                'checks': Decimal(request.POST.get('counted_checks', '0')),
                'other': Decimal(request.POST.get('counted_other', '0')),
                'breakdown': {}  # Podemos agregar desglose de denominaciones después
            }
            
            notes = request.POST.get('notes', '')
            
            closure = CashService.close_cash_register(
                cash_register,
                counted_amounts,
                notes,
                request.user
            )
            
            messages.success(request, f'Caja cerrada exitosamente. Diferencia: ${closure.difference}')
            return redirect('cash_register:closure_detail', pk=closure.pk)
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al cerrar la caja: {str(e)}')
    
    context = {
        'cash_register': cash_register,
        'summary': summary,
    }
    
    return render(request, 'cash_register/close_cash_register.html', context)


@login_required
def closure_list(request):
    """Lista de cierres de caja"""
    organization = request.organization
    
    closures = CashClosure.objects.filter(
        organization=organization
    ).select_related('cash_register', 'closed_by', 'reviewed_by')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        closures = closures.filter(status=status_filter)
    
    cash_register_id = request.GET.get('cash_register')
    if cash_register_id:
        closures = closures.filter(cash_register_id=cash_register_id)
    
    # Paginación
    paginator = Paginator(closures, 20)
    page = request.GET.get('page')
    closures = paginator.get_page(page)
    
    # Cajas para filtro
    cash_registers = CashRegister.objects.filter(
        organization=organization,
        is_active=True
    )
    
    context = {
        'closures': closures,
        'cash_registers': cash_registers,
        'status_filter': status_filter,
    }
    
    return render(request, 'cash_register/closure_list.html', context)


@login_required
def closure_detail(request, pk):
    """Detalle de un cierre de caja"""
    closure = get_object_or_404(
        CashClosure,
        pk=pk,
        organization=request.organization
    )
    
    # Movimientos del día
    movements = CashMovement.objects.filter(
        cash_register=closure.cash_register,
        created_at__date=closure.closure_date,
        is_deleted=False
    ).select_related('created_by')
    
    context = {
        'closure': closure,
        'movements': movements,
    }
    
    return render(request, 'cash_register/closure_detail.html', context)


@login_required
def approve_closure(request, pk):
    """Aprobar un cierre de caja"""
    closure = get_object_or_404(
        CashClosure,
        pk=pk,
        organization=request.organization
    )
    
    if request.method == 'POST':
        try:
            closure.approve(request.user)
            messages.success(request, 'Cierre aprobado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al aprobar: {str(e)}')
    
    return redirect('cash_register:closure_detail', pk=pk)


@login_required
def reject_closure(request, pk):
    """Rechazar un cierre de caja"""
    closure = get_object_or_404(
        CashClosure,
        pk=pk,
        organization=request.organization
    )
    
    if request.method == 'POST':
        try:
            closure.reject(request.user)
            messages.success(request, 'Cierre rechazado')
        except Exception as e:
            messages.error(request, f'Error al rechazar: {str(e)}')
    
    return redirect('cash_register:closure_detail', pk=pk)


# API Endpoints para AJAX

@login_required
def api_cash_register_summary(request, pk):
    """API: Obtener resumen actual de una caja"""
    try:
        cash_register = get_object_or_404(
            CashRegister,
            pk=pk,
            organization=request.organization
        )
        
        summary = CashService.get_cash_register_summary(cash_register)
        
        # Convertir Decimals a strings para JSON
        for key, value in summary.items():
            if isinstance(value, Decimal):
                summary[key] = str(value)
        
        return JsonResponse({
            'success': True,
            'summary': summary
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def api_daily_report(request):
    """API: Reporte diario"""
    try:
        organization = request.organization
        date_str = request.GET.get('date')
        
        if date_str:
            date_filter = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date_filter = timezone.now().date()
        
        report = CashService.get_daily_summary(organization, date_filter)
        
        # Convertir Decimals a strings
        report['total_income'] = str(report['total_income'])
        report['total_expense'] = str(report['total_expense'])
        report['total_net'] = str(report['total_net'])
        
        for summary in report['summaries']:
            summary['income'] = str(summary['income'])
            summary['expense'] = str(summary['expense'])
            summary['net'] = str(summary['net'])
            summary['cash_register'] = summary['cash_register'].name
        
        return JsonResponse({
            'success': True,
            'report': report
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def reports(request):
    """Vista de reportes"""
    organization = request.organization
    
    # Reportes predeterminados
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Flujo de efectivo últimos 30 días
    cash_flow = ReportService.get_cash_flow_analysis(organization, 30)
    
    # Reporte de cierres
    closure_report = ReportService.get_closure_report(
        organization,
        start_date=month_ago,
        end_date=today
    )
    
    context = {
        'cash_flow': cash_flow,
        'closure_report': closure_report,
    }
    
    return render(request, 'cash_register/reports.html', context)


# API endpoints para categorías
@login_required
def create_category_ajax(request):
    """Crear categoría desde modal (AJAX)"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            category_type = request.POST.get('category_type', '').strip()
            description = request.POST.get('description', '').strip()
            
            if not name or not category_type:
                return JsonResponse({
                    'success': False,
                    'error': 'Nombre y tipo son obligatorios'
                }, status=400)
            
            # Verificar si ya existe
            existing = CashCategory.objects.filter(
                organization=request.organization,
                name__iexact=name,
                category_type=category_type
            ).first()
            
            if existing:
                if not existing.is_active:
                    existing.is_active = True
                    existing.save()
                    return JsonResponse({
                        'success': True,
                        'category': {
                            'id': existing.id,
                            'name': existing.name,
                            'type': existing.category_type
                        },
                        'message': 'Categoría reactivada'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Esta categoría ya existe'
                    }, status=400)
            
            # Crear nueva categoría
            category = CashCategory.objects.create(
                organization=request.organization,
                name=name,
                category_type=category_type,
                description=description,
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'type': category.category_type,
                    'description': category.description
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


@login_required
def get_categories_ajax(request):
    """Obtener categorías por tipo (AJAX)"""
    category_type = request.GET.get('type', '')
    
    categories = CashCategory.objects.filter(
        organization=request.organization,
        is_active=True
    )
    
    if category_type:
        categories = categories.filter(category_type=category_type)
    
    data = [{
        'id': cat.id,
        'name': cat.name,
        'type': cat.category_type,
        'description': cat.description
    } for cat in categories]
    
    return JsonResponse({'categories': data})

