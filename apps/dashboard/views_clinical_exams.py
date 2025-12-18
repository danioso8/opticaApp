"""
Vistas para Resultados de Exámenes Especiales
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from io import BytesIO

from apps.patients.models import (
    Patient, ClinicalHistory, ExamOrder, 
    Tonometry, VisualFieldTest, Retinography
)
from apps.patients.forms_clinical_exams import TonometryForm, VisualFieldTestForm, RetinographyForm


@login_required
def tonometry_create(request, patient_id, history_id, order_id=None):
    """Crear resultado de tonometría"""
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    
    patient = get_object_or_404(Patient, id=patient_id, **org_filter)
    history = get_object_or_404(ClinicalHistory, id=history_id, patient=patient, **org_filter)
    
    # Si hay orden, obtenerla
    order = None
    if order_id:
        order = get_object_or_404(ExamOrder, id=order_id, clinical_history=history, **org_filter)
    
    if request.method == 'POST':
        form = TonometryForm(request.POST, organization=request.organization)
        if form.is_valid():
            tonometry = form.save(commit=False)
            tonometry.clinical_history = history
            tonometry.organization = request.organization
            if order:
                tonometry.exam_order = order
                order.mark_completed()  # Marcar orden como completada
            tonometry.save()
            
            messages.success(request, 'Tonometría registrada exitosamente.')
            
            # Redirigir según la acción
            if 'save_and_print' in request.POST:
                return redirect('dashboard:tonometry_pdf', patient_id=patient_id, history_id=history_id, tonometry_id=tonometry.id)
            else:
                return redirect('dashboard:tonometry_detail', patient_id=patient_id, history_id=history_id, tonometry_id=tonometry.id)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = TonometryForm(organization=request.organization)
    
    context = {
        'patient': patient,
        'history': history,
        'order': order,
        'form': form,
        'title': 'Registrar Tonometría'
    }
    
    return render(request, 'dashboard/patients/exams/tonometry_form.html', context)


@login_required
def tonometry_detail(request, patient_id, history_id, tonometry_id):
    """Ver detalle de tonometría"""
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    
    patient = get_object_or_404(Patient, id=patient_id, **org_filter)
    history = get_object_or_404(ClinicalHistory, id=history_id, patient=patient, **org_filter)
    tonometry = get_object_or_404(Tonometry, id=tonometry_id, clinical_history=history, **org_filter)
    
    context = {
        'patient': patient,
        'history': history,
        'tonometry': tonometry,
        'title': 'Resultado de Tonometría'
    }
    
    return render(request, 'dashboard/patients/exams/tonometry_detail.html', context)


@login_required
def tonometry_pdf(request, patient_id, history_id, tonometry_id):
    """Generar PDF del resultado de tonometría"""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from datetime import datetime
    
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    
    patient = get_object_or_404(Patient, id=patient_id, **org_filter)
    history = get_object_or_404(ClinicalHistory, id=history_id, patient=patient, **org_filter)
    tonometry = get_object_or_404(Tonometry, id=tonometry_id, clinical_history=history, **org_filter)
    
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
        spaceAfter=8
    )
    
    # Contenido del PDF
    story = []
    
    # Encabezado
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
    
    # Título
    story.append(Paragraph('<b>RESULTADO DE TONOMETRÍA</b>', title_style))
    story.append(Paragraph('<b>Medición de Presión Intraocular</b>', 
                          ParagraphStyle('subtitle', parent=heading_style, alignment=TA_CENTER, fontSize=12, textColor=colors.grey)))
    
    story.append(Spacer(1, 0.15*inch))
    
    # Información del paciente
    patient_data = [
        ['Nombre:', patient.full_name, 'Identificación:', patient.identification or 'N/A'],
        ['Edad:', f"{history.age_at_exam or 'N/A'} años", 'Fecha de Examen:', tonometry.exam_date.strftime('%d/%m/%Y')],
    ]
    
    patient_table = Table(patient_data, colWidths=[1.0*inch, 2.5*inch, 1.2*inch, 2.0*inch])
    patient_table.setStyle(TableStyle([
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
    
    story.append(patient_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Datos del examen
    story.append(Paragraph('<b>DATOS DEL EXAMEN</b>', heading_style))
    
    exam_data = [
        ['Realizado por:', tonometry.performed_by.full_name if tonometry.performed_by else 'N/A', 
         'Hora:', tonometry.time_measured.strftime('%H:%M')],
        ['Método:', tonometry.get_method_display(), 
         'Equipo:', tonometry.equipment_used or 'N/A'],
    ]
    
    exam_table = Table(exam_data, colWidths=[1.5*inch, 2.5*inch, 1.0*inch, 1.7*inch])
    exam_table.setStyle(TableStyle([
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
    
    story.append(exam_table)
    story.append(Spacer(1, 0.25*inch))
    
    # Resultados - Tabla destacada
    story.append(Paragraph('<b>RESULTADOS</b>', heading_style))
    
    # Determinar color según valores
    od_color = colors.Color(1.0, 0.9, 0.9) if tonometry.od_pressure > 21 else colors.Color(0.9, 1.0, 0.9)
    os_color = colors.Color(1.0, 0.9, 0.9) if tonometry.os_pressure > 21 else colors.Color(0.9, 1.0, 0.9)
    
    results_data = [
        ['OJO', 'PRESIÓN INTRAOCULAR', 'INTERPRETACIÓN'],
        ['OD (Derecho)', 
         f'{tonometry.od_pressure} mmHg', 
         'ELEVADA' if tonometry.od_pressure > 21 else 'NORMAL'],
        ['OS (Izquierdo)', 
         f'{tonometry.os_pressure} mmHg', 
         'ELEVADA' if tonometry.os_pressure > 21 else 'NORMAL'],
    ]
    
    results_table = Table(results_data, colWidths=[2.0*inch, 2.5*inch, 2.2*inch])
    results_table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.4, 0.6)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Datos OD
        ('BACKGROUND', (0, 1), (-1, 1), od_color),
        ('FONTSIZE', (0, 1), (-1, 1), 11),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (2, 1), 'CENTER'),
        
        # Datos OS
        ('BACKGROUND', (0, 2), (-1, 2), os_color),
        ('FONTSIZE', (0, 2), (-1, 2), 11),
        ('FONTNAME', (0, 2), (0, 2), 'Helvetica-Bold'),
        ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),
        ('ALIGN', (1, 2), (2, 2), 'CENTER'),
        
        # Bordes y padding
        ('GRID', (0, 0), (-1, -1), 1.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(results_table)
    
    # Notas por ojo si existen
    if tonometry.od_notes or tonometry.os_notes:
        story.append(Spacer(1, 0.1*inch))
        notes_data = []
        if tonometry.od_notes:
            notes_data.append(['Notas OD:', tonometry.od_notes])
        if tonometry.os_notes:
            notes_data.append(['Notas OS:', tonometry.os_notes])
        
        notes_table = Table(notes_data, colWidths=[1.2*inch, 5.5*inch])
        notes_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(notes_table)
    
    story.append(Spacer(1, 0.2*inch))
    
    # Valores de referencia
    ref_box_data = [[Paragraph(
        '<b>VALORES DE REFERENCIA:</b><br/>'
        'Normal: 10-21 mmHg | Sospecha Hipertensión Ocular: &gt;21 mmHg | Hipotensión: &lt;10 mmHg',
        ParagraphStyle('refbox', parent=normal_style, fontSize=9, alignment=TA_CENTER)
    )]]
    
    ref_box = Table(ref_box_data, colWidths=[6.7*inch])
    ref_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.95, 0.95, 1.0)),
        ('BOX', (0, 0), (-1, -1), 1, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(ref_box)
    story.append(Spacer(1, 0.2*inch))
    
    # Interpretación
    if tonometry.interpretation:
        story.append(Paragraph('<b>INTERPRETACIÓN CLÍNICA</b>', heading_style))
        story.append(Paragraph(tonometry.interpretation, normal_style))
        story.append(Spacer(1, 0.15*inch))
    
    # Recomendaciones
    if tonometry.recommendations:
        story.append(Paragraph('<b>RECOMENDACIONES</b>', heading_style))
        story.append(Paragraph(tonometry.recommendations, normal_style))
        story.append(Spacer(1, 0.15*inch))
    
    # Seguimiento
    if tonometry.requires_follow_up:
        follow_up_text = f"<b>REQUIERE SEGUIMIENTO:</b> Sí"
        if tonometry.follow_up_period:
            follow_up_text += f" - Período: {tonometry.follow_up_period}"
        
        follow_box = Table([[Paragraph(follow_up_text, normal_style)]], colWidths=[6.7*inch])
        follow_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(1.0, 1.0, 0.9)),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.Color(0.8, 0.6, 0.0)),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(follow_box)
        story.append(Spacer(1, 0.2*inch))
    
    # Firma
    story.append(Spacer(1, 0.3*inch))
    
    footer_data = [
        ['_' * 50],
        [f'{tonometry.performed_by.full_name if tonometry.performed_by else ""}'],
        [f'{tonometry.performed_by.professional_card if tonometry.performed_by and tonometry.performed_by.professional_card else ""}'],
        ['Firma y Sello del Profesional'],
    ]
    
    footer_table = Table(footer_data, colWidths=[3.5*inch])
    footer_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 3), (0, 3), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(footer_table)
    
    # Pie de página
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
    response['Content-Disposition'] = f'inline; filename="tonometria_{patient.full_name.replace(" ", "_")}_{tonometry.exam_date}.pdf"'
    
    return response
