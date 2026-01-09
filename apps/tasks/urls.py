"""
URLs para el sistema de Gestión de Tareas
"""
from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Kanban Board
    path('', views.kanban_board, name='kanban'),
    
    # Mis Tareas
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    
    # Calendario
    path('calendar/', views.calendar_view, name='calendar'),
    
    # CRUD de Tareas
    path('create/', views.task_create, name='create'),
    path('<int:pk>/', views.task_detail, name='detail'),
    path('<int:pk>/delete/', views.task_delete, name='delete'),
    
    # Actualizar estado (AJAX)
    path('<int:pk>/update-status/', views.task_update_status, name='update_status'),
    
    # Comentarios (AJAX)
    path('<int:pk>/add-comment/', views.add_comment, name='add_comment'),
    
    # Checklist (AJAX)
    path('<int:pk>/checklist/<int:item_id>/toggle/', views.toggle_checklist_item, name='toggle_checklist'),
]
