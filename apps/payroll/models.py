"""
Modelos para el módulo de Nómina Electrónica
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from apps.organizations.base_models import TenantModel


class Employee(TenantModel):
    """Modelo de empleados para nómina"""
    
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('PA', 'Pasaporte'),
        ('TI', 'Tarjeta de Identidad'),
    ]
    
    TIPO_CONTRATO_CHOICES = [
        ('INDEFINIDO', 'Indefinido'),
        ('FIJO', 'Término Fijo'),
        ('OBRA', 'Obra o Labor'),
        ('APRENDIZAJE', 'Aprendizaje'),
        ('PRESTACION', 'Prestación de Servicios'),
    ]
    
    SUBTIPO_TRABAJADOR_CHOICES = [
        ('00', 'Dependiente'),
        ('01', 'Dependiente Pensionado'),
        ('02', 'Dependiente Pensionado Activo'),
    ]
    
    # Información personal
    tipo_documento = models.CharField(max_length=2, choices=TIPO_DOCUMENTO_CHOICES, default='CC')
    numero_documento = models.CharField(max_length=20, unique=True, db_index=True)
    primer_nombre = models.CharField(max_length=100)
    segundo_nombre = models.CharField(max_length=100, blank=True, null=True)
    primer_apellido = models.CharField(max_length=100)
    segundo_apellido = models.CharField(max_length=100, blank=True, null=True)
    
    # Contacto
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    pais = models.CharField(max_length=2, default='CO')
    
    # Información laboral
    tipo_contrato = models.CharField(max_length=20, choices=TIPO_CONTRATO_CHOICES, default='INDEFINIDO')
    subtipo_trabajador = models.CharField(max_length=2, choices=SUBTIPO_TRABAJADOR_CHOICES, default='00')
    fecha_ingreso = models.DateField()
    fecha_retiro = models.DateField(blank=True, null=True)
    cargo = models.CharField(max_length=200)
    
    # Salario
    salario_basico = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Información bancaria
    banco = models.CharField(max_length=100, blank=True, null=True)
    tipo_cuenta = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('AHORROS', 'Ahorros'),
        ('CORRIENTE', 'Corriente'),
    ])
    numero_cuenta = models.CharField(max_length=50, blank=True, null=True)
    
    # Estado
    activo = models.BooleanField(default=True)
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['primer_apellido', 'primer_nombre']
        indexes = [
            models.Index(fields=['organization', 'activo']),
            models.Index(fields=['numero_documento']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.numero_documento}"
    
    def get_full_name(self):
        """Retorna el nombre completo del empleado"""
        nombres = ' '.join(filter(None, [self.primer_nombre, self.segundo_nombre]))
        apellidos = ' '.join(filter(None, [self.primer_apellido, self.segundo_apellido]))
        return f"{nombres} {apellidos}".strip()


class PayrollPeriod(TenantModel):
    """Período de nómina"""
    
    PERIODO_CHOICES = [
        ('QUINCENAL', 'Quincenal'),
        ('MENSUAL', 'Mensual'),
    ]
    
    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('CALCULADO', 'Calculado'),
        ('APROBADO', 'Aprobado'),
        ('ENVIADO_DIAN', 'Enviado a DIAN'),
        ('VALIDADO_DIAN', 'Validado por DIAN'),
        ('RECHAZADO_DIAN', 'Rechazado por DIAN'),
        ('PAGADO', 'Pagado'),
    ]
    
    nombre = models.CharField(max_length=200)
    tipo_periodo = models.CharField(max_length=20, choices=PERIODO_CHOICES, default='MENSUAL')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_pago = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='BORRADOR')
    
    # Totales
    total_devengado = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_deducciones = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_neto = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Observaciones
    observaciones = models.TextField(blank=True, null=True)
    
    # Auditoría de aprobación
    aprobado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payroll_periods_aprobados',
        help_text="Contador o propietario que aprobó la nómina"
    )
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    rol_aprobador = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=[
            ('PROPIETARIO', 'Propietario'),
            ('CONTADOR', 'Contador'),
            ('ADMIN', 'Administrador'),
        ],
        help_text="Rol del usuario que aprobó"
    )
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='payroll_periods_created')
    
    class Meta:
        verbose_name = 'Período de Nómina'
        verbose_name_plural = 'Períodos de Nómina'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['organization', 'estado']),
            models.Index(fields=['fecha_inicio', 'fecha_fin']),
        ]
        unique_together = ['organization', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_periodo_display()}"


class AccrualConcept(TenantModel):
    """Conceptos de devengados (ingresos)"""
    
    TIPO_CHOICES = [
        ('SALARIO', 'Salario Básico'),
        ('HORAS_EXTRAS', 'Horas Extras'),
        ('RECARGO', 'Recargo Nocturno/Festivo'),
        ('AUXILIO', 'Auxilio'),
        ('COMISION', 'Comisión'),
        ('BONIFICACION', 'Bonificación'),
        ('PRESTACION', 'Prestación Social'),
        ('VACACIONES', 'Vacaciones'),
        ('INCAPACIDAD', 'Incapacidad'),
        ('LICENCIA', 'Licencia'),
        ('OTRO', 'Otro'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True, db_index=True)
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    descripcion = models.TextField(blank=True, null=True)
    
    # Configuración
    activo = models.BooleanField(default=True)
    aplica_seguridad_social = models.BooleanField(default=True, help_text="¿Aplica para base de seguridad social?")
    aplica_prestaciones = models.BooleanField(default=True, help_text="¿Aplica para base de prestaciones sociales?")
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Concepto de Devengado'
        verbose_name_plural = 'Conceptos de Devengados'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['organization', 'activo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class DeductionConcept(TenantModel):
    """Conceptos de deducciones"""
    
    TIPO_CHOICES = [
        ('SALUD', 'Salud (4%)'),
        ('PENSION', 'Pensión (4%)'),
        ('FSP', 'Fondo de Solidaridad Pensional'),
        ('RETENCION', 'Retención en la Fuente'),
        ('PRESTAMO', 'Préstamo'),
        ('EMBARGO', 'Embargo Judicial'),
        ('COOPERATIVA', 'Cooperativa'),
        ('SINDICATO', 'Sindicato'),
        ('AHORRO', 'Ahorro Programado'),
        ('LIBRANZA', 'Libranza'),
        ('FONDO', 'Fondo de Empleados'),
        ('OTRO', 'Otra Deducción'),
    ]
    
    BASE_CALCULO_CHOICES = [
        ('SALARIO', 'Sobre Salario Base'),
        ('VALOR_FIJO', 'Valor Fijo'),
        ('DEVENGADO', 'Sobre Total Devengado'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True, db_index=True)
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    descripcion = models.TextField(blank=True, null=True)
    
    # Configuración
    activo = models.BooleanField(default=True)
    es_obligatoria = models.BooleanField(default=False, help_text="Deducción de ley (salud, pensión, etc.)")
    porcentaje_base = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Porcentaje que se aplica automáticamente (ej: 4 para salud)"
    )
    base_calculo = models.CharField(
        max_length=20,
        choices=BASE_CALCULO_CHOICES,
        default='SALARIO',
        help_text="Sobre qué base se calcula la deducción"
    )
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Concepto de Deducción'
        verbose_name_plural = 'Conceptos de Deducciones'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['organization', 'activo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class PayrollEntry(TenantModel):
    """Entrada de nómina por empleado"""
    
    periodo = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='entries')
    empleado = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='payroll_entries')
    
    # Días trabajados
    dias_trabajados = models.IntegerField(default=30)
    
    # Totales
    total_devengado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deducciones = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_neto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Observaciones
    observaciones = models.TextField(blank=True, null=True)
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Entrada de Nómina'
        verbose_name_plural = 'Entradas de Nómina'
        ordering = ['periodo', 'empleado']
        unique_together = ['periodo', 'empleado']
        indexes = [
            models.Index(fields=['organization', 'periodo']),
            models.Index(fields=['empleado']),
        ]
    
    def __str__(self):
        return f"{self.periodo} - {self.empleado.get_full_name()}"
    
    def calculate_totals(self):
        """Calcula los totales de devengados y deducciones"""
        self.total_devengado = sum(
            accrual.valor for accrual in self.accruals.all()
        )
        self.total_deducciones = sum(
            deduction.valor for deduction in self.deductions.all()
        )
        self.total_neto = self.total_devengado - self.total_deducciones
        self.save()


class Accrual(TenantModel):
    """Devengado (ingreso) por empleado"""
    
    entrada = models.ForeignKey(PayrollEntry, on_delete=models.CASCADE, related_name='accruals')
    concepto = models.ForeignKey(AccrualConcept, on_delete=models.PROTECT)
    
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    
    observaciones = models.TextField(blank=True, null=True)
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Devengado'
        verbose_name_plural = 'Devengados'
        ordering = ['entrada', 'concepto']
        indexes = [
            models.Index(fields=['organization', 'entrada']),
        ]
    
    def __str__(self):
        return f"{self.concepto.nombre}: ${self.valor}"
    
    def save(self, *args, **kwargs):
        """Calcula el valor automáticamente si no está definido"""
        if not self.valor:
            self.valor = self.cantidad * self.valor_unitario
        super().save(*args, **kwargs)


class Deduction(TenantModel):
    """Deducción por empleado"""
    
    entrada = models.ForeignKey(PayrollEntry, on_delete=models.CASCADE, related_name='deductions')
    concepto = models.ForeignKey(DeductionConcept, on_delete=models.PROTECT)
    
    porcentaje = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Porcentaje aplicado"
    )
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    
    observaciones = models.TextField(blank=True, null=True)
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Deducción'
        verbose_name_plural = 'Deducciones'
        ordering = ['entrada', 'concepto']
        indexes = [
            models.Index(fields=['organization', 'entrada']),
        ]
    
    def __str__(self):
        return f"{self.concepto.nombre}: ${self.valor}"


class ElectronicPayrollDocument(TenantModel):
    """Documento electrónico de nómina para DIAN"""
    
    ESTADO_CHOICES = [
        ('GENERADO', 'Generado'),
        ('FIRMADO', 'Firmado'),
        ('ENVIADO', 'Enviado a DIAN'),
        ('APROBADO', 'Aprobado por DIAN'),
        ('RECHAZADO', 'Rechazado por DIAN'),
    ]
    
    entrada = models.OneToOneField(PayrollEntry, on_delete=models.CASCADE, related_name='electronic_document')
    
    # Identificación del documento
    consecutivo = models.CharField(max_length=50, unique=True, db_index=True)
    cufe = models.CharField(max_length=255, blank=True, null=True, help_text="Código Único de Factura Electrónica")
    
    # Documento XML
    xml_content = models.TextField(blank=True, null=True)
    xml_signed = models.TextField(blank=True, null=True)
    
    # Estado
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='GENERADO')
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(blank=True, null=True)
    fecha_validacion = models.DateTimeField(blank=True, null=True)
    
    # Respuesta DIAN
    respuesta_dian = models.TextField(blank=True, null=True)
    codigo_respuesta = models.CharField(max_length=10, blank=True, null=True)
    mensaje_respuesta = models.TextField(blank=True, null=True)
    
    # Archivos
    pdf_file = models.FileField(upload_to='payroll/pdf/', blank=True, null=True)
    xml_file = models.FileField(upload_to='payroll/xml/', blank=True, null=True)
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Documento Electrónico de Nómina'
        verbose_name_plural = 'Documentos Electrónicos de Nómina'
        ordering = ['-fecha_generacion']
        indexes = [
            models.Index(fields=['organization', 'estado']),
            models.Index(fields=['consecutivo']),
            models.Index(fields=['cufe']),
        ]
    
    def __str__(self):
        return f"Documento {self.consecutivo} - {self.estado}"


# ============================================================================
# MODELOS AVANZADOS PARA AUTOMATIZACIÓN
# ============================================================================

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
    
    # Porcentajes de deducciones configurables (Colombia 2026)
    porcentaje_salud = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('4.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Porcentaje de salud que aporta el empleado (por defecto 4%)"
    )
    porcentaje_pension = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('4.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Porcentaje de pensión que aporta el empleado (por defecto 4%)"
    )
    porcentaje_fsp_4_a_16 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Porcentaje FSP para salarios entre 4 y 16 SMLV (por defecto 1%)"
    )
    porcentaje_fsp_16_a_17 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.20'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Porcentaje FSP para salarios entre 16 y 17 SMLV (por defecto 1.2%)"
    )
    porcentaje_fsp_17_a_18 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.40'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Porcentaje FSP para salarios entre 17 y 18 SMLV (por defecto 1.4%)"
    )
    porcentaje_fsp_18_a_19 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.60'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Porcentaje FSP para salarios entre 18 y 19 SMLV (por defecto 1.6%)"
    )
    porcentaje_fsp_19_a_20 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.80'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Porcentaje FSP para salarios entre 19 y 20 SMLV (por defecto 1.8%)"
    )
    porcentaje_fsp_mayor_20 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('2.00'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Porcentaje FSP para salarios mayores a 20 SMLV (por defecto 2%)"
    )
    
    # Valores legales Colombia 2026
    salario_minimo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('1300000'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Salario mínimo legal vigente"
    )
    auxilio_transporte = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('162000'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Auxilio de transporte legal vigente"
    )
    
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
        PayrollPeriod,
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
    usuario_procesador = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='periodos_procesados'
    )
    
    # Notas y comentarios
    notas_revision = models.TextField(blank=True)
    notas_aprobacion = models.TextField(blank=True)
    motivo_rechazo = models.TextField(blank=True)
    
    # Validaciones
    validaciones_pasadas = models.TextField(blank=True, default='')
    errores_validacion = models.TextField(blank=True, default='')
    warnings = models.TextField(blank=True, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Workflow de Período'
        verbose_name_plural = 'Workflows de Períodos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'estado']),
        ]
    
    def __str__(self):
        return f"Workflow {self.period} - {self.estado}"
    
    def puede_enviar_a_revision(self):
        """Puede enviar a revisión si está en borrador"""
        return self.estado == 'BORRADOR'
    
    def puede_aprobar(self):
        """Puede aprobar si está en revisión"""
        return self.estado == 'EN_REVISION'
    
    def puede_rechazar(self):
        """Puede rechazar si está en revisión o aprobado"""
        return self.estado in ['EN_REVISION', 'APROBADO']
    
    def puede_procesar(self):
        """Puede procesar si está aprobado"""
        return self.estado == 'APROBADO'


class EmployeePeriodAssignment(TenantModel):
    """
    Asignación de empleados a períodos de nómina
    """
    period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        related_name='asignaciones'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='asignaciones_periodo'
    )
    
    # Estado
    incluido = models.BooleanField(
        default=True,
        help_text="Si está incluido en este período de nómina"
    )
    motivo_exclusion = models.TextField(blank=True)
    
    # Información del período
    salario_periodo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    dias_trabajados = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1)],
        help_text="Días trabajados en este período"
    )
    
    # Totales calculados
    total_devengado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_deducido = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    neto_pagar = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Control de cálculos
    calculado_automaticamente = models.BooleanField(default=False)
    fecha_calculo = models.DateTimeField(null=True, blank=True)
    requiere_recalculo = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Asignación de Empleado a Período'
        verbose_name_plural = 'Asignaciones de Empleados a Períodos'
        unique_together = ['period', 'employee']
        ordering = ['employee__primer_apellido', 'employee__primer_nombre']
        indexes = [
            models.Index(fields=['organization', 'period', 'incluido']),
        ]
    
    def __str__(self):
        return f"{self.employee} - {self.period}"


class PayrollCalculationLog(TenantModel):
    """
    Log de cálculos automáticos de nómina
    """
    TIPO_CALCULO_CHOICES = [
        ('INICIAL', 'Cálculo Inicial'),
        ('RECALCULO', 'Recálculo'),
        ('AUTOMATICO', 'Generación Automática'),
        ('MANUAL', 'Ajuste Manual'),
    ]
    
    period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        related_name='logs_calculo'
    )
    tipo_calculo = models.CharField(max_length=20, choices=TIPO_CALCULO_CHOICES)
    
    # Resultados
    empleados_procesados = models.IntegerField(default=0)
    empleados_con_errores = models.IntegerField(default=0)
    total_devengado = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_deducido = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_neto = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Detalles
    detalles = models.TextField(blank=True, default='')
    errores = models.TextField(blank=True, default='')
    
    # Timing
    tiempo_inicio = models.DateTimeField(auto_now_add=True)
    tiempo_fin = models.DateTimeField(null=True, blank=True)
    duracion_segundos = models.IntegerField(null=True, blank=True)
    
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
        indexes = [
            models.Index(fields=['organization', 'period']),
            models.Index(fields=['tipo_calculo']),
        ]
    
    def __str__(self):
        return f"Cálculo {self.tipo_calculo} - {self.period}"


class PayrollNotification(TenantModel):
    """
    Notificaciones del sistema de nómina
    """
    TIPO_NOTIFICACION_CHOICES = [
        ('BORRADOR_GENERADO', 'Borrador Generado'),
        ('REVISION_PENDIENTE', 'Revisión Pendiente'),
        ('APROBACION_REQUERIDA', 'Aprobación Requerida'),
        ('NOMINA_APROBADA', 'Nómina Aprobada'),
        ('NOMINA_PROCESADA', 'Nómina Procesada'),
        ('NOMINA_RECHAZADA', 'Nómina Rechazada'),
        ('ERROR_CALCULO', 'Error en Cálculo'),
        ('WARNING', 'Advertencia'),
    ]
    
    tipo = models.CharField(max_length=30, choices=TIPO_NOTIFICACION_CHOICES)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    
    period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        null=True,
        blank=True
    )
    
    usuarios = models.ManyToManyField(
        'auth.User',
        related_name='notificaciones_nomina',
        blank=True
    )
    
    # Estado
    leida = models.BooleanField(default=False)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    requiere_accion = models.BooleanField(default=False)
    url_accion = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'leida']),
            models.Index(fields=['tipo']),
        ]
    
    def __str__(self):
        return f"{self.tipo} - {self.titulo}"


class Incapacity(TenantModel):
    """Incapacidades médicas de empleados"""
    
    TIPO_CHOICES = [
        ('COMUN', 'Enfermedad Común'),
        ('LABORAL', 'Accidente de Trabajo'),
        ('PROFESIONAL', 'Enfermedad Profesional'),
        ('LICENCIA_MATERNIDAD', 'Licencia de Maternidad'),
        ('LICENCIA_PATERNIDAD', 'Licencia de Paternidad'),
    ]
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
        ('PROCESADA', 'Procesada en Nómina'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='incapacidades'
    )
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_incapacidad = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Días totales de incapacidad"
    )
    
    # Información médica
    diagnostico = models.TextField(blank=True, null=True)
    numero_incapacidad = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Número de radicado de la incapacidad"
    )
    
    # Pago
    porcentaje_pago = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('66.67'),
        help_text="Porcentaje que paga la EPS (ej: 66.67% para enfermedad común)"
    )
    valor_dia = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Valor por día de incapacidad"
    )
    total_incapacidad = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total a pagar por incapacidad"
    )
    
    # Estado
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    aprobada_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incapacidades_aprobadas'
    )
    fecha_aprobacion = models.DateTimeField(blank=True, null=True)
    
    # Adjuntos
    documento_soporte = models.FileField(
        upload_to='incapacidades/',
        blank=True,
        null=True,
        help_text="Documento médico o incapacidad escaneada"
    )
    
    # Observaciones
    observaciones = models.TextField(blank=True, null=True)
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='incapacidades_creadas'
    )
    
    class Meta:
        verbose_name = 'Incapacidad'
        verbose_name_plural = 'Incapacidades'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['organization', 'employee', 'estado']),
            models.Index(fields=['fecha_inicio', 'fecha_fin']),
        ]
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.get_tipo_display()} ({self.fecha_inicio} al {self.fecha_fin})"
    
    def save(self, *args, **kwargs):
        """Calcular días y valores automáticamente"""
        if self.fecha_inicio and self.fecha_fin:
            delta = self.fecha_fin - self.fecha_inicio
            self.dias_incapacidad = delta.days + 1
            
            # Calcular valor por día (salario mensual / 30)
            if self.employee and self.employee.salario_basico:
                self.valor_dia = self.employee.salario_basico / 30
                
                # Calcular total según tipo de incapacidad
                if self.tipo == 'COMUN':
                    # Primeros 2 días: empleador paga 100%
                    # Del día 3 en adelante: EPS paga 66.67%
                    if self.dias_incapacidad <= 2:
                        self.total_incapacidad = self.valor_dia * self.dias_incapacidad
                    else:
                        dias_empleador = 2
                        dias_eps = self.dias_incapacidad - 2
                        self.total_incapacidad = (
                            (self.valor_dia * dias_empleador) +
                            (self.valor_dia * dias_eps * (self.porcentaje_pago / 100))
                        )
                elif self.tipo in ['LABORAL', 'PROFESIONAL']:
                    # ARL paga 100% desde el día 1
                    self.total_incapacidad = self.valor_dia * self.dias_incapacidad
                elif self.tipo == 'LICENCIA_MATERNIDAD':
                    # EPS paga 100% por 18 semanas
                    self.total_incapacidad = self.valor_dia * self.dias_incapacidad
                elif self.tipo == 'LICENCIA_PATERNIDAD':
                    # EPS paga 100% por 2 semanas
                    self.total_incapacidad = self.valor_dia * self.dias_incapacidad
        
        super().save(*args, **kwargs)


# Importar extensiones de modelos
from .models_extensions import (
    LaborContract,
    SocialBenefit,
    VacationRequest,
    EmployeeLoan,
    MonthlyProvision,
    PILAReport
)

__all__ = [
    'Employee', 'PayrollPeriod', 'AccrualConcept', 'DeductionConcept',
    'PayrollEntry', 'Accrual', 'Deduction', 'ElectronicPayrollDocument',
    'PayrollAutomationConfig', 'PayrollPeriodWorkflow', 'EmployeePeriodAssignment',
    'PayrollCalculationLog', 'PayrollNotification', 'Incapacity',
    # Extensiones
    'LaborContract', 'SocialBenefit', 'VacationRequest', 
    'EmployeeLoan', 'MonthlyProvision', 'PILAReport'
]