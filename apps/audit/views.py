"""
Vistas para el sistema de auditoría.
Permite consultar y analizar los registros de auditoría.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, F
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from datetime import datetime, timedelta
import json
import csv
from .models import AuditLog, AuditConfig, AuditRetentionLog
from .services import AuditService


@login_required
def audit_dashboard(request):
    """Dashboard principal de auditoría."""
    organization = request.organization
    
    # Rango de fechas (últimos 30 días por defecto)
    date_to = timezone.now()
    date_from = date_to - timedelta(days=30)
    
    # Estadísticas generales
    total_logs = AuditLog.objects.filter(
        organization=organization,
        created_at__gte=date_from
    ).count()
    
    # Estadísticas por acción
    action_stats = AuditLog.objects.filter(
        organization=organization,
        created_at__gte=date_from
    ).values('action').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Usuarios más activos
    top_users = AuditLog.objects.filter(
        organization=organization,
        created_at__gte=date_from,
        user__isnull=False
    ).values('user__username', 'user__first_name', 'user__last_name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Actividad reciente
    recent_logs = AuditLog.objects.filter(
        organization=organization
    ).select_related('user', 'content_type').order_by('-created_at')[:20]
    
    # IPs únicas
    unique_ips = AuditLog.objects.filter(
        organization=organization,
        created_at__gte=date_from,
        ip_address__isnull=False
    ).values('ip_address').distinct().count()
    
    # Intentos de login fallidos
    failed_logins = AuditLog.objects.filter(
        organization=organization,
        action='LOGIN_FAILED',
        created_at__gte=date_from
    ).count()
    
    context = {
        'total_logs': total_logs,
        'action_stats': action_stats,
        'top_users': top_users,
        'recent_logs': recent_logs,
        'unique_ips': unique_ips,
        'failed_logins': failed_logins,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'audit/dashboard.html', context)


@login_required
def audit_logs(request):
    """Lista de registros de auditoría con filtros."""
    organization = request.organization
    
    # Filtros
    action = request.GET.get('action')
    user_id = request.GET.get('user')
    model = request.GET.get('model')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search')
    ip_address = request.GET.get('ip')
    
    logs = AuditLog.objects.filter(organization=organization)
    
    if action:
        logs = logs.filter(action=action)
    
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    if model:
        try:
            content_type = ContentType.objects.get(model=model)
            logs = logs.filter(content_type=content_type)
        except ContentType.DoesNotExist:
            pass
    
    if date_from:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        logs = logs.filter(created_at__gte=date_from_obj)
    
    if date_to:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
        # Incluir todo el día
        date_to_obj = date_to_obj.replace(hour=23, minute=59, second=59)
        logs = logs.filter(created_at__lte=date_to_obj)
    
    if search:
        logs = logs.filter(
            Q(object_repr__icontains=search) |
            Q(description__icontains=search) |
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )
    
    if ip_address:
        logs = logs.filter(ip_address=ip_address)
    
    logs = logs.select_related('user', 'content_type').order_by('-created_at')
    
    # Paginación simple (primeros 100)
    logs = logs[:100]
    
    # Datos para filtros
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    users = User.objects.filter(
        organization_memberships__organization=organization
    ).distinct().order_by('first_name', 'last_name')
    
    # Modelos disponibles
    content_types = ContentType.objects.filter(
        auditlog__organization=organization
    ).distinct().order_by('model')
    
    context = {
        'logs': logs,
        'action_choices': AuditLog.ACTION_CHOICES,
        'users': users,
        'content_types': content_types,
        'current_action': action,
        'current_user': user_id,
        'current_model': model,
        'current_date_from': date_from,
        'current_date_to': date_to,
        'current_search': search,
        'current_ip': ip_address,
    }
    
    return render(request, 'audit/logs.html', context)


@login_required
def audit_detail(request, pk):
    """Detalle de un registro de auditoría."""
    organization = request.organization
    
    log = get_object_or_404(
        AuditLog,
        pk=pk,
        organization=organization
    )
    
    # Logs relacionados (mismo objeto)
    related_logs = None
    if log.content_type and log.object_id:
        related_logs = AuditLog.objects.filter(
            organization=organization,
            content_type=log.content_type,
            object_id=log.object_id
        ).exclude(pk=pk).order_by('-created_at')[:10]
    
    # Logs del mismo usuario en el mismo día
    user_logs = None
    if log.user:
        day_start = log.created_at.replace(hour=0, minute=0, second=0)
        day_end = log.created_at.replace(hour=23, minute=59, second=59)
        user_logs = AuditLog.objects.filter(
            organization=organization,
            user=log.user,
            created_at__gte=day_start,
            created_at__lte=day_end
        ).exclude(pk=pk).order_by('-created_at')[:10]
    
    context = {
        'log': log,
        'related_logs': related_logs,
        'user_logs': user_logs,
    }
    
    return render(request, 'audit/detail.html', context)


@login_required
def audit_user_activity(request, user_id):
    """Actividad de un usuario específico."""
    organization = request.organization
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    user = get_object_or_404(User, pk=user_id)
    
    # Verificar que el usuario pertenece a la organización
    if not user.organization_memberships.filter(organization=organization).exists():
        messages.error(request, 'Usuario no encontrado en tu organización.')
        return redirect('audit:dashboard')
    
    # Rango de fechas
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    logs = AuditLog.objects.filter(
        organization=organization,
        user=user
    )
    
    if date_from:
        logs = logs.filter(created_at__gte=datetime.strptime(date_from, '%Y-%m-%d'))
    
    if date_to:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        logs = logs.filter(created_at__lte=date_to_obj)
    
    # Estadísticas
    action_stats = logs.values('action').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # IPs únicas
    ips = logs.values('ip_address').distinct().count()
    
    # Actividad reciente
    recent_logs = logs.select_related('content_type').order_by('-created_at')[:50]
    
    context = {
        'target_user': user,
        'total_logs': logs.count(),
        'action_stats': action_stats,
        'unique_ips': ips,
        'recent_logs': recent_logs,
        'current_date_from': date_from,
        'current_date_to': date_to,
    }
    
    return render(request, 'audit/user_activity.html', context)


@login_required
def audit_export(request):
    """Exportar registros de auditoría a CSV."""
    organization = request.organization
    
    # Usar los mismos filtros que la vista de logs
    action = request.GET.get('action')
    user_id = request.GET.get('user')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    logs = AuditLog.objects.filter(organization=organization)
    
    if action:
        logs = logs.filter(action=action)
    if user_id:
        logs = logs.filter(user_id=user_id)
    if date_from:
        logs = logs.filter(created_at__gte=datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        logs = logs.filter(created_at__lte=date_to_obj)
    
    logs = logs.select_related('user', 'content_type').order_by('-created_at')
    
    # Crear CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="audit_logs_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Fecha', 'Usuario', 'Acción', 'Objeto', 'IP', 'Descripción'])
    
    for log in logs[:1000]:  # Limitar a 1000 registros
        writer.writerow([
            log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            log.user.get_full_name() if log.user else 'Sistema',
            log.get_action_display(),
            log.object_repr,
            log.ip_address or '',
            log.description or ''
        ])
    
    return response


@login_required
def audit_config_list(request):
    """Lista de configuraciones de auditoría."""
    organization = request.organization
    
    configs = AuditConfig.objects.filter(
        Q(organization=organization) | Q(organization__isnull=True)
    ).order_by('model_name')
    
    context = {
        'configs': configs,
    }
    
    return render(request, 'audit/config_list.html', context)


@login_required
def audit_stats_api(request):
    """API para obtener estadísticas de auditoría (para gráficos)."""
    organization = request.organization
    
    days = int(request.GET.get('days', 7))
    date_from = timezone.now() - timedelta(days=days)
    
    # Actividad por día
    from django.db.models.functions import TruncDate
    
    daily_activity = AuditLog.objects.filter(
        organization=organization,
        created_at__gte=date_from
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Actividad por acción
    action_activity = AuditLog.objects.filter(
        organization=organization,
        created_at__gte=date_from
    ).values('action').annotate(
        count=Count('id')
    ).order_by('-count')
    
    data = {
        'daily': [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'count': item['count']
            }
            for item in daily_activity
        ],
        'actions': [
            {
                'action': item['action'],
                'count': item['count']
            }
            for item in action_activity
        ]
    }
    
    return JsonResponse(data)

