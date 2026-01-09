"""
URLs para el sistema de Workflows
"""
from django.urls import path
from . import views

app_name = 'workflows'

urlpatterns = [
    # Dashboard de workflows
    path('', views.workflow_list, name='list'),
    path('<int:pk>/', views.workflow_detail, name='detail'),
    
    # Instancias de workflows
    path('instances/', views.instance_list, name='instance_list'),
    path('instances/<int:pk>/', views.instance_detail, name='instance_detail'),
    path('instances/<int:instance_pk>/transition/<int:transition_pk>/', views.execute_transition, name='execute_transition'),
    
    # Aprobaciones
    path('approvals/', views.my_approvals, name='my_approvals'),
    path('approvals/<int:pk>/approve/', views.approve_transition, name='approve'),
    path('approvals/<int:pk>/reject/', views.reject_transition, name='reject'),
    
    # API Endpoints
    path('api/pending-count/', views.api_pending_approvals_count, name='api_pending_count'),
    path('api/<int:pk>/states/', views.api_workflow_states, name='api_states'),
]
