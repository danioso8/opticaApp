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
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    
    # Calendario
    path('calendar/', views.calendar_view, name='calendar'),
]
