"""
URLs para el sistema de auditoría.
"""
from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    # Dashboard
    path('', views.audit_dashboard, name='dashboard'),
    
    # Logs
    path('logs/', views.audit_logs, name='logs'),
    path('logs/<int:pk>/', views.audit_detail, name='detail'),
    path('logs/export/', views.audit_export, name='export'),
    
    # Análisis
    path('user/<int:user_id>/', views.audit_user_activity, name='user_activity'),
    
    # Configuración
    path('config/', views.audit_config_list, name='config'),
    
    # API
    path('api/stats/', views.audit_stats_api, name='stats_api'),
]
