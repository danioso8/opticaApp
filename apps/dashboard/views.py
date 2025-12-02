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
    clinical_history_edit,
    clinical_history_delete
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


# ==================== AUTENTICACIÓN ====================

def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.username}!')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Credenciales inválidas')
    
    return render(request, 'dashboard/login.html')


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.info(request, 'Sesión cerrada')
    return redirect('dashboard:login')


# ==================== DASHBOARD PRINCIPAL ====================

@login_required
def dashboard_home(request):
    """Página principal del dashboard"""
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
    
    org_filter = {'organization': request.organization} if hasattr(request, 'organization') and request.organization else {}
    
    config = AppointmentConfiguration.get_config(request.organization) if request.organization else None
    working_hours = WorkingHours.objects.filter(**org_filter).order_by('day_of_week', 'start_time')
    blocked_dates = BlockedDate.objects.filter(date__gte=timezone.now().date(), **org_filter).order_by('date')
    specific_schedules = SpecificDateSchedule.objects.filter(date__gte=timezone.now().date(), **org_filter).order_by('date', 'start_time')
    
    context = {
        'config': config,
        'working_hours': working_hours,
        'blocked_dates': blocked_dates,
        'specific_schedules': specific_schedules,
    }
    
    return render(request, 'dashboard/configuration.html', context)


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
        
        date_str = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        notes = request.POST.get('notes', '')
        
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
            
            schedule = SpecificDateSchedule.objects.create(
                organization=request.organization,
                date=date,
                start_time=start_time,
                end_time=end_time,
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
