"""
Vistas para generación de certificados médicos en PDF
"""
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from apps.patients.models import Patient
from apps.patients.models_clinical import ClinicalHistory
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime


# ==================== CERTIFICADO DE EXAMEN VISUAL ====================
@login_required
@require_http_methods(["GET"])
def visual_exam_certificate_pdf(request, patient_id, history_id):
    """Genera certificado de examen visual realizado"""
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    patient = get_object_or_404(Patient, id=patient_id, **org_filter)
    history = get_object_or_404(ClinicalHistory, id=history_id, patient=patient, **org_filter)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.75*inch, leftMargin=0.75*inch, 
                           topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Encabezado con datos de la organización
    org_name = request.organization.name if hasattr(request, 'organization') and request.organization else 'Centro Óptico'
    org_address = request.organization.address if hasattr(request, 'organization') and request.organization and request.organization.address else ''
    org_phone = request.organization.phone if hasattr(request, 'organization') and request.organization and request.organization.phone else ''
    
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=16, textColor=colors.Color(0, 0.2, 0.5),
                                 fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=6)
    subheader_style = ParagraphStyle('Subheader', parent=styles['Normal'], fontSize=9, 
                                    alignment=TA_CENTER, spaceAfter=20)
    
    story.append(Paragraph(org_name, header_style))
    if org_address:
        story.append(Paragraph(org_address, subheader_style))
    if org_phone:
        story.append(Paragraph(f'Tel: {org_phone}', subheader_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Título del certificado
    title_style = ParagraphStyle('Title', parent=styles['Normal'], fontSize=18, textColor=colors.Color(0, 0.2, 0.5),
                                fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=30, spaceBefore=10)
    story.append(Paragraph('CERTIFICADO DE EXAMEN VISUAL', title_style))
    
    # Número de certificado
    cert_number = f"CEV-{history.id:06d}-{datetime.now().year}"
    cert_style = ParagraphStyle('CertNum', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, spaceAfter=20)
    story.append(Paragraph(f'Certificado N°: {cert_number}', cert_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Texto del certificado
    text_style = ParagraphStyle('BodyText', parent=styles['Normal'], fontSize=11, alignment=TA_JUSTIFY, 
                               leading=18, spaceAfter=15)
    
    exam_date = history.date.strftime('%d de %B de %Y') if history.date else datetime.now().strftime('%d de %B de %Y')
    
    certificate_text = f"""
    Por medio del presente certificado, se hace constar que el(la) paciente 
    <b>{patient.full_name}</b>, identificado(a) con documento N° <b>{patient.identification or 'N/A'}</b>, 
    se realizó un <b>EXAMEN VISUAL COMPLETO</b> en nuestras instalaciones el día <b>{exam_date}</b>.
    """
    
    story.append(Paragraph(certificate_text, text_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Resultados del examen
    results_title = ParagraphStyle('ResultsTitle', parent=styles['Normal'], fontSize=12, 
                                  fontName='Helvetica-Bold', spaceAfter=10, spaceBefore=10)
    story.append(Paragraph('RESULTADOS DEL EXAMEN:', results_title))
    
    results_data = [
        ['Agudeza Visual OD:', history.va_od_sc_distance or 'No registrado'],
        ['Agudeza Visual OI:', history.va_os_sc_distance or 'No registrado'],
        ['Estado General:', 'Examen realizado satisfactoriamente'],
    ]
    
    results_table = Table(results_data, colWidths=[2.5*inch, 3.5*inch])
    results_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    story.append(results_table)
    story.append(Spacer(1, 0.4*inch))
    
    # Texto de validez
    validity_text = f"""
    Se expide el presente certificado a solicitud del interesado, para los fines que estime convenientes, 
    el día {datetime.now().strftime('%d de %B de %Y')}.
    """
    story.append(Paragraph(validity_text, text_style))
    
    story.append(Spacer(1, 0.6*inch))
    
    # Firma
    signature_style = ParagraphStyle('Signature', parent=styles['Normal'], fontSize=10, 
                                    alignment=TA_CENTER, fontName='Helvetica-Bold')
    story.append(Paragraph('_________________________', signature_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(f'{org_name}', signature_style))
    story.append(Paragraph('Optometría', ParagraphStyle('SubSig', parent=styles['Normal'], 
                                                        fontSize=9, alignment=TA_CENTER)))
    
    doc.build(story)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="certificado_examen_{patient.full_name.replace(" ", "_")}.pdf"'
    return response


# ==================== CERTIFICADO MÉDICO OFTALMOLÓGICO ====================
@login_required
@require_http_methods(["GET"])
def medical_certificate_pdf(request, patient_id, history_id):
    """Genera certificado médico oftalmológico"""
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    patient = get_object_or_404(Patient, id=patient_id, **org_filter)
    history = get_object_or_404(ClinicalHistory, id=history_id, patient=patient, **org_filter)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Encabezado
    org_name = request.organization.name if hasattr(request, 'organization') and request.organization else 'Centro Médico'
    org_address = request.organization.address if hasattr(request, 'organization') and request.organization and request.organization.address else ''
    org_phone = request.organization.phone if hasattr(request, 'organization') and request.organization and request.organization.phone else ''
    
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=16, textColor=colors.Color(0, 0.2, 0.5),
                                 fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=6)
    subheader_style = ParagraphStyle('Subheader', parent=styles['Normal'], fontSize=9, 
                                    alignment=TA_CENTER, spaceAfter=20)
    
    story.append(Paragraph(org_name, header_style))
    if org_address:
        story.append(Paragraph(org_address, subheader_style))
    if org_phone:
        story.append(Paragraph(f'Tel: {org_phone}', subheader_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Título
    title_style = ParagraphStyle('Title', parent=styles['Normal'], fontSize=18, textColor=colors.Color(0, 0.2, 0.5),
                                fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=30, spaceBefore=10)
    story.append(Paragraph('CERTIFICADO MÉDICO OFTALMOLÓGICO', title_style))
    
    # Número de certificado
    cert_number = f"CMO-{history.id:06d}-{datetime.now().year}"
    cert_style = ParagraphStyle('CertNum', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, spaceAfter=20)
    story.append(Paragraph(f'Certificado N°: {cert_number}', cert_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Texto del certificado
    text_style = ParagraphStyle('BodyText', parent=styles['Normal'], fontSize=11, alignment=TA_JUSTIFY,
                               leading=18, spaceAfter=15)
    
    exam_date = history.date.strftime('%d de %B de %Y') if history.date else datetime.now().strftime('%d de %B de %Y')
    
    certificate_text = f"""
    El suscrito profesional de la salud visual certifica que el(la) señor(a) <b>{patient.full_name}</b>, 
    identificado(a) con documento N° <b>{patient.identification or 'N/A'}</b>, fue evaluado(a) en esta 
    institución el día <b>{exam_date}</b>, encontrándose los siguientes hallazgos:
    """
    
    story.append(Paragraph(certificate_text, text_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Hallazgos
    findings_title = ParagraphStyle('FindingsTitle', parent=styles['Normal'], fontSize=12,
                                   fontName='Helvetica-Bold', spaceAfter=10, spaceBefore=10)
    story.append(Paragraph('HALLAZGOS CLÍNICOS:', findings_title))
    
    diagnosis_text = history.diagnosis if hasattr(history, 'diagnosis') and history.diagnosis else 'Evaluación oftalmológica completa realizada.'
    
    findings_data = [
        ['Diagnóstico:', diagnosis_text],
        ['Recomendaciones:', 'Uso de corrección óptica según fórmula prescrita' if (history.final_rx_od_sphere or history.final_rx_os_sphere) else 'Control periódico'],
    ]
    
    findings_table = Table(findings_data, colWidths=[2*inch, 4*inch])
    findings_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    story.append(findings_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Texto de validez
    validity_text = f"""
    Se expide el presente certificado médico a solicitud del paciente para los fines que considere pertinentes, 
    el día {datetime.now().strftime('%d de %B de %Y')}.
    """
    story.append(Paragraph(validity_text, text_style))
    
    story.append(Spacer(1, 0.6*inch))
    
    # Firma
    signature_style = ParagraphStyle('Signature', parent=styles['Normal'], fontSize=10,
                                    alignment=TA_CENTER, fontName='Helvetica-Bold')
    story.append(Paragraph('_________________________', signature_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(f'{org_name}', signature_style))
    story.append(Paragraph('Optometría Profesional', ParagraphStyle('SubSig', parent=styles['Normal'],
                                                                    fontSize=9, alignment=TA_CENTER)))
    
    doc.build(story)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="certificado_medico_{patient.full_name.replace(" ", "_")}.pdf"'
    return response
