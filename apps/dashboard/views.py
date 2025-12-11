from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta

# Importar vistas de historia clínica
from .views_clinical import (
    clinical_history_list,
    clinical_history_create,
    clinical_history_detail,
    # clinical_history_edit,  # Deshabilitado - Las historias clínicas son documentos permanentes
    # clinical_history_delete,  # Deshabilitado - Las historias clínicas son documentos permanentes
    clinical_history_pdf,
    latest_fundoscopy,
    visual_exam_create,
    visual_exam_edit,
    visual_exam_detail,
    visual_exam_pdf,
    visual_exam_delete
)

from apps.appointments.models import (
    Appointment,
    AppointmentConfiguration,
    WorkingHours,
    BlockedDate
)
from apps.patients.models import Patient
from apps.sales.models import Sale
from apps.appointments.utils import (
    get_available_slots_for_date,
    get_appointments_stats
)
from apps.appointments.signals import (
    notify_appointment_updated,
    notify_system_toggled
)
from apps.patients.views import (
    patient_list as patients_list_view,
    patient_detail as patient_detail_view,
    patient_create,
    patient_edit,
    patient_delete,
    patient_search_api
)


# ==================== WHATSAPP STATUS ====================

def check_whatsapp_status():
    """Verifica el estado del bot de WhatsApp"""
    from django.conf import settings
    import requests
    
    api_url = getattr(settings, 'WHATSAPP_API_URL', 'http://localhost:3000')
    
    try:
        response = requests.get(f'{api_url}/health', timeout=2)
        if response.status_code == 200:
            data = response.json()
            return {
                'server_running': True,
                'connected': data.get('connected', False),
                'api_url': api_url
            }
    except:
        pass
    
    return {
        'server_running': False,
        'connected': False,
        'api_url': api_url
    }


# ==================== AUTENTICACIÓN ====================

def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        next_url = request.GET.get('next', 'dashboard:home')
        if next_url.startswith('/'):
            return redirect(next_url)
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or request.GET.get('next', '')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.username}!')
            
            # Redirigir al next URL si existe
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            
            # Redirigir a la lista de organizaciones para que seleccione una
            return redirect('organizations:list')
        else:
            messages.error(request, 'Credenciales inválidas')
    
    return render(request, 'dashboard/login.html')


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.info(request, 'Sesión cerrada')
    return redirect('dashboard:login')


@login_required
def user_profile(request):
    """Vista de perfil del usuario"""
    if request.method == 'POST':
        # Actualizar información del usuario
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        
        try:
            user.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('dashboard:user_profile')
        except Exception as e:
            messages.error(request, f'Error al actualizar el perfil: {str(e)}')
    
    return render(request, 'dashboard/user/profile.html', {
        'user': request.user
    })


@login_required
def user_security(request):
    """Vista de seguridad del usuario"""
    from django.contrib.auth import update_session_auth_hash
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validar contraseña actual
        if not request.user.check_password(current_password):
            messages.error(request, 'La contraseña actual es incorrecta')
            return redirect('dashboard:user_security')
        
        # Validar que las contraseñas coincidan
        if new_password != confirm_password:
            messages.error(request, 'Las contraseñas nuevas no coinciden')
            return redirect('dashboard:user_security')
        
        # Validar longitud mínima
        if len(new_password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres')
            return redirect('dashboard:user_security')
        
        # Actualizar contraseña
        try:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Mantener la sesión activa
            messages.success(request, 'Contraseña actualizada correctamente')
            return redirect('dashboard:user_security')
        except Exception as e:
            messages.error(request, f'Error al actualizar la contraseña: {str(e)}')
    
    return render(request, 'dashboard/user/security.html')


# ==================== DASHBOARD PRINCIPAL ====================

@login_required
def dashboard_home(request):
    """Página principal del dashboard"""
    # Verificar si hay una organización seleccionada
    if not hasattr(request, 'organization') or not request.organization:
        messages.info(request, 'Por favor selecciona una empresa para comenzar')
        return redirect('organizations:list')
    
    today = timezone.now().date()
    
    # Filtrar por organización si existe
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    
    # Estadísticas del día
    today_appointments = Appointment.objects.filter(appointment_date=today, **org_filter)
    
    # Estadísticas de ventas
    today_sales = Sale.objects.filter(created_at__date=today, status='completed', **org_filter)
    today_revenue = sum(sale.total for sale in today_sales)
    month_sales = Sale.objects.filter(created_at__date__year=today.year, created_at__date__month=today.month, status='completed', **org_filter)
    month_revenue = sum(sale.total for sale in month_sales)
    
    stats = {
        'today': {
            'total': today_appointments.count(),
            'pending': today_appointments.filter(status='pending').count(),
            'confirmed': today_appointments.filter(status='confirmed').count(),
            'completed': today_appointments.filter(status='completed').count(),
            'cancelled': today_appointments.filter(status='cancelled').count(),
        },
        'sales': {
            'today_count': today_sales.count(),
            'today_revenue': today_revenue,
            'month_count': month_sales.count(),
            'month_revenue': month_revenue,
        },
        'total_patients': Patient.objects.filter(is_active=True, **org_filter).count(),
        'system_open': AppointmentConfiguration.get_config(request.organization).is_open if request.organization else True,
        'whatsapp': check_whatsapp_status(),
    }
    
    # Próximas citas (siguientes 5)
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=today,
        **org_filter
    ).exclude(status__in=['cancelled', 'completed']).order_by('appointment_date', 'appointment_time')[:5]
    
    context = {
        'stats': stats,
        'upcoming_appointments': upcoming_appointments,
        'today': today,
    }
    
    return render(request, 'dashboard/home.html', context)


# ==================== GESTIÓN DE CITAS ====================

@login_required
def appointments_list(request):
    """Vista unificada: Citas de hoy y todas las citas con filtros"""
    today = timezone.now().date()
    
    # Filtrar por organización
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    
    # Citas de hoy
    today_appointments = Appointment.objects.filter(
        appointment_date=today,
        **org_filter
    ).select_related('patient', 'attended_by').order_by('appointment_time')
    
    # Todas las citas con filtros
    all_appointments = Appointment.objects.filter(**org_filter).select_related('patient', 'attended_by')
    
    # Aplicar filtros
    status_filter = request.GET.get('status')
    date_filter = request.GET.get('date')
    search = request.GET.get('search')
    
    if status_filter:
        all_appointments = all_appointments.filter(status=status_filter)
    
    if date_filter:
        all_appointments = all_appointments.filter(appointment_date=date_filter)
    
    if search:
        all_appointments = all_appointments.filter(
            Q(full_name__icontains=search) |
            Q(phone_number__icontains=search)
        )
    
    all_appointments = all_appointments.order_by('-appointment_date', '-appointment_time')
    
    # Estadísticas
    stats = get_appointments_stats()
    
    context = {
        'today_appointments': today_appointments,
        'all_appointments': all_appointments,
        'status_choices': Appointment.STATUS_CHOICES,
        'today': today,
        'stats': stats,
    }
    
    return render(request, 'dashboard/appointments/index.html', context)


@login_required
def appointments_today(request):
    """Citas del día en tiempo real"""
    today = timezone.now().date()
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    appointments = Appointment.objects.filter(
        appointment_date=today,
        **org_filter
    ).select_related('patient', 'attended_by').order_by('appointment_time')
    
    stats = get_appointments_stats()
    
    context = {
        'appointments': appointments,
        'stats': stats,
        'today': today,
    }
    
    return render(request, 'dashboard/appointments/today.html', context)


@login_required
def appointment_detail(request, pk):
    """Detalle de una cita"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'dashboard/appointments/detail.html', context)


@login_required
def appointment_change_status(request, pk):
    """Cambiar estado de una cita (AJAX)"""
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(Appointment.STATUS_CHOICES):
            appointment.status = new_status
            
            if new_status == 'completed':
                appointment.attended_by = request.user
            
            appointment.save()
            
            # Notificar cambio en tiempo real
            notify_appointment_updated(appointment)
            
            # Enviar notificación si se cancela la cita (WhatsApp/Email según entorno)
            if new_status == 'cancelled':
                try:
                    from apps.appointments.notifications import notify_appointment_cancelled
                    notify_appointment_cancelled(appointment)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error al enviar notificación de cancelación: {e}")
            
            return JsonResponse({
                'success': True,
                'message': f'Estado cambiado a {appointment.get_status_display()}'
            })
        
        return JsonResponse({
            'success': False,
            'message': 'Estado inválido'
        }, status=400)
    
    return JsonResponse({'success': False}, status=405)


# ==================== CONFIGURACIÓN ====================

@login_required
def configuration(request):
    """Vista de configuración del sistema"""
    from apps.appointments.models import SpecificDateSchedule
    from django.contrib.auth.models import Group
    
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    
    config = AppointmentConfiguration.get_config(request.organization) if request.organization else None
    working_hours = WorkingHours.objects.filter(**org_filter).order_by('day_of_week', 'start_time')
    blocked_dates = BlockedDate.objects.filter(date__gte=timezone.now().date(), **org_filter).order_by('date')
    specific_schedules = SpecificDateSchedule.objects.filter(date__gte=timezone.now().date(), **org_filter).order_by('date', 'start_time')
    
    # Obtener doctores del modelo Doctor
    from apps.patients.models import Doctor
    
    doctors_queryset = Doctor.objects.filter(is_active=True)
    
    # Filtrar por organización si existe
    if request.organization:
        doctors_queryset = doctors_queryset.filter(organization=request.organization)
    
    # Crear objetos pseudo-member para compatibilidad con el template
    class PseudoMember:
        def __init__(self, doctor):
            # Crear un objeto user falso con los datos del doctor
            self.user = type('obj', (object,), {
                'id': doctor.id,
                'first_name': doctor.full_name.split()[0] if doctor.full_name else '',
                'last_name': ' '.join(doctor.full_name.split()[1:]) if len(doctor.full_name.split()) > 1 else '',
                'username': doctor.full_name,
                'get_full_name': lambda: doctor.full_name
            })()
    
    doctors = [PseudoMember(doc) for doc in doctors_queryset]
    
    # Enriquecer specific_schedules con objetos Doctor
    doctors_dict = {doc.id: doc for doc in doctors_queryset}
    for schedule in specific_schedules:
        if schedule.doctor_id:
            schedule.doctor_obj = doctors_dict.get(schedule.doctor_id)
    
    context = {
        'config': config,
        'working_hours': working_hours,
        'blocked_dates': blocked_dates,
        'specific_schedules': specific_schedules,
        'doctors': doctors,
    }
    
    return render(request, 'dashboard/configuration.html', context)


@login_required
def update_general_config(request):
    """Actualizar configuración general (AJAX)"""
    if request.method == 'POST':
        if not request.organization:
            return JsonResponse({'success': False, 'message': 'No hay organización activa'}, status=400)
        
        try:
            config = AppointmentConfiguration.get_config(request.organization)
            
            # Actualizar campos
            slot_duration = request.POST.get('slot_duration')
            max_daily_appointments = request.POST.get('max_daily_appointments')
            advance_booking_days = request.POST.get('advance_booking_days')
            
            if slot_duration:
                config.slot_duration = int(slot_duration)
            if max_daily_appointments:
                config.max_daily_appointments = int(max_daily_appointments)
            if advance_booking_days:
                config.advance_booking_days = int(advance_booking_days)
            
            config.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Configuración actualizada correctamente'
            })
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Valores inválidos. Por favor ingresa números válidos.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False}, status=405)


@login_required
def toggle_system(request):
    """Abrir/Cerrar sistema de agendamiento (AJAX)"""
    if request.method == 'POST':
        if not request.organization:
            return JsonResponse({'success': False, 'message': 'No hay organización activa'}, status=400)
        
        config = AppointmentConfiguration.get_config(request.organization)
        config.is_open = not config.is_open
        config.save()
        
        # Notificar cambio en tiempo real
        notify_system_toggled(config.is_open)
        
        return JsonResponse({
            'success': True,
            'is_open': config.is_open,
            'message': f'Sistema {"abierto" if config.is_open else "cerrado"}'
        })
    
    return JsonResponse({'success': False}, status=405)


@login_required
def block_date(request):
    """Bloquear una fecha (AJAX)"""
    if request.method == 'POST':
        date_str = request.POST.get('date')
        reason = request.POST.get('reason', 'Bloqueado por administrador')
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            if not request.organization:
                return JsonResponse({'success': False, 'message': 'No hay organización activa'}, status=400)
            
            blocked, created = BlockedDate.objects.get_or_create(
                date=date,
                organization=request.organization,
                defaults={
                    'reason': reason,
                    'created_by': request.user
                }
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Fecha bloqueada' if created else 'Esta fecha ya estaba bloqueada'
            })
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de fecha inválido'
            }, status=400)
    
    return JsonResponse({'success': False}, status=405)


# ==================== PACIENTES ====================
# Las vistas de pacientes están importadas desde apps.patients.views

patients_list = patients_list_view
patient_detail = patient_detail_view


# ==================== CALENDARIO ====================

@login_required
def calendar_view(request):
    """Vista de calendario"""
    today = timezone.now().date()
    
    # Obtener mes actual o el solicitado
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    
    # Generar días del mes
    from calendar import monthrange
    days_in_month = monthrange(year, month)[1]
    
    # Obtener todas las citas del mes
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    appointments = Appointment.objects.filter(
        appointment_date__year=year,
        appointment_date__month=month,
        **org_filter
    ).values('appointment_date').annotate(count=Count('id'))
    
    appointments_dict = {item['appointment_date']: item['count'] for item in appointments}
    
    context = {
        'year': year,
        'month': month,
        'today': today,
        'days_in_month': days_in_month,
        'appointments': appointments_dict,
    }
    
    return render(request, 'dashboard/calendar.html', context)


@login_required
def patient_edit(request, pk):
    """Editar paciente (AJAX)"""
    if request.method == 'POST':
        org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
        patient = get_object_or_404(Patient, pk=pk, **org_filter)
        
        try:
            patient.full_name = request.POST.get('full_name')
            patient.identification_type = request.POST.get('identification_type', 'CC')
            patient.identification = request.POST.get('identification', '')
            patient.date_of_birth = request.POST.get('date_of_birth') or None
            patient.gender = request.POST.get('gender', '')
            patient.phone_number = request.POST.get('phone_number')
            patient.email = request.POST.get('email', '')
            patient.address = request.POST.get('address', '')
            patient.allergies = request.POST.get('allergies', '')
            patient.medical_conditions = request.POST.get('medical_conditions', '')
            patient.current_medications = request.POST.get('current_medications', '')
            # Datos adicionales de óptica
            patient.occupation = request.POST.get('occupation', '')
            patient.residence_area = request.POST.get('residence_area', '')
            patient.business_name = request.POST.get('business_name', '')
            patient.business_address = request.POST.get('business_address', '')
            patient.business_phone = request.POST.get('business_phone', '')
            patient.business_type = request.POST.get('business_type', '')
            patient.civil_status = request.POST.get('civil_status', '')
            patient.bank_entity = request.POST.get('bank_entity', '')
            patient.account_number = request.POST.get('account_number', '')
            patient.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Paciente {patient.full_name} actualizado exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar paciente: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


@login_required
def patient_delete(request, pk):
    """Eliminar paciente (AJAX)"""
    if request.method == 'POST':
        org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
        patient = get_object_or_404(Patient, pk=pk, **org_filter)
        
        try:
            patient_name = patient.full_name
            patient.is_active = False
            patient.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Paciente {patient_name} desactivado exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al desactivar paciente: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


@login_required
def patient_search_api(request):
    """API para buscar pacientes (para autocomplete y edición)"""
    query = request.GET.get('q', '')
    patient_id = request.GET.get('id', '')
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    
    # Búsqueda por ID (para editar)
    if patient_id:
        try:
            patient = Patient.objects.get(id=patient_id, is_active=True, **org_filter)
            patient_data = {
                'id': patient.id,
                'full_name': patient.full_name,
                'identification': patient.identification or '',
                'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else '',
                'gender': patient.gender or '',
                'phone_number': patient.phone_number,
                'email': patient.email or '',
                'address': patient.address or '',
                'allergies': patient.allergies or '',
                'medical_conditions': patient.medical_conditions or '',
                'current_medications': patient.current_medications or '',
                'occupation': patient.occupation or '',
                'residence_area': patient.residence_area or '',
                'business_name': patient.business_name or '',
                'business_address': patient.business_address or '',
                'business_phone': patient.business_phone or '',
                'business_type': patient.business_type or '',
                'civil_status': patient.civil_status or '',
                'bank_entity': patient.bank_entity or '',
                'account_number': patient.account_number or ''
            }
            return JsonResponse({'patients': [patient_data]})
        except Patient.DoesNotExist:
            return JsonResponse({'patients': []})
    
    # Búsqueda por texto (autocomplete)
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    patients = Patient.objects.filter(
        is_active=True,
        **org_filter
    ).filter(
        Q(full_name__icontains=query) |
        Q(phone_number__icontains=query) |
        Q(identification__icontains=query)
    )[:10]
    
    results = [{
        'id': p.id,
        'name': p.full_name,
        'phone': p.phone_number,
        'identification': p.identification or 'N/A'
    } for p in patients]
    
    return JsonResponse({'results': results})


# ==================== GESTIÓN DE PACIENTES (CRUD) ====================

@login_required
def patient_create(request):
    """Crear nuevo paciente (AJAX)"""
    if request.method == 'POST':
        # Debug log
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"DEBUG patient_create - User: {request.user.username}, Organization: {getattr(request, 'organization', 'NOT SET')}")
        
        # Verificar organización
        organization = getattr(request, 'organization', None)
        if not organization:
            # Si no hay organización en el request, obtener la organización por defecto
            from apps.organizations.models import Organization
            organization = Organization.objects.filter(is_active=True).first()
            logger.error(f"DEBUG - Fallback organization: {organization}")
            if not organization:
                return JsonResponse({
                    'success': False, 
                    'message': 'No hay organización configurada. Por favor contacta al administrador.'
                }, status=400)
        
        try:
            # Validar si ya existe un paciente con esa identificación
            identification = request.POST.get('identification', '').strip()
            existing = None
            
            if identification:
                existing = Patient.objects.filter(
                    organization=organization,
                    identification=identification
                ).first()
                
                if existing and existing.is_active:
                    # Si existe y está activo, no permitir duplicado
                    return JsonResponse({
                        'success': False,
                        'message': f'Ya existe un paciente activo con la identificación {identification}. Nombre: {existing.full_name}',
                        'patient_id': existing.id
                    }, status=400)
                elif existing and not existing.is_active:
                    # Si existe pero está inactivo, reactivarlo y actualizar datos
                    existing.is_active = True
                    existing.full_name = request.POST.get('full_name')
                    existing.identification_type = request.POST.get('identification_type', 'CC')
                    existing.date_of_birth = request.POST.get('date_of_birth') or None
                    existing.gender = request.POST.get('gender', '')
                    existing.phone_number = request.POST.get('phone_number')
                    existing.email = request.POST.get('email', '')
                    existing.address = request.POST.get('address', '')
                    existing.allergies = request.POST.get('allergies', '')
                    existing.medical_conditions = request.POST.get('medical_conditions', '')
                    existing.current_medications = request.POST.get('current_medications', '')
                    existing.occupation = request.POST.get('occupation', '')
                    existing.residence_area = request.POST.get('residence_area', '')
                    existing.business_name = request.POST.get('business_name', '')
                    existing.business_address = request.POST.get('business_address', '')
                    existing.business_phone = request.POST.get('business_phone', '')
                    existing.business_type = request.POST.get('business_type', '')
                    existing.civil_status = request.POST.get('civil_status', '')
                    existing.bank_entity = request.POST.get('bank_entity', '')
                    existing.account_number = request.POST.get('account_number', '')
                    existing.save()
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Paciente {existing.full_name} reactivado exitosamente',
                        'patient_id': existing.id,
                        'patient_name': existing.full_name,
                        'reactivated': True
                    })
            
            patient = Patient.objects.create(
                organization=organization,
                full_name=request.POST.get('full_name'),
                identification_type=request.POST.get('identification_type', 'CC'),
                identification=identification,
                date_of_birth=request.POST.get('date_of_birth') or None,
                gender=request.POST.get('gender', ''),
                phone_number=request.POST.get('phone_number'),
                email=request.POST.get('email', ''),
                address=request.POST.get('address', ''),
                allergies=request.POST.get('allergies', ''),
                medical_conditions=request.POST.get('medical_conditions', ''),
                current_medications=request.POST.get('current_medications', ''),
                # Datos adicionales de óptica
                occupation=request.POST.get('occupation', ''),
                residence_area=request.POST.get('residence_area', ''),
                business_name=request.POST.get('business_name', ''),
                business_address=request.POST.get('business_address', ''),
                business_phone=request.POST.get('business_phone', ''),
                business_type=request.POST.get('business_type', ''),
                civil_status=request.POST.get('civil_status', ''),
                bank_entity=request.POST.get('bank_entity', ''),
                account_number=request.POST.get('account_number', '')
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Paciente {patient.full_name} creado exitosamente',
                'patient_id': patient.id,
                'patient_name': patient.full_name
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al crear paciente: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


@login_required
def patient_edit(request, pk):
    """Editar paciente (AJAX)"""
    if request.method == 'POST':
        org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
        patient = get_object_or_404(Patient, pk=pk, **org_filter)
        
        try:
            patient.full_name = request.POST.get('full_name')
            patient.identification_type = request.POST.get('identification_type', 'CC')
            patient.identification = request.POST.get('identification', '')
            patient.date_of_birth = request.POST.get('date_of_birth') or None
            patient.gender = request.POST.get('gender', '')
            patient.phone_number = request.POST.get('phone_number')
            patient.email = request.POST.get('email', '')
            patient.address = request.POST.get('address', '')
            patient.allergies = request.POST.get('allergies', '')
            patient.medical_conditions = request.POST.get('medical_conditions', '')
            patient.current_medications = request.POST.get('current_medications', '')
            # Datos adicionales de óptica
            patient.occupation = request.POST.get('occupation', '')
            patient.residence_area = request.POST.get('residence_area', '')
            patient.business_name = request.POST.get('business_name', '')
            patient.business_address = request.POST.get('business_address', '')
            patient.business_phone = request.POST.get('business_phone', '')
            patient.business_type = request.POST.get('business_type', '')
            patient.civil_status = request.POST.get('civil_status', '')
            patient.bank_entity = request.POST.get('bank_entity', '')
            patient.account_number = request.POST.get('account_number', '')
            patient.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Paciente {patient.full_name} actualizado exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar paciente: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


@login_required
def patient_delete(request, pk):
    """Eliminar paciente (AJAX)"""
    if request.method == 'POST':
        org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
        patient = get_object_or_404(Patient, pk=pk, **org_filter)
        
        try:
            patient_name = patient.full_name
            patient.is_active = False
            patient.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Paciente {patient_name} desactivado exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al desactivar paciente: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


# ==================== GESTIÓN DE HORARIOS ====================

@login_required
def add_working_hour(request):
    """Agregar horario de atención (AJAX)"""
    if request.method == 'POST':
        day_of_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            if not request.organization:
                return JsonResponse({'success': False, 'message': 'No hay organización activa'}, status=400)
            
            working_hour = WorkingHours.objects.create(
                organization=request.organization,
                day_of_week=int(day_of_week),
                start_time=start_time,
                end_time=end_time,
                is_active=is_active
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Horario agregado exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al agregar horario: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False}, status=405)


@login_required
def toggle_working_hour(request, pk):
    """Activar/desactivar horario de atención (AJAX)"""
    if request.method == 'POST':
        try:
            working_hour = get_object_or_404(WorkingHours, pk=pk)
            working_hour.is_active = not working_hour.is_active
            working_hour.save()
            
            return JsonResponse({
                'success': True,
                'is_active': working_hour.is_active,
                'message': f'Horario {"activado" if working_hour.is_active else "desactivado"}'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False}, status=405)


@login_required
def delete_working_hour(request, pk):
    """Eliminar horario de atención (AJAX)"""
    if request.method == 'DELETE':
        try:
            working_hour = get_object_or_404(WorkingHours, pk=pk)
            working_hour.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Horario eliminado exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False}, status=405)


# ==================== GESTIÓN DE HORARIOS ESPECÍFICOS ====================

@login_required
def add_specific_schedule(request):
    """Agregar horario específico por fecha (AJAX)"""
    if request.method == 'POST':
        from apps.appointments.models import SpecificDateSchedule
        from django.contrib.auth.models import User
        
        date_str = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        notes = request.POST.get('notes', '')
        doctor_id = request.POST.get('doctor')
        slot_duration = request.POST.get('slot_duration', 30)
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Validar que la fecha no sea pasada
            if date < timezone.now().date():
                return JsonResponse({
                    'success': False,
                    'message': 'No puedes agregar horarios en fechas pasadas'
                }, status=400)
            
            if not request.organization:
                return JsonResponse({'success': False, 'message': 'No hay organización activa'}, status=400)
            
            # Obtener doctor si se especificó
            doctor = None
            if doctor_id:
                try:
                    doctor = User.objects.get(id=doctor_id)
                except User.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'Doctor no encontrado'
                    }, status=400)
            
            schedule = SpecificDateSchedule.objects.create(
                organization=request.organization,
                doctor=doctor,
                date=date,
                start_time=start_time,
                end_time=end_time,
                slot_duration=int(slot_duration),
                notes=notes,
                is_active=True,
                created_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Horario específico agregado exitosamente'
            })
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de fecha inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al agregar horario: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False}, status=405)


@login_required
def toggle_specific_schedule(request, pk):
    """Activar/desactivar horario específico (AJAX)"""
    if request.method == 'POST':
        from apps.appointments.models import SpecificDateSchedule
        
        try:
            schedule = get_object_or_404(SpecificDateSchedule, pk=pk)
            schedule.is_active = not schedule.is_active
            schedule.save()
            
            return JsonResponse({
                'success': True,
                'is_active': schedule.is_active,
                'message': f'Horario {"activado" if schedule.is_active else "desactivado"}'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False}, status=405)


@login_required
def delete_specific_schedule(request, pk):
    """Eliminar horario específico (AJAX)"""
    if request.method == 'POST':
        from apps.appointments.models import SpecificDateSchedule
        
        try:
            schedule = get_object_or_404(SpecificDateSchedule, pk=pk)
            schedule.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Horario eliminado exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False}, status=405)


@login_required
def edit_specific_schedule(request, pk):
    """Editar horario específico (AJAX)"""
    from apps.appointments.models import SpecificDateSchedule
    from django.contrib.auth.models import User
    
    schedule = get_object_or_404(SpecificDateSchedule, pk=pk, organization=request.organization)
    
    if request.method == 'GET':
        # Devolver datos del horario para edición
        return JsonResponse({
            'success': True,
            'schedule': {
                'id': schedule.id,
                'date': schedule.date.strftime('%Y-%m-%d'),
                'start_time': schedule.start_time.strftime('%H:%M'),
                'end_time': schedule.end_time.strftime('%H:%M'),
                'slot_duration': schedule.slot_duration,
                'notes': schedule.notes or '',
                'doctor': schedule.doctor.id if schedule.doctor else None,
            }
        })
    
    elif request.method == 'POST':
        date_str = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        notes = request.POST.get('notes', '')
        doctor_id = request.POST.get('doctor')
        slot_duration = request.POST.get('slot_duration', 30)
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Validar que la fecha no sea pasada (solo si se está cambiando)
            if date != schedule.date and date < timezone.now().date():
                return JsonResponse({
                    'success': False,
                    'message': 'No puedes cambiar a una fecha pasada'
                }, status=400)
            
            # Obtener doctor si se especificó
            doctor = None
            if doctor_id:
                try:
                    doctor = User.objects.get(id=doctor_id)
                except User.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'Doctor no encontrado'
                    }, status=400)
            
            # Actualizar campos
            schedule.date = date
            schedule.start_time = start_time
            schedule.end_time = end_time
            schedule.slot_duration = int(slot_duration)
            schedule.notes = notes
            schedule.doctor = doctor
            schedule.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Horario actualizado exitosamente'
            })
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de fecha inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar horario: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False}, status=405)


# ==================== WHATSAPP API ====================

@login_required
def whatsapp_status_api(request):
    """API para verificar el estado del bot de WhatsApp"""
    status = check_whatsapp_status()
    return JsonResponse(status)


@login_required
def whatsapp_test_send(request):
    """Enviar mensaje de prueba por WhatsApp"""
    if request.method == 'POST':
        import json
        from apps.appointments.whatsapp_local import whatsapp_notifier
        
        try:
            data = json.loads(request.body)
            phone = data.get('phone')
            
            if not phone:
                return JsonResponse({
                    'success': False,
                    'message': 'Número de teléfono requerido'
                }, status=400)
            
            # Verificar estado primero
            status = check_whatsapp_status()
            if not status['server_running']:
                return JsonResponse({
                    'success': False,
                    'message': 'Servidor WhatsApp no está corriendo',
                    'help': 'Ejecuta: cd whatsapp-bot && npm start'
                }, status=503)
            
            if not status['connected']:
                return JsonResponse({
                    'success': False,
                    'message': 'WhatsApp no está conectado',
                    'help': f'Ve a {status["api_url"]}/qr para conectar'
                }, status=503)
            
            # Enviar mensaje de prueba
            org_name = request.organization.name if hasattr(request, 'organization') and request.organization else 'Sistema'
            
            message = f"""
👓 *{org_name.upper()}*

¡Hola! Este es un mensaje de prueba.

✅ El sistema de notificaciones WhatsApp está funcionando correctamente.

_Este mensaje fue enviado desde el panel de administración_
            """.strip()
            
            success = whatsapp_notifier.send_message(phone, message)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': f'Mensaje enviado exitosamente a {phone}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Error al enviar el mensaje'
                }, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False}, status=405)


# ==================== CONFIGURACIÓN DE NOTIFICACIONES ====================

@login_required
def notification_settings(request):
    """Vista de configuración de notificaciones"""
    from apps.appointments.models_notifications import NotificationSettings
    
    org = request.organization if hasattr(request, 'organization') and request.organization else None
    settings = NotificationSettings.get_settings(org)
    
    context = {
        'settings': settings,
        'page_title': 'Configuración de Notificaciones',
    }
    
    return render(request, 'dashboard/notification_settings.html', context)


@login_required
def save_notification_settings(request):
    """Guardar configuración de notificaciones"""
    if request.method == 'POST':
        from apps.appointments.models_notifications import NotificationSettings
        
        org = request.organization if hasattr(request, 'organization') and request.organization else None
        settings = NotificationSettings.get_settings(org)
        
        # Twilio WhatsApp
        settings.twilio_enabled = request.POST.get('twilio_enabled') == 'on'
        settings.twilio_account_sid = request.POST.get('twilio_account_sid', '').strip()
        settings.twilio_auth_token = request.POST.get('twilio_auth_token', '').strip()
        settings.twilio_whatsapp_from = request.POST.get('twilio_whatsapp_from', 'whatsapp:+14155238886').strip()
        
        # Email
        settings.email_enabled = request.POST.get('email_enabled') == 'on'
        settings.email_from = request.POST.get('email_from', '').strip()
        
        # WhatsApp Local
        settings.local_whatsapp_enabled = request.POST.get('local_whatsapp_enabled') == 'on'
        settings.local_whatsapp_url = request.POST.get('local_whatsapp_url', 'http://localhost:3000').strip()
        
        # Notificaciones automáticas
        settings.send_confirmation = request.POST.get('send_confirmation') == 'on'
        settings.send_reminder = request.POST.get('send_reminder') == 'on'
        settings.send_cancellation = request.POST.get('send_cancellation') == 'on'
        
        settings.save()
        
        messages.success(request, '✅ Configuración de notificaciones guardada correctamente')
        return redirect('dashboard:notification_settings')
    
    return redirect('dashboard:notification_settings')


@login_required
def test_notification(request):
    """Enviar notificación de prueba"""
    if request.method == 'POST':
        import json
        from apps.appointments.models_notifications import NotificationSettings
        
        try:
            data = json.loads(request.body)
            phone_or_email = data.get('destination')
            method = data.get('method', 'auto')
            
            if not phone_or_email:
                return JsonResponse({
                    'success': False,
                    'message': 'Teléfono o email requerido'
                }, status=400)
            
            org = request.organization if hasattr(request, 'organization') and request.organization else None
            settings = NotificationSettings.get_settings(org)
            
            # Determinar método a usar
            if method == 'twilio' and settings.twilio_enabled:
                # Enviar por Twilio
                from twilio.rest import Client
                
                if not settings.twilio_account_sid or not settings.twilio_auth_token:
                    return JsonResponse({
                        'success': False,
                        'message': 'Twilio no está configurado correctamente. Verifica tus credenciales.'
                    }, status=400)
                
                # Validar formato del Account SID
                if not settings.twilio_account_sid.startswith('AC'):
                    return JsonResponse({
                        'success': False,
                        'message': f'El Account SID debe comenzar con "AC", no con "{settings.twilio_account_sid[:2]}". Verifica tus credenciales en https://console.twilio.com'
                    }, status=400)
                
                try:
                    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
                    
                    # Formatear número
                    phone = ''.join(filter(str.isdigit, phone_or_email))
                    if not phone.startswith('57'):
                        phone = '57' + phone
                    to_number = f'whatsapp:+{phone}'
                    
                    org_name = org.name if org else 'OCEANO OPTICO'
                    
                    message = f"""
👓 *{org_name.upper()}*

¡Hola! Este es un mensaje de prueba.

✅ El sistema de notificaciones WhatsApp (Twilio) está funcionando correctamente.

_Mensaje enviado desde el panel de administración_
                    """.strip()
                    
                    response = client.messages.create(
                        from_=settings.twilio_whatsapp_from,
                        body=message,
                        to=to_number
                    )
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'WhatsApp enviado exitosamente via Twilio',
                        'sid': response.sid
                    })
                    
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'message': f'Error de Twilio: {str(e)}'
                    }, status=500)
            
            elif method == 'local_whatsapp' and settings.local_whatsapp_enabled:
                # Enviar por WhatsApp local
                from apps.appointments.whatsapp_local import whatsapp_notifier
                
                org_name = org.name if org else 'Sistema'
                message = f"""
👓 *{org_name.upper()}*

¡Hola! Este es un mensaje de prueba.

✅ El sistema de notificaciones WhatsApp local está funcionando correctamente.

_Mensaje enviado desde el panel de administración_
                """.strip()
                
                success = whatsapp_notifier.send_message(phone_or_email, message)
                
                if success:
                    return JsonResponse({
                        'success': True,
                        'message': f'WhatsApp local enviado exitosamente'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Error al enviar por WhatsApp local'
                    }, status=500)
            
            elif method == 'email' and settings.email_enabled:
                # Enviar por email
                from django.core.mail import send_mail
                from django.conf import settings as django_settings
                
                org_name = org.name if org else 'OCEANO OPTICO'
                subject = f'Prueba de Notificaciones - {org_name}'
                message = f"""
Hola,

Este es un correo de prueba del sistema de notificaciones de {org_name}.

✅ Si recibes este mensaje, el sistema de email está funcionando correctamente.

--
{org_name}
Sistema de Citas
                """.strip()
                
                from_email = settings.email_from if settings.email_from else django_settings.DEFAULT_FROM_EMAIL
                
                send_mail(
                    subject,
                    message,
                    from_email,
                    [phone_or_email],
                    fail_silently=False,
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Email enviado exitosamente'
                })
            
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Ningún método de notificación está habilitado'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False}, status=405)


# ==================== CREAR PACIENTE DESDE CITA ====================

@login_required
def create_patient_from_appointment(request):
    """Crear un paciente desde el detalle de una cita"""
    if request.method == 'POST':
        try:
            import traceback
            
            # Obtener datos del formulario
            full_name = request.POST.get('full_name')
            phone_number = request.POST.get('phone_number')
            
            if not full_name or not phone_number:
                return JsonResponse({
                    'success': False,
                    'message': 'Nombre y teléfono son requeridos'
                }, status=400)
            
            # Obtener la organización del usuario a través de OrganizationMember
            from apps.organizations.models import OrganizationMember
            
            membership = OrganizationMember.objects.filter(user=request.user, is_active=True).first()
            if not membership:
                # Si no tiene membership, intentar obtener de organizaciones que posee
                owned_org = request.user.owned_organizations.filter(is_active=True).first()
                if owned_org:
                    user_org = owned_org
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Tu usuario no pertenece a ninguna organización. Contacta al administrador.'
                    }, status=400)
            else:
                user_org = membership.organization
            
            # Verificar si ya existe un paciente con ese teléfono
            existing_patient = Patient.objects.filter(
                organization=user_org,
                phone_number=phone_number
            ).first()
            
            if existing_patient:
                return JsonResponse({
                    'success': False,
                    'message': f'Ya existe un paciente con ese teléfono: {existing_patient.full_name}'
                }, status=400)
            
            # Crear el paciente
            patient = Patient.objects.create(
                organization=user_org,
                full_name=full_name,
                identification=request.POST.get('identification', ''),
                date_of_birth=request.POST.get('date_of_birth') or None,
                gender=request.POST.get('gender', ''),
                phone_number=phone_number,
                email=request.POST.get('email', ''),
                address=request.POST.get('address', ''),
                allergies=request.POST.get('allergies', ''),
                medical_conditions=request.POST.get('medical_conditions', ''),
                current_medications=request.POST.get('current_medications', ''),
                occupation=request.POST.get('occupation', ''),
                civil_status=request.POST.get('civil_status', ''),
                residence_area=request.POST.get('residence_area', ''),
                has_companion=request.POST.get('has_companion') == 'true',
                companion_name=request.POST.get('companion_name', ''),
                companion_relationship=request.POST.get('companion_relationship', ''),
                companion_phone=request.POST.get('companion_phone', ''),
                is_active=True
            )
            
            # Asociar el paciente con la cita
            appointment_id = request.POST.get('appointment_id')
            if appointment_id:
                appointment = Appointment.objects.get(
                    id=appointment_id,
                    organization=user_org
                )
                appointment.patient = patient
                appointment.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Paciente creado exitosamente',
                'patient_id': patient.id
            })
            
        except Appointment.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Cita no encontrada'
            }, status=404)
        except Exception as e:
            # Imprimir el traceback completo en consola
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Error al crear paciente: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


# ==================== DOCTORES / OPTÓMETRAS ====================

@login_required
def doctors_list(request):
    """Vista para listar todos los doctores"""
    from apps.patients.models import Doctor
    from apps.organizations.models import OrganizationMember
    
    # Obtener la organización del usuario
    try:
        org_member = OrganizationMember.objects.filter(user=request.user).first()
        if not org_member:
            messages.error(request, 'No tienes una organización asignada')
            return redirect('dashboard:home')
        
        organization = org_member.organization
    except Exception as e:
        messages.error(request, f'Error al obtener organización: {str(e)}')
        return redirect('dashboard:home')
    
    # Obtener doctores de la organización
    doctors = Doctor.objects.filter(
        organization=organization,
        is_active=True
    ).order_by('-created_at')
    
    context = {
        'doctors': doctors,
        'total_doctors': doctors.count(),
    }
    
    return render(request, 'dashboard/doctors/list.html', context)


@login_required
def doctor_detail(request, pk):
    """Vista para ver detalles de un doctor"""
    from apps.patients.models import Doctor
    from apps.organizations.models import OrganizationMember
    
    # Obtener la organización del usuario
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    # Obtener el doctor
    doctor = get_object_or_404(
        Doctor,
        pk=pk,
        organization=org_member.organization
    )
    
    context = {
        'doctor': doctor,
    }
    
    return render(request, 'dashboard/doctors/detail.html', context)


@login_required
def doctor_create(request):
    """Vista para crear un nuevo doctor"""
    from apps.patients.models import Doctor
    from apps.organizations.models import OrganizationMember
    
    # Obtener la organización del usuario
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        try:
            # Crear el doctor
            doctor = Doctor(
                organization=org_member.organization,
                full_name=request.POST.get('full_name'),
                identification_type=request.POST.get('identification_type', 'CC'),
                identification=request.POST.get('identification'),
                specialty=request.POST.get('specialty'),
                professional_card=request.POST.get('professional_card', ''),
                rethus=request.POST.get('rethus', ''),
                graduation_date=request.POST.get('graduation_date') or None,
                university=request.POST.get('university', ''),
                email=request.POST.get('email', ''),
                phone=request.POST.get('phone', ''),
                mobile=request.POST.get('mobile', ''),
                address=request.POST.get('address', ''),
                monday_schedule=request.POST.get('monday_schedule', ''),
                tuesday_schedule=request.POST.get('tuesday_schedule', ''),
                wednesday_schedule=request.POST.get('wednesday_schedule', ''),
                thursday_schedule=request.POST.get('thursday_schedule', ''),
                friday_schedule=request.POST.get('friday_schedule', ''),
                saturday_schedule=request.POST.get('saturday_schedule', ''),
                sunday_schedule=request.POST.get('sunday_schedule', ''),
                bio=request.POST.get('bio', ''),
                notes=request.POST.get('notes', ''),
                is_active=request.POST.get('is_active') == 'on'
            )
            
            # Manejar archivos
            if 'signature' in request.FILES:
                doctor.signature = request.FILES['signature']
            if 'photo' in request.FILES:
                doctor.photo = request.FILES['photo']
            
            doctor.save()
            
            messages.success(request, f'Doctor {doctor.full_name} creado exitosamente')
            return redirect('dashboard:doctor_detail', pk=doctor.pk)
            
        except Exception as e:
            messages.error(request, f'Error al crear doctor: {str(e)}')
    
    context = {
        'specialty_choices': Doctor.SPECIALTY_CHOICES,
    }
    
    return render(request, 'dashboard/doctors/form.html', context)


@login_required
def doctor_edit(request, pk):
    """Vista para editar un doctor"""
    from apps.patients.models import Doctor
    from apps.organizations.models import OrganizationMember
    
    # Obtener la organización del usuario
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    # Obtener el doctor
    doctor = get_object_or_404(
        Doctor,
        pk=pk,
        organization=org_member.organization
    )
    
    if request.method == 'POST':
        try:
            # Actualizar datos básicos
            doctor.full_name = request.POST.get('full_name')
            doctor.identification_type = request.POST.get('identification_type', 'CC')
            doctor.identification = request.POST.get('identification')
            doctor.specialty = request.POST.get('specialty')
            doctor.professional_card = request.POST.get('professional_card', '')
            doctor.rethus = request.POST.get('rethus', '')
            doctor.graduation_date = request.POST.get('graduation_date') or None
            doctor.university = request.POST.get('university', '')
            doctor.email = request.POST.get('email', '')
            doctor.phone = request.POST.get('phone', '')
            doctor.mobile = request.POST.get('mobile', '')
            doctor.address = request.POST.get('address', '')
            
            # Actualizar horarios
            doctor.monday_schedule = request.POST.get('monday_schedule', '')
            doctor.tuesday_schedule = request.POST.get('tuesday_schedule', '')
            doctor.wednesday_schedule = request.POST.get('wednesday_schedule', '')
            doctor.thursday_schedule = request.POST.get('thursday_schedule', '')
            doctor.friday_schedule = request.POST.get('friday_schedule', '')
            doctor.saturday_schedule = request.POST.get('saturday_schedule', '')
            doctor.sunday_schedule = request.POST.get('sunday_schedule', '')
            
            # Actualizar información adicional
            doctor.bio = request.POST.get('bio', '')
            doctor.notes = request.POST.get('notes', '')
            doctor.is_active = request.POST.get('is_active') == 'on'
            
            # Manejar archivos
            if 'signature' in request.FILES:
                doctor.signature = request.FILES['signature']
            if 'photo' in request.FILES:
                doctor.photo = request.FILES['photo']
            
            doctor.save()
            
            messages.success(request, f'Doctor {doctor.full_name} actualizado exitosamente')
            return redirect('dashboard:doctor_detail', pk=doctor.pk)
            
        except Exception as e:
            messages.error(request, f'Error al actualizar doctor: {str(e)}')
    
    context = {
        'doctor': doctor,
        'specialty_choices': Doctor.SPECIALTY_CHOICES,
        'is_edit': True,
    }
    
    return render(request, 'dashboard/doctors/form.html', context)


@login_required
def doctor_delete(request, pk):
    """Vista para eliminar un doctor (soft delete)"""
    from apps.patients.models import Doctor
    from apps.organizations.models import OrganizationMember
    
    if request.method == 'POST':
        # Obtener la organización del usuario
        org_member = OrganizationMember.objects.filter(user=request.user).first()
        if not org_member:
            messages.error(request, 'No tienes una organización asignada')
            return redirect('dashboard:home')
        
        # Obtener el doctor
        doctor = get_object_or_404(
            Doctor,
            pk=pk,
            organization=org_member.organization
        )
        
        try:
            # Soft delete
            doctor.is_active = False
            doctor.save()
            
            messages.success(request, f'Doctor {doctor.full_name} desactivado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al desactivar doctor: {str(e)}')
    
    return redirect('dashboard:doctors_list')


@login_required
def notifications_demo(request):
    """Vista de demostración del sistema de notificaciones moderno"""
    return render(request, 'dashboard/notifications_demo.html')


@login_required
def landing_page_config(request):
    """Vista para configurar la landing page"""
    from apps.organizations.models import LandingPageConfig
    from apps.organizations.forms import LandingPageConfigForm
    
    org = request.organization if hasattr(request, 'organization') and request.organization else None
    
    if not org:
        messages.error(request, 'Debes seleccionar una organización primero')
        return redirect('organizations:list')
    
    # Obtener o crear configuración
    config, created = LandingPageConfig.objects.get_or_create(organization=org)
    
    if request.method == 'POST':
        form = LandingPageConfigForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Configuración de landing page guardada correctamente')
            return redirect('dashboard:landing_page_config')
        else:
            # Mostrar errores específicos del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            messages.error(request, 'Por favor corrige los errores del formulario')
    else:
        form = LandingPageConfigForm(instance=config)
    
    context = {
        'form': form,
        'config': config,
        'page_title': 'Configuración de Landing Page',
        'page_subtitle': 'Personaliza los colores e imágenes de tu página pública',
    }
    
    return render(request, 'dashboard/landing_page_config_pro.html', context)


# ==================== PARÁMETROS CLÍNICOS ====================

@login_required
def clinical_parameters(request):
    """Vista principal de parámetros clínicos"""
    from apps.patients.models_clinical_config import ClinicalParameter
    
    org = request.organization if hasattr(request, 'organization') and request.organization else None
    if not org:
        messages.error(request, 'Debes seleccionar una organización primero')
        return redirect('organizations:list')
    
    # Filtros
    parameter_type = request.GET.get('type', '')
    search_query = request.GET.get('q', '')
    
    # Obtener parámetros
    parameters = ClinicalParameter.objects.filter(organization=org)
    
    if parameter_type:
        parameters = parameters.filter(parameter_type=parameter_type)
    
    if search_query:
        parameters = parameters.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    parameters = parameters.order_by('parameter_type', 'display_order', 'name')
    
    # Estadísticas por tipo
    stats = ClinicalParameter.objects.filter(
        organization=org
    ).values('parameter_type').annotate(
        count=Count('id')
    ).order_by('parameter_type')
    
    context = {
        'parameters': parameters,
        'parameter_types': ClinicalParameter.PARAMETER_TYPES,
        'selected_type': parameter_type,
        'search_query': search_query,
        'stats': stats,
        'page_title': 'Parámetros Clínicos',
        'page_subtitle': 'Gestiona medicamentos, tratamientos, diagnósticos y más',
    }
    
    return render(request, 'dashboard/clinical_parameters.html', context)


@login_required
def clinical_parameter_create(request):
    """Crear nuevo parámetro clínico"""
    from apps.patients.models_clinical_config import ClinicalParameter
    from apps.patients.forms_clinical_config import ClinicalParameterForm
    
    org = request.organization if hasattr(request, 'organization') and request.organization else None
    if not org:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Debes seleccionar una organización primero'}, status=400)
        messages.error(request, 'Debes seleccionar una organización primero')
        return redirect('organizations:list')
    
    if request.method == 'POST':
        form = ClinicalParameterForm(request.POST)
        if form.is_valid():
            try:
                parameter = form.save(commit=False)
                parameter.organization = org
                parameter.created_by = request.user
                parameter.save()
                
                # Si es una petición AJAX, retornar JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Parámetro "{parameter.name}" creado exitosamente',
                        'parameter': {
                            'id': parameter.id,
                            'name': parameter.name,
                            'description': parameter.description or '',
                            'dosage': parameter.dosage or '',
                            'frequency': parameter.frequency or '',
                            'duration': parameter.duration or '',
                            'administration_route': parameter.get_administration_route_display() if parameter.administration_route else '',
                            'category': parameter.category or '',
                        }
                    })
                
                messages.success(request, f'✅ Parámetro "{parameter.name}" creado exitosamente')
                return redirect('dashboard:clinical_parameters')
            except Exception as e:
                # Manejar error de duplicado u otros errores de base de datos
                error_msg = str(e)
                if 'unique constraint' in error_msg.lower() or 'duplicate' in error_msg.lower():
                    error_msg = f'Ya existe un parámetro con el nombre "{form.cleaned_data.get("name")}" en esta categoría'
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False, 
                        'message': error_msg,
                        'errors': {'__all__': error_msg}
                    }, status=400)
                else:
                    messages.error(request, f'❌ Error: {error_msg}')
        else:
            # Si hay errores y es AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {field: str(error[0]) for field, error in form.errors.items()}
                return JsonResponse({'success': False, 'message': 'Errores en el formulario', 'errors': errors}, status=400)
    else:
        form = ClinicalParameterForm()
    
    context = {
        'form': form,
        'page_title': 'Nuevo Parámetro Clínico',
        'page_subtitle': 'Agrega un nuevo medicamento, tratamiento o diagnóstico',
    }
    
    return render(request, 'dashboard/clinical_parameter_form.html', context)


@login_required
def clinical_parameter_edit(request, pk):
    """Editar parámetro clínico"""
    from apps.patients.models_clinical_config import ClinicalParameter
    from apps.patients.forms_clinical_config import ClinicalParameterForm
    
    org = request.organization if hasattr(request, 'organization') and request.organization else None
    parameter = get_object_or_404(ClinicalParameter, pk=pk, organization=org)
    
    if request.method == 'POST':
        form = ClinicalParameterForm(request.POST, instance=parameter)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Parámetro "{parameter.name}" actualizado exitosamente')
            return redirect('dashboard:clinical_parameters')
    else:
        form = ClinicalParameterForm(instance=parameter)
    
    context = {
        'form': form,
        'parameter': parameter,
        'page_title': 'Editar Parámetro Clínico',
        'page_subtitle': f'Modificando: {parameter.name}',
    }
    
    return render(request, 'dashboard/clinical_parameter_form.html', context)


@login_required
def clinical_parameter_delete(request, pk):
    """Eliminar parámetro clínico"""
    from apps.patients.models_clinical_config import ClinicalParameter
    
    org = request.organization if hasattr(request, 'organization') and request.organization else None
    parameter = get_object_or_404(ClinicalParameter, pk=pk, organization=org)
    
    if request.method == 'POST':
        name = parameter.name
        parameter.delete()
        messages.success(request, f'✅ Parámetro "{name}" eliminado exitosamente')
    
    return redirect('dashboard:clinical_parameters')


@login_required
def clinical_parameter_bulk_import(request):
    """Importar parámetros en masa"""
    from apps.patients.models_clinical_config import ClinicalParameter
    from apps.patients.forms_clinical_config import BulkParameterImportForm
    
    org = request.organization if hasattr(request, 'organization') and request.organization else None
    if not org:
        messages.error(request, 'Debes seleccionar una organización primero')
        return redirect('organizations:list')
    
    if request.method == 'POST':
        form = BulkParameterImportForm(request.POST)
        if form.is_valid():
            parameter_type = form.cleaned_data['parameter_type']
            parameters_text = form.cleaned_data['parameters_text']
            set_active = form.cleaned_data['set_active']
            
            lines = parameters_text.strip().split('\n')
            created_count = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Separar código y nombre si existe guión
                parts = line.split('-', 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    description = parts[1].strip()
                    code = ''
                else:
                    name = line.strip()
                    description = ''
                    code = ''
                
                # Crear parámetro si no existe
                parameter, created = ClinicalParameter.objects.get_or_create(
                    organization=org,
                    parameter_type=parameter_type,
                    name=name,
                    defaults={
                        'code': code,
                        'description': description,
                        'is_active': set_active,
                        'created_by': request.user
                    }
                )
                
                if created:
                    created_count += 1
            
            messages.success(request, f'✅ Se crearon {created_count} parámetros nuevos')
            return redirect('dashboard:clinical_parameters')
    else:
        form = BulkParameterImportForm()
    
    context = {
        'form': form,
        'page_title': 'Importar Parámetros en Masa',
        'page_subtitle': 'Agrega múltiples parámetros rápidamente',
    }
    
    return render(request, 'dashboard/clinical_parameter_bulk_import.html', context)


@login_required
def medication_templates(request):
    """Vista de plantillas de medicación"""
    from apps.patients.models_clinical_config import MedicationTemplate
    
    org = request.organization if hasattr(request, 'organization') and request.organization else None
    if not org:
        messages.error(request, 'Debes seleccionar una organización primero')
        return redirect('organizations:list')
    
    templates = MedicationTemplate.objects.filter(organization=org).order_by('-usage_count', 'name')
    
    context = {
        'templates': templates,
        'page_title': 'Plantillas de Medicación',
        'page_subtitle': 'Prescripciones predefinidas para diagnósticos comunes',
    }
    
    return render(request, 'dashboard/medication_templates.html', context)


@login_required
def treatment_protocols(request):
    """Vista de protocolos de tratamiento"""
    from apps.patients.models_clinical_config import TreatmentProtocol
    
    org = request.organization if hasattr(request, 'organization') and request.organization else None
    if not org:
        messages.error(request, 'Debes seleccionar una organización primero')
        return redirect('organizations:list')
    
    protocols = TreatmentProtocol.objects.filter(organization=org).order_by('-usage_count', 'name')
    
    context = {
        'protocols': protocols,
        'page_title': 'Protocolos de Tratamiento',
        'page_subtitle': 'Protocolos estandarizados para diferentes condiciones',
    }
    
    return render(request, 'dashboard/treatment_protocols.html', context)
