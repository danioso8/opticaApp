"""
Vistas para el sistema de Gestión de Tareas
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Case, When, IntegerField
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import (
    Task, TaskCategory, TaskComment, TaskActivity,
    TaskChecklist, TaskReminder
)
from .services import (
    TaskService, TaskCommentService, TaskActivityService,
    TaskChecklistService, TaskReminderService
)


@login_required
def kanban_board(request):
    """Vista Kanban de tareas"""
    organization = request.organization
    
    # Filtros
    category_id = request.GET.get('category')
    assigned_to = request.GET.get('assigned_to')
    priority = request.GET.get('priority')
    search = request.GET.get('search', '')
    
    # Base queryset
    tasks = Task.objects.filter(organization=organization)
    
    # Aplicar filtros
    if category_id:
        tasks = tasks.filter(category_id=category_id)
    if assigned_to:
        tasks = tasks.filter(assigned_to_id=assigned_to)
    if priority:
        tasks = tasks.filter(priority=priority)
    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Agrupar por estado
    todo_tasks = tasks.filter(status='todo').select_related('assigned_to', 'category', 'created_by').order_by('-priority', 'due_date')
    in_progress_tasks = tasks.filter(status='in_progress').select_related('assigned_to', 'category', 'created_by').order_by('-priority', 'due_date')
    review_tasks = tasks.filter(status='review').select_related('assigned_to', 'category', 'created_by').order_by('-priority', 'due_date')
    done_tasks = tasks.filter(status='done').select_related('assigned_to', 'category', 'created_by').order_by('-completed_at')[:20]
    
    # Categorías y usuarios para filtros
    categories = TaskCategory.objects.filter(organization=organization, is_active=True).order_by('name')
    team_members = organization.members.filter(is_active=True).select_related('user').order_by('user__first_name')
    
    # Estadísticas rápidas
    stats = {
        'total': tasks.count(),
        'todo': todo_tasks.count(),
        'in_progress': in_progress_tasks.count(),
        'review': review_tasks.count(),
        'done': done_tasks.count(),
    }
    
    context = {
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'review_tasks': review_tasks,
        'done_tasks': done_tasks,
        'categories': categories,
        'team_members': team_members,
        'stats': stats,
        'selected_category': category_id,
        'selected_assigned': assigned_to,
        'selected_priority': priority,
        'search': search,
    }
    
    return render(request, 'tasks/kanban.html', context)


@login_required
def my_tasks(request):
    """Mis tareas asignadas"""
    organization = request.organization
    
    # Tareas asignadas al usuario actual
    tasks = Task.objects.filter(
        organization=organization,
        assigned_to=request.user
    ).exclude(
        status='done'
    ).select_related('category', 'created_by').order_by('-priority', 'due_date')
    
    # Categorías
    categories = TaskCategory.objects.filter(organization=organization, is_active=True).order_by('name')
    
    # Estadísticas simples
    stats = {
        'total': tasks.count(),
        'pending': tasks.filter(status='pending').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'review': tasks.filter(status='review').count(),
    }
    
    context = {
        'tasks': tasks,
        'categories': categories,
        'stats': stats,
    }
    
    return render(request, 'tasks/my_tasks.html', context)


@login_required
def task_detail(request, pk):
    """Detalle de una tarea"""
    organization = request.organization
    task = get_object_or_404(
        Task,
        pk=pk,
        organization=organization
    )
    
    # Comentarios
    comments = TaskComment.objects.filter(task=task).select_related('user').order_by('created_at')
    
    # Checklist
    checklist_items = TaskChecklist.objects.filter(task=task).order_by('order', 'created_at')
    
    # Actividad
    activities = TaskActivity.objects.filter(task=task).select_related('user').order_by('-timestamp')[:20]
    
    # Recordatorios
    reminders = TaskReminder.objects.filter(task=task, is_active=True).order_by('remind_at')
    
    # Calcular progreso del checklist
    if checklist_items.exists():
        total_items = checklist_items.count()
        completed_items = checklist_items.filter(is_completed=True).count()
        checklist_progress = int((completed_items / total_items) * 100)
    else:
        checklist_progress = 0
    
    context = {
        'task': task,
        'comments': comments,
        'checklist_items': checklist_items,
        'activities': activities,
        'reminders': reminders,
        'checklist_progress': checklist_progress,
    }
    
    return render(request, 'tasks/task_detail.html', context)


@login_required
def task_create(request):
    """Crear nueva tarea"""
    if request.method == 'POST':
        organization = request.organization
        
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        category_id = request.POST.get('category')
        assigned_to_id = request.POST.get('assigned_to')
        priority = request.POST.get('priority', 'medium')
        due_date = request.POST.get('due_date')
        
        if not title:
            messages.error(request, 'El título es requerido')
            return redirect('tasks:kanban')
        
        # Crear tarea
        task_data = {
            'title': title,
            'description': description,
            'priority': priority,
        }
        
        if category_id:
            task_data['category_id'] = category_id
        if assigned_to_id:
            task_data['assigned_to_id'] = assigned_to_id
        if due_date:
            task_data['due_date'] = due_date
        
        task = TaskService.create_task(
            organization=organization,
            created_by=request.user,
            **task_data
        )
        
        messages.success(request, f'Tarea creada: {task.title}')
        return redirect('tasks:detail', pk=task.pk)
    
    # GET - mostrar formulario
    categories = TaskCategory.objects.filter(
        organization=request.organization,
        is_active=True
    ).order_by('name')
    
    team_members = request.organization.members.filter(
        is_active=True
    ).select_related('user').order_by('user__first_name')
    
    context = {
        'categories': categories,
        'team_members': team_members,
    }
    
    return render(request, 'tasks/task_create.html', context)


@login_required
def task_update_status(request, pk):
    """Actualizar estado de tarea (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    organization = request.organization
    task = get_object_or_404(Task, pk=pk, organization=organization)
    
    new_status = request.POST.get('status')
    
    if new_status not in ['todo', 'in_progress', 'review', 'done', 'cancelled']:
        return JsonResponse({'success': False, 'error': 'Estado inválido'}, status=400)
    
    old_status = task.status
    task.status = new_status
    
    if new_status == 'done':
        task.completed_at = timezone.now()
    
    task.save()
    
    # Registrar actividad
    TaskActivityService.log_activity(
        task=task,
        user=request.user,
        action='status_changed',
        description=f'Estado cambiado: {old_status} → {new_status}'
    )
    
    return JsonResponse({
        'success': True,
        'new_status': new_status,
        'old_status': old_status
    })


@login_required
def task_delete(request, pk):
    """Eliminar tarea"""
    if request.method != 'POST':
        messages.error(request, 'Método no permitido')
        return redirect('tasks:kanban')
    
    organization = request.organization
    task = get_object_or_404(Task, pk=pk, organization=organization)
    
    task_title = task.title
    task.delete()
    
    messages.success(request, f'Tarea eliminada: {task_title}')
    return redirect('tasks:kanban')


@login_required
def add_comment(request, pk):
    """Agregar comentario a tarea (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    organization = request.organization
    task = get_object_or_404(Task, pk=pk, organization=organization)
    
    comment_text = request.POST.get('comment', '').strip()
    
    if not comment_text:
        return JsonResponse({'success': False, 'error': 'El comentario no puede estar vacío'}, status=400)
    
    comment = TaskCommentService.add_comment(
        task=task,
        user=request.user,
        comment=comment_text
    )
    
    return JsonResponse({
        'success': True,
        'comment': {
            'id': comment.id,
            'user': request.user.get_full_name() or request.user.username,
            'comment': comment.comment,
            'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),
        }
    })


@login_required
def toggle_checklist_item(request, pk, item_id):
    """Marcar/desmarcar item de checklist (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    organization = request.organization
    task = get_object_or_404(Task, pk=pk, organization=organization)
    item = get_object_or_404(TaskChecklist, pk=item_id, task=task)
    
    item.is_completed = not item.is_completed
    if item.is_completed:
        item.completed_by = request.user
        item.completed_at = timezone.now()
    else:
        item.completed_by = None
        item.completed_at = None
    
    item.save()
    
    # Calcular progreso
    total_items = task.checklist_items.count()
    completed_items = task.checklist_items.filter(is_completed=True).count()
    progress = int((completed_items / total_items) * 100) if total_items > 0 else 0
    
    # Registrar actividad
    action = 'marcó' if item.is_completed else 'desmarcó'
    TaskActivityService.log_activity(
        task=task,
        user=request.user,
        action='checklist_updated',
        description=f'{action} checklist: {item.item_text}'
    )
    
    return JsonResponse({
        'success': True,
        'is_completed': item.is_completed,
        'progress': progress
    })


@login_required
def calendar_view(request):
    """Vista de calendario de tareas"""
    organization = request.organization
    
    # Obtener mes actual o del parámetro
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if month and year:
        current_date = datetime(int(year), int(month), 1)
    else:
        current_date = datetime.now()
    
    # Tareas del mes
    start_date = current_date.replace(day=1)
    if current_date.month == 12:
        end_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
    else:
        end_date = current_date.replace(month=current_date.month + 1, day=1)
    
    tasks = Task.objects.filter(
        organization=organization,
        due_date__gte=start_date,
        due_date__lt=end_date
    ).exclude(status='done').select_related('assigned_to', 'category').order_by('due_date')
    
    # Agrupar tareas por fecha
    tasks_by_date = {}
    for task in tasks:
        date_key = task.due_date.strftime('%Y-%m-%d')
        if date_key not in tasks_by_date:
            tasks_by_date[date_key] = []
        tasks_by_date[date_key].append(task)
    
    context = {
        'current_date': current_date,
        'tasks_by_date': json.dumps(tasks_by_date, default=str),
        'tasks': tasks,
    }
    
    return render(request, 'tasks/calendar.html', context)
