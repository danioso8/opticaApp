from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta

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
    
    # Estadísticas del día
    today_appointments = Appointment.objects.filter(appointment_date=today)
    
    # Estadísticas de ventas
    today_sales = Sale.objects.filter(created_at__date=today, status='completed')
    today_revenue = sum(sale.total for sale in today_sales)
    month_sales = Sale.objects.filter(created_at__date__year=today.year, created_at__date__month=today.month, status='completed')
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
        'total_patients': Patient.objects.filter(is_active=True).count(),
        'system_open': AppointmentConfiguration.get_config().is_open,
    }
    
    # Próximas citas (siguientes 5)
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=today
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
    
    # Citas de hoy
    today_appointments = Appointment.objects.filter(
        appointment_date=today
    ).select_related('patient', 'attended_by').order_by('appointment_time')
    
    # Todas las citas con filtros
    all_appointments = Appointment.objects.all().select_related('patient', 'attended_by')
    
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
    appointments = Appointment.objects.filter(
        appointment_date=today
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
    
    config = AppointmentConfiguration.get_config()
    working_hours = WorkingHours.objects.all().order_by('day_of_week', 'start_time')
    blocked_dates = BlockedDate.objects.filter(date__gte=timezone.now().date()).order_by('date')
    specific_schedules = SpecificDateSchedule.objects.filter(date__gte=timezone.now().date()).order_by('date', 'start_time')
    
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
        config = AppointmentConfiguration.get_config()
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
            
            blocked, created = BlockedDate.objects.get_or_create(
                date=date,
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

@login_required
def patients_list(request):
    """Lista de pacientes"""
    patients = Patient.objects.filter(is_active=True)
    
    search = request.GET.get('search')
    if search:
        patients = patients.filter(
            Q(full_name__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(identification__icontains=search)
        )
    
    patients = patients.order_by('-created_at')
    
    context = {
        'patients': patients,
    }
    
    return render(request, 'dashboard/patients/list.html', context)


@login_required
def patient_detail(request, pk):
    """Detalle de un paciente"""
    patient = get_object_or_404(Patient, pk=pk)
    appointments = patient.appointments.all().order_by('-appointment_date')
    
    context = {
        'patient': patient,
        'appointments': appointments,
    }
    
    return render(request, 'dashboard/patients/detail.html', context)


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
    appointments = Appointment.objects.filter(
        appointment_date__year=year,
        appointment_date__month=month
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
            working_hour = WorkingHours.objects.create(
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
            
            schedule = SpecificDateSchedule.objects.create(
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
