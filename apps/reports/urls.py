"""
URLs para el sistema de reportes.
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard
    path('', views.report_dashboard, name='dashboard'),
    
    # Plantillas
    path('templates/', views.template_list, name='templates'),
    path('templates/<int:pk>/', views.template_detail, name='template_detail'),
    
    # Generar reportes
    path('generate/<int:template_id>/', views.generate_report, name='generate'),
    
    # Reportes generados
    path('reports/', views.report_list, name='reports'),
    path('reports/<int:pk>/', views.report_detail, name='detail'),
    path('reports/<int:pk>/download/', views.download_report, name='download'),
    path('reports/<int:pk>/share/', views.share_report, name='share'),
    path('reports/<int:pk>/delete/', views.delete_report, name='delete'),
    
    # Programados
    path('scheduled/', views.scheduled_list, name='scheduled'),
    path('scheduled/create/<int:template_id>/', views.scheduled_create, name='scheduled_create'),
    path('scheduled/<int:pk>/toggle/', views.scheduled_toggle, name='scheduled_toggle'),
]
