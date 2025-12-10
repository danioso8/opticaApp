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
    
    # Obtener parámetros clínicos
    from apps.patients.models import ClinicalParameter
    lens_materials = ClinicalParameter.objects.filter(
        organization=request.organization,
        parameter_type='lens_material',
        is_active=True
    ).order_by('display_order', 'name')
    
    lens_coatings = ClinicalParameter.objects.filter(
        organization=request.organization,
        parameter_type='treatment',
        is_active=True
    ).order_by('display_order', 'name')
    
    medications = ClinicalParameter.objects.filter(
        organization=request.organization,
        parameter_type__in=['medication', 'topical_medication', 'systemic_medication'],
        is_active=True
    ).order_by('display_order', 'name')
    
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
                current_clinical_condition=request.POST.get('current_clinical_condition', ''),
                
                # Antecedentes Generales
                pathological_history=request.POST.get('pathological_history', ''),
                pharmacological_history=request.POST.get('pharmacological_history', ''),
                surgical_history=request.POST.get('surgical_history', ''),
                allergic_history=request.POST.get('allergic_history', ''),
                trauma_history=request.POST.get('trauma_history', ''),
                other_general_history=request.POST.get('other_general_history', ''),
                medical_history=request.POST.get('medical_history', ''),
                
                # Antecedentes Oculares
                ocular_pathological_history=request.POST.get('ocular_pathological_history', ''),
                ocular_pharmacological_history=request.POST.get('ocular_pharmacological_history', ''),
                ocular_surgical_history=request.POST.get('ocular_surgical_history', ''),
                ocular_trauma_history=request.POST.get('ocular_trauma_history', ''),
                ocular_therapeutic_history=request.POST.get('ocular_therapeutic_history', ''),
                
                # Signos y Síntomas
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
                
                # Antecedentes Familiares Generales
                family_diabetes=request.POST.get('family_diabetes') == 'on',
                family_hypertension=request.POST.get('family_hypertension') == 'on',
                family_heart_disease=request.POST.get('family_heart_disease') == 'on',
                family_cancer=request.POST.get('family_cancer') == 'on',
                family_general_notes=request.POST.get('family_general_notes', ''),
                
                # Antecedentes Familiares Oculares
                family_glaucoma=request.POST.get('family_glaucoma') == 'on',
                family_cataracts=request.POST.get('family_cataracts') == 'on',
                family_macular_degeneration=request.POST.get('family_macular_degeneration') == 'on',
                family_retinal_detachment=request.POST.get('family_retinal_detachment') == 'on',
                family_myopia=request.POST.get('family_myopia') == 'on',
                family_hyperopia=request.POST.get('family_hyperopia') == 'on',
                family_strabismus=request.POST.get('family_strabismus') == 'on',
                family_ocular_notes=request.POST.get('family_ocular_notes', ''),
                family_history_notes=request.POST.get('family_history_notes', ''),
                
                occupation_visual_demand=request.POST.get('occupation_visual_demand', ''),
                screen_hours_daily=request.POST.get('screen_hours_daily') or None,
                reading_hours_daily=request.POST.get('reading_hours_daily') or None,
                
                # Agudeza Visual
                distance_chart=request.POST.get('distance_chart', ''),
                near_chart=request.POST.get('near_chart', ''),
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
                
                # Examen Externo
                external_exam_od=request.POST.get('external_exam_od', ''),
                external_exam_os=request.POST.get('external_exam_os', ''),
                
                # Biomicroscopía
                biomicroscopy_od_lids=request.POST.get('biomicroscopy_od_lids', ''),
                biomicroscopy_od_conjunctiva=request.POST.get('biomicroscopy_od_conjunctiva', ''),
                biomicroscopy_od_cornea=request.POST.get('biomicroscopy_od_cornea', ''),
                biomicroscopy_od_anterior_chamber=request.POST.get('biomicroscopy_od_anterior_chamber', ''),
                biomicroscopy_od_iris=request.POST.get('biomicroscopy_od_iris', ''),
                biomicroscopy_od_lens=request.POST.get('biomicroscopy_od_lens', ''),
                biomicroscopy_od_pupil=request.POST.get('biomicroscopy_od_pupil', ''),
                
                biomicroscopy_os_lids=request.POST.get('biomicroscopy_os_lids', ''),
                biomicroscopy_os_conjunctiva=request.POST.get('biomicroscopy_os_conjunctiva', ''),
                biomicroscopy_os_cornea=request.POST.get('biomicroscopy_os_cornea', ''),
                biomicroscopy_os_anterior_chamber=request.POST.get('biomicroscopy_os_anterior_chamber', ''),
                biomicroscopy_os_iris=request.POST.get('biomicroscopy_os_iris', ''),
                biomicroscopy_os_lens=request.POST.get('biomicroscopy_os_lens', ''),
                biomicroscopy_os_pupil=request.POST.get('biomicroscopy_os_pupil', ''),
                
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
    
    # Obtener el último examen visual del paciente para pre-cargar datos
    last_exam = ClinicalHistory.objects.filter(
        patient=patient,
        **org_filter
    ).order_by('-date').first()
    
    context = {
        'patient': patient,
        'today': datetime.now().date(),
        'doctors': doctors,
        'lens_materials': lens_materials,
        'lens_coatings': lens_coatings,
        'medications': medications,
        'last_exam': last_exam,  # Último examen para pre-cargar datos
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
    
    # Obtener parámetros clínicos
    from apps.patients.models import ClinicalParameter
    lens_materials = ClinicalParameter.objects.filter(
        organization=request.organization,
        parameter_type='lens_material',
        is_active=True
    ).order_by('display_order', 'name')
    
    lens_coatings = ClinicalParameter.objects.filter(
        organization=request.organization,
        parameter_type='treatment',
        is_active=True
    ).order_by('display_order', 'name')
    
    medications = ClinicalParameter.objects.filter(
        organization=request.organization,
        parameter_type__in=['medication', 'topical_medication', 'systemic_medication'],
        is_active=True
    ).order_by('display_order', 'name')
    
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
            
            # Actualizar campos básicos
            history.date = request.POST.get('date') or history.date
            history.doctor = doctor
            history.chief_complaint = request.POST.get('chief_complaint', '')
            history.current_illness = request.POST.get('current_illness', '')
            history.current_clinical_condition = request.POST.get('current_clinical_condition', '')
            
            # Antecedentes Generales
            history.pathological_history = request.POST.get('pathological_history', '')
            history.pharmacological_history = request.POST.get('pharmacological_history', '')
            history.surgical_history = request.POST.get('surgical_history', '')
            history.allergic_history = request.POST.get('allergic_history', '')
            history.trauma_history = request.POST.get('trauma_history', '')
            history.other_general_history = request.POST.get('other_general_history', '')
            history.medical_history = request.POST.get('medical_history', '')
            
            # Antecedentes Oculares
            history.ocular_pathological_history = request.POST.get('ocular_pathological_history', '')
            history.ocular_pharmacological_history = request.POST.get('ocular_pharmacological_history', '')
            history.ocular_surgical_history = request.POST.get('ocular_surgical_history', '')
            history.ocular_trauma_history = request.POST.get('ocular_trauma_history', '')
            history.ocular_therapeutic_history = request.POST.get('ocular_therapeutic_history', '')
            
            # Signos y Síntomas
            history.blurred_vision = request.POST.get('blurred_vision') == 'on'
            history.eye_pain = request.POST.get('eye_pain') == 'on'
            history.headaches = request.POST.get('headaches') == 'on'
            history.photophobia = request.POST.get('photophobia') == 'on'
            history.diplopia = request.POST.get('diplopia') == 'on'
            history.tearing = request.POST.get('tearing') == 'on'
            history.redness = request.POST.get('redness') == 'on'
            history.itching = request.POST.get('itching') == 'on'
            history.floaters = request.POST.get('floaters') == 'on'
            history.halos = request.POST.get('halos') == 'on'
            history.symptoms_notes = request.POST.get('symptoms_notes', '')
            
            # Antecedentes Oftalmológicos
            history.previous_eye_surgery = request.POST.get('previous_eye_surgery') == 'on'
            history.surgery_details = request.POST.get('surgery_details', '')
            history.previous_glasses = request.POST.get('previous_glasses') == 'on'
            history.glasses_since = request.POST.get('glasses_since', '')
            history.previous_contact_lenses = request.POST.get('previous_contact_lenses') == 'on'
            
            # Antecedentes Familiares Generales
            history.family_diabetes = request.POST.get('family_diabetes') == 'on'
            history.family_hypertension = request.POST.get('family_hypertension') == 'on'
            history.family_heart_disease = request.POST.get('family_heart_disease') == 'on'
            history.family_cancer = request.POST.get('family_cancer') == 'on'
            history.family_general_notes = request.POST.get('family_general_notes', '')
            
            # Antecedentes Familiares Oculares
            history.family_glaucoma = request.POST.get('family_glaucoma') == 'on'
            history.family_cataracts = request.POST.get('family_cataracts') == 'on'
            history.family_macular_degeneration = request.POST.get('family_macular_degeneration') == 'on'
            history.family_retinal_detachment = request.POST.get('family_retinal_detachment') == 'on'
            history.family_myopia = request.POST.get('family_myopia') == 'on'
            history.family_hyperopia = request.POST.get('family_hyperopia') == 'on'
            history.family_strabismus = request.POST.get('family_strabismus') == 'on'
            history.family_ocular_notes = request.POST.get('family_ocular_notes', '')
            history.family_history_notes = request.POST.get('family_history_notes', '')
            
            # Ocupación y Hábitos
            history.occupation_visual_demand = request.POST.get('occupation_visual_demand', '')
            history.screen_hours_daily = request.POST.get('screen_hours_daily') or None
            history.reading_hours_daily = request.POST.get('reading_hours_daily') or None
            
            # Cartillas utilizadas
            history.distance_chart = request.POST.get('distance_chart', '')
            history.near_chart = request.POST.get('near_chart', '')
            
            # Agudeza Visual
            history.va_od_sc_distance = request.POST.get('va_od_sc_distance', '')
            history.va_od_cc_distance = request.POST.get('va_od_cc_distance', '')
            history.va_od_ph_distance = request.POST.get('va_od_ph_distance', '')
            history.va_od_sc_near = request.POST.get('va_od_sc_near', '')
            history.va_od_cc_near = request.POST.get('va_od_cc_near', '')
            
            history.va_os_sc_distance = request.POST.get('va_os_sc_distance', '')
            history.va_os_cc_distance = request.POST.get('va_os_cc_distance', '')
            history.va_os_ph_distance = request.POST.get('va_os_ph_distance', '')
            history.va_os_sc_near = request.POST.get('va_os_sc_near', '')
            history.va_os_cc_near = request.POST.get('va_os_cc_near', '')
            
            # Refracción Objetiva
            refraction_od_sphere = request.POST.get('refraction_od_sphere', '').strip()
            history.refraction_od_sphere = refraction_od_sphere if refraction_od_sphere else None
            refraction_od_cylinder = request.POST.get('refraction_od_cylinder', '').strip()
            history.refraction_od_cylinder = float(refraction_od_cylinder) if refraction_od_cylinder else None
            refraction_od_axis = request.POST.get('refraction_od_axis', '').strip()
            history.refraction_od_axis = int(refraction_od_axis) if refraction_od_axis else None
            refraction_od_add = request.POST.get('refraction_od_add', '').strip()
            history.refraction_od_add = float(refraction_od_add) if refraction_od_add else None
            
            refraction_os_sphere = request.POST.get('refraction_os_sphere', '').strip()
            history.refraction_os_sphere = refraction_os_sphere if refraction_os_sphere else None
            refraction_os_cylinder = request.POST.get('refraction_os_cylinder', '').strip()
            history.refraction_os_cylinder = float(refraction_os_cylinder) if refraction_os_cylinder else None
            refraction_os_axis = request.POST.get('refraction_os_axis', '').strip()
            history.refraction_os_axis = int(refraction_os_axis) if refraction_os_axis else None
            refraction_os_add = request.POST.get('refraction_os_add', '').strip()
            history.refraction_os_add = float(refraction_os_add) if refraction_os_add else None
            
            # Refracción Subjetiva
            subjective_od_sphere = request.POST.get('subjective_od_sphere', '').strip()
            history.subjective_od_sphere = subjective_od_sphere if subjective_od_sphere else None
            subjective_od_cylinder = request.POST.get('subjective_od_cylinder', '').strip()
            history.subjective_od_cylinder = float(subjective_od_cylinder) if subjective_od_cylinder else None
            subjective_od_axis = request.POST.get('subjective_od_axis', '').strip()
            history.subjective_od_axis = int(subjective_od_axis) if subjective_od_axis else None
            subjective_od_add = request.POST.get('subjective_od_add', '').strip()
            history.subjective_od_add = float(subjective_od_add) if subjective_od_add else None
            history.subjective_od_va = request.POST.get('subjective_od_va', '').strip() or None
            
            subjective_os_sphere = request.POST.get('subjective_os_sphere', '').strip()
            history.subjective_os_sphere = subjective_os_sphere if subjective_os_sphere else None
            subjective_os_cylinder = request.POST.get('subjective_os_cylinder', '').strip()
            history.subjective_os_cylinder = float(subjective_os_cylinder) if subjective_os_cylinder else None
            subjective_os_axis = request.POST.get('subjective_os_axis', '').strip()
            history.subjective_os_axis = int(subjective_os_axis) if subjective_os_axis else None
            subjective_os_add = request.POST.get('subjective_os_add', '').strip()
            history.subjective_os_add = float(subjective_os_add) if subjective_os_add else None
            history.subjective_os_va = request.POST.get('subjective_os_va', '').strip() or None
            
            # Queratometría
            keratometry_od_k1 = request.POST.get('keratometry_od_k1')
            history.keratometry_od_k1 = float(keratometry_od_k1) if keratometry_od_k1 else None
            keratometry_od_k1_axis = request.POST.get('keratometry_od_k1_axis')
            history.keratometry_od_k1_axis = int(keratometry_od_k1_axis) if keratometry_od_k1_axis else None
            keratometry_od_k2 = request.POST.get('keratometry_od_k2')
            history.keratometry_od_k2 = float(keratometry_od_k2) if keratometry_od_k2 else None
            keratometry_od_k2_axis = request.POST.get('keratometry_od_k2_axis')
            history.keratometry_od_k2_axis = int(keratometry_od_k2_axis) if keratometry_od_k2_axis else None
            
            keratometry_os_k1 = request.POST.get('keratometry_os_k1')
            history.keratometry_os_k1 = float(keratometry_os_k1) if keratometry_os_k1 else None
            keratometry_os_k1_axis = request.POST.get('keratometry_os_k1_axis')
            history.keratometry_os_k1_axis = int(keratometry_os_k1_axis) if keratometry_os_k1_axis else None
            keratometry_os_k2 = request.POST.get('keratometry_os_k2')
            history.keratometry_os_k2 = float(keratometry_os_k2) if keratometry_os_k2 else None
            keratometry_os_k2_axis = request.POST.get('keratometry_os_k2_axis')
            history.keratometry_os_k2_axis = int(keratometry_os_k2_axis) if keratometry_os_k2_axis else None
            
            # Pupilas
            history.pupil_od_size = request.POST.get('pupil_od_size', '')
            history.pupil_od_reaction = request.POST.get('pupil_od_reaction', '')
            history.pupil_os_size = request.POST.get('pupil_os_size', '')
            history.pupil_os_reaction = request.POST.get('pupil_os_reaction', '')
            history.pupil_rapd = request.POST.get('pupil_rapd') == 'on'
            
            # Tonometría
            iop_od = request.POST.get('iop_od')
            history.iop_od = float(iop_od) if iop_od else None
            iop_os = request.POST.get('iop_os')
            history.iop_os = float(iop_os) if iop_os else None
            history.iop_method = request.POST.get('iop_method', '')
            
            # Examen Externo
            history.external_exam_od = request.POST.get('external_exam_od', '')
            history.external_exam_os = request.POST.get('external_exam_os', '')
            
            # Biomicroscopía
            history.biomicroscopy_od_lids = request.POST.get('biomicroscopy_od_lids', '')
            history.biomicroscopy_od_conjunctiva = request.POST.get('biomicroscopy_od_conjunctiva', '')
            history.biomicroscopy_od_cornea = request.POST.get('biomicroscopy_od_cornea', '')
            history.biomicroscopy_od_anterior_chamber = request.POST.get('biomicroscopy_od_anterior_chamber', '')
            history.biomicroscopy_od_iris = request.POST.get('biomicroscopy_od_iris', '')
            history.biomicroscopy_od_lens = request.POST.get('biomicroscopy_od_lens', '')
            history.biomicroscopy_od_pupil = request.POST.get('biomicroscopy_od_pupil', '')
            
            history.biomicroscopy_os_lids = request.POST.get('biomicroscopy_os_lids', '')
            history.biomicroscopy_os_conjunctiva = request.POST.get('biomicroscopy_os_conjunctiva', '')
            history.biomicroscopy_os_cornea = request.POST.get('biomicroscopy_os_cornea', '')
            history.biomicroscopy_os_anterior_chamber = request.POST.get('biomicroscopy_os_anterior_chamber', '')
            history.biomicroscopy_os_iris = request.POST.get('biomicroscopy_os_iris', '')
            history.biomicroscopy_os_lens = request.POST.get('biomicroscopy_os_lens', '')
            history.biomicroscopy_os_pupil = request.POST.get('biomicroscopy_os_pupil', '')
            
            # Fondo de Ojo
            history.fundoscopy_od_vitreous = request.POST.get('fundoscopy_od_vitreous', '')
            history.fundoscopy_od_optic_disc = request.POST.get('fundoscopy_od_optic_disc', '')
            history.fundoscopy_od_macula = request.POST.get('fundoscopy_od_macula', '')
            history.fundoscopy_od_vessels = request.POST.get('fundoscopy_od_vessels', '')
            history.fundoscopy_od_periphery = request.POST.get('fundoscopy_od_periphery', '')
            
            history.fundoscopy_os_vitreous = request.POST.get('fundoscopy_os_vitreous', '')
            history.fundoscopy_os_optic_disc = request.POST.get('fundoscopy_os_optic_disc', '')
            history.fundoscopy_os_macula = request.POST.get('fundoscopy_os_macula', '')
            history.fundoscopy_os_vessels = request.POST.get('fundoscopy_os_vessels', '')
            history.fundoscopy_os_periphery = request.POST.get('fundoscopy_os_periphery', '')
            
            # Motilidad
            history.motility_od = request.POST.get('motility_od', '')
            history.motility_os = request.POST.get('motility_os', '')
            history.cover_test = request.POST.get('cover_test', '')
            history.convergence = request.POST.get('convergence', '')
            
            # Visión de Colores
            history.color_vision_od = request.POST.get('color_vision_od', '')
            history.color_vision_os = request.POST.get('color_vision_os', '')
            history.color_vision_test = request.POST.get('color_vision_test', '')
            
            # Diagnóstico
            history.diagnosis = request.POST.get('diagnosis', '')
            history.dx_myopia = request.POST.get('dx_myopia') == 'on'
            history.dx_hyperopia = request.POST.get('dx_hyperopia') == 'on'
            history.dx_astigmatism = request.POST.get('dx_astigmatism') == 'on'
            history.dx_presbyopia = request.POST.get('dx_presbyopia') == 'on'
            history.dx_amblyopia = request.POST.get('dx_amblyopia') == 'on'
            history.dx_strabismus = request.POST.get('dx_strabismus') == 'on'
            history.dx_cataracts = request.POST.get('dx_cataracts') == 'on'
            history.dx_glaucoma = request.POST.get('dx_glaucoma') == 'on'
            history.dx_dry_eye = request.POST.get('dx_dry_eye') == 'on'
            history.dx_conjunctivitis = request.POST.get('dx_conjunctivitis') == 'on'
            history.dx_keratoconus = request.POST.get('dx_keratoconus') == 'on'
            
            # Tratamiento
            history.treatment_plan = request.POST.get('treatment_plan', '')
            history.prescription_glasses = request.POST.get('prescription_glasses') == 'on'
            history.prescription_contact_lenses = request.POST.get('prescription_contact_lenses') == 'on'
            history.prescription_medication = request.POST.get('prescription_medication') == 'on'
            history.medication_details = request.POST.get('medication_details', '')
            
            history.lens_type = request.POST.get('lens_type', '')
            history.lens_material = request.POST.get('lens_material', '')
            history.lens_coating = request.POST.get('lens_coating', '')
            
            # Seguimiento
            follow_up_date = request.POST.get('follow_up_date')
            history.follow_up_date = follow_up_date if follow_up_date else None
            history.follow_up_notes = request.POST.get('follow_up_notes', '')
            history.observations = request.POST.get('observations', '')
            history.recommendations = request.POST.get('recommendations', '')
            
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
        'lens_materials': lens_materials,
        'lens_coatings': lens_coatings,
        'medications': medications,
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
def latest_fundoscopy(request, patient_id):
    """Obtener datos del último examen de fondo de ojo"""
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    patient = get_object_or_404(Patient, id=patient_id, **org_filter)
    
    # Buscar la historia clínica más reciente con datos de fondo de ojo
    latest_history = ClinicalHistory.objects.filter(
        patient=patient,
        **org_filter
    ).exclude(
        fundoscopy_od_vitreous='',
        fundoscopy_od_optic_disc='',
        fundoscopy_os_vitreous='',
        fundoscopy_os_optic_disc=''
    ).order_by('-date').first()
    
    if latest_history:
        return JsonResponse({
            'success': True,
            'fundoscopy': {
                'od_vitreous': latest_history.fundoscopy_od_vitreous or '',
                'od_optic_disc': latest_history.fundoscopy_od_optic_disc or '',
                'od_cup_disc_ratio': latest_history.fundoscopy_od_cup_disc_ratio or '',
                'od_macula': latest_history.fundoscopy_od_macula or '',
                'od_vessels': latest_history.fundoscopy_od_vessels or '',
                'od_retina': latest_history.fundoscopy_od_retina or '',
                'os_vitreous': latest_history.fundoscopy_os_vitreous or '',
                'os_optic_disc': latest_history.fundoscopy_os_optic_disc or '',
                'os_cup_disc_ratio': latest_history.fundoscopy_os_cup_disc_ratio or '',
                'os_macula': latest_history.fundoscopy_os_macula or '',
                'os_vessels': latest_history.fundoscopy_os_vessels or '',
                'os_retina': latest_history.fundoscopy_os_retina or '',
            },
            'date': latest_history.date.strftime('%d/%m/%Y')
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'No se encontraron registros previos de fondo de ojo'
        })


@login_required
def clinical_history_pdf(request, patient_id, history_id):
    """Generar PDF de historia clínica"""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
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
    
    # FÓRMULA DE LENTES ÓPTICOS
    # Mostrar si hay datos de refracción (independiente de prescription_glasses)
    if any([
        history.refraction_od_sphere, history.refraction_od_cylinder,
        history.refraction_os_sphere, history.refraction_os_cylinder
    ]):
        story.append(PageBreak())
        
        # Encabezado estilo fórmula profesional
        formula_title_style = ParagraphStyle(
            'FormulaTitle',
            parent=title_style,
            fontSize=16,
            textColor=colors.Color(0.1, 0.3, 0.5),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            borderWidth=2,
            borderColor=colors.Color(0.1, 0.3, 0.5),
            borderPadding=10,
            backColor=colors.Color(0.95, 0.97, 1)
        )
        
        story.append(Paragraph("FÓRMULA DE LENTES ÓPTICOS", formula_title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Tabla de fórmula principal - formato profesional
        formula_data = [
            ['', 'ESFERA', 'CILINDRO', 'EJE', 'ADICIÓN', 'PRISMA BASE', 'GRADUADOS', 'AV LEJOS', 'AV CERCA'],
            [
                'OD',
                str(history.refraction_od_sphere) if history.refraction_od_sphere else '-',
                str(history.refraction_od_cylinder) if history.refraction_od_cylinder else '-',
                str(history.refraction_od_axis) + '°' if history.refraction_od_axis else '-',
                '+' + str(history.refraction_od_add) if history.refraction_od_add else '-',
                str(history.refraction_od_prism) if history.refraction_od_prism else '-',
                str(history.refraction_od_dnp) if history.refraction_od_dnp else '-',
                str(history.va_od_cc_distance) if history.va_od_cc_distance else '20/20',
                str(history.va_od_cc_near) if history.va_od_cc_near else '0.75M',
            ],
            [
                'OS',
                str(history.refraction_os_sphere) if history.refraction_os_sphere else '-',
                str(history.refraction_os_cylinder) if history.refraction_os_cylinder else '-',
                str(history.refraction_os_axis) + '°' if history.refraction_os_axis else '-',
                '+' + str(history.refraction_os_add) if history.refraction_os_add else '-',
                str(history.refraction_os_prism) if history.refraction_os_prism else '-',
                str(history.refraction_os_dnp) if history.refraction_os_dnp else '-',
                str(history.va_os_cc_distance) if history.va_os_cc_distance else '20/20',
                str(history.va_os_cc_near) if history.va_os_cc_near else '0.75M',
            ]
        ]
        
        formula_table = Table(formula_data, colWidths=[0.5*inch, 0.65*inch, 0.7*inch, 0.55*inch, 0.7*inch, 0.85*inch, 0.85*inch, 0.75*inch, 0.75*inch])
        formula_table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.15, 0.35, 0.55)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            # Filas de datos
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (0, -1), colors.Color(0.92, 0.92, 0.92)),
            # Bordes y líneas
            ('GRID', (0, 0), (-1, -1), 1.5, colors.black),
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.Color(0.15, 0.35, 0.55)),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.Color(0.15, 0.35, 0.55)),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.Color(0.15, 0.35, 0.55)),
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(formula_table)
        story.append(Spacer(1, 0.4*inch))
        
        # Sección: TOMAR CENTROS ÓPTICOS
        if history.pd_distance or history.pd_near or history.pd_od or history.pd_os:
            center_title = Paragraph("<b>TOMAR CENTROS ÓPTICOS</b>", heading_style)
            story.append(center_title)
            story.append(Spacer(1, 0.1*inch))
            
            center_data = [
                ['Distancia Pupilar (mm)', 'Altura (mm)', 'Alternativa'],
            ]
            
            # Fila con los datos
            dp_text = f"{history.pd_distance}" if history.pd_distance else "N/A"
            if history.pd_near:
                dp_text += f" / {history.pd_near}"
            
            altura_text = f"DN/PA: {history.pd_od or 'N/A'} / {history.pd_os or 'N/A'}"
            
            center_data.append([dp_text, altura_text, 'Sí/No'])
            
            center_table = Table(center_data, colWidths=[2.3*inch, 2.3*inch, 2*inch])
            center_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(center_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Detalles de lentes y dispositivo
        details_data = [
            ['Tipo Lentes:', history.lens_type or 'No especificado', 'Detalle:', 'AR'],
            ['Color y Tints:', history.lens_material or '-', 'Dip:', f"{history.pd_distance or 'N/A'}/{history.pd_near or 'N/A'}"],
            ['Uso Dispositivo:', 'Permanente' if history.prescription_glasses else '-', 'Control:', '1 año'],
        ]
        
        details_table = Table(details_data, colWidths=[1.5*inch, 2*inch, 1.2*inch, 2*inch])
        details_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Observaciones de la prescripción
        if history.optical_prescription_notes or history.lens_type or history.lens_material or history.lens_coating:
            story.append(Paragraph("Observaciones:", heading_style))
            obs_text = ""
            if history.lens_type:
                obs_text += f"<b>Tipo:</b> {history.lens_type}. "
            if history.lens_material:
                obs_text += f"<b>Material:</b> {history.lens_material}. "
            if history.lens_coating:
                obs_text += f"<b>Tratamientos:</b> {history.lens_coating}. "
            if history.lens_brand:
                obs_text += f"<b>Marca:</b> {history.lens_brand}. "
            if history.frame_type:
                obs_text += f"<b>Montura:</b> {history.frame_type}. "
            if history.optical_prescription_notes:
                obs_text += f"<br/>{history.optical_prescription_notes}"
            
            story.append(Paragraph(obs_text, normal_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Nota de advertencia (similar a la imagen)
        warning_style = ParagraphStyle(
            'Warning',
            parent=normal_style,
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.Color(0.3, 0.3, 0.3),
            borderWidth=1,
            borderColor=colors.grey,
            borderPadding=5
        )
        story.append(Paragraph("NO SE DA GARANTÍA POR LENTES ADQUIRIDOS EN OTRA ÓPTICA", warning_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Información del optómetra y sello
        org_name = request.organization.name if hasattr(request, 'organization') and request.organization else 'ÓPTICA'
        org_info = f"<b>Optómetra:</b> {history.doctor.full_name if history.doctor else 'N/A'}<br/>"
        org_info += f"<b>Reg Médico:</b> {history.doctor.professional_card if history.doctor and history.doctor.professional_card else 'N/A'}"
        
        story.append(Paragraph(org_info, normal_style))
        story.append(Spacer(1, 0.3*inch))
    
    # MANEJO Y OBSERVACIONES
    story.append(PageBreak())
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
        [f'T.P. {history.doctor.professional_card if history.doctor and history.doctor.professional_card else ""}', ''],
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


@login_required
def visual_exam_create(request, patient_id):
    """Crear examen visual simplificado (solo datos de examen de ojos)"""
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    patient = get_object_or_404(Patient, id=patient_id, **org_filter)
    
    # Obtener doctores activos de la organización
    doctors = Doctor.objects.filter(
        organization=request.organization,
        is_active=True
    ).order_by('full_name')
    
    if request.method == 'POST':
        try:
            # Crear historia clínica con solo los datos del examen visual
            history = ClinicalHistory.objects.create(
                patient=patient,
                organization=request.organization,
                date=request.POST.get('date'),
                doctor_id=request.POST.get('doctor') if request.POST.get('doctor') else None,
                
                # Cartillas utilizadas
                distance_chart=request.POST.get('distance_chart', ''),
                near_chart=request.POST.get('near_chart', ''),
                
                # Agudeza Visual - Lejos
                va_od_sc_distance=request.POST.get('va_od_sc_distance', ''),
                va_od_cc_distance=request.POST.get('va_od_cc_distance', ''),
                va_os_sc_distance=request.POST.get('va_os_sc_distance', ''),
                va_os_cc_distance=request.POST.get('va_os_cc_distance', ''),
                
                # Agudeza Visual - Cerca
                va_od_sc_near=request.POST.get('va_od_sc_near', ''),
                va_od_cc_near=request.POST.get('va_od_cc_near', ''),
                va_os_sc_near=request.POST.get('va_os_sc_near', ''),
                va_os_cc_near=request.POST.get('va_os_cc_near', ''),
                
                # Refracción OD
                refraction_od_sphere=request.POST.get('refraction_od_sphere', ''),
                refraction_od_cylinder=float(request.POST.get('refraction_od_cylinder') or 0) if request.POST.get('refraction_od_cylinder') else None,
                refraction_od_axis=int(request.POST.get('refraction_od_axis') or 0) if request.POST.get('refraction_od_axis') else None,
                refraction_od_add=float(request.POST.get('refraction_od_add') or 0) if request.POST.get('refraction_od_add') else None,
                refraction_od_prism=request.POST.get('refraction_od_prism', ''),
                refraction_od_dnp=float(request.POST.get('refraction_od_dnp') or 0) if request.POST.get('refraction_od_dnp') else None,
                
                # Refracción OS
                refraction_os_sphere=request.POST.get('refraction_os_sphere', ''),
                refraction_os_cylinder=float(request.POST.get('refraction_os_cylinder') or 0) if request.POST.get('refraction_os_cylinder') else None,
                refraction_os_axis=int(request.POST.get('refraction_os_axis') or 0) if request.POST.get('refraction_os_axis') else None,
                refraction_os_add=float(request.POST.get('refraction_os_add') or 0) if request.POST.get('refraction_os_add') else None,
                refraction_os_prism=request.POST.get('refraction_os_prism', ''),
                refraction_os_dnp=float(request.POST.get('refraction_os_dnp') or 0) if request.POST.get('refraction_os_dnp') else None,
                
                # Distancia Pupilar
                pd_distance=float(request.POST.get('pd_distance') or 0) if request.POST.get('pd_distance') else None,
                pd_near=float(request.POST.get('pd_near') or 0) if request.POST.get('pd_near') else None,
                pd_od=float(request.POST.get('pd_od') or 0) if request.POST.get('pd_od') else None,
                pd_os=float(request.POST.get('pd_os') or 0) if request.POST.get('pd_os') else None,
                
                # Queratometría OD
                keratometry_od_k1=float(request.POST.get('keratometry_od_k1') or 0) if request.POST.get('keratometry_od_k1') else None,
                keratometry_od_k2=float(request.POST.get('keratometry_od_k2') or 0) if request.POST.get('keratometry_od_k2') else None,
                keratometry_od_k1_axis=int(request.POST.get('keratometry_od_axis') or 0) if request.POST.get('keratometry_od_axis') else None,
                
                # Queratometría OS
                keratometry_os_k1=float(request.POST.get('keratometry_os_k1') or 0) if request.POST.get('keratometry_os_k1') else None,
                keratometry_os_k2=float(request.POST.get('keratometry_os_k2') or 0) if request.POST.get('keratometry_os_k2') else None,
                keratometry_os_k1_axis=int(request.POST.get('keratometry_os_axis') or 0) if request.POST.get('keratometry_os_axis') else None,
                
                # ANAMNESIS
                chief_complaint=request.POST.get('chief_complaint', 'Examen visual de rutina'),
                current_illness=request.POST.get('current_illness', ''),
                
                # ANTECEDENTES GENERALES
                pathological_history=request.POST.get('pathological_history', ''),
                pharmacological_history=request.POST.get('pharmacological_history', ''),
                surgical_history=request.POST.get('surgical_history', ''),
                allergic_history=request.POST.get('allergic_history', ''),
                trauma_history=request.POST.get('trauma_history', ''),
                other_general_history=request.POST.get('other_general_history', ''),
                
                # ANTECEDENTES OCULARES
                ocular_pathological_history=request.POST.get('ocular_pathological_history', ''),
                ocular_pharmacological_history=request.POST.get('ocular_pharmacological_history', ''),
                ocular_surgical_history=request.POST.get('ocular_surgical_history', ''),
                ocular_trauma_history=request.POST.get('ocular_trauma_history', ''),
                previous_glasses=request.POST.get('previous_glasses') == 'on',
                previous_contact_lenses=request.POST.get('previous_contact_lenses') == 'on',
                ocular_therapeutic_history=request.POST.get('ocular_therapeutic_history', ''),
                
                # ANTECEDENTES FAMILIARES - Generales
                family_diabetes=request.POST.get('family_diabetes') == 'on',
                family_hypertension=request.POST.get('family_hypertension') == 'on',
                family_heart_disease=request.POST.get('family_heart_disease') == 'on',
                family_cancer=request.POST.get('family_cancer') == 'on',
                family_general_notes=request.POST.get('family_general_notes', ''),
                
                # ANTECEDENTES FAMILIARES - Oculares
                family_glaucoma=request.POST.get('family_glaucoma') == 'on',
                family_cataracts=request.POST.get('family_cataracts') == 'on',
                family_macular_degeneration=request.POST.get('family_macular_degeneration') == 'on',
                family_retinal_detachment=request.POST.get('family_retinal_detachment') == 'on',
                family_myopia=request.POST.get('family_myopia') == 'on',
                family_strabismus=request.POST.get('family_strabismus') == 'on',
                family_ocular_notes=request.POST.get('family_ocular_notes', ''),
                
                # SEGMENTO ANTERIOR - OD
                biomicroscopy_od_lids=request.POST.get('biomicroscopy_od_lids', ''),
                biomicroscopy_od_conjunctiva=request.POST.get('biomicroscopy_od_conjunctiva', ''),
                biomicroscopy_od_cornea=request.POST.get('biomicroscopy_od_cornea', ''),
                biomicroscopy_od_anterior_chamber=request.POST.get('biomicroscopy_od_anterior_chamber', ''),
                biomicroscopy_od_iris=request.POST.get('biomicroscopy_od_iris', ''),
                biomicroscopy_od_lens=request.POST.get('biomicroscopy_od_lens', ''),
                biomicroscopy_od_pupil=request.POST.get('biomicroscopy_od_pupil', ''),
                
                # SEGMENTO ANTERIOR - OS
                biomicroscopy_os_lids=request.POST.get('biomicroscopy_os_lids', ''),
                biomicroscopy_os_conjunctiva=request.POST.get('biomicroscopy_os_conjunctiva', ''),
                biomicroscopy_os_cornea=request.POST.get('biomicroscopy_os_cornea', ''),
                biomicroscopy_os_anterior_chamber=request.POST.get('biomicroscopy_os_anterior_chamber', ''),
                biomicroscopy_os_iris=request.POST.get('biomicroscopy_os_iris', ''),
                biomicroscopy_os_lens=request.POST.get('biomicroscopy_os_lens', ''),
                biomicroscopy_os_pupil=request.POST.get('biomicroscopy_os_pupil', ''),
                
                # SEGMENTO POSTERIOR - OD
                fundoscopy_od_vitreous=request.POST.get('fundoscopy_od_vitreous', ''),
                fundoscopy_od_optic_disc=request.POST.get('fundoscopy_od_optic_disc', ''),
                fundoscopy_od_cup_disc_ratio=request.POST.get('fundoscopy_od_cup_disc_ratio', ''),
                fundoscopy_od_macula=request.POST.get('fundoscopy_od_macula', ''),
                fundoscopy_od_vessels=request.POST.get('fundoscopy_od_vessels', ''),
                fundoscopy_od_retina=request.POST.get('fundoscopy_od_retina', ''),
                
                # SEGMENTO POSTERIOR - OS
                fundoscopy_os_vitreous=request.POST.get('fundoscopy_os_vitreous', ''),
                fundoscopy_os_optic_disc=request.POST.get('fundoscopy_os_optic_disc', ''),
                fundoscopy_os_cup_disc_ratio=request.POST.get('fundoscopy_os_cup_disc_ratio', ''),
                fundoscopy_os_macula=request.POST.get('fundoscopy_os_macula', ''),
                fundoscopy_os_vessels=request.POST.get('fundoscopy_os_vessels', ''),
                fundoscopy_os_retina=request.POST.get('fundoscopy_os_retina', ''),
                
                # DIAGNÓSTICO - Checkboxes
                dx_myopia=request.POST.get('dx_myopia') == 'on',
                dx_hyperopia=request.POST.get('dx_hyperopia') == 'on',
                dx_astigmatism=request.POST.get('dx_astigmatism') == 'on',
                dx_presbyopia=request.POST.get('dx_presbyopia') == 'on',
                diagnosis=request.POST.get('diagnosis', ''),
                
                # PRESCRIPCIÓN - Checkboxes
                prescription_glasses=request.POST.get('prescription_glasses') == 'on',
                prescription_contact_lenses=request.POST.get('prescription_contact_lenses') == 'on',
                prescription_medication=request.POST.get('prescription_medication') == 'on',
                
                # LENTES OFTÁLMICOS
                lens_type=request.POST.get('lens_type', ''),
                lens_material=request.POST.get('lens_material', ''),
                lens_coating=request.POST.get('lens_coating', ''),
                lens_brand=request.POST.get('lens_brand', ''),
                frame_type=request.POST.get('frame_type', ''),
                
                # MEDICAMENTOS
                medication_details=request.POST.get('medication_details', ''),
                
                # LENTES DE CONTACTO
                contact_lens_type=request.POST.get('contact_lens_type', ''),
                contact_lens_brand=request.POST.get('contact_lens_brand', ''),
                contact_lens_material=request.POST.get('contact_lens_material', ''),
                contact_lens_wearing=request.POST.get('contact_lens_wearing', ''),
                
                # TRATAMIENTOS Y TERAPIAS
                therapy=', '.join(request.POST.getlist('therapy')),
                visual_therapy=', '.join(request.POST.getlist('visual_therapy')),
                
                # EXÁMENES COMPLEMENTARIOS
                complementary_exam=', '.join(request.POST.getlist('complementary_exam')),
                lab_test=', '.join(request.POST.getlist('lab_test')),
                
                # RECOMENDACIONES Y SEGUIMIENTO
                recommendation=', '.join(request.POST.getlist('recommendation')),
                follow_up_reason=request.POST.get('follow_up_reason', ''),
                referral_specialty=request.POST.get('referral_specialty', ''),
                treatment_plan=request.POST.get('treatment_plan', ''),
                
                # OBSERVACIONES Y CONDUCTA
                observations=request.POST.get('exam_notes', ''),
                recommendations_text=request.POST.get('recommendations_text', ''),
                additional_notes=request.POST.get('additional_notes', '')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Examen visual guardado exitosamente',
                'history_id': history.id
            })
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"ERROR COMPLETO: {error_details}")
            return JsonResponse({
                'success': False,
                'message': f'Error al guardar el examen: {str(e)}',
                'details': error_details
            }, status=400)
    
    # GET - Mostrar formulario
    # Obtener parámetros clínicos
    from apps.patients.models import ClinicalParameter
    
    # Función auxiliar para obtener parámetros por tipo
    def get_params(param_types):
        if isinstance(param_types, str):
            param_types = [param_types]
        return ClinicalParameter.objects.filter(
            organization=request.organization,
            parameter_type__in=param_types,
            is_active=True
        ).order_by('display_order', 'name')
    
    context = {
        'patient': patient,
        'doctors': doctors,
        'today': datetime.now().date(),
        
        # Medicamentos
        'medications': get_params(['medication', 'topical_medication', 'systemic_medication']),
        'topical_medications': get_params('topical_medication'),
        'systemic_medications': get_params('systemic_medication'),
        
        # Lentes Oftálmicos
        'lens_types': get_params('lens_type'),
        'lens_materials': get_params('lens_material'),
        'lens_coatings': get_params(['lens_coating', 'treatment']),
        'lens_brands': get_params('lens_brand'),
        'frame_types': get_params('frame_type'),
        
        # Lentes de Contacto
        'contact_lens_types': get_params('contact_lens_type'),
        'contact_lens_brands': get_params('contact_lens_brand'),
        'contact_lens_materials': get_params('contact_lens_material'),
        'contact_lens_wearings': get_params('contact_lens_wearing'),
        
        # Diagnósticos
        'diagnoses': get_params('diagnosis'),
        'diagnosis_categories': get_params('diagnosis_category'),
        
        # Tratamientos y Terapias
        'treatments': get_params('treatment'),
        'therapies': get_params('therapy'),
        'visual_therapies': get_params('visual_therapy'),
        
        # Exámenes
        'complementary_exams': get_params('complementary_exam'),
        'lab_tests': get_params('lab_test'),
        
        # Otros
        'recommendations': get_params('recommendation'),
        'referral_specialties': get_params('referral_specialty'),
        'follow_up_reasons': get_params('follow_up_reason'),
    }
    
    return render(request, 'dashboard/patients/visual_exam_form.html', context)


@login_required
def visual_exam_edit(request, patient_id, history_id):
    """Editar examen visual simplificado"""
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
            # Actualizar historia clínica
            history.date = request.POST.get('date')
            history.doctor_id = request.POST.get('doctor') if request.POST.get('doctor') else None
            
            # Cartillas utilizadas
            history.distance_chart = request.POST.get('distance_chart', '')
            history.near_chart = request.POST.get('near_chart', '')
            
            # Agudeza Visual - Lejos
            history.va_od_sc_distance = request.POST.get('va_od_sc_distance', '')
            history.va_od_cc_distance = request.POST.get('va_od_cc_distance', '')
            history.va_os_sc_distance = request.POST.get('va_os_sc_distance', '')
            history.va_os_cc_distance = request.POST.get('va_os_cc_distance', '')
            
            # Agudeza Visual - Cerca
            history.va_od_sc_near = request.POST.get('va_od_sc_near', '')
            history.va_od_cc_near = request.POST.get('va_od_cc_near', '')
            history.va_os_sc_near = request.POST.get('va_os_sc_near', '')
            history.va_os_cc_near = request.POST.get('va_os_cc_near', '')
            
            # Función para normalizar números (coma a punto)
            def normalize_number(value):
                if not value:
                    return None
                value = str(value).strip().replace(',', '.')
                return value if value else None
            
            # Refracción OD
            sphere_od = normalize_number(request.POST.get('refraction_od_sphere', ''))
            history.refraction_od_sphere = float(sphere_od) if sphere_od else None
            
            cyl_od = normalize_number(request.POST.get('refraction_od_cylinder', ''))
            history.refraction_od_cylinder = float(cyl_od) if cyl_od else None
            
            axis_od = request.POST.get('refraction_od_axis', '').strip()
            history.refraction_od_axis = int(axis_od) if axis_od else None
            
            add_od = normalize_number(request.POST.get('refraction_od_add', ''))
            history.refraction_od_add = float(add_od) if add_od else None
            
            prism_od = normalize_number(request.POST.get('refraction_od_prism', ''))
            history.refraction_od_prism = float(prism_od) if prism_od else None
            
            dnp_od = normalize_number(request.POST.get('refraction_od_dnp', ''))
            history.refraction_od_dnp = float(dnp_od) if dnp_od else None
            
            # Refracción OS
            sphere_os = normalize_number(request.POST.get('refraction_os_sphere', ''))
            history.refraction_os_sphere = float(sphere_os) if sphere_os else None
            
            cyl_os = normalize_number(request.POST.get('refraction_os_cylinder', ''))
            history.refraction_os_cylinder = float(cyl_os) if cyl_os else None
            
            axis_os = request.POST.get('refraction_os_axis', '').strip()
            history.refraction_os_axis = int(axis_os) if axis_os else None
            
            add_os = normalize_number(request.POST.get('refraction_os_add', ''))
            history.refraction_os_add = float(add_os) if add_os else None
            
            prism_os = normalize_number(request.POST.get('refraction_os_prism', ''))
            history.refraction_os_prism = float(prism_os) if prism_os else None
            
            dnp_os = normalize_number(request.POST.get('refraction_os_dnp', ''))
            history.refraction_os_dnp = float(dnp_os) if dnp_os else None
            
            # Distancia Pupilar
            pd_distance_val = normalize_number(request.POST.get('pd_distance', ''))
            history.pd_distance = float(pd_distance_val) if pd_distance_val else None
            
            pd_near_val = normalize_number(request.POST.get('pd_near', ''))
            history.pd_near = float(pd_near_val) if pd_near_val else None
            
            pd_od_val = normalize_number(request.POST.get('pd_od', ''))
            history.pd_od = float(pd_od_val) if pd_od_val else None
            
            pd_os_val = normalize_number(request.POST.get('pd_os', ''))
            history.pd_os = float(pd_os_val) if pd_os_val else None
            
            # Queratometría OD
            k1_od_val = normalize_number(request.POST.get('keratometry_od_k1', ''))
            history.keratometry_od_k1 = float(k1_od_val) if k1_od_val else None
            
            k2_od_val = normalize_number(request.POST.get('keratometry_od_k2', ''))
            history.keratometry_od_k2 = float(k2_od_val) if k2_od_val else None
            
            kaxis_od_val = request.POST.get('keratometry_od_axis', '').strip()
            history.keratometry_od_k1_axis = int(kaxis_od_val) if kaxis_od_val else None
            
            # Queratometría OS
            k1_os_val = normalize_number(request.POST.get('keratometry_os_k1', ''))
            history.keratometry_os_k1 = float(k1_os_val) if k1_os_val else None
            
            k2_os_val = normalize_number(request.POST.get('keratometry_os_k2', ''))
            history.keratometry_os_k2 = float(k2_os_val) if k2_os_val else None
            
            kaxis_os_val = request.POST.get('keratometry_os_axis', '').strip()
            history.keratometry_os_k1_axis = int(kaxis_os_val) if kaxis_os_val else None
            
            # ANAMNESIS
            history.chief_complaint = request.POST.get('chief_complaint', '')
            history.current_illness = request.POST.get('current_illness', '')
            
            # ANTECEDENTES GENERALES
            history.pathological_history = request.POST.get('pathological_history', '')
            history.pharmacological_history = request.POST.get('pharmacological_history', '')
            history.surgical_history = request.POST.get('surgical_history', '')
            history.allergic_history = request.POST.get('allergic_history', '')
            history.trauma_history = request.POST.get('trauma_history', '')
            history.other_general_history = request.POST.get('other_general_history', '')
            
            # ANTECEDENTES OCULARES
            history.ocular_pathological_history = request.POST.get('ocular_pathological_history', '')
            history.ocular_pharmacological_history = request.POST.get('ocular_pharmacological_history', '')
            history.ocular_surgical_history = request.POST.get('ocular_surgical_history', '')
            history.ocular_trauma_history = request.POST.get('ocular_trauma_history', '')
            history.previous_glasses = request.POST.get('previous_glasses') == 'on'
            history.previous_contact_lenses = request.POST.get('previous_contact_lenses') == 'on'
            history.ocular_therapeutic_history = request.POST.get('ocular_therapeutic_history', '')
            
            # ANTECEDENTES FAMILIARES - Generales
            history.family_diabetes = request.POST.get('family_diabetes') == 'on'
            history.family_hypertension = request.POST.get('family_hypertension') == 'on'
            history.family_heart_disease = request.POST.get('family_heart_disease') == 'on'
            history.family_cancer = request.POST.get('family_cancer') == 'on'
            history.family_general_notes = request.POST.get('family_general_notes', '')
            
            # ANTECEDENTES FAMILIARES - Oculares
            history.family_glaucoma = request.POST.get('family_glaucoma') == 'on'
            history.family_cataracts = request.POST.get('family_cataracts') == 'on'
            history.family_macular_degeneration = request.POST.get('family_macular_degeneration') == 'on'
            history.family_retinal_detachment = request.POST.get('family_retinal_detachment') == 'on'
            history.family_myopia = request.POST.get('family_myopia') == 'on'
            history.family_strabismus = request.POST.get('family_strabismus') == 'on'
            history.family_ocular_notes = request.POST.get('family_ocular_notes', '')
            
            # SEGMENTO ANTERIOR - OD
            history.biomicroscopy_od_lids = request.POST.get('biomicroscopy_od_lids', '')
            history.biomicroscopy_od_conjunctiva = request.POST.get('biomicroscopy_od_conjunctiva', '')
            history.biomicroscopy_od_cornea = request.POST.get('biomicroscopy_od_cornea', '')
            history.biomicroscopy_od_anterior_chamber = request.POST.get('biomicroscopy_od_anterior_chamber', '')
            history.biomicroscopy_od_iris = request.POST.get('biomicroscopy_od_iris', '')
            history.biomicroscopy_od_lens = request.POST.get('biomicroscopy_od_lens', '')
            history.biomicroscopy_od_pupil = request.POST.get('biomicroscopy_od_pupil', '')
            
            # SEGMENTO ANTERIOR - OS
            history.biomicroscopy_os_lids = request.POST.get('biomicroscopy_os_lids', '')
            history.biomicroscopy_os_conjunctiva = request.POST.get('biomicroscopy_os_conjunctiva', '')
            history.biomicroscopy_os_cornea = request.POST.get('biomicroscopy_os_cornea', '')
            history.biomicroscopy_os_anterior_chamber = request.POST.get('biomicroscopy_os_anterior_chamber', '')
            history.biomicroscopy_os_iris = request.POST.get('biomicroscopy_os_iris', '')
            history.biomicroscopy_os_lens = request.POST.get('biomicroscopy_os_lens', '')
            history.biomicroscopy_os_pupil = request.POST.get('biomicroscopy_os_pupil', '')
            
            # SEGMENTO POSTERIOR - OD
            history.fundoscopy_od_vitreous = request.POST.get('fundoscopy_od_vitreous', '')
            history.fundoscopy_od_optic_disc = request.POST.get('fundoscopy_od_optic_disc', '')
            history.fundoscopy_od_cup_disc_ratio = request.POST.get('fundoscopy_od_cup_disc_ratio', '')
            history.fundoscopy_od_macula = request.POST.get('fundoscopy_od_macula', '')
            history.fundoscopy_od_vessels = request.POST.get('fundoscopy_od_vessels', '')
            history.fundoscopy_od_retina = request.POST.get('fundoscopy_od_retina', '')
            
            # SEGMENTO POSTERIOR - OS
            history.fundoscopy_os_vitreous = request.POST.get('fundoscopy_os_vitreous', '')
            history.fundoscopy_os_optic_disc = request.POST.get('fundoscopy_os_optic_disc', '')
            history.fundoscopy_os_cup_disc_ratio = request.POST.get('fundoscopy_os_cup_disc_ratio', '')
            history.fundoscopy_os_macula = request.POST.get('fundoscopy_os_macula', '')
            history.fundoscopy_os_vessels = request.POST.get('fundoscopy_os_vessels', '')
            history.fundoscopy_os_retina = request.POST.get('fundoscopy_os_retina', '')
            
            # DIAGNÓSTICO - Checkboxes
            history.dx_myopia = request.POST.get('dx_myopia') == 'on'
            history.dx_hyperopia = request.POST.get('dx_hyperopia') == 'on'
            history.dx_astigmatism = request.POST.get('dx_astigmatism') == 'on'
            history.dx_presbyopia = request.POST.get('dx_presbyopia') == 'on'
            history.diagnosis = request.POST.get('diagnosis', '')
            
            # PRESCRIPCIÓN - Checkboxes
            history.prescription_glasses = request.POST.get('prescription_glasses') == 'on'
            history.prescription_contact_lenses = request.POST.get('prescription_contact_lenses') == 'on'
            history.prescription_medication = request.POST.get('prescription_medication') == 'on'
            
            # LENTES OFTÁLMICOS
            history.lens_type = request.POST.get('lens_type', '')
            history.lens_material = request.POST.get('lens_material', '')
            history.lens_coating = request.POST.get('lens_coating', '')
            history.lens_brand = request.POST.get('lens_brand', '')
            history.frame_type = request.POST.get('frame_type', '')
            
            # MEDICAMENTOS
            history.medication_details = request.POST.get('medication_details', '')
            
            # LENTES DE CONTACTO
            history.contact_lens_type = request.POST.get('contact_lens_type', '')
            history.contact_lens_brand = request.POST.get('contact_lens_brand', '')
            history.contact_lens_material = request.POST.get('contact_lens_material', '')
            history.contact_lens_wearing = request.POST.get('contact_lens_wearing', '')
            
            # TRATAMIENTOS Y TERAPIAS
            history.therapy = ', '.join(request.POST.getlist('therapy'))
            history.visual_therapy = ', '.join(request.POST.getlist('visual_therapy'))
            
            # EXÁMENES COMPLEMENTARIOS
            history.complementary_exam = ', '.join(request.POST.getlist('complementary_exam'))
            history.lab_test = ', '.join(request.POST.getlist('lab_test'))
            
            # RECOMENDACIONES Y SEGUIMIENTO
            history.recommendation = ', '.join(request.POST.getlist('recommendation'))
            history.follow_up_reason = request.POST.get('follow_up_reason', '')
            history.referral_specialty = request.POST.get('referral_specialty', '')
            history.treatment_plan = request.POST.get('treatment_plan', '')
            
            # OBSERVACIONES Y CONDUCTA
            history.observations = request.POST.get('exam_notes', '')
            history.recommendations_text = request.POST.get('recommendations_text', '')
            history.additional_notes = request.POST.get('additional_notes', '')
            
            history.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Examen visual actualizado exitosamente',
                'history_id': history.id
            })
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"ERROR COMPLETO: {error_details}")
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar el examen: {str(e)}',
                'details': error_details
            }, status=400)
    
    # GET - Mostrar formulario con datos
    # Obtener parámetros clínicos
    from apps.patients.models import ClinicalParameter
    
    # Función auxiliar para obtener parámetros por tipo
    def get_params(param_types):
        if isinstance(param_types, str):
            param_types = [param_types]
        return ClinicalParameter.objects.filter(
            organization=request.organization,
            parameter_type__in=param_types,
            is_active=True
        ).order_by('display_order', 'name')
    
    context = {
        'patient': patient,
        'doctors': doctors,
        'history': history,
        'today': datetime.now().date(),
        
        # Medicamentos
        'medications': get_params(['medication', 'topical_medication', 'systemic_medication']),
        'topical_medications': get_params('topical_medication'),
        'systemic_medications': get_params('systemic_medication'),
        
        # Lentes Oftálmicos
        'lens_types': get_params('lens_type'),
        'lens_materials': get_params('lens_material'),
        'lens_coatings': get_params(['lens_coating', 'treatment']),
        'lens_brands': get_params('lens_brand'),
        'frame_types': get_params('frame_type'),
        
        # Lentes de Contacto
        'contact_lens_types': get_params('contact_lens_type'),
        'contact_lens_brands': get_params('contact_lens_brand'),
        'contact_lens_materials': get_params('contact_lens_material'),
        'contact_lens_wearings': get_params('contact_lens_wearing'),
        
        # Diagnósticos
        'diagnoses': get_params('diagnosis'),
        'diagnosis_categories': get_params('diagnosis_category'),
        
        # Tratamientos y Terapias
        'treatments': get_params('treatment'),
        'therapies': get_params('therapy'),
        'visual_therapies': get_params('visual_therapy'),
        
        # Exámenes
        'complementary_exams': get_params('complementary_exam'),
        'lab_tests': get_params('lab_test'),
        
        # Otros
        'recommendations': get_params('recommendation'),
        'referral_specialties': get_params('referral_specialty'),
        'follow_up_reasons': get_params('follow_up_reason'),
    }
    
    return render(request, 'dashboard/patients/visual_exam_form.html', context)


@login_required
def visual_exam_detail(request, patient_id, history_id):
    """Ver detalle de examen visual"""
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    patient = get_object_or_404(Patient, id=patient_id, **org_filter)
    history = get_object_or_404(ClinicalHistory, id=history_id, patient=patient, **org_filter)
    
    context = {
        'patient': patient,
        'history': history,
    }
    
    return render(request, 'dashboard/patients/visual_exam_detail.html', context)


@login_required
def visual_exam_pdf(request, patient_id, history_id):
    """Generar PDF específico de fórmula de lentes ópticos"""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    patient = get_object_or_404(Patient, id=patient_id, **org_filter)
    history = get_object_or_404(ClinicalHistory, id=history_id, patient=patient, **org_filter)
    
    # Crear buffer para el PDF
    buffer = BytesIO()
    
    # Configurar documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.Color(0.1, 0.3, 0.5),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.Color(0.2, 0.2, 0.2),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=6
    )
    
    # Contenido del PDF
    story = []
    
    # ========== ENCABEZADO PROFESIONAL ==========
    # Crear tabla de encabezado con logo y datos de la óptica
    org_name = request.organization.name if hasattr(request, 'organization') and request.organization else 'Óptica'
    org_address = request.organization.address if hasattr(request, 'organization') and request.organization and request.organization.address else 'Dirección no especificada'
    org_phone = request.organization.phone if hasattr(request, 'organization') and request.organization and request.organization.phone else ''
    org_email = request.organization.email if hasattr(request, 'organization') and request.organization and request.organization.email else ''
    
    # Estilos para el encabezado
    header_org_style = ParagraphStyle(
        'HeaderOrg',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.Color(0.0, 0.2, 0.5),
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        leading=20
    )
    
    header_subtitle_style = ParagraphStyle(
        'HeaderSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.Color(0.2, 0.2, 0.2),
        fontName='Helvetica',
        alignment=TA_CENTER,
        leading=12
    )
    
    header_title_style = ParagraphStyle(
        'HeaderTitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.black,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        leading=16,
        spaceAfter=4
    )
    
    header_date_style = ParagraphStyle(
        'HeaderDate',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        fontName='Helvetica',
        alignment=TA_CENTER,
        leading=12
    )
    
    # Tabla del encabezado (3 columnas: Logo | Info Central | Código)
    from datetime import datetime
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    header_data = [
        [
            # Columna izquierda - Logo placeholder (puedes agregar imagen después)
            Paragraph('<para align="center"><b><font size="24" color="#003366">Ó</font></b></para>', header_org_style),
            # Columna central - Información principal
            [
                Paragraph(f'<b>{org_name}</b>', header_org_style),
                Paragraph('Credilentes Sede Paraísos' if 'Credilentes' in org_name else org_name, header_subtitle_style),
                Paragraph(f'<b>CRA.5 NLM 50-45</b>' if not org_address or org_address == 'Dirección no especificada' else org_address[:50], header_subtitle_style),
                Paragraph(f'Tel: L UNICA 3223159-8520 | Email: {org_email}' if org_email else f'Tel: {org_phone}' if org_phone else '', header_subtitle_style),
            ],
            # Columna derecha - Título del documento
            [
                Paragraph('<b>FÓRMULA DE LENTES</b>', header_title_style),
                Paragraph('<b>OFTÁLMICOS</b>', header_title_style),
                Spacer(1, 0.05*inch),
                Paragraph(current_date, header_date_style),
            ]
        ]
    ]
    
    header_table = Table(header_data, colWidths=[1.2*inch, 3.8*inch, 1.8*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Línea separadora
    line_separator = Table([['']], colWidths=[7*inch])
    line_separator.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 2, colors.Color(0.0, 0.2, 0.5)),
    ]))
    story.append(line_separator)
    story.append(Spacer(1, 0.15*inch))
    
    # Información del paciente
    patient_data = [
        ['Identificación:', f"{patient.identification}" if patient.identification else 'N/A', 'Edad:', f"{history.age_at_exam or patient.age} años" if hasattr(patient, 'age') or history.age_at_exam else 'N/A'],
        ['Nombre:', patient.full_name, 'Número de HC:', str(history.id)],
        ['Dirección:', patient.address[:40] if patient.address else 'N/A', 'Afiliación:', 'Particular'],
        ['Teléfono:', patient.phone_number or 'N/A', 'Edad:', f"{history.age_at_exam or 'N/A'} años"],
        ['', '', 'Relac:', 'S'],
    ]
    
    patient_table = Table(patient_data, colWidths=[1.3*inch, 2.5*inch, 1.2*inch, 2*inch])
    patient_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(patient_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Tabla de fórmula principal
    formula_data = [
        ['', 'ESFERA', 'CILINDRO', 'EJE', 'ADICIÓN', 'PRISMA BASE', 'GRADUADOS', 'AV LEJOS', 'AV CERCA'],
        [
            'OD',
            str(history.refraction_od_sphere) if history.refraction_od_sphere else 'N/A',
            str(history.refraction_od_cylinder) if history.refraction_od_cylinder else '',
            str(history.refraction_od_axis) + '°' if history.refraction_od_axis else '',
            '+' + str(history.refraction_od_add) if history.refraction_od_add else '',
            str(history.refraction_od_prism) if history.refraction_od_prism else '',
            str(history.refraction_od_dnp) if history.refraction_od_dnp else '20/20',
            str(history.va_od_cc_distance) if history.va_od_cc_distance else '20/20',
            str(history.va_od_cc_near) if history.va_od_cc_near else '0.75M',
        ],
        [
            'OI',
            str(history.refraction_os_sphere) if history.refraction_os_sphere else 'N/A',
            str(history.refraction_os_cylinder) if history.refraction_os_cylinder else '',
            str(history.refraction_os_axis) + '°' if history.refraction_os_axis else '',
            '+' + str(history.refraction_os_add) if history.refraction_os_add else '',
            str(history.refraction_os_prism) if history.refraction_os_prism else '',
            str(history.refraction_os_dnp) if history.refraction_os_dnp else '20/20',
            str(history.va_os_cc_distance) if history.va_os_cc_distance else '20/20',
            str(history.va_os_cc_near) if history.va_os_cc_near else '0.75M',
        ]
    ]
    
    formula_table = Table(formula_data, colWidths=[0.5*inch, 0.75*inch, 0.75*inch, 0.6*inch, 0.75*inch, 0.9*inch, 0.9*inch, 0.75*inch, 0.75*inch])
    formula_table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.4, 0.6)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        # Filas de datos
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        # Bordes
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LINEABOVE', (0, 0), (-1, 0), 2, colors.Color(0.2, 0.4, 0.6)),
        ('LINEBELOW', (0, -1), (-1, -1), 2, colors.Color(0.2, 0.4, 0.6)),
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(formula_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Detalles adicionales
    details_data = [
        ['Tipo Lentes:', history.lens_type or '-', 'Detalle:', 'AR'],
        ['Color y Tins:', history.lens_material or '-', 'Dip:', f"{history.pd_distance or 'N/A'} / {history.pd_near or 'N/A'}"],
    ]
    
    # Agregar distancia pupilar si existe
    if history.pd_distance or history.pd_near:
        details_data.append(['Distancia Pupilar (mm):', f"Lejos: {history.pd_distance or 'N/A'} mm  |  Cerca: {history.pd_near or 'N/A'} mm", 'Altura:', f"OD: {history.pd_od or 'N/A'} / OI: {history.pd_os or 'N/A'}"])
    
    details_data.append(['Uso Dispositivo:', 'Permanente', 'Control:', '1 año'])
    
    details_table = Table(details_data, colWidths=[1.5*inch, 2.5*inch, 1.2*inch, 1.8*inch])
    details_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(details_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Observaciones
    if history.optical_prescription_notes or history.lens_coating:
        story.append(Paragraph("Observaciones:", heading_style))
        obs_text = ""
        if history.lens_coating:
            obs_text += f"<b>Tratamientos:</b> {history.lens_coating}. "
        if history.lens_brand:
            obs_text += f"<b>Marca:</b> {history.lens_brand}. "
        if history.frame_type:
            obs_text += f"<b>Montura:</b> {history.frame_type}. "
        if history.optical_prescription_notes:
            obs_text += f"{history.optical_prescription_notes}"
        
        story.append(Paragraph(obs_text or "Ninguna", normal_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Advertencia
    warning_style = ParagraphStyle(
        'Warning',
        parent=normal_style,
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.Color(0.3, 0.3, 0.3),
        borderWidth=1,
        borderColor=colors.grey,
        borderPadding=8
    )
    story.append(Paragraph("NO SE DA GARANTÍA POR LENTES ADQUIRIDOS EN OTRA ÓPTICA", warning_style))
    story.append(Spacer(1, 0.4*inch))
    
    # Pie de página con información del optómetra
    footer_data = [
        ['Optómetra:', history.doctor.full_name if history.doctor else 'N/A', 'Rep Médico:', ''],
        ['', '', '', ''],
        ['_' * 40, '', '_' * 40, ''],
        ['Firma del Optómetra', '', 'Firma del Paciente', ''],
    ]
    
    if history.doctor and history.doctor.professional_card:
        footer_data[0][3] = history.doctor.professional_card
    
    footer_table = Table(footer_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    footer_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 2), (-1, 3), 'CENTER'),
        ('FONTSIZE', (0, 3), (-1, 3), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(footer_table)
    
    # Construir PDF
    doc.build(story)
    
    # Retornar respuesta
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="formula_lentes_{patient.full_name.replace(" ", "_")}_{history.date}.pdf"'
    
    return response
