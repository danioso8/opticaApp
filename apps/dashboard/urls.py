from django.urls import path
from . import views
from .views_analytics import (
    analytics_dashboard,
    api_realtime_metrics,
    api_revenue_trend,
    api_heatmap_data,
    api_appointments_distribution,
    api_top_products,
    satisfaction_survey,
)
from .views_ar_tryon import (
    ar_tryon_home,
    ar_tryon_camera,
    ar_tryon_catalog,
    ar_tryon_sessions,
    ar_tryon_session_detail,
    api_record_try_on,
    api_save_photo,
    api_rate_frame,
    api_frame_details,
    api_detect_face_shape,
)

app_name = 'dashboard'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Perfil y Seguridad
    path('profile/', views.user_profile, name='user_profile'),
    path('security/', views.user_security, name='user_security'),
    
    # Dashboard principal
    path('', views.dashboard_home, name='home'),
    
    # Analytics Dashboard
    path('analytics/', analytics_dashboard, name='analytics_dashboard'),
    path('analytics/api/realtime-metrics/', api_realtime_metrics, name='api_realtime_metrics'),
    path('analytics/api/revenue-trend/', api_revenue_trend, name='api_revenue_trend'),
    path('analytics/api/heatmap-data/', api_heatmap_data, name='api_heatmap_data'),
    path('analytics/api/appointments-distribution/', api_appointments_distribution, name='api_appointments_distribution'),
    path('analytics/api/top-products/', api_top_products, name='api_top_products'),
    path('analytics/satisfaction-survey/', satisfaction_survey, name='satisfaction_survey'),
    
    # AR Virtual Try-On
    path('ar-tryon/', ar_tryon_home, name='ar_tryon_home'),
    path('ar-tryon/camera/', ar_tryon_camera, name='ar_tryon_camera'),
    path('ar-tryon/catalog/', ar_tryon_catalog, name='ar_tryon_catalog'),
    path('ar-tryon/sessions/', ar_tryon_sessions, name='ar_tryon_sessions'),
    path('ar-tryon/sessions/<int:session_id>/', ar_tryon_session_detail, name='ar_tryon_session_detail'),
    path('ar-tryon/api/record-try-on/', api_record_try_on, name='api_record_try_on'),
    path('ar-tryon/api/save-photo/', api_save_photo, name='api_save_photo'),
    path('ar-tryon/api/rate-frame/', api_rate_frame, name='api_rate_frame'),
    path('ar-tryon/api/frame/<int:frame_id>/', api_frame_details, name='api_frame_details'),
    path('ar-tryon/api/detect-face-shape/', api_detect_face_shape, name='api_detect_face_shape'),
    
    # Gestión de citas
    path('appointments/', views.appointments_list, name='appointments_list'),
    path('appointments/today/', views.appointments_today, name='appointments_today'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:pk>/change-status/', views.appointment_change_status, name='appointment_change_status'),
    
    # Configuración
    path('configuration/', views.configuration, name='configuration'),
    path('configuration/update/', views.update_general_config, name='update_general_config'),
    path('toggle-system/', views.toggle_system, name='toggle_system'),
    path('block-date/', views.block_date, name='block_date'),
    path('add-working-hour/', views.add_working_hour, name='add_working_hour'),
    path('toggle-working-hour/<int:pk>/', views.toggle_working_hour, name='toggle_working_hour'),
    path('delete-working-hour/<int:pk>/', views.delete_working_hour, name='delete_working_hour'),
    
    # Configuración de Notificaciones
    path('notifications/settings/', views.notification_settings, name='notification_settings'),
    path('notifications/settings/save/', views.save_notification_settings, name='save_notification_settings'),
    path('notifications/test/', views.test_notification, name='test_notification'),
    
    # Configuración de Landing Page
    path('configuration/landing-page/', views.landing_page_config, name='landing_page_config'),
    
    # Parámetros Clínicos
    path('configuration/clinical-parameters/', views.clinical_parameters, name='clinical_parameters'),
    path('configuration/clinical-parameters/create/', views.clinical_parameter_create, name='clinical_parameter_create'),
    path('configuration/clinical-parameters/<int:pk>/edit/', views.clinical_parameter_edit, name='clinical_parameter_edit'),
    path('configuration/clinical-parameters/<int:pk>/delete/', views.clinical_parameter_delete, name='clinical_parameter_delete'),
    path('configuration/clinical-parameters/bulk-import/', views.clinical_parameter_bulk_import, name='clinical_parameter_bulk_import'),
    
    # Plantillas de Medicación
    path('configuration/medication-templates/', views.medication_templates, name='medication_templates'),
    
    # Protocolos de Tratamiento
    path('configuration/treatment-protocols/', views.treatment_protocols, name='treatment_protocols'),
    
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
    path('patients/create-from-appointment/', views.create_patient_from_appointment, name='create_patient_from_appointment'),
    
    # Historia Clínica
    path('patients/<int:patient_id>/clinical-history/', views.clinical_history_list, name='clinical_history_list'),
    path('patients/<int:patient_id>/clinical-history/create/', views.clinical_history_create, name='clinical_history_create'),
    path('patients/<int:patient_id>/clinical-history/<int:history_id>/', views.clinical_history_detail, name='clinical_history_detail'),
    # Rutas de edición y eliminación deshabilitadas - Las historias clínicas son documentos permanentes
    # path('patients/<int:patient_id>/clinical-history/<int:history_id>/edit/', views.clinical_history_edit, name='clinical_history_edit'),
    # path('patients/<int:patient_id>/clinical-history/<int:history_id>/delete/', views.clinical_history_delete, name='clinical_history_delete'),
    path('patients/<int:patient_id>/clinical-history/<int:history_id>/pdf/', views.clinical_history_pdf, name='clinical_history_pdf'),
    path('patients/<int:patient_id>/clinical-history/latest-fundoscopy/', views.latest_fundoscopy, name='latest_fundoscopy'),
    
    # Examen Visual Simplificado
    path('patients/<int:patient_id>/visual-exam/create/', views.visual_exam_create, name='visual_exam_create'),
    path('patients/<int:patient_id>/visual-exam/<int:history_id>/edit/', views.visual_exam_edit, name='visual_exam_edit'),
    path('patients/<int:patient_id>/visual-exam/<int:history_id>/', views.visual_exam_detail, name='visual_exam_detail'),
    path('patients/<int:patient_id>/visual-exam/<int:history_id>/pdf/', views.visual_exam_pdf, name='visual_exam_pdf'),
    path('patients/<int:patient_id>/visual-exam/<int:history_id>/delete/', views.visual_exam_delete, name='visual_exam_delete'),
    
    # Calendario
    path('calendar/', views.calendar_view, name='calendar'),
    
    # Doctores / Optómetras
    path('doctors/', views.doctors_list, name='doctors_list'),
    path('doctors/create/', views.doctor_create, name='doctor_create'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('doctors/<int:pk>/edit/', views.doctor_edit, name='doctor_edit'),
    path('doctors/<int:pk>/delete/', views.doctor_delete, name='doctor_delete'),
    
    # WhatsApp API
    path('api/whatsapp/status/', views.whatsapp_status_api, name='whatsapp_status'),
    path('api/whatsapp/test-send/', views.whatsapp_test_send, name='whatsapp_test_send'),
    
    # Demostración
    path('notifications-demo/', views.notifications_demo, name='notifications_demo'),
]
