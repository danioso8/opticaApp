"""
Vistas para el sistema de reportes.
Permite crear, generar y gestionar reportes personalizados.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, HttpResponse
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
import json
from .models import ReportTemplate, Report, ScheduledReport, ReportShare
from .services import ReportService


@login_required
def report_dashboard(request):
    """Dashboard principal de reportes."""
    organization = request.organization
    
    # Estadísticas
    stats = {
        'templates': ReportTemplate.objects.filter(
            Q(organization=organization) | Q(organization__isnull=True, is_public=True)
        ).count(),
        'generated': Report.objects.filter(organization=organization).count(),
        'scheduled': ScheduledReport.objects.filter(
            organization=organization,
            is_active=True
        ).count(),
        'shared': ReportShare.objects.filter(
            report__organization=organization
        ).count(),
    }
    
    # Reportes recientes
    recent_reports = Report.objects.filter(
        organization=organization
    ).select_related('template', 'generated_by')[:10]
    
    # Reportes programados próximos
    upcoming_scheduled = ScheduledReport.objects.filter(
        organization=organization,
        is_active=True,
        next_run_at__isnull=False
    ).order_by('next_run_at')[:5]
    
    # Plantillas más usadas
    popular_templates = ReportTemplate.objects.filter(
        Q(organization=organization) | Q(organization__isnull=True, is_public=True)
    ).annotate(
        usage_count=Count('generated_reports')
    ).order_by('-usage_count')[:5]
    
    context = {
        'stats': stats,
        'recent_reports': recent_reports,
        'upcoming_scheduled': upcoming_scheduled,
        'popular_templates': popular_templates,
    }
    
    return render(request, 'reports/dashboard.html', context)


@login_required
def template_list(request):
    """Lista de plantillas de reportes."""
    organization = request.organization
    
    # Filtros
    report_type = request.GET.get('type')
    search = request.GET.get('search')
    
    templates = ReportTemplate.objects.filter(
        Q(organization=organization) | Q(organization__isnull=True, is_public=True),
        is_active=True
    )
    
    if report_type:
        templates = templates.filter(report_type=report_type)
    
    if search:
        templates = templates.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    templates = templates.select_related('created_by').order_by('report_type', 'name')
    
    context = {
        'templates': templates,
        'report_types': ReportTemplate.REPORT_TYPE_CHOICES,
        'current_type': report_type,
        'search': search,
    }
    
    return render(request, 'reports/template_list.html', context)


@login_required
def template_detail(request, pk):
    """Detalle de plantilla de reporte."""
    organization = request.organization
    
    template = get_object_or_404(
        ReportTemplate,
        pk=pk
    )
    
    # Verificar acceso
    if template.organization and template.organization != organization:
        if not template.is_public:
            messages.error(request, 'No tienes permiso para ver esta plantilla.')
            return redirect('reports:templates')
    
    # Reportes generados con esta plantilla
    generated_reports = Report.objects.filter(
        template=template,
        organization=organization
    ).select_related('generated_by').order_by('-created_at')[:10]
    
    context = {
        'template': template,
        'generated_reports': generated_reports,
    }
    
    return render(request, 'reports/template_detail.html', context)


@login_required
def generate_report(request, template_id):
    """Generar un nuevo reporte."""
    organization = request.organization
    
    template = get_object_or_404(ReportTemplate, pk=template_id)
    
    if request.method == 'POST':
        try:
            # Obtener parámetros
            date_from = request.POST.get('date_from')
            date_to = request.POST.get('date_to')
            output_format = request.POST.get('output_format', 'pdf')
            
            # Convertir fechas
            if date_from:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            if date_to:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            
            # Otros parámetros
            parameters = {}
            for key, value in request.POST.items():
                if key.startswith('param_'):
                    param_name = key.replace('param_', '')
                    parameters[param_name] = value
            
            # Generar reporte
            report = ReportService.generate_report(
                template=template,
                organization=organization,
                user=request.user,
                parameters=parameters,
                output_format=output_format,
                date_from=date_from,
                date_to=date_to
            )
            
            messages.success(request, 'Reporte generado exitosamente.')
            return redirect('reports:detail', pk=report.pk)
            
        except Exception as e:
            messages.error(request, f'Error al generar reporte: {str(e)}')
    
    # Formulario de generación
    context = {
        'template': template,
        'output_formats': Report.FORMAT_CHOICES,
    }
    
    return render(request, 'reports/generate.html', context)


@login_required
def report_list(request):
    """Lista de reportes generados."""
    organization = request.organization
    
    # Filtros
    status = request.GET.get('status')
    template_id = request.GET.get('template')
    search = request.GET.get('search')
    
    reports = Report.objects.filter(organization=organization)
    
    if status:
        reports = reports.filter(status=status)
    
    if template_id:
        reports = reports.filter(template_id=template_id)
    
    if search:
        reports = reports.filter(name__icontains=search)
    
    reports = reports.select_related('template', 'generated_by').order_by('-created_at')
    
    # Templates para filtro
    templates = ReportTemplate.objects.filter(
        Q(organization=organization) | Q(organization__isnull=True, is_public=True)
    ).order_by('name')
    
    context = {
        'reports': reports,
        'status_choices': Report.STATUS_CHOICES,
        'templates': templates,
        'current_status': status,
        'current_template': template_id,
        'search': search,
    }
    
    return render(request, 'reports/report_list.html', context)


@login_required
def report_detail(request, pk):
    """Detalle de un reporte generado."""
    organization = request.organization
    
    report = get_object_or_404(
        Report,
        pk=pk,
        organization=organization
    )
    
    # Compartidos
    shares = ReportShare.objects.filter(report=report).select_related('shared_with')
    
    context = {
        'report': report,
        'shares': shares,
    }
    
    return render(request, 'reports/report_detail.html', context)


@login_required
def download_report(request, pk):
    """Descargar archivo de reporte."""
    organization = request.organization
    
    report = get_object_or_404(
        Report,
        pk=pk,
        organization=organization
    )
    
    if report.status != 'completed':
        messages.error(request, 'El reporte aún no está completado.')
        return redirect('reports:detail', pk=pk)
    
    if not report.file:
        messages.error(request, 'Archivo no disponible.')
        return redirect('reports:detail', pk=pk)
    
    # Servir archivo
    response = FileResponse(report.file.open(), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{report.name}.{report.output_format}"'
    
    return response


@login_required
def scheduled_list(request):
    """Lista de reportes programados."""
    organization = request.organization
    
    scheduled = ScheduledReport.objects.filter(
        organization=organization
    ).select_related('template', 'created_by').order_by('-is_active', 'next_run_at')
    
    context = {
        'scheduled_reports': scheduled,
    }
    
    return render(request, 'reports/scheduled_list.html', context)


@login_required
def scheduled_create(request, template_id):
    """Crear reporte programado."""
    organization = request.organization
    template = get_object_or_404(ReportTemplate, pk=template_id)
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            frequency = request.POST.get('frequency')
            time_str = request.POST.get('time', '09:00')
            output_format = request.POST.get('output_format', 'pdf')
            recipients = request.POST.get('recipients', '').split(',')
            
            # Crear programación
            scheduled = ScheduledReport.objects.create(
                template=template,
                organization=organization,
                name=name,
                frequency=frequency,
                time=datetime.strptime(time_str, '%H:%M').time(),
                output_format=output_format,
                recipients=[email.strip() for email in recipients if email.strip()],
                created_by=request.user
            )
            
            # Calcular próxima ejecución
            scheduled.calculate_next_run()
            
            messages.success(request, 'Reporte programado creado exitosamente.')
            return redirect('reports:scheduled')
            
        except Exception as e:
            messages.error(request, f'Error al crear programación: {str(e)}')
    
    context = {
        'template': template,
        'frequencies': ScheduledReport.FREQUENCY_CHOICES,
        'output_formats': Report.FORMAT_CHOICES,
    }
    
    return render(request, 'reports/scheduled_create.html', context)


@login_required
def scheduled_toggle(request, pk):
    """Activar/desactivar reporte programado."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    organization = request.organization
    
    scheduled = get_object_or_404(
        ScheduledReport,
        pk=pk,
        organization=organization
    )
    
    scheduled.is_active = not scheduled.is_active
    scheduled.save()
    
    return JsonResponse({
        'success': True,
        'is_active': scheduled.is_active
    })


@login_required
def share_report(request, pk):
    """Compartir reporte con otros usuarios."""
    organization = request.organization
    
    report = get_object_or_404(
        Report,
        pk=pk,
        organization=organization
    )
    
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            message = request.POST.get('message', '')
            can_download = request.POST.get('can_download') == 'on'
            expires_days = int(request.POST.get('expires_days', 30))
            
            # Buscar usuario
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            try:
                shared_with = User.objects.get(email=email)
            except User.DoesNotExist:
                shared_with = None
            
            # Crear compartido
            share = ReportShare.objects.create(
                report=report,
                shared_by=request.user,
                shared_with=shared_with,
                shared_with_email=email if not shared_with else '',
                message=message,
                can_download=can_download,
                expires_at=timezone.now() + timedelta(days=expires_days)
            )
            
            # TODO: Enviar notificación por email
            
            messages.success(request, f'Reporte compartido con {email}')
            return redirect('reports:detail', pk=pk)
            
        except Exception as e:
            messages.error(request, f'Error al compartir: {str(e)}')
    
    context = {
        'report': report,
    }
    
    return render(request, 'reports/share.html', context)


@login_required
def delete_report(request, pk):
    """Eliminar reporte generado."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    organization = request.organization
    
    report = get_object_or_404(
        Report,
        pk=pk,
        organization=organization
    )
    
    report.delete()
    
    return JsonResponse({'success': True})

