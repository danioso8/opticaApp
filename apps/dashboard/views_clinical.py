"""
Vistas para Historia Clínica Oftalmológica
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime

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
