"""
Vistas para gestión de órdenes de exámenes especiales
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML
import tempfile

from apps.patients.models import ClinicalHistory, ExamOrder
from apps.patients.models_clinical_exams import ExamOrder
from .forms_exam_orders import ExamOrderForm


@login_required
def create_exam_order(request, history_id):
    """Crear una nueva orden de examen desde la historia clínica"""
    history = get_object_or_404(ClinicalHistory, id=history_id, organization=request.user.organization)
    
    if request.method == 'POST':
        form = ExamOrderForm(request.POST, organization=request.user.organization)
        if form.is_valid():
            exam_order = form.save(commit=False)
            exam_order.clinical_history = history
            exam_order.ordered_by = request.user
            exam_order.organization = request.user.organization
            exam_order.save()
            
            messages.success(request, f'Orden de {exam_order.get_exam_type_display()} creada exitosamente')
            return redirect('patients:clinical_history_detail', pk=history.id)
    else:
        form = ExamOrderForm(organization=request.user.organization)
    
    context = {
        'form': form,
        'history': history,
        'patient': history.patient,
    }
    return render(request, 'exams/order_form.html', context)


@login_required
def exam_order_list(request):
    """Lista de todas las órdenes de exámenes"""
    status_filter = request.GET.get('status', '')
    exam_type_filter = request.GET.get('exam_type', '')
    
    orders = ExamOrder.objects.filter(
        organization=request.user.organization
    ).select_related('clinical_history__patient', 'ordered_by')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    if exam_type_filter:
        orders = orders.filter(exam_type=exam_type_filter)
    
    orders = orders.order_by('-order_date', '-created_at')
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'exam_type_filter': exam_type_filter,
        'exam_types': ExamOrder.EXAM_TYPES,
        'statuses': ExamOrder.STATUS_CHOICES,
    }
    return render(request, 'exams/order_list.html', context)


@login_required
def exam_order_detail(request, order_id):
    """Detalle de una orden de examen"""
    order = get_object_or_404(
        ExamOrder,
        id=order_id,
        organization=request.user.organization
    )
    
    context = {
        'order': order,
        'patient': order.clinical_history.patient,
        'history': order.clinical_history,
    }
    return render(request, 'exams/order_detail.html', context)


@login_required
def exam_order_pdf(request, order_id):
    """Generar PDF de la orden médica"""
    order = get_object_or_404(
        ExamOrder,
        id=order_id,
        organization=request.user.organization
    )
    
    # Renderizar template HTML
    html_string = render_to_string('exams/order_pdf.html', {
        'order': order,
        'patient': order.clinical_history.patient,
        'organization': request.user.organization,
        'generated_date': timezone.now(),
    })
    
    # Generar PDF
    html = HTML(string=html_string)
    result = html.write_pdf()
    
    # Respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="orden_examen_{order.id}_{order.clinical_history.patient.full_name}.pdf"'
    response['Content-Transfer-Encoding'] = 'binary'
    response.write(result)
    
    return response


@login_required
def update_exam_order_status(request, order_id):
    """Actualizar el estado de una orden"""
    order = get_object_or_404(
        ExamOrder,
        id=order_id,
        organization=request.user.organization
    )
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(ExamOrder.STATUS_CHOICES).keys():
            order.status = new_status
            
            if new_status == 'scheduled':
                order.scheduled_date = request.POST.get('scheduled_date')
            elif new_status == 'completed':
                order.performed_date = timezone.now().date()
            elif new_status == 'cancelled':
                order.cancellation_reason = request.POST.get('cancellation_reason', '')
            
            order.save()
            messages.success(request, f'Estado actualizado a: {order.get_status_display()}')
        
        return redirect('patients:exam_order_detail', order_id=order.id)
    
    return redirect('patients:exam_order_detail', order_id=order.id)


@login_required
def pending_exams_dashboard(request):
    """Dashboard de exámenes pendientes"""
    pending_orders = ExamOrder.objects.filter(
        organization=request.user.organization,
        status__in=['pending', 'scheduled']
    ).select_related('clinical_history__patient', 'ordered_by').order_by('order_date')
    
    # Estadísticas
    stats = {
        'total_pending': pending_orders.filter(status='pending').count(),
        'total_scheduled': pending_orders.filter(status='scheduled').count(),
        'urgent': pending_orders.filter(priority='urgent').count(),
        'stat': pending_orders.filter(priority='stat').count(),
    }
    
    context = {
        'pending_orders': pending_orders,
        'stats': stats,
    }
    return render(request, 'exams/dashboard.html', context)
