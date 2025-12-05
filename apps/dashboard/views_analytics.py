"""
Vistas para Dashboard Analytics Avanzado
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from .utils_analytics import MetricsCalculator
from .models_analytics import KPITarget, CustomerSatisfaction


@login_required
def analytics_dashboard(request):
    """Dashboard principal de analytics"""
    if not request.organization:
        return redirect('organizations:list')
    
    calculator = MetricsCalculator(request.organization)
    
    # KPIs principales
    kpis = calculator.get_kpi_summary()
    
    # Comparativa mensual
    monthly_comparison = calculator.get_monthly_comparison()
    
    # Satisfacción del cliente
    satisfaction = calculator.get_satisfaction_summary()
    
    # Top productos
    top_products = calculator.get_top_products(limit=5)
    
    # Objetivos activos
    active_targets = KPITarget.objects.filter(
        organization=request.organization,
        is_active=True,
        period_end__gte=timezone.now().date()
    ).order_by('period_end')[:5]
    
    context = {
        'kpis': kpis,
        'monthly_comparison': monthly_comparison,
        'satisfaction': satisfaction,
        'top_products': top_products,
        'active_targets': active_targets,
    }
    
    return render(request, 'dashboard/analytics/dashboard.html', context)


@login_required
def api_realtime_metrics(request):
    """API para métricas en tiempo real (AJAX/WebSocket)"""
    if not request.organization:
        return JsonResponse({'error': 'No organization'}, status=400)
    
    calculator = MetricsCalculator(request.organization)
    kpis = calculator.get_kpi_summary()
    
    return JsonResponse({
        'success': True,
        'timestamp': timezone.now().isoformat(),
        'metrics': {
            'revenue_today': {
                'value': float(kpis['revenue_today']['value']),
                'change': float(kpis['revenue_today']['change']),
                'trend': kpis['revenue_today']['trend']
            },
            'appointments_today': {
                'value': kpis['appointments_today']['value'],
                'change': float(kpis['appointments_today']['change']),
                'trend': kpis['appointments_today']['trend']
            },
            'new_patients': {
                'value': kpis['new_patients']['value'],
                'change': float(kpis['new_patients']['change']),
                'trend': kpis['new_patients']['trend']
            },
            'conversion_rate': {
                'value': float(kpis['conversion_rate']['value']),
                'change': float(kpis['conversion_rate']['change']),
                'trend': kpis['conversion_rate']['trend']
            }
        }
    })


@login_required
def api_revenue_trend(request):
    """API para gráfico de tendencia de ingresos"""
    if not request.organization:
        return JsonResponse({'error': 'No organization'}, status=400)
    
    days = int(request.GET.get('days', 30))
    calculator = MetricsCalculator(request.organization)
    trend_data = calculator.get_revenue_trend(days=days)
    
    # Formatear para Chart.js
    labels = [item['created_at__date'].strftime('%d/%m') for item in trend_data]
    values = [float(item['total']) for item in trend_data]
    
    return JsonResponse({
        'success': True,
        'labels': labels,
        'datasets': [{
            'label': 'Ingresos',
            'data': values,
            'backgroundColor': 'rgba(99, 102, 241, 0.2)',
            'borderColor': 'rgba(99, 102, 241, 1)',
            'borderWidth': 2,
            'fill': True
        }]
    })


@login_required
def api_heatmap_data(request):
    """API para heatmap de horarios populares"""
    if not request.organization:
        return JsonResponse({'error': 'No organization'}, status=400)
    
    days = int(request.GET.get('days', 30))
    calculator = MetricsCalculator(request.organization)
    
    # Calcular y guardar datos
    heatmap_data = calculator.calculate_heatmap_data(days=days)
    
    # Formatear para visualización
    formatted_data = []
    for (day, hour), data in heatmap_data.items():
        formatted_data.append({
            'day': day,
            'hour': hour,
            'count': data['count'],
            'revenue': float(data['revenue'])
        })
    
    return JsonResponse({
        'success': True,
        'data': formatted_data
    })


@login_required
def api_appointments_distribution(request):
    """API para distribución de citas por estado"""
    if not request.organization:
        return JsonResponse({'error': 'No organization'}, status=400)
    
    calculator = MetricsCalculator(request.organization)
    distribution = calculator.get_appointments_by_status()
    
    # Formatear para gráfico de dona
    labels = []
    values = []
    colors = {
        'pending': '#FCD34D',  # Amarillo
        'confirmed': '#60A5FA',  # Azul
        'completed': '#34D399',  # Verde
        'cancelled': '#F87171',  # Rojo
        'no_show': '#9CA3AF',  # Gris
    }
    
    for item in distribution:
        labels.append(item['status'].replace('_', ' ').title())
        values.append(item['count'])
    
    return JsonResponse({
        'success': True,
        'labels': labels,
        'datasets': [{
            'data': values,
            'backgroundColor': [colors.get(item['status'], '#9CA3AF') for item in distribution]
        }]
    })


@login_required
def api_top_products(request):
    """API para productos más vendidos"""
    if not request.organization:
        return JsonResponse({'error': 'No organization'}, status=400)
    
    limit = int(request.GET.get('limit', 5))
    calculator = MetricsCalculator(request.organization)
    top_products = calculator.get_top_products(limit=limit)
    
    return JsonResponse({
        'success': True,
        'products': top_products
    })


@login_required
def satisfaction_survey(request, patient_id):
    """Vista para encuesta de satisfacción"""
    from apps.patients.models import Patient
    
    patient = Patient.objects.get(id=patient_id, organization=request.organization)
    
    if request.method == 'POST':
        survey = CustomerSatisfaction.objects.create(
            organization=request.organization,
            patient=patient,
            overall_rating=int(request.POST.get('overall_rating', 5)),
            service_rating=int(request.POST.get('service_rating', 5)),
            quality_rating=int(request.POST.get('quality_rating', 5)),
            speed_rating=int(request.POST.get('speed_rating', 5)),
            nps_score=int(request.POST.get('nps_score')) if request.POST.get('nps_score') else None,
            comments=request.POST.get('comments', ''),
            responded_via=request.POST.get('responded_via', 'web')
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': '¡Gracias por tu feedback!'
            })
        
        messages.success(request, '¡Gracias por tu feedback!')
        return redirect('dashboard:patient_detail', patient_id=patient.id)
    
    context = {
        'patient': patient
    }
    
    return render(request, 'dashboard/analytics/satisfaction_survey.html', context)
