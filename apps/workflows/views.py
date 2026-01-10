"""
Vistas para el sistema de Workflows
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from .models import (
    WorkflowDefinition, WorkflowTransition, WorkflowAction,
    WorkflowInstance, WorkflowHistory, WorkflowApproval
)
from .services import (
    WorkflowService, WorkflowApprovalService, WorkflowHistoryService
)
from apps.organizations.decorators import require_feature


@login_required
@require_feature('workflows')
def workflow_list(request):
    """Lista de workflows disponibles"""
    organization = request.organization
    
    # Workflows activos
    workflows = WorkflowDefinition.objects.filter(
        organization=organization,
        is_active=True
    ).annotate(
        active_instances=Count('instances', filter=Q(instances__status='active')),
        total_instances=Count('instances')
    ).order_by('-created_at')
    
    # Estadísticas
    total_workflows = workflows.count()
    total_active_instances = WorkflowInstance.objects.filter(
        workflow__organization=organization,
        status='active'
    ).count()
    
    # Mis aprobaciones pendientes
    pending_approvals = WorkflowApproval.objects.filter(
        approver=request.user,
        status='pending',
        transition__workflow__organization=organization
    ).count()
    
    context = {
        'workflows': workflows,
        'total_workflows': total_workflows,
        'total_active_instances': total_active_instances,
        'pending_approvals': pending_approvals,
    }
    
    return render(request, 'workflows/workflow_list.html', context)


@login_required
def workflow_detail(request, pk):
    """Detalle de un workflow"""
    organization = request.organization
    workflow = get_object_or_404(
        WorkflowDefinition,
        pk=pk,
        organization=organization
    )
    
    # Transiciones del workflow
    transitions = WorkflowTransition.objects.filter(
        workflow=workflow
    ).select_related('workflow').order_by('from_state', 'to_state')
    
    # Acciones automáticas
    actions = WorkflowAction.objects.filter(
        workflow=workflow
    ).order_by('transition', 'order')
    
    # Instancias activas
    active_instances = WorkflowInstance.objects.filter(
        workflow=workflow,
        status='active'
    ).select_related('created_by').order_by('-created_at')[:10]
    
    # Estadísticas
    stats = {
        'total_instances': WorkflowInstance.objects.filter(workflow=workflow).count(),
        'active_instances': WorkflowInstance.objects.filter(workflow=workflow, status='active').count(),
        'completed_instances': WorkflowInstance.objects.filter(workflow=workflow, status='completed').count(),
        'cancelled_instances': WorkflowInstance.objects.filter(workflow=workflow, status='cancelled').count(),
    }
    
    context = {
        'workflow': workflow,
        'transitions': transitions,
        'actions': actions,
        'active_instances': active_instances,
        'stats': stats,
    }
    
    return render(request, 'workflows/workflow_detail.html', context)


@login_required
def instance_list(request):
    """Lista de instancias de workflows"""
    organization = request.organization
    
    # Filtros
    workflow_id = request.GET.get('workflow')
    status = request.GET.get('status')
    
    instances = WorkflowInstance.objects.filter(
        workflow__organization=organization
    ).select_related('workflow', 'created_by')
    
    if workflow_id:
        instances = instances.filter(workflow_id=workflow_id)
    
    if status:
        instances = instances.filter(status=status)
    
    instances = instances.order_by('-created_at')
    
    # Workflows disponibles para filtro
    workflows = WorkflowDefinition.objects.filter(
        organization=organization,
        is_active=True
    ).order_by('name')
    
    context = {
        'instances': instances,
        'workflows': workflows,
        'selected_workflow': workflow_id,
        'selected_status': status,
    }
    
    return render(request, 'workflows/instance_list.html', context)


@login_required
def instance_detail(request, pk):
    """Detalle de una instancia de workflow"""
    organization = request.organization
    instance = get_object_or_404(
        WorkflowInstance,
        pk=pk,
        workflow__organization=organization
    )
    
    # Transiciones disponibles desde el estado actual
    available_transitions = WorkflowService.get_available_transitions(
        workflow=instance.workflow,
        current_state=instance.current_state
    )
    
    # Verificar cuáles transiciones puede ejecutar el usuario
    transitions_with_permission = []
    for transition in available_transitions:
        can_transition = WorkflowService.can_transition(
            instance=instance,
            transition=transition,
            user=request.user
        )
        transitions_with_permission.append({
            'transition': transition,
            'can_execute': can_transition
        })
    
    # Historial de la instancia
    history = WorkflowHistoryService.get_instance_history(instance)
    
    # Aprobaciones pendientes (si las hay)
    pending_approvals = WorkflowApproval.objects.filter(
        instance=instance,
        status='pending'
    ).select_related('transition', 'requested_by', 'approver')
    
    context = {
        'instance': instance,
        'transitions': transitions_with_permission,
        'history': history,
        'pending_approvals': pending_approvals,
    }
    
    return render(request, 'workflows/instance_detail.html', context)


@login_required
def execute_transition(request, instance_pk, transition_pk):
    """Ejecuta una transición de workflow"""
    if request.method != 'POST':
        messages.error(request, 'Método no permitido')
        return redirect('workflows:instance_detail', pk=instance_pk)
    
    organization = request.organization
    instance = get_object_or_404(
        WorkflowInstance,
        pk=instance_pk,
        workflow__organization=organization
    )
    
    transition = get_object_or_404(
        WorkflowTransition,
        pk=transition_pk,
        workflow=instance.workflow
    )
    
    # Verificar si puede ejecutar la transición
    if not WorkflowService.can_transition(instance, transition, request.user):
        messages.error(request, 'No tienes permiso para ejecutar esta transición')
        return redirect('workflows:instance_detail', pk=instance_pk)
    
    # Si requiere aprobación y el usuario no es aprobador
    if transition.require_approval:
        # Solicitar aprobación
        approval = WorkflowApprovalService.request_approval(
            instance=instance,
            transition=transition,
            requested_by=request.user,
            comments=request.POST.get('comments', '')
        )
        messages.success(request, f'Solicitud de aprobación enviada. ID: {approval.id}')
        return redirect('workflows:instance_detail', pk=instance_pk)
    
    # Ejecutar transición directamente
    try:
        success = WorkflowService.execute_transition(
            instance=instance,
            transition=transition,
            user=request.user,
            comments=request.POST.get('comments', ''),
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        if success:
            messages.success(request, f'Transición ejecutada: {transition.from_state} → {transition.to_state}')
        else:
            messages.error(request, 'No se pudo ejecutar la transición')
    except Exception as e:
        messages.error(request, f'Error al ejecutar transición: {str(e)}')
    
    return redirect('workflows:instance_detail', pk=instance_pk)


@login_required
def my_approvals(request):
    """Mis aprobaciones pendientes"""
    organization = request.organization
    
    # Aprobaciones pendientes donde el usuario es aprobador
    pending_approvals = WorkflowApproval.objects.filter(
        approver=request.user,
        status='pending',
        transition__workflow__organization=organization
    ).select_related(
        'instance', 'instance__workflow', 'transition', 'requested_by'
    ).order_by('-requested_at')
    
    # Aprobaciones completadas (últimas 20)
    completed_approvals = WorkflowApproval.objects.filter(
        approver=request.user,
        status__in=['approved', 'rejected'],
        transition__workflow__organization=organization
    ).select_related(
        'instance', 'instance__workflow', 'transition', 'requested_by'
    ).order_by('-responded_at')[:20]
    
    context = {
        'pending_approvals': pending_approvals,
        'completed_approvals': completed_approvals,
    }
    
    return render(request, 'workflows/my_approvals.html', context)


@login_required
def approve_transition(request, pk):
    """Aprobar una transición"""
    if request.method != 'POST':
        messages.error(request, 'Método no permitido')
        return redirect('workflows:my_approvals')
    
    organization = request.organization
    approval = get_object_or_404(
        WorkflowApproval,
        pk=pk,
        approver=request.user,
        status='pending',
        transition__workflow__organization=organization
    )
    
    comments = request.POST.get('comments', '')
    
    try:
        WorkflowApprovalService.approve_transition(
            approval=approval,
            approver=request.user,
            comments=comments,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, 'Transición aprobada y ejecutada exitosamente')
    except Exception as e:
        messages.error(request, f'Error al aprobar: {str(e)}')
    
    return redirect('workflows:my_approvals')


@login_required
def reject_transition(request, pk):
    """Rechazar una transición"""
    if request.method != 'POST':
        messages.error(request, 'Método no permitido')
        return redirect('workflows:my_approvals')
    
    organization = request.organization
    approval = get_object_or_404(
        WorkflowApproval,
        pk=pk,
        approver=request.user,
        status='pending',
        transition__workflow__organization=organization
    )
    
    comments = request.POST.get('comments', '')
    
    if not comments:
        messages.error(request, 'Debes proporcionar un motivo para rechazar')
        return redirect('workflows:my_approvals')
    
    try:
        WorkflowApprovalService.reject_transition(
            approval=approval,
            approver=request.user,
            comments=comments
        )
        messages.success(request, 'Solicitud rechazada')
    except Exception as e:
        messages.error(request, f'Error al rechazar: {str(e)}')
    
    return redirect('workflows:my_approvals')


# API Endpoints para AJAX

@login_required
def api_pending_approvals_count(request):
    """Retorna el número de aprobaciones pendientes del usuario (para badge)"""
    count = WorkflowApproval.objects.filter(
        approver=request.user,
        status='pending',
        transition__workflow__organization=request.organization
    ).count()
    
    return JsonResponse({'count': count})


@login_required
def api_workflow_states(request, pk):
    """Retorna los estados de un workflow (para visualización)"""
    workflow = get_object_or_404(
        WorkflowDefinition,
        pk=pk,
        organization=request.organization
    )
    
    states = workflow.states if workflow.states else []
    
    return JsonResponse({
        'states': states,
        'initial_state': workflow.initial_state,
        'final_states': workflow.final_states
    })


