"""
Extensiones de modelos para sistema de nómina completo
Incluye: Prestaciones sociales, Vacaciones, Préstamos, Contratos, Provisiones
"""
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.organizations.base_models import TenantModel
from .models import Employee, PayrollPeriod


class LaborContract(TenantModel):
    """
    Contratos laborales de empleados
    """
    TIPO_CONTRATO_CHOICES = [
        ('INDEFINIDO', 'Término Indefinido'),
        ('FIJO', 'Término Fijo'),
        ('OBRA_LABOR', 'Obra o Labor'),
        ('PRESTACION_SERVICIOS', 'Prestación de Servicios'),
        ('APRENDIZAJE', 'Aprendizaje'),
        ('TEMPORAL', 'Temporal'),
    ]
    
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('SUSPENDIDO', 'Suspendido'),
        ('TERMINADO', 'Terminado'),
        ('LIQUIDADO', 'Liquidado'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name='contratos'
    )
    
    # Información del contrato
    numero_contrato = models.CharField(max_length=50, unique=True)
    tipo_contrato = models.CharField(max_length=30, choices=TIPO_CONTRATO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')
    
    # Fechas
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True, help_text="Solo para contratos a término fijo")
    fecha_terminacion = models.DateField(null=True, blank=True)
    
    # Información salarial
    salario_contratado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    auxilio_transporte = models.BooleanField(
        default=True,
        help_text="¿Tiene derecho a auxilio de transporte?"
    )
    
    # Jornada laboral
    horas_semanales = models.IntegerField(
        default=48,
        validators=[MinValueValidator(1), MaxValueValidator(168)]
    )
    
    # Causales de terminación
    causal_terminacion = models.TextField(blank=True)
    preaviso_dado = models.BooleanField(default=False)
    
    # Documentos
    archivo_contrato = models.FileField(
        upload_to='contratos/%Y/%m/',
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Contrato Laboral'
        verbose_name_plural = 'Contratos Laborales'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['organization', 'employee', 'estado']),
            models.Index(fields=['fecha_inicio', 'fecha_fin']),
        ]
    
    def __str__(self):
        return f"{self.numero_contrato} - {self.employee.get_full_name()}"
    
    @property
    def dias_trabajados(self):
        """Calcula días trabajados desde inicio hasta hoy o fecha terminación"""
        fecha_fin = self.fecha_terminacion or timezone.now().date()
        return (fecha_fin - self.fecha_inicio).days
    
    @property
    def esta_activo(self):
        """Verifica si el contrato está activo"""
        return self.estado == 'ACTIVO'


class SocialBenefit(TenantModel):
    """
    Prestaciones sociales acumuladas
    Prima, Cesantías, Intereses sobre cesantías
    """
    TIPO_CHOICES = [
        ('CESANTIAS', 'Cesantías'),
        ('INTERESES_CESANTIAS', 'Intereses sobre Cesantías'),
        ('PRIMA', 'Prima de Servicios'),
        ('VACACIONES', 'Vacaciones'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name='prestaciones_sociales'
    )
    
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    
    # Período de causación
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    # Días y valores
    dias_causados = models.IntegerField(default=0)
    valor_causado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Saldo
    valor_pagado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    saldo_pendiente = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Cálculo automático
    calculado_automaticamente = models.BooleanField(default=False)
    fecha_calculo = models.DateTimeField(null=True, blank=True)
    
    # Observaciones
    observaciones = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Prestación Social'
        verbose_name_plural = 'Prestaciones Sociales'
        ordering = ['-fecha_fin', 'employee', 'tipo']
        indexes = [
            models.Index(fields=['organization', 'employee', 'tipo']),
            models.Index(fields=['fecha_inicio', 'fecha_fin']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.employee.get_full_name()} ({self.fecha_inicio} - {self.fecha_fin})"


class VacationRequest(TenantModel):
    """
    Solicitudes y registro de vacaciones
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Aprobación'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
        ('DISFRUTADA', 'Disfrutada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name='solicitudes_vacaciones'
    )
    
    # Fechas de vacaciones
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_reintegro = models.DateField(
        help_text="Fecha de regreso al trabajo"
    )
    
    # Días
    dias_solicitados = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    dias_habiles = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Días hábiles (sin contar fines de semana)"
    )
    dias_calendario = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Días de calendario totales"
    )
    
    # Período que causan
    periodo_inicio = models.DateField(
        help_text="Inicio del período laboral que causan estas vacaciones"
    )
    periodo_fin = models.DateField(
        help_text="Fin del período laboral que causan estas vacaciones"
    )
    
    # Estado y aprobación
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE'
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    aprobado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vacaciones_aprobadas'
    )
    
    # Pago anticipado
    pago_anticipado = models.BooleanField(
        default=True,
        help_text="¿Se paga antes de salir a vacaciones?"
    )
    valor_pago = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    fecha_pago = models.DateField(null=True, blank=True)
    
    # Observaciones
    motivo_rechazo = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Solicitud de Vacaciones'
        verbose_name_plural = 'Solicitudes de Vacaciones'
        ordering = ['-fecha_solicitud']
        indexes = [
            models.Index(fields=['organization', 'employee', 'estado']),
            models.Index(fields=['fecha_inicio', 'fecha_fin']),
        ]
    
    def __str__(self):
        return f"Vacaciones {self.employee.get_full_name()} ({self.fecha_inicio} - {self.fecha_fin})"
    
    def aprobar(self, user):
        """Aprueba la solicitud de vacaciones"""
        self.estado = 'APROBADA'
        self.aprobado_por = user
        self.fecha_aprobacion = timezone.now()
        self.save()
    
    def rechazar(self, user, motivo):
        """Rechaza la solicitud de vacaciones"""
        self.estado = 'RECHAZADA'
        self.aprobado_por = user
        self.fecha_aprobacion = timezone.now()
        self.motivo_rechazo = motivo
        self.save()


class EmployeeLoan(TenantModel):
    """
    Préstamos a empleados
    """
    ESTADO_CHOICES = [
        ('SOLICITADO', 'Solicitado'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('ACTIVO', 'Activo - En descuento'),
        ('PAGADO', 'Pagado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name='prestamos'
    )
    
    # Información del préstamo
    numero_prestamo = models.CharField(max_length=50, unique=True)
    fecha_solicitud = models.DateField()
    fecha_aprobacion = models.DateField(null=True, blank=True)
    fecha_desembolso = models.DateField(null=True, blank=True)
    
    # Monto
    monto_solicitado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00'))]
    )
    monto_aprobado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Cuotas
    numero_cuotas = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(60)],
        help_text="Número de cuotas para pagar"
    )
    valor_cuota = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    cuotas_pagadas = models.IntegerField(default=0)
    
    # Interés
    tasa_interes = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Tasa de interés mensual (%)"
    )
    
    # Saldos
    total_pagado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    saldo_pendiente = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='SOLICITADO'
    )
    
    # Aprobación
    aprobado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prestamos_aprobados'
    )
    
    # Observaciones
    motivo_solicitud = models.TextField()
    motivo_rechazo = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Préstamo a Empleado'
        verbose_name_plural = 'Préstamos a Empleados'
        ordering = ['-fecha_solicitud']
        indexes = [
            models.Index(fields=['organization', 'employee', 'estado']),
            models.Index(fields=['numero_prestamo']),
        ]
    
    def __str__(self):
        return f"Préstamo {self.numero_prestamo} - {self.employee.get_full_name()}"
    
    def calcular_cuota(self):
        """Calcula el valor de la cuota mensual"""
        if self.tasa_interes > 0:
            # Fórmula con interés
            r = self.tasa_interes / Decimal('100')
            n = Decimal(str(self.numero_cuotas))
            p = self.monto_aprobado
            cuota = p * (r * (1 + r)**n) / ((1 + r)**n - 1)
        else:
            # Sin interés
            cuota = self.monto_aprobado / Decimal(str(self.numero_cuotas))
        
        return cuota.quantize(Decimal('0.01'))
    
    def aprobar(self, user, monto_aprobado=None):
        """Aprueba el préstamo"""
        self.estado = 'APROBADO'
        self.aprobado_por = user
        self.fecha_aprobacion = timezone.now().date()
        if monto_aprobado:
            self.monto_aprobado = monto_aprobado
        else:
            self.monto_aprobado = self.monto_solicitado
        
        self.valor_cuota = self.calcular_cuota()
        self.saldo_pendiente = self.monto_aprobado
        self.save()
    
    def desembolsar(self):
        """Marca el préstamo como desembolsado y activo"""
        if self.estado == 'APROBADO':
            self.estado = 'ACTIVO'
            self.fecha_desembolso = timezone.now().date()
            self.save()


class MonthlyProvision(TenantModel):
    """
    Provisiones mensuales de prestaciones sociales
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name='provisiones_mensuales'
    )
    
    period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        related_name='provisiones'
    )
    
    # Valores provisionados
    cesantias = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Provisión mensual de cesantías (8.33%)"
    )
    intereses_cesantias = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Provisión mensual de intereses sobre cesantías (1%)"
    )
    prima = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Provisión mensual de prima (8.33%)"
    )
    vacaciones = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Provisión mensual de vacaciones (4.17%)"
    )
    
    # Total
    total_provision = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Base salarial
    salario_base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Cálculo automático
    calculado_automaticamente = models.BooleanField(default=False)
    fecha_calculo = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Provisión Mensual'
        verbose_name_plural = 'Provisiones Mensuales'
        ordering = ['-period', 'employee']
        unique_together = ['organization', 'period', 'employee']
        indexes = [
            models.Index(fields=['organization', 'period']),
            models.Index(fields=['employee']),
        ]
    
    def __str__(self):
        return f"Provisión {self.employee.get_full_name()} - {self.period}"
    
    def calcular(self):
        """Calcula las provisiones mensuales"""
        # Cesantías: 8.33% del salario mensual
        self.cesantias = (self.salario_base * Decimal('0.0833')).quantize(Decimal('0.01'))
        
        # Intereses sobre cesantías: 1% anual = 0.0833% mensual
        self.intereses_cesantias = (self.salario_base * Decimal('0.000833')).quantize(Decimal('0.01'))
        
        # Prima: 8.33% del salario mensual
        self.prima = (self.salario_base * Decimal('0.0833')).quantize(Decimal('0.01'))
        
        # Vacaciones: 4.17% del salario mensual
        self.vacaciones = (self.salario_base * Decimal('0.0417')).quantize(Decimal('0.01'))
        
        # Total
        self.total_provision = self.cesantias + self.intereses_cesantias + self.prima + self.vacaciones
        
        self.calculado_automaticamente = True
        self.fecha_calculo = timezone.now()


class PILAReport(TenantModel):
    """
    Reporte de planilla PILA para seguridad social
    """
    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('GENERADO', 'Generado'),
        ('ENVIADO', 'Enviado'),
        ('VALIDADO', 'Validado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    
    period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.PROTECT,
        related_name='reportes_pila'
    )
    
    # Información del reporte
    numero_planilla = models.CharField(max_length=50, unique=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    
    # Período de cotización
    mes = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    anio = models.IntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2100)]
    )
    
    # Totales
    total_empleados = models.IntegerField(default=0)
    total_salud = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_pension = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_riesgos = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_caja = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_aportes = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='BORRADOR'
    )
    
    # Archivo
    archivo_pila = models.FileField(
        upload_to='pila/%Y/%m/',
        null=True,
        blank=True,
        help_text="Archivo en formato PILA"
    )
    
    # Respuesta
    respuesta_operador = models.TextField(blank=True)
    errores = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Reporte PILA'
        verbose_name_plural = 'Reportes PILA'
        ordering = ['-anio', '-mes']
        indexes = [
            models.Index(fields=['organization', 'mes', 'anio']),
            models.Index(fields=['numero_planilla']),
        ]
    
    def __str__(self):
        return f"PILA {self.mes}/{self.anio} - {self.numero_planilla}"
