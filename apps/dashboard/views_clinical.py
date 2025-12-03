"""
Vistas para Historia Clínica Oftalmológica
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime
from io import BytesIO

from apps.patients.models import Patient, ClinicalHistory, ClinicalHistoryAttachment, Doctor


@login_required
def clinical_history_list(request, patient_id):
    """Lista de historias clínicas de un paciente"""
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    patient = get_object_or_404(Patient, id=patient_id, **org_filter)
    
    histories = ClinicalHistory.objects.filter(
        patient=patient,
        **org_filter
    ).order_by('-date')
    
    context = {
        'patient': patient,
        'histories': histories,
    }
    
    return render(request, 'dashboard/patients/clinical_history_list.html', context)


@login_required
def clinical_history_create(request, patient_id):
    """Crear nueva historia clínica"""
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    patient = get_object_or_404(Patient, id=patient_id, **org_filter)
    
    # Obtener doctores activos de la organización
    doctors = Doctor.objects.filter(
        organization=request.organization,
        is_active=True
    ).order_by('full_name')
    
    if request.method == 'POST':
        try:
            # Obtener el doctor seleccionado
            doctor_id = request.POST.get('doctor')
            doctor = None
            if doctor_id:
                try:
                    doctor = Doctor.objects.get(id=doctor_id, organization=request.organization)
                except Doctor.DoesNotExist:
                    pass
            
            # Crear historia clínica
            history = ClinicalHistory.objects.create(
                organization=request.organization,
                patient=patient,
                date=request.POST.get('date') or datetime.now().date(),
                doctor=doctor,
                
                # Anamnesis
                chief_complaint=request.POST.get('chief_complaint', ''),
                current_illness=request.POST.get('current_illness', ''),
                blurred_vision=request.POST.get('blurred_vision') == 'on',
                eye_pain=request.POST.get('eye_pain') == 'on',
                headaches=request.POST.get('headaches') == 'on',
                photophobia=request.POST.get('photophobia') == 'on',
                diplopia=request.POST.get('diplopia') == 'on',
                tearing=request.POST.get('tearing') == 'on',
                redness=request.POST.get('redness') == 'on',
                itching=request.POST.get('itching') == 'on',
                floaters=request.POST.get('floaters') == 'on',
                halos=request.POST.get('halos') == 'on',
                symptoms_notes=request.POST.get('symptoms_notes', ''),
                
                # Antecedentes
                previous_eye_surgery=request.POST.get('previous_eye_surgery') == 'on',
                surgery_details=request.POST.get('surgery_details', ''),
                previous_glasses=request.POST.get('previous_glasses') == 'on',
                glasses_since=request.POST.get('glasses_since', ''),
                previous_contact_lenses=request.POST.get('previous_contact_lenses') == 'on',
                
                family_glaucoma=request.POST.get('family_glaucoma') == 'on',
                family_cataracts=request.POST.get('family_cataracts') == 'on',
                family_macular_degeneration=request.POST.get('family_macular_degeneration') == 'on',
                family_diabetes=request.POST.get('family_diabetes') == 'on',
                family_hypertension=request.POST.get('family_hypertension') == 'on',
                family_history_notes=request.POST.get('family_history_notes', ''),
                
                occupation_visual_demand=request.POST.get('occupation_visual_demand', ''),
                screen_hours_daily=request.POST.get('screen_hours_daily') or None,
                reading_hours_daily=request.POST.get('reading_hours_daily') or None,
                
                # Agudeza Visual
                va_od_sc_distance=request.POST.get('va_od_sc_distance', ''),
                va_od_sc_near=request.POST.get('va_od_sc_near', ''),
                va_od_cc_distance=request.POST.get('va_od_cc_distance', ''),
                va_od_cc_near=request.POST.get('va_od_cc_near', ''),
                va_os_sc_distance=request.POST.get('va_os_sc_distance', ''),
                va_os_sc_near=request.POST.get('va_os_sc_near', ''),
                va_os_cc_distance=request.POST.get('va_os_cc_distance', ''),
                va_os_cc_near=request.POST.get('va_os_cc_near', ''),
                va_ou_distance=request.POST.get('va_ou_distance', ''),
                va_ou_near=request.POST.get('va_ou_near', ''),
                
                # Refracción
                refraction_od_sphere=request.POST.get('refraction_od_sphere') or None,
                refraction_od_cylinder=request.POST.get('refraction_od_cylinder') or None,
                refraction_od_axis=request.POST.get('refraction_od_axis') or None,
                refraction_od_add=request.POST.get('refraction_od_add') or None,
                refraction_od_prism=request.POST.get('refraction_od_prism', ''),
                
                refraction_os_sphere=request.POST.get('refraction_os_sphere') or None,
                refraction_os_cylinder=request.POST.get('refraction_os_cylinder') or None,
                refraction_os_axis=request.POST.get('refraction_os_axis') or None,
                refraction_os_add=request.POST.get('refraction_os_add') or None,
                refraction_os_prism=request.POST.get('refraction_os_prism', ''),
                
                pd_distance=request.POST.get('pd_distance') or None,
                pd_near=request.POST.get('pd_near') or None,
                pd_od=request.POST.get('pd_od') or None,
                pd_os=request.POST.get('pd_os') or None,
                
                # Queratometría
                keratometry_od_k1=request.POST.get('keratometry_od_k1') or None,
                keratometry_od_k1_axis=request.POST.get('keratometry_od_k1_axis') or None,
                keratometry_od_k2=request.POST.get('keratometry_od_k2') or None,
                keratometry_od_k2_axis=request.POST.get('keratometry_od_k2_axis') or None,
                
                keratometry_os_k1=request.POST.get('keratometry_os_k1') or None,
                keratometry_os_k1_axis=request.POST.get('keratometry_os_k1_axis') or None,
                keratometry_os_k2=request.POST.get('keratometry_os_k2') or None,
                keratometry_os_k2_axis=request.POST.get('keratometry_os_k2_axis') or None,
                
                # Tonometría
                iop_od=request.POST.get('iop_od') or None,
                iop_os=request.POST.get('iop_os') or None,
                iop_method=request.POST.get('iop_method', ''),
                
                # Biomicroscopía
                biomicroscopy_od_lids=request.POST.get('biomicroscopy_od_lids', ''),
                biomicroscopy_od_conjunctiva=request.POST.get('biomicroscopy_od_conjunctiva', ''),
                biomicroscopy_od_cornea=request.POST.get('biomicroscopy_od_cornea', ''),
                biomicroscopy_od_anterior_chamber=request.POST.get('biomicroscopy_od_anterior_chamber', ''),
                biomicroscopy_od_iris=request.POST.get('biomicroscopy_od_iris', ''),
                biomicroscopy_od_lens=request.POST.get('biomicroscopy_od_lens', ''),
                
                biomicroscopy_os_lids=request.POST.get('biomicroscopy_os_lids', ''),
                biomicroscopy_os_conjunctiva=request.POST.get('biomicroscopy_os_conjunctiva', ''),
                biomicroscopy_os_cornea=request.POST.get('biomicroscopy_os_cornea', ''),
                biomicroscopy_os_anterior_chamber=request.POST.get('biomicroscopy_os_anterior_chamber', ''),
                biomicroscopy_os_iris=request.POST.get('biomicroscopy_os_iris', ''),
                biomicroscopy_os_lens=request.POST.get('biomicroscopy_os_lens', ''),
                
                # Fondo de Ojo
                fundoscopy_od_vitreous=request.POST.get('fundoscopy_od_vitreous', ''),
                fundoscopy_od_optic_disc=request.POST.get('fundoscopy_od_optic_disc', ''),
                fundoscopy_od_macula=request.POST.get('fundoscopy_od_macula', ''),
                fundoscopy_od_vessels=request.POST.get('fundoscopy_od_vessels', ''),
                fundoscopy_od_periphery=request.POST.get('fundoscopy_od_periphery', ''),
                
                fundoscopy_os_vitreous=request.POST.get('fundoscopy_os_vitreous', ''),
                fundoscopy_os_optic_disc=request.POST.get('fundoscopy_os_optic_disc', ''),
                fundoscopy_os_macula=request.POST.get('fundoscopy_os_macula', ''),
                fundoscopy_os_vessels=request.POST.get('fundoscopy_os_vessels', ''),
                fundoscopy_os_periphery=request.POST.get('fundoscopy_os_periphery', ''),
                
                # Motilidad
                motility_od=request.POST.get('motility_od', ''),
                motility_os=request.POST.get('motility_os', ''),
                cover_test=request.POST.get('cover_test', ''),
                convergence=request.POST.get('convergence', ''),
                
                # Visión de Colores
                color_vision_od=request.POST.get('color_vision_od', ''),
                color_vision_os=request.POST.get('color_vision_os', ''),
                color_vision_test=request.POST.get('color_vision_test', ''),
                
                # Diagnóstico
                diagnosis=request.POST.get('diagnosis', ''),
                dx_myopia=request.POST.get('dx_myopia') == 'on',
                dx_hyperopia=request.POST.get('dx_hyperopia') == 'on',
                dx_astigmatism=request.POST.get('dx_astigmatism') == 'on',
                dx_presbyopia=request.POST.get('dx_presbyopia') == 'on',
                dx_amblyopia=request.POST.get('dx_amblyopia') == 'on',
                dx_strabismus=request.POST.get('dx_strabismus') == 'on',
                dx_cataracts=request.POST.get('dx_cataracts') == 'on',
                dx_glaucoma=request.POST.get('dx_glaucoma') == 'on',
                dx_dry_eye=request.POST.get('dx_dry_eye') == 'on',
                dx_conjunctivitis=request.POST.get('dx_conjunctivitis') == 'on',
                dx_keratoconus=request.POST.get('dx_keratoconus') == 'on',
                
                # Tratamiento
                treatment_plan=request.POST.get('treatment_plan', ''),
                prescription_glasses=request.POST.get('prescription_glasses') == 'on',
                prescription_contact_lenses=request.POST.get('prescription_contact_lenses') == 'on',
                prescription_medication=request.POST.get('prescription_medication') == 'on',
                medication_details=request.POST.get('medication_details', ''),
                
                lens_type=request.POST.get('lens_type', ''),
                lens_material=request.POST.get('lens_material', ''),
                lens_coating=request.POST.get('lens_coating', ''),
                
                # Seguimiento
                follow_up_date=request.POST.get('follow_up_date') or None,
                follow_up_notes=request.POST.get('follow_up_notes', ''),
                observations=request.POST.get('observations', ''),
                recommendations=request.POST.get('recommendations', ''),
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Historia clínica creada exitosamente',
                    'history_id': history.id
                })
            
            return redirect('dashboard:clinical_history_detail', patient_id=patient.id, history_id=history.id)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error al crear historia clínica: {str(e)}'
                }, status=400)
            return redirect('dashboard:clinical_history_list', patient_id=patient.id)
    
    context = {
        'patient': patient,
        'today': datetime.now().date(),
        'doctors': doctors,
    }
    
    return render(request, 'dashboard/patients/clinical_history_form.html', context)


@login_required
def clinical_history_detail(request, patient_id, history_id):
    """Ver detalle de historia clínica"""
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    patient = get_object_or_404(Patient, id=patient_id, **org_filter)
    history = get_object_or_404(ClinicalHistory, id=history_id, patient=patient, **org_filter)
    
    context = {
        'patient': patient,
        'history': history,
    }
    
    return render(request, 'dashboard/patients/clinical_history_detail.html', context)


@login_required
def clinical_history_edit(request, patient_id, history_id):
    """Editar historia clínica"""
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    patient = get_object_or_404(Patient, id=patient_id, **org_filter)
    history = get_object_or_404(ClinicalHistory, id=history_id, patient=patient, **org_filter)
    
    # Obtener doctores activos de la organización
    doctors = Doctor.objects.filter(
        organization=request.organization,
        is_active=True
    ).order_by('full_name')
    
    if request.method == 'POST':
        try:
            # Obtener el doctor seleccionado
            doctor_id = request.POST.get('doctor')
            doctor = None
            if doctor_id:
                try:
                    doctor = Doctor.objects.get(id=doctor_id, organization=request.organization)
                except Doctor.DoesNotExist:
                    pass
            
            # Actualizar campos (similar a create)
            history.date = request.POST.get('date') or history.date
            history.doctor = doctor
            history.chief_complaint = request.POST.get('chief_complaint', '')
            history.diagnosis = request.POST.get('diagnosis', '')
            history.treatment_plan = request.POST.get('treatment_plan', '')
            # ... actualizar todos los campos necesarios ...
            
            history.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Historia clínica actualizada exitosamente'
                })
            
            return redirect('dashboard:clinical_history_detail', patient_id=patient.id, history_id=history.id)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error al actualizar historia clínica: {str(e)}'
                }, status=400)
    
    context = {
        'patient': patient,
        'history': history,
        'doctors': doctors,
        'is_edit': True,
    }
    
    return render(request, 'dashboard/patients/clinical_history_form.html', context)


@login_required
def clinical_history_delete(request, patient_id, history_id):
    """Eliminar historia clínica"""
    if request.method == 'POST':
        org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
        patient = get_object_or_404(Patient, id=patient_id, **org_filter)
        history = get_object_or_404(ClinicalHistory, id=history_id, patient=patient, **org_filter)
        
        try:
            history.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Historia clínica eliminada exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar historia clínica: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


@login_required
def clinical_history_pdf(request, patient_id, history_id):
    """Generar PDF de historia clínica"""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
    from reportlab.lib import colors
    from apps.patients.pdf_utils import (
        draw_eye_fundus_diagram, draw_refraction_table, 
        draw_keratometry_table, draw_iop_table, NumberedCanvas
    )
    
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    patient = get_object_or_404(Patient, id=patient_id, **org_filter)
    history = get_object_or_404(ClinicalHistory, id=history_id, patient=patient, **org_filter)
    
    # Crear buffer para el PDF
    buffer = BytesIO()
    
    # Configurar documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=1.2*inch,
        bottomMargin=0.8*inch
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.Color(0.2, 0.4, 0.6),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.Color(0.2, 0.4, 0.6),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=colors.Color(0.2, 0.4, 0.6),
        borderPadding=5,
        backColor=colors.Color(0.9, 0.95, 1)
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=10
    )
    
    # Contenido del PDF
    story = []
    
    # Título
    story.append(Paragraph("HISTORIA CLÍNICA DE OPTOMETRÍA", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Información del Paciente
    story.append(Paragraph("DATOS DEL PACIENTE", heading_style))
    
    patient_data = [
        ['Nombre:', patient.full_name, 'Número de HC:', str(history.id)],
        ['Identificación:', f"{patient.get_identification_type_display()} {patient.identification}", 'Edad:', f"{history.age_at_exam or 'N/A'} años"],
        ['Fecha de Nacimiento:', str(patient.date_of_birth) if patient.date_of_birth else 'N/A', 'Sexo:', patient.get_gender_display() if patient.gender else 'N/A'],
        ['Teléfono:', patient.phone_number or 'N/A', 'Email:', patient.email or 'N/A'],
        ['Fecha del Examen:', str(history.date), 'Médico/Optómetra:', history.doctor.full_name if history.doctor else 'N/A'],
    ]
    
    patient_table = Table(patient_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.9, 0.9, 0.9)),
        ('BACKGROUND', (2, 0), (2, -1), colors.Color(0.9, 0.9, 0.9)),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(patient_table)
    story.append(Spacer(1, 0.3*inch))
    
    # ANAMNESIS
    story.append(Paragraph("ANAMNESIS", heading_style))
    
    if history.chief_complaint:
        story.append(Paragraph(f"<b>Motivo de Consulta:</b> {history.chief_complaint}", normal_style))
    
    if history.current_illness:
        story.append(Paragraph(f"<b>Enfermedad Actual:</b> {history.current_illness}", normal_style))
    
    if history.medical_history:
        story.append(Paragraph(f"<b>Antecedentes Médicos:</b> {history.medical_history}", normal_style))
    
    # Síntomas
    symptoms = []
    if history.blurred_vision: symptoms.append("Visión borrosa")
    if history.eye_pain: symptoms.append("Dolor ocular")
    if history.headaches: symptoms.append("Cefaleas")
    if history.photophobia: symptoms.append("Fotofobia")
    if history.diplopia: symptoms.append("Diplopía")
    if history.tearing: symptoms.append("Lagrimeo")
    if history.redness: symptoms.append("Enrojecimiento")
    if history.itching: symptoms.append("Picazón")
    if history.floaters: symptoms.append("Moscas volantes")
    if history.halos: symptoms.append("Halos de luz")
    
    if symptoms:
        story.append(Paragraph(f"<b>Síntomas:</b> {', '.join(symptoms)}", normal_style))
    
    if history.symptoms_notes:
        story.append(Paragraph(f"<b>Notas de Síntomas:</b> {history.symptoms_notes}", normal_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # MÓDULO DE REFRACCIÓN
    story.append(Paragraph("MÓDULO DE REFRACCIÓN", heading_style))
    story.append(draw_refraction_table(history))
    story.append(Spacer(1, 0.1*inch))
    
    if history.pd_distance or history.pd_near:
        pd_text = f"<b>Distancia Pupilar:</b> Lejos: {history.pd_distance or 'N/A'} mm, Cerca: {history.pd_near or 'N/A'} mm"
        story.append(Paragraph(pd_text, normal_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # QUERATOMETRÍA
    if any([history.keratometry_od_k1, history.keratometry_os_k1]):
        story.append(Paragraph("QUERATOMETRÍA", heading_style))
        story.append(draw_keratometry_table(history))
        story.append(Spacer(1, 0.2*inch))
    
    # PRESIÓN INTRAOCULAR
    if history.iop_od or history.iop_os:
        story.append(Paragraph("PRESIÓN INTRAOCULAR", heading_style))
        story.append(draw_iop_table(history))
        story.append(Spacer(1, 0.2*inch))
    
    # EXAMEN EXTERNO
    if history.external_exam_od or history.external_exam_os:
        story.append(Paragraph("EXAMEN EXTERNO", heading_style))
        if history.external_exam_od:
            story.append(Paragraph(f"<b>OD:</b> {history.external_exam_od}", normal_style))
        if history.external_exam_os:
            story.append(Paragraph(f"<b>OS:</b> {history.external_exam_os}", normal_style))
        story.append(Spacer(1, 0.2*inch))
    
    # BIOMICROSCOPÍA
    has_biomicroscopy = any([
        history.biomicroscopy_od_lids, history.biomicroscopy_od_conjunctiva,
        history.biomicroscopy_od_cornea, history.biomicroscopy_od_anterior_chamber,
        history.biomicroscopy_od_iris, history.biomicroscopy_od_lens,
        history.biomicroscopy_os_lids, history.biomicroscopy_os_conjunctiva,
        history.biomicroscopy_os_cornea, history.biomicroscopy_os_anterior_chamber,
        history.biomicroscopy_os_iris, history.biomicroscopy_os_lens
    ])
    
    if has_biomicroscopy:
        story.append(Paragraph("BIOMICROSCOPÍA - SEGMENTO ANTERIOR", heading_style))
        
        bio_data = []
        bio_data.append(['', 'OD', 'OS'])
        
        if history.biomicroscopy_od_lids or history.biomicroscopy_os_lids:
            bio_data.append(['Párpados', history.biomicroscopy_od_lids or '-', history.biomicroscopy_os_lids or '-'])
        if history.biomicroscopy_od_conjunctiva or history.biomicroscopy_os_conjunctiva:
            bio_data.append(['Conjuntiva', history.biomicroscopy_od_conjunctiva or '-', history.biomicroscopy_os_conjunctiva or '-'])
        if history.biomicroscopy_od_cornea or history.biomicroscopy_os_cornea:
            bio_data.append(['Córnea', history.biomicroscopy_od_cornea or '-', history.biomicroscopy_os_cornea or '-'])
        if history.biomicroscopy_od_anterior_chamber or history.biomicroscopy_os_anterior_chamber:
            bio_data.append(['Cámara Anterior', history.biomicroscopy_od_anterior_chamber or '-', history.biomicroscopy_os_anterior_chamber or '-'])
        if history.biomicroscopy_od_iris or history.biomicroscopy_os_iris:
            bio_data.append(['Iris', history.biomicroscopy_od_iris or '-', history.biomicroscopy_os_iris or '-'])
        if history.biomicroscopy_od_lens or history.biomicroscopy_os_lens:
            bio_data.append(['Cristalino', history.biomicroscopy_od_lens or '-', history.biomicroscopy_os_lens or '-'])
        if history.biomicroscopy_od_pupil or history.biomicroscopy_os_pupil:
            bio_data.append(['Pupila', history.biomicroscopy_od_pupil or '-', history.biomicroscopy_os_pupil or '-'])
        
        bio_table = Table(bio_data, colWidths=[1.8*inch, 2.5*inch, 2.5*inch])
        bio_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.3, 0.5, 0.6)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (0, -1), colors.Color(0.9, 0.9, 0.9)),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(bio_table)
        story.append(Spacer(1, 0.2*inch))
    
    # NUEVA PÁGINA PARA FONDO DE OJO
    story.append(PageBreak())
    
    # FONDO DE OJO con gráficos
    story.append(Paragraph("FONDO DE OJO", heading_style))
    
    # Dibujos de fondo de ojo
    from reportlab.platypus import Image as PLImage
    from reportlab.graphics import renderPDF
    
    fundus_drawings = []
    fundus_drawings.append(draw_eye_fundus_diagram(width=220, height=220, eye='OD'))
    fundus_drawings.append(Spacer(0.5*inch, 1))
    fundus_drawings.append(draw_eye_fundus_diagram(width=220, height=220, eye='OS'))
    
    fundus_table = Table([[fundus_drawings[0], fundus_drawings[2]]], colWidths=[3.5*inch, 3.5*inch])
    fundus_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(fundus_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Detalles del fondo de ojo
    fundus_data = []
    fundus_data.append(['', 'OD', 'OS'])
    
    if history.fundoscopy_od_vitreous or history.fundoscopy_os_vitreous:
        fundus_data.append(['Vítreo', history.fundoscopy_od_vitreous or 'Normal', history.fundoscopy_os_vitreous or 'Normal'])
    
    if history.fundoscopy_od_optic_disc or history.fundoscopy_os_optic_disc:
        fundus_data.append(['Disco Óptico', history.fundoscopy_od_optic_disc or 'Normal', history.fundoscopy_os_optic_disc or 'Normal'])
    
    if history.fundoscopy_od_cup_disc_ratio or history.fundoscopy_os_cup_disc_ratio:
        fundus_data.append(['Copa/Disco', history.fundoscopy_od_cup_disc_ratio or '-', history.fundoscopy_os_cup_disc_ratio or '-'])
    
    if history.fundoscopy_od_macula or history.fundoscopy_os_macula:
        fundus_data.append(['Mácula', history.fundoscopy_od_macula or 'Normal', history.fundoscopy_os_macula or 'Normal'])
    
    if history.fundoscopy_od_vessels or history.fundoscopy_os_vessels:
        fundus_data.append(['Vasos', history.fundoscopy_od_vessels or 'Normales', history.fundoscopy_os_vessels or 'Normales'])
    
    if history.fundoscopy_od_retina or history.fundoscopy_os_retina:
        fundus_data.append(['Retina', history.fundoscopy_od_retina or 'Aplicada', history.fundoscopy_os_retina or 'Aplicada'])
    
    if len(fundus_data) > 1:
        fundus_detail_table = Table(fundus_data, colWidths=[1.5*inch, 2.5*inch, 2.5*inch])
        fundus_detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.4, 0.3, 0.5)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (0, -1), colors.Color(0.9, 0.9, 0.9)),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(fundus_detail_table)
    
    story.append(Spacer(1, 0.2*inch))
    
    # MOTILIDAD OCULAR
    if history.motility_od or history.motility_os or history.cover_test or history.convergence:
        story.append(Paragraph("MÓDULO OCULOMOTOR", heading_style))
        
        if history.motility_od:
            story.append(Paragraph(f"<b>Motilidad OD:</b> {history.motility_od}", normal_style))
        if history.motility_os:
            story.append(Paragraph(f"<b>Motilidad OS:</b> {history.motility_os}", normal_style))
        if history.cover_test:
            story.append(Paragraph(f"<b>Test de Cover:</b> {history.cover_test}", normal_style))
        if history.convergence:
            story.append(Paragraph(f"<b>Convergencia:</b> {history.convergence}", normal_style))
        
        story.append(Spacer(1, 0.2*inch))
    
    # EXÁMENES COMPLEMENTARIOS
    if history.complementary_exams:
        story.append(Paragraph("EXÁMENES COMPLEMENTARIOS", heading_style))
        story.append(Paragraph(history.complementary_exams, normal_style))
        story.append(Spacer(1, 0.2*inch))
    
    # CONCLUSIONES
    story.append(Paragraph("CONCLUSIONES", heading_style))
    
    # Diagnóstico
    if history.diagnosis:
        story.append(Paragraph(f"<b>Diagnóstico:</b> {history.diagnosis}", normal_style))
    
    # Diagnósticos específicos
    diagnoses = []
    if history.dx_myopia: diagnoses.append("Miopía")
    if history.dx_hyperopia: diagnoses.append("Hipermetropía")
    if history.dx_astigmatism: diagnoses.append("Astigmatismo")
    if history.dx_presbyopia: diagnoses.append("Presbicia")
    if history.dx_amblyopia: diagnoses.append("Ambliopía")
    if history.dx_strabismus: diagnoses.append("Estrabismo")
    if history.dx_cataracts: diagnoses.append("Cataratas")
    if history.dx_glaucoma: diagnoses.append("Glaucoma")
    if history.dx_dry_eye: diagnoses.append("Ojo seco")
    if history.dx_conjunctivitis: diagnoses.append("Conjuntivitis")
    if history.dx_keratoconus: diagnoses.append("Queratocono")
    
    if diagnoses:
        story.append(Paragraph(f"<b>Diagnósticos específicos:</b> {', '.join(diagnoses)}", normal_style))
    
    if history.differential_diagnosis:
        story.append(Paragraph(f"<b>Diagnóstico Diferencial:</b> {history.differential_diagnosis}", normal_style))
    
    if history.prognosis:
        story.append(Paragraph(f"<b>Pronóstico:</b> {history.prognosis}", normal_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # MANEJO Y OBSERVACIONES
    story.append(Paragraph("MANEJO Y OBSERVACIONES", heading_style))
    
    if history.disposition:
        story.append(Paragraph(f"<b>Disposición:</b> {history.disposition}", normal_style))
    
    if history.treatment_plan:
        story.append(Paragraph(f"<b>Plan de Tratamiento:</b> {history.treatment_plan}", normal_style))
    
    # Prescripciones
    if history.prescription_glasses:
        story.append(Paragraph("<b>✓ Prescripción de Lentes</b>", normal_style))
        if history.lens_type:
            story.append(Paragraph(f"Tipo: {history.get_lens_type_display()}", normal_style))
        if history.optical_prescription_notes:
            story.append(Paragraph(f"Notas: {history.optical_prescription_notes}", normal_style))
    
    if history.prescription_medication:
        story.append(Paragraph("<b>✓ Prescripción de Medicamentos</b>", normal_style))
        if history.pharmaceutical_prescription:
            story.append(Paragraph(f"{history.pharmaceutical_prescription}", normal_style))
        if history.topical_medication_protocol:
            story.append(Paragraph(f"<b>Protocolo Tópico:</b> {history.topical_medication_protocol}", normal_style))
    
    if history.recommendations:
        story.append(Paragraph(f"<b>Recomendaciones:</b> {history.recommendations}", normal_style))
    
    if history.follow_up_date:
        story.append(Paragraph(f"<b>Fecha de Seguimiento:</b> {history.follow_up_date}", normal_style))
    
    if history.referral_to:
        story.append(Paragraph(f"<b>Remisión a:</b> {history.referral_to}", normal_style))
        if history.referral_reason:
            story.append(Paragraph(f"<b>Motivo:</b> {history.referral_reason}", normal_style))
    
    if history.observations:
        story.append(Paragraph(f"<b>Observaciones:</b> {history.observations}", normal_style))
    
    # Firma
    story.append(Spacer(1, 0.5*inch))
    
    signature_data = [
        ['', ''],
        ['_' * 40, '_' * 40],
        [f'{history.doctor.full_name if history.doctor else ""}', 'Paciente o Acudiente'],
        [f'{history.doctor.specialty if history.doctor else ""}', ''],
        [f'Reg. {history.doctor.license_number if history.doctor and history.doctor.license_number else ""}', ''],
    ]
    
    signature_table = Table(signature_data, colWidths=[3*inch, 3*inch])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 2), (0, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(signature_table)
    
    # Construir PDF con canvas personalizado
    organization_name = request.organization.name if hasattr(request, 'organization') and request.organization else 'Óptica'
    doctor_name = history.doctor.full_name if history.doctor else ''
    
    doc.build(
        story,
        canvasmaker=lambda *args, **kwargs: NumberedCanvas(
            *args,
            organization_name=organization_name,
            doctor_name=doctor_name,
            **kwargs
        )
    )
    
    # Retornar PDF
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    filename = f'Historia_Clinica_{patient.full_name.replace(" ", "_")}_{history.date}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
