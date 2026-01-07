"""
URLs para el módulo de nómina
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmployeeViewSet, PayrollPeriodViewSet, AccrualConceptViewSet,
    DeductionConceptViewSet, PayrollEntryViewSet, AccrualViewSet,
    DeductionViewSet, ElectronicPayrollDocumentViewSet,
    # Vistas del frontend
    payroll_dashboard, employee_list, employee_create, employee_edit, employee_delete,
    period_list, period_create, period_detail, period_calculate, period_approve,
    concept_list, accrual_concept_create, accrual_concept_edit, accrual_concept_delete,
    deduction_concept_create, deduction_concept_edit, deduction_concept_delete,
    download_payslip, download_payroll_report, send_to_dian, check_dian_status,
    # Vistas del workflow
    workflow_dashboard, workflow_enviar_revision, workflow_aprobar, workflow_rechazar,
    workflow_procesar, workflow_period_detail, workflow_generar_borrador, workflow_configuracion,
    # Vistas nuevas: Prestaciones sociales
    contract_list, contract_create, contract_detail,
    vacation_list, vacation_create, vacation_approve, vacation_reject,
    loan_list, loan_create, loan_approve, loan_disburse,
    social_benefits_dashboard, provision_list, pila_list, pila_create,
    # Incapacidades y empleados liquidados
    incapacity_list, incapacity_create, incapacity_edit, incapacity_delete,
    incapacity_approve, incapacity_reject, terminated_employees,
    # Edición manual de entradas
    entry_edit, entry_add_accrual, entry_add_deduction,
    entry_delete_accrual, entry_delete_deduction
)

app_name = 'payroll'

# Router para API REST
router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'accrual-concepts', AccrualConceptViewSet, basename='accrual-concept')
router.register(r'deduction-concepts', DeductionConceptViewSet, basename='deduction-concept')
router.register(r'periods', PayrollPeriodViewSet, basename='period')
router.register(r'entries', PayrollEntryViewSet, basename='entry')
router.register(r'accruals', AccrualViewSet, basename='accrual')
router.register(r'deductions', DeductionViewSet, basename='deduction')
router.register(r'documents', ElectronicPayrollDocumentViewSet, basename='document')

urlpatterns = [
    # Frontend URLs
    path('', payroll_dashboard, name='payroll_dashboard'),
    
    # Empleados
    path('empleados/', employee_list, name='employee_list'),
    path('empleados/crear/', employee_create, name='employee_create'),
    path('empleados/<int:pk>/editar/', employee_edit, name='employee_edit'),
    path('empleados/<int:pk>/eliminar/', employee_delete, name='employee_delete'),
    
    # Períodos de nómina
    path('periodos/', period_list, name='period_list'),
    path('periodos/crear/', period_create, name='period_create'),
    path('periodos/<int:pk>/', period_detail, name='period_detail'),
    path('periodos/<int:pk>/calcular/', period_calculate, name='period_calculate'),
    path('periodos/<int:pk>/aprobar/', period_approve, name='period_approve'),
    
    # Conceptos
    path('conceptos/', concept_list, name='concept_list'),
    path('conceptos/devengados/crear/', accrual_concept_create, name='accrual_concept_create'),
    path('conceptos/devengados/<int:pk>/editar/', accrual_concept_edit, name='accrual_concept_edit'),
    path('conceptos/devengados/<int:pk>/eliminar/', accrual_concept_delete, name='accrual_concept_delete'),
    path('conceptos/deducciones/crear/', deduction_concept_create, name='deduction_concept_create'),
    path('conceptos/deducciones/<int:pk>/editar/', deduction_concept_edit, name='deduction_concept_edit'),
    path('conceptos/deducciones/<int:pk>/eliminar/', deduction_concept_delete, name='deduction_concept_delete'),
    
    # PDFs y DIAN
    path('descargar-desprendible/<int:entry_id>/', download_payslip, name='download_payslip'),
    path('descargar-reporte/<int:period_id>/', download_payroll_report, name='download_payroll_report'),
    path('enviar-dian/<int:period_id>/', send_to_dian, name='send_to_dian'),
    path('consultar-dian/<int:period_id>/', check_dian_status, name='check_dian_status'),
    
    # Workflow URLs
    path('workflow/', workflow_dashboard, name='workflow_dashboard'),
    path('workflow/generar-borrador/', workflow_generar_borrador, name='workflow_generar_borrador'),
    path('workflow/configuracion/', workflow_configuracion, name='workflow_configuracion'),
    path('workflow/periodo/<int:period_id>/', workflow_period_detail, name='workflow_period_detail'),
    path('workflow/<int:period_id>/enviar-revision/', workflow_enviar_revision, name='workflow_enviar_revision'),
    path('workflow/<int:period_id>/aprobar/', workflow_aprobar, name='workflow_aprobar'),
    path('workflow/<int:period_id>/rechazar/', workflow_rechazar, name='workflow_rechazar'),
    path('workflow/<int:period_id>/procesar/', workflow_procesar, name='workflow_procesar'),
    
    # Contratos Laborales
    path('contratos/', contract_list, name='contract_list'),
    path('contratos/crear/', contract_create, name='contract_create'),
    path('contratos/<int:pk>/', contract_detail, name='contract_detail'),
    
    # Vacaciones
    path('vacaciones/', vacation_list, name='vacation_list'),
    path('vacaciones/crear/', vacation_create, name='vacation_create'),
    path('vacaciones/<int:pk>/aprobar/', vacation_approve, name='vacation_approve'),
    path('vacaciones/<int:pk>/rechazar/', vacation_reject, name='vacation_reject'),
    
    # Préstamos
    path('prestamos/', loan_list, name='loan_list'),
    path('prestamos/crear/', loan_create, name='loan_create'),
    path('prestamos/<int:pk>/aprobar/', loan_approve, name='loan_approve'),
    path('prestamos/<int:pk>/desembolsar/', loan_disburse, name='loan_disburse'),
    
    # Prestaciones Sociales
    path('prestaciones/', social_benefits_dashboard, name='social_benefits_dashboard'),
    path('provisiones/', provision_list, name='provision_list'),
    
    # PILA
    path('pila/', pila_list, name='pila_list'),
    path('pila/crear/', pila_create, name='pila_create'),
    
    # Incapacidades
    path('incapacidades/', incapacity_list, name='incapacity_list'),
    path('incapacidades/crear/', incapacity_create, name='incapacity_create'),
    path('incapacidades/<int:pk>/editar/', incapacity_edit, name='incapacity_edit'),
    path('incapacidades/<int:pk>/eliminar/', incapacity_delete, name='incapacity_delete'),
    path('incapacidades/<int:pk>/aprobar/', incapacity_approve, name='incapacity_approve'),
    path('incapacidades/<int:pk>/rechazar/', incapacity_reject, name='incapacity_reject'),
    
    # Empleados Liquidados
    path('periodos/<int:period_id>/empleados-liquidados/', terminated_employees, name='terminated_employees'),
    
    # Edición Manual de Entradas (Borrador)
    path('entradas/<int:pk>/editar/', entry_edit, name='entry_edit'),
    path('entradas/<int:entry_id>/agregar-devengado/', entry_add_accrual, name='entry_add_accrual'),
    path('entradas/<int:entry_id>/agregar-deduccion/', entry_add_deduction, name='entry_add_deduction'),
    path('devengados/<int:pk>/eliminar/', entry_delete_accrual, name='entry_delete_accrual'),
    path('deducciones/<int:pk>/eliminar/', entry_delete_deduction, name='entry_delete_deduction'),
    
    # API REST
    path('api/', include(router.urls)),
]
