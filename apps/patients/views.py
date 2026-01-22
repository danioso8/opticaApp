from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Prefetch
from django.core.paginator import Paginator
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from datetime import datetime

from .models import Patient
from apps.appointments.models import Appointment


def patient_list(request):
    """Lista de pacientes con búsqueda y filtros - OPTIMIZADO con cache"""
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    
    # Generar cache key
    search = request.GET.get('search', '')
    order_by = request.GET.get('order', '-created_at')
    page_number = request.GET.get('page', '1')
    org_id = getattr(request, 'tenant_id', 'no_org')
    
    cache_key = f"patients_list:{org_id}:{search}:{order_by}:{page_number}"
    
    # Intentar obtener del cache
    cached_data = cache.get(cache_key)
    if cached_data and not search:  # No cachear búsquedas para tener datos frescos
        return render(request, 'patients/patient_list.html', cached_data)
    
    # Optimizar query con only (solo campos necesarios)
    patients = Patient.objects.filter(is_active=True, **org_filter).only(
        'id', 'full_name', 'phone_number', 'identification', 'email', 
        'created_at', 'date_of_birth'
    )
    
    # Búsqueda
    if search:
        patients = patients.filter(
            Q(full_name__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(identification__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Estadísticas (cachear separadamente)
    stats_cache_key = f"patient_stats:{org_id}"
    stats = cache.get(stats_cache_key)
    
    if stats is None:
        total_patients = Patient.objects.filter(is_active=True, **org_filter).count()
        patients_with_appointments = Patient.objects.filter(
            is_active=True, **org_filter
        ).annotate(
            appointment_count=Count('appointments')
        ).filter(appointment_count__gt=0).count()
        
        stats = {
            'total_patients': total_patients,
            'patients_with_appointments': patients_with_appointments
        }
        cache.set(stats_cache_key, stats, 300)  # 5 minutos
    
    # Ordenar
    patients = patients.order_by(order_by)
    
    # Paginación
    paginator = Paginator(patients, 20)
    page_obj = paginator.get_page(page_number)
    
    # Prefetch última historia clínica (1 query en lugar de N queries)
    from apps.patients.models_clinical import ClinicalHistory
    patient_ids = [p.id for p in page_obj]
    latest_histories = {}
    
    if patient_ids:
        histories = ClinicalHistory.objects.filter(
            patient_id__in=patient_ids
        ).order_by('patient_id', '-created_at').distinct('patient_id')
        
        for history in histories:
            latest_histories[history.patient_id] = history
    
    for patient in page_obj:
        patient.latest_history = latest_histories.get(patient.id)
    
    context = {
        'patients': page_obj,
        'total_patients': stats['total_patients'],
        'patients_with_appointments': stats['patients_with_appointments'],
        'search': search,
        'order_by': order_by,
    }
    
    return render(request, 'dashboard/patients/list.html', context)


def patient_detail(request, pk):
    """Detalle de un paciente"""
    from apps.patients.models import Doctor
    
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    patient = get_object_or_404(Patient, pk=pk, **org_filter)
    
    # Citas del paciente
    appointments = patient.appointments.all().order_by('-appointment_date', '-appointment_time')
    
    # Estadísticas
    total_appointments = appointments.count()
    completed_appointments = appointments.filter(status='completed').count()
    cancelled_appointments = appointments.filter(status='cancelled').count()
    upcoming_appointments = appointments.filter(
        status__in=['pending', 'confirmed']
    ).order_by('appointment_date', 'appointment_time')[:5]
    
    # Obtener doctores de la organización
    doctors = Doctor.objects.filter(**org_filter, is_active=True).order_by('full_name')
    
    context = {
        'patient': patient,
        'appointments': appointments[:10],  # Últimas 10
        'upcoming_appointments': upcoming_appointments,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'doctors': doctors,
    }
    
    return render(request, 'dashboard/patients/detail.html', context)


def patient_create(request):
    """Crear nuevo paciente"""
    if request.method == 'POST':
        try:
            # Validar organización
            if not hasattr(request, 'organization') or not request.organization:
                messages.error(request, 'No hay organización activa')
                return redirect('dashboard:patients_list')
            
            # Crear paciente
            patient = Patient.objects.create(
                organization=request.organization,
                full_name=request.POST.get('full_name'),
                identification=request.POST.get('identification') or None,
                date_of_birth=request.POST.get('date_of_birth') or None,
                gender=request.POST.get('gender', ''),
                phone_number=request.POST.get('phone_number'),
                email=request.POST.get('email', ''),
                address=request.POST.get('address', ''),
                allergies=request.POST.get('allergies', ''),
                medical_conditions=request.POST.get('medical_conditions', ''),
                current_medications=request.POST.get('current_medications', ''),
            )
            
            # Registrar en auditoría
            from apps.dashboard.audit_utils import log_action
            log_action(
                user=request.user,
                organization=request.organization,
                action='patient_create',
                description=f'Creó el paciente: {patient.full_name}',
                content_type='Patient',
                object_id=patient.pk,
                request=request
            )
            
            messages.success(request, f'Paciente {patient.full_name} creado exitosamente')
            return redirect('dashboard:patient_detail', pk=patient.pk)
        
        except Exception as e:
            messages.error(request, f'Error al crear paciente: {str(e)}')
    
    context = {
        'gender_choices': Patient.GENDER_CHOICES,
    }
    
    return render(request, 'dashboard/patients/create.html', context)


def patient_edit(request, pk):
    """Editar paciente"""
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    patient = get_object_or_404(Patient, pk=pk, **org_filter)
    
    if request.method == 'POST':
        try:
            patient.full_name = request.POST.get('full_name')
            patient.identification = request.POST.get('identification') or None
            
            date_of_birth = request.POST.get('date_of_birth')
            if date_of_birth:
                patient.date_of_birth = date_of_birth
            else:
                patient.date_of_birth = None
            
            patient.gender = request.POST.get('gender', '')
            patient.phone_number = request.POST.get('phone_number')
            patient.email = request.POST.get('email', '')
            patient.address = request.POST.get('address', '')
            patient.allergies = request.POST.get('allergies', '')
            patient.medical_conditions = request.POST.get('medical_conditions', '')
            patient.current_medications = request.POST.get('current_medications', '')
            
            patient.save()
            
            # Registrar en auditoría
            from apps.dashboard.audit_utils import log_action
            log_action(
                user=request.user,
                organization=request.organization,
                action='patient_edit',
                description=f'Editó el paciente: {patient.full_name}',
                content_type='Patient',
                object_id=patient.pk,
                request=request
            )
            
            messages.success(request, f'Paciente {patient.full_name} actualizado exitosamente')
            return redirect('dashboard:patient_detail', pk=patient.pk)
        
        except Exception as e:
            messages.error(request, f'Error al actualizar paciente: {str(e)}')
    
    context = {
        'patient': patient,
        'gender_choices': Patient.GENDER_CHOICES,
    }
    
    return render(request, 'dashboard/patients/edit.html', context)


def patient_delete(request, pk):
    """Eliminar (desactivar) paciente"""
    if request.method == 'POST':
        org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
        patient = get_object_or_404(Patient, pk=pk, **org_filter)
        
        # Desactivar en lugar de eliminar
        patient.is_active = False
        patient.save()
        
        # Registrar en auditoría
        from apps.dashboard.audit_utils import log_action
        log_action(
            user=request.user,
            organization=request.organization,
            action='patient_delete',
            description=f'Desactivó el paciente: {patient.full_name}',
            content_type='Patient',
            object_id=patient.pk,
            request=request
        )
        
        messages.success(request, f'Paciente {patient.full_name} desactivado')
        return redirect('dashboard:patients_list')
    
    return redirect('dashboard:patients_list')


def patient_search_api(request):
    """API para búsqueda de pacientes (AJAX)"""
    query = request.GET.get('q', '')
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    patients = Patient.objects.filter(
        Q(full_name__icontains=query) |
        Q(phone_number__icontains=query) |
        Q(identification__icontains=query),
        is_active=True,
        **org_filter
    )[:10]
    
    results = [{
        'id': p.id,
        'full_name': p.full_name,
        'phone_number': p.phone_number,
        'identification': p.identification or '',
        'age': p.age or '',
    } for p in patients]
    
    return JsonResponse({'results': results})
