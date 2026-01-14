from django.urls import path, include
from . import views
from . import views_exam_orders
from . import views_clinical_exams
from . import views_team
from . import views_employee
from . import views_whatsapp_baileys
from . import views_certificates
from . import views_modules
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
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Perfil y Seguridad
    path('profile/', views.user_profile, name='user_profile'),
    path('security/', views.user_security, name='user_security'),
    
    # Dashboard principal
    path('', views.dashboard_home, name='home'),
    
    # Gestión de Equipo (Usuarios y Permisos)
    path('team/', views_team.team_list, name='team_list'),
    path('team/add/', views_team.team_member_add, name='team_member_add'),
    path('team/<int:member_id>/edit/', views_team.team_member_edit, name='team_member_edit'),
    path('team/<int:member_id>/permissions/', views_team.team_member_permissions, name='team_member_permissions'),
    path('team/<int:member_id>/delete/', views_team.team_member_delete, name='team_member_delete'),
    path('team/modules/', views_team.team_modules_list, name='team_modules_list'),
    path('team/activity/', views_team.team_activity_log, name='team_activity_log'),
    path('team/doctor/<int:doctor_id>/data/', views_team.get_doctor_data, name='get_doctor_data'),
    path('team/employee/<int:employee_id>/data/', views_team.get_employee_data_for_team, name='get_employee_data_for_team'),
    
    # Gestión de Empleados
    path('employees/', views_employee.employee_list, name='employee_list'),
    path('employees/create/', views_employee.employee_create, name='employee_create'),
    path('employees/<int:pk>/update/', views_employee.employee_update, name='employee_update'),
    path('employees/<int:pk>/delete/', views_employee.employee_delete, name='employee_delete'),
    path('employees/<int:pk>/data/', views_employee.get_employee_data, name='get_employee_data'),
    
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
    path('appointments/<int:pk>/edit/', views.appointment_edit, name='appointment_edit'),
    path('appointments/<int:pk>/change-status/', views.appointment_change_status, name='appointment_change_status'),
    path('appointments/<int:pk>/resend-notification/', views.appointment_resend_notification, name='appointment_resend_notification'),
    
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
    
    # WhatsApp Baileys (Local)
    path('whatsapp-baileys/', views_whatsapp_baileys.whatsapp_baileys_config, name='whatsapp_baileys_config'),
    path('whatsapp-baileys/start/', views_whatsapp_baileys.whatsapp_start_session, name='whatsapp_start_session'),
    path('whatsapp-baileys/qr/', views_whatsapp_baileys.whatsapp_get_qr, name='whatsapp_get_qr'),
    path('whatsapp-baileys/status/', views_whatsapp_baileys.whatsapp_get_status, name='whatsapp_get_status'),
    path('whatsapp-baileys/logout/', views_whatsapp_baileys.whatsapp_logout, name='whatsapp_logout'),
    path('whatsapp-baileys/clear/', views_whatsapp_baileys.whatsapp_clear_session, name='whatsapp_clear_session'),
    path('whatsapp-baileys/test/', views_whatsapp_baileys.whatsapp_test_message, name='whatsapp_test_message'),
    
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
    path('configuration/specific-schedule/<int:pk>/edit/', views.edit_specific_schedule, name='edit_specific_schedule'),
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
    
    # Certificados
    path('patients/<int:patient_id>/visual-exam/<int:history_id>/certificate/', views_certificates.visual_exam_certificate_pdf, name='visual_exam_certificate'),
    path('patients/<int:patient_id>/visual-exam/<int:history_id>/medical-certificate/', views_certificates.medical_certificate_pdf, name='medical_certificate'),
    
    # Órdenes de Exámenes Especiales
    path('patients/<int:patient_id>/history/<int:history_id>/exam-order/create/', views_exam_orders.exam_order_create, name='exam_order_create'),
    path('exam-orders/', views_exam_orders.exam_order_list, name='exam_order_list'),
    path('exam-orders/<int:order_id>/', views_exam_orders.exam_order_detail, name='exam_order_detail'),
    path('exam-orders/<int:order_id>/update-status/', views_exam_orders.exam_order_update_status, name='exam_order_update_status'),
    path('exam-orders/<int:order_id>/cancel/', views_exam_orders.exam_order_cancel, name='exam_order_cancel'),
    path('exam-orders/<int:order_id>/delete/', views_exam_orders.exam_order_delete, name='exam_order_delete'),
    path('patients/<int:patient_id>/history/<int:history_id>/exam-order/<int:order_id>/pdf/', views_exam_orders.exam_order_pdf, name='exam_order_pdf'),
    
    # Resultados de Exámenes - Tonometría
    path('patients/<int:patient_id>/history/<int:history_id>/tonometry/create/', views_clinical_exams.tonometry_create, name='tonometry_create'),
    path('patients/<int:patient_id>/history/<int:history_id>/tonometry/create/<int:order_id>/', views_clinical_exams.tonometry_create, name='tonometry_create_from_order'),
    path('patients/<int:patient_id>/history/<int:history_id>/tonometry/<int:tonometry_id>/', views_clinical_exams.tonometry_detail, name='tonometry_detail'),
    path('patients/<int:patient_id>/history/<int:history_id>/tonometry/<int:tonometry_id>/pdf/', views_clinical_exams.tonometry_pdf, name='tonometry_pdf'),
    
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
    path('whatsapp/usage-history/', views.whatsapp_usage_history, name='whatsapp_usage_history'),
    
    # Push Notifications API
    path('api/notifications/new-appointments/', views.get_new_appointments, name='api_new_appointments'),
    path('api/notifications/mark-read/', views.mark_notification_read, name='api_mark_notification_read'),
    
    # Testing
    path('test-notifications/', views.test_notifications_page, name='test_notifications'),
    
    # Demostración
    path('notifications-demo/', views.notifications_demo, name='notifications_demo'),
    
    # Sidebar Customizer
    path('menu/customize/', views.sidebar_customizer, name='customize_menu'),
    
    # Módulos y Suscripciones
    path('modules/marketplace/', views_modules.module_marketplace, name='module_marketplace'),
    path('modules/selector/', views_modules.module_selector, name='module_selector'),
    path('modules/checkout/', views_modules.module_checkout, name='module_checkout'),
    path('modules/my-plan/', views_modules.my_plan, name='my_plan'),
    
    # Promociones y Campañas de Marketing
    path('promociones/', include('apps.promotions.urls')),
    
    # Workflows (Automatización)
    path('workflows/', include('apps.workflows.urls')),
    
    # Tasks (Gestión de Tareas)
    path('tasks/', include('apps.tasks.urls')),
    
    # Reports (Reportes)
    path('reports/', include('apps.reports.urls')),
    
    # Audit (Auditoría)
    path('audit/', include('apps.audit.urls')),
]
