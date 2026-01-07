"""
Modelos avanzados para sistema automatizado de nómina
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.organizations.base_models import TenantModel


class PayrollAutomationConfig(TenantModel):
    """
    Configuración de automatización de nómina
    """
    # Calendario de pagos
    dia_pago_mensual = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1)],
        help_text="Día del mes para pago de nómina mensual (1-31)"
    )
    dia_pago_quincenal_1 = models.IntegerField(
        default=15,
        validators=[MinValueValidator(1)],
        help_text="Primer día de pago quincenal"
    )
    dia_pago_quincenal_2 = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1)],
        help_text="Segundo día de pago quincenal"
    )
    
    # Automatización
    auto_generar_borradores = models.BooleanField(
        default=True,
        help_text="Generar automáticamente borradores de nómina"
    )
    dias_anticipacion_borrador = models.IntegerField(
        default=5,
        help_text="Días antes de la fecha de pago para generar borrador"
    )
    
    # Notificaciones
    enviar_notificacion_borrador = models.BooleanField(default=True)
    enviar_notificacion_aprobacion = models.BooleanField(default=True)
    enviar_notificacion_procesado = models.BooleanField(default=True)
    
    # Validaciones automáticas
    validar_salario_minimo = models.BooleanField(default=True)
    validar_seguridad_social = models.BooleanField(default=True)
    validar_prestaciones = models.BooleanField(default=True)
    
    # Cálculos automáticos
    calcular_horas_extras = models.BooleanField(default=True)
    calcular_auxilio_transporte = models.BooleanField(default=True)
    calcular_prestaciones_sociales = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración de Automatización'
        verbose_name_plural = 'Configuraciones de Automatización'
    
    def __str__(self):
        return f"Config Automatización - {self.organization.name}"


class PayrollPeriodWorkflow(TenantModel):
    """
    Workflow de aprobación de períodos de nómina
    """
    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador - Generado automáticamente'),
        ('EN_REVISION', 'En Revisión - Esperando aprobación'),
        ('APROBADO', 'Aprobado - Listo para procesar'),
        ('PROCESADO', 'Procesado - Nómina ejecutada'),
        ('RECHAZADO', 'Rechazado - Requiere correcciones'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    period = models.OneToOneField(
        'payroll.PayrollPeriod',
        on_delete=models.CASCADE,
        related_name='workflow'
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='BORRADOR')
    
    # Timestamps de transiciones
    fecha_borrador = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_procesado = models.DateTimeField(null=True, blank=True)
    fecha_rechazo = models.DateTimeField(null=True, blank=True)
    
    # Usuarios responsables
    usuario_creador = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='periodos_creados'
    )
    usuario_revisor = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='periodos_revisados'
    )
    usuario_aprobador = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='periodos_aprobados'
    )
    
    # Notas y comentarios
    notas_borrador = models.TextField(blank=True, help_text="Observaciones del borrador generado")
    notas_revision = models.TextField(blank=True, help_text="Comentarios de la revisión")
    notas_aprobacion = models.TextField(blank=True, help_text="Comentarios de aprobación")
    motivo_rechazo = models.TextField(blank=True, help_text="Razón del rechazo")
    
    # Validaciones automáticas
    validaciones_pasadas = models.JSONField(default=dict, blank=True)
    errores_detectados = models.JSONField(default=list, blank=True)
    advertencias = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Workflow de Período'
        verbose_name_plural = 'Workflows de Períodos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.period} - {self.get_estado_display()}"
    
    def puede_enviar_a_revision(self):
        return self.estado == 'BORRADOR'
    
    def puede_aprobar(self):
        return self.estado == 'EN_REVISION'
    
    def puede_procesar(self):
        return self.estado == 'APROBADO'
    
    def puede_rechazar(self):
        return self.estado in ['BORRADOR', 'EN_REVISION']


class EmployeePeriodAssignment(TenantModel):
    """
    Asignación de empleados a períodos de nómina
    """
    period = models.ForeignKey(
        'payroll.PayrollPeriod',
        on_delete=models.CASCADE,
        related_name='employee_assignments'
    )
    employee = models.ForeignKey(
        'payroll.Employee',
        on_delete=models.CASCADE,
        related_name='period_assignments'
    )
    
    # Estado de inclusión
    incluido = models.BooleanField(
        default=True,
        help_text="Si está marcado, el empleado será incluido en este período"
    )
    motivo_exclusion = models.TextField(
        blank=True,
        help_text="Razón por la que no se incluye (vacaciones, licencia, etc.)"
    )
    
    # Datos del período (pueden cambiar respecto al empleado)
    salario_periodo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Salario aplicable para este período"
    )
    dias_trabajados = models.IntegerField(
        default=30,
        help_text="Días efectivamente trabajados en el período"
    )
    
    # Cálculos automáticos
    total_devengado = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_deducido = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    neto_pagar = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Control
    calculado_automaticamente = models.BooleanField(default=False)
    fecha_calculo = models.DateTimeField(null=True, blank=True)
    requiere_recalculo = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Asignación de Empleado a Período'
        verbose_name_plural = 'Asignaciones de Empleados a Períodos'
        unique_together = ['period', 'employee']
        ordering = ['employee__primer_apellido', 'employee__primer_nombre']
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.period}"


class PayrollCalculationLog(TenantModel):
    """
    Log de cálculos automáticos de nómina
    """
    period = models.ForeignKey(
        'payroll.PayrollPeriod',
        on_delete=models.CASCADE,
        related_name='calculation_logs'
    )
    
    # Información del cálculo
    tipo_calculo = models.CharField(
        max_length=50,
        choices=[
            ('INICIAL', 'Cálculo Inicial'),
            ('RECALCULO', 'Recálculo'),
            ('AJUSTE', 'Ajuste Manual'),
            ('AUTOMATICO', 'Cálculo Automático Programado'),
        ]
    )
    
    # Resultados
    empleados_procesados = models.IntegerField(default=0)
    empleados_con_errores = models.IntegerField(default=0)
    total_devengado = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_deducciones = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_neto = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Detalles
    detalles = models.JSONField(default=dict)
    errores = models.JSONField(default=list)
    warnings = models.JSONField(default=list)
    
    # Tiempo de ejecución
    tiempo_inicio = models.DateTimeField(auto_now_add=True)
    tiempo_fin = models.DateTimeField(null=True, blank=True)
    duracion_segundos = models.FloatField(null=True, blank=True)
    
    # Usuario
    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Log de Cálculo'
        verbose_name_plural = 'Logs de Cálculos'
        ordering = ['-tiempo_inicio']
    
    def __str__(self):
        return f"Cálculo {self.tipo_calculo} - {self.period} - {self.tiempo_inicio}"


class PayrollNotification(TenantModel):
    """
    Notificaciones automáticas del sistema de nómina
    """
    TIPO_CHOICES = [
        ('BORRADOR_GENERADO', 'Borrador Generado'),
        ('REVISION_PENDIENTE', 'Revisión Pendiente'),
        ('APROBACION_REQUERIDA', 'Aprobación Requerida'),
        ('NOMINA_APROBADA', 'Nómina Aprobada'),
        ('NOMINA_PROCESADA', 'Nómina Procesada'),
        ('NOMINA_RECHAZADA', 'Nómina Rechazada'),
        ('ERROR_CALCULO', 'Error en Cálculo'),
        ('ADVERTENCIA', 'Advertencia'),
    ]
    
    period = models.ForeignKey(
        'payroll.PayrollPeriod',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    
    # Destinatarios
    usuarios = models.ManyToManyField('auth.User', related_name='payroll_notifications')
    
    # Contenido
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    datos_adicionales = models.JSONField(default=dict, blank=True)
    
    # Estado
    leida = models.BooleanField(default=False)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    
    # Acción
    requiere_accion = models.BooleanField(default=False)
    url_accion = models.CharField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notificación de Nómina'
        verbose_name_plural = 'Notificaciones de Nómina'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.period}"
