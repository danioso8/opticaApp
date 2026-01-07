from django.contrib import admin
from .models import (
    Employee, PayrollPeriod, AccrualConcept, DeductionConcept,
    PayrollEntry, Accrual, Deduction, ElectronicPayrollDocument,
    LaborContract, SocialBenefit, VacationRequest, EmployeeLoan,
    MonthlyProvision, PILAReport, Incapacity
)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['numero_documento', 'get_full_name', 'cargo', 'salario_basico', 'activo', 'fecha_ingreso']
    list_filter = ['activo', 'tipo_contrato', 'organization']
    search_fields = ['numero_documento', 'primer_nombre', 'primer_apellido', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('tipo_documento', 'numero_documento', 'primer_nombre', 'segundo_nombre', 
                      'primer_apellido', 'segundo_apellido')
        }),
        ('Contacto', {
            'fields': ('email', 'telefono', 'direccion', 'ciudad', 'departamento', 'pais')
        }),
        ('Información Laboral', {
            'fields': ('organization', 'tipo_contrato', 'subtipo_trabajador', 'fecha_ingreso', 
                      'fecha_retiro', 'cargo', 'salario_basico')
        }),
        ('Información Bancaria', {
            'fields': ('banco', 'tipo_cuenta', 'numero_cuenta')
        }),
        ('Estado', {
            'fields': ('activo', 'created_at', 'updated_at')
        }),
    )


@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_periodo', 'fecha_inicio', 'fecha_fin', 'fecha_pago', 'estado', 'total_neto', 'aprobado_por', 'rol_aprobador']
    list_filter = ['estado', 'tipo_periodo', 'rol_aprobador', 'organization']
    search_fields = ['nombre', 'aprobado_por__username', 'aprobado_por__first_name', 'aprobado_por__last_name']
    readonly_fields = ['created_at', 'updated_at', 'total_devengado', 'total_deducciones', 'total_neto', 
                       'aprobado_por', 'fecha_aprobacion', 'rol_aprobador']
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('organization', 'nombre', 'tipo_periodo')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin', 'fecha_pago')
        }),
        ('Estado y Aprobación', {
            'fields': ('estado', 'aprobado_por', 'fecha_aprobacion', 'rol_aprobador'),
            'classes': ('wide',)
        }),
        ('Totales', {
            'fields': ('total_devengado', 'total_deducciones', 'total_neto')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AccrualConcept)
class AccrualConceptAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo', 'activo', 'aplica_seguridad_social']
    list_filter = ['tipo', 'activo', 'organization']
    search_fields = ['codigo', 'nombre']


@admin.register(DeductionConcept)
class DeductionConceptAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo', 'porcentaje_base', 'activo']
    list_filter = ['tipo', 'activo', 'organization']
    search_fields = ['codigo', 'nombre']


class AccrualInline(admin.TabularInline):
    model = Accrual
    extra = 1


class DeductionInline(admin.TabularInline):
    model = Deduction
    extra = 1


@admin.register(PayrollEntry)
class PayrollEntryAdmin(admin.ModelAdmin):
    list_display = ['periodo', 'empleado', 'dias_trabajados', 'total_devengado', 'total_deducciones', 'total_neto']
    list_filter = ['periodo', 'organization']
    search_fields = ['empleado__numero_documento', 'empleado__primer_nombre', 'empleado__primer_apellido']
    readonly_fields = ['total_devengado', 'total_deducciones', 'total_neto', 'created_at', 'updated_at']
    inlines = [AccrualInline, DeductionInline]


@admin.register(ElectronicPayrollDocument)
class ElectronicPayrollDocumentAdmin(admin.ModelAdmin):
    list_display = ['consecutivo', 'entrada', 'estado', 'fecha_generacion', 'fecha_validacion', 'cufe']
    list_filter = ['estado', 'organization']
    search_fields = ['consecutivo', 'cufe', 'entrada__empleado__numero_documento']
    readonly_fields = ['fecha_generacion', 'created_at', 'updated_at']
    date_hierarchy = 'fecha_generacion'


# ===== NUEVOS MODELOS: PRESTACIONES SOCIALES Y EXTENSIONES =====

@admin.register(LaborContract)
class LaborContractAdmin(admin.ModelAdmin):
    list_display = ['numero_contrato', 'employee', 'tipo_contrato', 'fecha_inicio', 'fecha_fin', 'salario_contratado', 'estado']
    list_filter = ['tipo_contrato', 'estado', 'organization']
    search_fields = ['numero_contrato', 'employee__numero_documento', 'employee__primer_nombre', 'employee__primer_apellido']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Información del Contrato', {
            'fields': ('organization', 'employee', 'numero_contrato', 'tipo_contrato', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin', 'fecha_terminacion')
        }),
        ('Información Salarial', {
            'fields': ('salario_contratado', 'auxilio_transporte', 'otros_beneficios')
        }),
        ('Jornada Laboral', {
            'fields': ('horas_semanales', 'cargo')
        }),
        ('Terminación', {
            'fields': ('causal_terminacion', 'indemnizacion')
        }),
        ('Documentos', {
            'fields': ('archivo_contrato',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SocialBenefit)
class SocialBenefitAdmin(admin.ModelAdmin):
    list_display = ['employee', 'tipo', 'fecha_inicio', 'fecha_fin', 'dias_causados', 'valor_causado', 'saldo_pendiente']
    list_filter = ['tipo', 'organization']
    search_fields = ['employee__numero_documento', 'employee__primer_nombre', 'employee__primer_apellido']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Información General', {
            'fields': ('organization', 'employee', 'tipo', 'calculado_automaticamente')
        }),
        ('Período de Causación', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Valores', {
            'fields': ('dias_causados', 'valor_causado', 'valor_pagado', 'saldo_pendiente')
        }),
        ('Pago', {
            'fields': ('fecha_pago', 'observaciones')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VacationRequest)
class VacationRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'fecha_inicio', 'fecha_fin', 'dias_solicitados', 'estado', 'pago_anticipado', 'valor_pago']
    list_filter = ['estado', 'pago_anticipado', 'organization']
    search_fields = ['employee__numero_documento', 'employee__primer_nombre', 'employee__primer_apellido']
    readonly_fields = ['created_at', 'updated_at', 'aprobado_por', 'fecha_aprobacion']
    date_hierarchy = 'fecha_inicio'
    actions = ['aprobar_vacaciones', 'rechazar_vacaciones']
    
    fieldsets = (
        ('Información General', {
            'fields': ('organization', 'employee', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_solicitud', 'fecha_inicio', 'fecha_fin', 'fecha_reintegro')
        }),
        ('Días', {
            'fields': ('dias_solicitados', 'dias_habiles', 'dias_calendario')
        }),
        ('Período que Causan', {
            'fields': ('periodo_inicio', 'periodo_fin')
        }),
        ('Pago', {
            'fields': ('pago_anticipado', 'valor_pago')
        }),
        ('Aprobación', {
            'fields': ('aprobado_por', 'fecha_aprobacion', 'motivo_rechazo')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def aprobar_vacaciones(self, request, queryset):
        for vacation in queryset.filter(estado='PENDIENTE'):
            vacation.aprobar(request.user)
        self.message_user(request, f"{queryset.count()} solicitudes aprobadas exitosamente")
    aprobar_vacaciones.short_description = "Aprobar vacaciones seleccionadas"
    
    def rechazar_vacaciones(self, request, queryset):
        for vacation in queryset.filter(estado='PENDIENTE'):
            vacation.rechazar(request.user, "Rechazado desde admin")
        self.message_user(request, f"{queryset.count()} solicitudes rechazadas")
    rechazar_vacaciones.short_description = "Rechazar vacaciones seleccionadas"


@admin.register(EmployeeLoan)
class EmployeeLoanAdmin(admin.ModelAdmin):
    list_display = ['numero_prestamo', 'employee', 'fecha_solicitud', 'monto_solicitado', 'numero_cuotas', 'valor_cuota', 'saldo_pendiente', 'estado']
    list_filter = ['estado', 'organization']
    search_fields = ['numero_prestamo', 'employee__numero_documento', 'employee__primer_nombre', 'employee__primer_apellido']
    readonly_fields = ['created_at', 'updated_at', 'valor_cuota', 'aprobado_por', 'fecha_aprobacion', 'fecha_desembolso']
    date_hierarchy = 'fecha_solicitud'
    
    fieldsets = (
        ('Información del Préstamo', {
            'fields': ('organization', 'employee', 'numero_prestamo', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_solicitud', 'fecha_aprobacion', 'fecha_desembolso')
        }),
        ('Montos', {
            'fields': ('monto_solicitado', 'monto_aprobado')
        }),
        ('Cuotas', {
            'fields': ('numero_cuotas', 'tasa_interes', 'valor_cuota', 'cuotas_pagadas', 'saldo_pendiente')
        }),
        ('Detalles', {
            'fields': ('motivo_solicitud', 'observaciones', 'aprobado_por')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MonthlyProvision)
class MonthlyProvisionAdmin(admin.ModelAdmin):
    list_display = ['period', 'employee', 'cesantias', 'intereses_cesantias', 'prima', 'vacaciones', 'total_provision']
    list_filter = ['period', 'organization']
    search_fields = ['employee__numero_documento', 'employee__primer_nombre', 'employee__primer_apellido']
    readonly_fields = ['created_at', 'updated_at', 'total_provision']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información General', {
            'fields': ('organization', 'period', 'employee', 'calculado_automaticamente')
        }),
        ('Salario Base', {
            'fields': ('salario_base',)
        }),
        ('Provisiones', {
            'fields': ('cesantias', 'intereses_cesantias', 'prima', 'vacaciones', 'total_provision')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PILAReport)
class PILAReportAdmin(admin.ModelAdmin):
    list_display = ['numero_planilla', 'mes', 'anio', 'total_empleados', 'total_salud', 'total_pension', 'total_aportes', 'estado']
    list_filter = ['estado', 'mes', 'anio', 'organization']
    search_fields = ['numero_planilla']
    readonly_fields = ['created_at', 'updated_at', 'fecha_generacion', 'fecha_envio']
    date_hierarchy = 'fecha_generacion'
    
    fieldsets = (
        ('Información General', {
            'fields': ('organization', 'numero_planilla', 'mes', 'anio', 'estado')
        }),
        ('Totales', {
            'fields': ('total_empleados', 'total_salud', 'total_pension', 'total_riesgos', 'total_caja', 'total_aportes')
        }),
        ('Fechas', {
            'fields': ('fecha_generacion', 'fecha_envio')
        }),
        ('Archivo', {
            'fields': ('archivo_pila',)
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Incapacity)
class IncapacityAdmin(admin.ModelAdmin):
    list_display = ['employee', 'tipo', 'fecha_inicio', 'fecha_fin', 'dias_incapacidad', 'total_incapacidad', 'estado']
    list_filter = ['estado', 'tipo', 'organization']
    search_fields = ['employee__primer_nombre', 'employee__primer_apellido', 'employee__numero_documento', 'diagnostico']
    readonly_fields = ['dias_incapacidad', 'valor_dia', 'total_incapacidad', 'created_at', 'updated_at', 'fecha_aprobacion']
    date_hierarchy = 'fecha_inicio'
    
    fieldsets = (
        ('Información del Empleado', {
            'fields': ('organization', 'employee')
        }),
        ('Detalles de la Incapacidad', {
            'fields': ('tipo', 'fecha_inicio', 'fecha_fin', 'dias_incapacidad')
        }),
        ('Información Médica', {
            'fields': ('diagnostico', 'numero_incapacidad', 'documento_soporte')
        }),
        ('Cálculo del Pago', {
            'fields': ('porcentaje_pago', 'valor_dia', 'total_incapacidad')
        }),
        ('Estado y Aprobación', {
            'fields': ('estado', 'aprobada_por', 'fecha_aprobacion', 'observaciones')
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('employee', 'created_by', 'aprobada_por')
