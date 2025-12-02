from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard principal
    path('', views.dashboard_home, name='home'),
    
    # Gestión de citas
    path('appointments/', views.appointments_list, name='appointments_list'),
    path('appointments/today/', views.appointments_today, name='appointments_today'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:pk>/change-status/', views.appointment_change_status, name='appointment_change_status'),
    
    # Configuración
    path('configuration/', views.configuration, name='configuration'),
    path('toggle-system/', views.toggle_system, name='toggle_system'),
    path('block-date/', views.block_date, name='block_date'),
    path('add-working-hour/', views.add_working_hour, name='add_working_hour'),
    path('toggle-working-hour/<int:pk>/', views.toggle_working_hour, name='toggle_working_hour'),
    path('delete-working-hour/<int:pk>/', views.delete_working_hour, name='delete_working_hour'),
    
    # Horarios específicos
    path('configuration/add-specific-schedule/', views.add_specific_schedule, name='add_specific_schedule'),
    path('configuration/specific-schedule/<int:pk>/toggle/', views.toggle_specific_schedule, name='toggle_specific_schedule'),
    path('configuration/specific-schedule/<int:pk>/delete/', views.delete_specific_schedule, name='delete_specific_schedule'),
    
    # Pacientes
    path('patients/', views.patients_list, name='patients_list'),
    path('patients/create/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_edit, name='patient_edit'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    path('patients/search-api/', views.patient_search_api, name='patient_search_api'),
    
    # Historia Clínica
    path('patients/<int:patient_id>/clinical-history/', views.clinical_history_list, name='clinical_history_list'),
    path('patients/<int:patient_id>/clinical-history/create/', views.clinical_history_create, name='clinical_history_create'),
    path('patients/<int:patient_id>/clinical-history/<int:history_id>/', views.clinical_history_detail, name='clinical_history_detail'),
    path('patients/<int:patient_id>/clinical-history/<int:history_id>/edit/', views.clinical_history_edit, name='clinical_history_edit'),
    path('patients/<int:patient_id>/clinical-history/<int:history_id>/delete/', views.clinical_history_delete, name='clinical_history_delete'),
    
    # Calendario
    path('calendar/', views.calendar_view, name='calendar'),
]
