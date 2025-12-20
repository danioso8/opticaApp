"""
Vistas para Gestión de Órdenes de Exámenes Especiales
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from io import BytesIO
import logging

from apps.patients.models import Patient, ClinicalHistory, ExamOrder, Doctor
from apps.patients.forms_exam_orders import ExamOrderForm, ExamOrderFilterForm, ExamOrderStatusForm

logger = logging.getLogger(__name__)


@login_required
def exam_order_create(request, patient_id, history_id):
    """Crear una nueva orden de examen"""
    try:
        # Log para debugging
        logger.info(f"Intentando crear orden para paciente {patient_id}, historia {history_id}")
        
        # Obtener organización de manera segura
        organization = getattr(request, 'organization', None)
        logger.info(f"Organización: {organization}")
        
        # Buscar el paciente
        if organization:
            patient = get_object_or_404(Patient, id=patient_id, organization=organization)
            history = get_object_or_404(ClinicalHistory, id=history_id, patient=patient, organization=organization)
        else:
            patient = get_object_or_404(Patient, id=patient_id)
            history = get_object_or_404(ClinicalHistory, id=history_id, patient=patient)
        
        logger.info(f"Paciente encontrado: {patient.full_name}")
        
        if request.method == 'POST':
            logger.info("Procesando POST request")
            logger.info(f"POST data: {request.POST}")
            
            form = ExamOrderForm(request.POST, organization=organization)
            
            if form.is_valid():
                logger.info("Formulario válido, guardando orden")
                order = form.save(commit=False)
                order.clinical_history = history
                
                # Asignar organización si existe
                if organization:
                    order.organization = organization
                
                # Si no se especificó un médico, intentar usar el usuario actual si es doctor
                if not order.ordered_by and organization:
                    try:
                        doctor = Doctor.objects.filter(user=request.user, organization=organization).first()
                        if doctor:
                            order.ordered_by = doctor
                            logger.info(f"Doctor asignado: {doctor.full_name}")
                    except Exception as e:
                        logger.error(f"Error al asignar doctor: {e}")
                
                order.save()
                logger.info(f"Orden guardada exitosamente: {order.id}")
                
                messages.success(request, f'✅ Orden de {order.get_exam_type_display()} creada exitosamente.')
                
                # Redirigir según la acción del usuario
                if 'save_and_print' in request.POST:
                    return redirect('dashboard:exam_order_pdf', patient_id=patient_id, history_id=history_id, order_id=order.id)
                else:
                    return redirect('dashboard:clinical_history_detail', patient_id=patient_id, history_id=history_id)
            else:
                logger.error(f"Formulario inválido. Errores: {form.errors}")
                messages.error(request, f'Por favor corrige los errores: {form.errors}')
        else:
            logger.info("Mostrando formulario GET")
            form = ExamOrderForm(organization=organization)
        
        context = {
            'patient': patient,
            'history': history,
            'form': form,
            'title': 'Nueva Orden de Examen'
        }
        
        return render(request, 'dashboard/patients/exams/order_form.html', context)
        
    except Exception as e:
        logger.error(f'Error en exam_order_create: {str(e)}', exc_info=True)
        messages.error(request, f'❌ Error al crear la orden: {str(e)}')
        return redirect('dashboard:patients_list')


@login_required
def exam_order_list(request):
    """Listar todas las órdenes de exámenes"""
    try:
        logger.info("Cargando listado de órdenes de examen")
        organization = getattr(request, 'organization', None)
        org_filter = {'organization': organization} if organization else {}
        
        # Obtener órdenes (sin select_related de performed_by por ahora)
        orders = ExamOrder.objects.filter(**org_filter).select_related(
            'clinical_history__patient',
            'ordered_by'
        ).order_by('-order_date', '-created_at')
        
        logger.info(f"Se encontraron {orders.count()} órdenes")
        
        # Aplicar filtros
        filter_form = ExamOrderFilterForm(request.GET)
        if filter_form.is_valid():
            status = filter_form.cleaned_data.get('status')
            exam_type = filter_form.cleaned_data.get('exam_type')
            date_from = filter_form.cleaned_data.get('date_from')
            date_to = filter_form.cleaned_data.get('date_to')
            search = filter_form.cleaned_data.get('search')
            
            if status:
                orders = orders.filter(status=status)
            
            if exam_type:
                orders = orders.filter(exam_type=exam_type)
            
            if date_from:
                orders = orders.filter(order_date__gte=date_from)
            
            if date_to:
                orders = orders.filter(order_date__lte=date_to)
            
            if search:
                orders = orders.filter(
                    Q(clinical_history__patient__full_name__icontains=search) |
                    Q(clinical_history__patient__identification__icontains=search)
                )
        
        # Estadísticas
        stats = {
            'total': orders.count(),
            'pending': orders.filter(status='pending').count(),
            'scheduled': orders.filter(status='scheduled').count(),
            'in_progress': orders.filter(status='in_progress').count(),
            'completed': orders.filter(status='completed').count(),
        }
        
        logger.info(f"Estadísticas calculadas: {stats}")
        
        context = {
            'orders': orders,
            'filter_form': filter_form,
            'stats': stats,
            'title': 'Órdenes de Exámenes'
        }
        
        return render(request, 'dashboard/patients/exams/order_list.html', context)
    
    except Exception as e:
        logger.error(f'Error en exam_order_list: {str(e)}', exc_info=True)
        messages.error(request, f'❌ Error al cargar las órdenes: {str(e)}')
        return redirect('dashboard:home')
        
        if exam_type:
            orders = orders.filter(exam_type=exam_type)
        
        if date_from:
            orders = orders.filter(order_date__gte=date_from)
        
        if date_to:
            orders = orders.filter(order_date__lte=date_to)
        
        if search:
            orders = orders.filter(
                Q(clinical_history__patient__full_name__icontains=search) |
                Q(clinical_history__patient__identification__icontains=search)
            )
    
    # Estadísticas
    stats = {
        'total': orders.count(),
        'pending': orders.filter(status='pending').count(),
        'scheduled': orders.filter(status='scheduled').count(),
        'in_progress': orders.filter(status='in_progress').count(),
        'completed': orders.filter(status='completed').count(),
    }
    
    context = {
        'orders': orders,
        'filter_form': filter_form,
        'stats': stats,
        'title': 'Órdenes de Exámenes'
    }
    
    return render(request, 'dashboard/patients/exams/order_list.html', context)


@login_required
@login_required
def exam_order_detail(request, order_id):
    """Ver detalle de una orden"""
    try:
        logger.info(f"Cargando detalle de orden {order_id}")
        organization = getattr(request, 'organization', None)
        org_filter = {'organization': organization} if organization else {}
        
        order = get_object_or_404(
            ExamOrder.objects.select_related('clinical_history__patient', 'ordered_by'),
            id=order_id,
            **org_filter
        )
        
        context = {
            'order': order,
            'patient': order.clinical_history.patient if order.clinical_history else None,
            'history': order.clinical_history,
            'title': f'Orden de {order.get_exam_type_display()}'
        }
        
        logger.info(f"Detalle de orden {order_id} cargado correctamente")
        return render(request, 'dashboard/patients/exams/order_detail.html', context)
    
    except Exception as e:
        logger.error(f'Error en exam_order_detail: {str(e)}', exc_info=True)
        messages.error(request, f'❌ Error al cargar el detalle: {str(e)}')
        return redirect('dashboard:exam_order_list')


@login_required
def exam_order_update_status(request, order_id):
    """Actualizar estado de una orden"""
    try:
        logger.info(f"Actualizando estado de orden {order_id}")
        organization = getattr(request, 'organization', None)
        org_filter = {'organization': organization} if organization else {}
        
        order = get_object_or_404(ExamOrder, id=order_id, **org_filter)
        
        if request.method == 'POST':
            form = ExamOrderStatusForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
                messages.success(request, f'✅ Estado actualizado a: {order.get_status_display()}')
                logger.info(f"Estado de orden {order_id} actualizado a {order.status}")
                return redirect('dashboard:exam_order_detail', order_id=order.id)
        else:
            form = ExamOrderStatusForm(instance=order)
        
        context = {
            'order': order,
            'form': form,
            'patient': order.clinical_history.patient if order.clinical_history else None,
            'history': order.clinical_history,
            'title': 'Actualizar Estado'
        }
        
        return render(request, 'dashboard/patients/exams/order_status_form.html', context)
    
    except Exception as e:
        logger.error(f'Error en exam_order_update_status: {str(e)}', exc_info=True)
        messages.error(request, f'❌ Error al actualizar estado: {str(e)}')
        return redirect('dashboard:exam_order_list')


@login_required
def exam_order_cancel(request, order_id):
    """Cancelar una orden"""
    organization = getattr(request, 'organization', None)
    org_filter = {'organization': organization} if organization else {}
    
    order = get_object_or_404(ExamOrder, id=order_id, **org_filter)
    
    if request.method == 'POST':
        cancellation_reason = request.POST.get('cancellation_reason', '')
        order.status = 'cancelled'
        order.cancellation_reason = cancellation_reason
        order.save()
        
        messages.success(request, 'Orden cancelada exitosamente.')
        return redirect('dashboard:exam_order_list')
    
    context = {
        'order': order,
        'title': 'Cancelar Orden'
    }
    
    return render(request, 'dashboard/patients/exams/order_cancel.html', context)


@login_required
def exam_order_pdf(request, patient_id, history_id, order_id):
    """Generar PDF de la orden médica"""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from datetime import datetime
    
    organization = getattr(request, 'organization', None)
    org_filter = {'organization': organization} if organization else {}
    
    patient = get_object_or_404(Patient, id=patient_id, **org_filter)
    history = get_object_or_404(ClinicalHistory, id=history_id, patient=patient, **org_filter)
    order = get_object_or_404(ExamOrder, id=order_id, clinical_history=history, **org_filter)
    
    # Crear buffer para el PDF
    buffer = BytesIO()
    
    # Configurar documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.Color(0.0, 0.2, 0.5),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.Color(0.2, 0.2, 0.2),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        alignment=TA_JUSTIFY
    )
    
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.Color(0.3, 0.3, 0.3),
        fontName='Helvetica-Bold'
    )
    
    # Contenido del PDF
    story = []
    
    # Encabezado de la organización
    org_name = request.organization.name if hasattr(request, 'organization') and request.organization else 'Centro Médico'
    org_address = request.organization.address if hasattr(request, 'organization') and request.organization and request.organization.address else ''
    org_phone = request.organization.phone if hasattr(request, 'organization') and request.organization and request.organization.phone else ''
    
    header_org_style = ParagraphStyle(
        'HeaderOrg',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.Color(0.0, 0.2, 0.5),
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        leading=16
    )
    
    story.append(Paragraph(f'<b>{org_name}</b>', header_org_style))
    if org_address:
        story.append(Paragraph(org_address, ParagraphStyle('addr', parent=normal_style, fontSize=9, alignment=TA_CENTER)))
    if org_phone:
        story.append(Paragraph(f'Tel: {org_phone}', ParagraphStyle('phone', parent=normal_style, fontSize=9, alignment=TA_CENTER)))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Título del documento
    story.append(Paragraph('<b>ORDEN MÉDICA</b>', title_style))
    story.append(Paragraph(f'<b>{order.get_exam_type_display()}</b>', 
                          ParagraphStyle('subtitle', parent=heading_style, alignment=TA_CENTER, fontSize=14)))
    
    story.append(Spacer(1, 0.15*inch))
    
    # Información del paciente
    patient_data = [
        [Paragraph('<b>DATOS DEL PACIENTE</b>', heading_style)],
    ]
    
    patient_table_data = [
        ['Nombre:', patient.full_name, 'Identificación:', patient.identification or 'N/A'],
        ['Edad:', f"{history.age_at_exam or 'N/A'} años", 'Teléfono:', patient.phone_number or 'N/A'],
        ['Dirección:', patient.address or 'N/A', '', ''],
    ]
    
    patient_table = Table(patient_table_data, colWidths=[1.0*inch, 2.5*inch, 1.2*inch, 2.0*inch])
    patient_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.95, 0.95, 0.95)),
        ('BACKGROUND', (2, 0), (2, 1), colors.Color(0.95, 0.95, 0.95)),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    story.append(patient_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Información de la orden
    story.append(Paragraph('<b>INFORMACIÓN DE LA ORDEN</b>', heading_style))
    
    order_data = [
        ['Fecha de Orden:', order.order_date.strftime('%d/%m/%Y'), 'Prioridad:', order.get_priority_display()],
        ['Ordenado por:', order.ordered_by.full_name if order.ordered_by else 'N/A', 
         'T.P:', order.ordered_by.professional_card if order.ordered_by and order.ordered_by.professional_card else 'N/A'],
    ]
    
    order_table = Table(order_data, colWidths=[1.5*inch, 2.5*inch, 1.2*inch, 1.5*inch])
    order_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.95, 0.95, 0.95)),
        ('BACKGROUND', (2, 0), (2, -1), colors.Color(0.95, 0.95, 0.95)),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    story.append(order_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Indicación clínica
    story.append(Paragraph('<b>INDICACIÓN CLÍNICA</b>', heading_style))
    story.append(Paragraph(order.clinical_indication, normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Instrucciones especiales
    if order.special_instructions:
        story.append(Paragraph('<b>INSTRUCCIONES ESPECIALES</b>', heading_style))
        story.append(Paragraph(order.special_instructions, normal_style))
        story.append(Spacer(1, 0.15*inch))
    
    # Cuadro del examen a realizar
    exam_box_data = [[Paragraph(f'<b>EXAMEN A REALIZAR:</b><br/><font size="12">{order.get_exam_type_display()}</font>', 
                                ParagraphStyle('exambox', parent=normal_style, fontSize=11, alignment=TA_CENTER))]]
    
    exam_box = Table(exam_box_data, colWidths=[6.5*inch])
    exam_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.9, 0.95, 1.0)),
        ('BOX', (0, 0), (-1, -1), 2, colors.Color(0.0, 0.2, 0.5)),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(exam_box)
    story.append(Spacer(1, 0.3*inch))
    
    # Notas importantes
    notes_style = ParagraphStyle(
        'Notes',
        parent=normal_style,
        fontSize=8,
        textColor=colors.Color(0.4, 0.4, 0.4),
        borderWidth=1,
        borderColor=colors.grey,
        borderPadding=10,
        alignment=TA_JUSTIFY
    )
    
    story.append(Paragraph(
        '<b>NOTAS IMPORTANTES:</b><br/>'
        '• Esta orden tiene una vigencia de 30 días desde la fecha de emisión.<br/>'
        '• El paciente debe presentar esta orden al momento de realizar el examen.<br/>'
        '• Para cualquier consulta, comunicarse con el centro médico.',
        notes_style
    ))
    
    story.append(Spacer(1, 0.4*inch))
    
    # Firma del médico
    footer_data = [
        ['_' * 50],
        [f'{order.ordered_by.full_name if order.ordered_by else ""}'],
        [f'{order.ordered_by.professional_card if order.ordered_by and order.ordered_by.professional_card else ""}'],
        ['Firma y Sello del Médico'],
    ]
    
    footer_table = Table(footer_data, colWidths=[3.5*inch])
    footer_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 3), (0, 3), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(footer_table)
    
    # Pie de página con fecha de emisión
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        f'Documento generado el: {datetime.now().strftime("%d/%m/%Y a las %H:%M")}',
        ParagraphStyle('footer', parent=normal_style, fontSize=7, alignment=TA_CENTER, textColor=colors.grey)
    ))
    
    # Construir PDF
    doc.build(story)
    
    # Retornar respuesta
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="orden_examen_{patient.full_name.replace(" ", "_")}_{order.order_date}.pdf"'
    
    return response


@login_required
def exam_order_delete(request, order_id):
    """Eliminar una orden de examen"""
    organization = getattr(request, 'organization', None)
    org_filter = {'organization': organization} if organization else {}
    
    order = get_object_or_404(ExamOrder, id=order_id, **org_filter)
    
    if request.method == 'POST':
        # Guardar información antes de eliminar
        exam_type = order.get_exam_type_display()
        patient_name = order.clinical_history.patient.full_name
        
        # Eliminar la orden (esto también eliminará los resultados relacionados por CASCADE)
        order.delete()
        
        messages.success(request, f'Orden de {exam_type} para {patient_name} eliminada exitosamente.')
        return redirect('dashboard:exam_order_list')
    
    context = {
        'order': order,
        'patient': order.clinical_history.patient,
        'history': order.clinical_history,
        'title': 'Eliminar Orden de Examen'
    }
    
    return render(request, 'dashboard/patients/exams/order_delete_confirm.html', context)
