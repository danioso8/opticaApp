"""
Motor de cálculo automático de nómina
"""
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
import json
from apps.payroll.models import (
    PayrollPeriod, Employee, PayrollEntry, Accrual, Deduction,
    AccrualConcept, DeductionConcept,
    EmployeePeriodAssignment, PayrollCalculationLog,
    PayrollAutomationConfig, PayrollPeriodWorkflow
)


class PayrollCalculationEngine:
    """
    Motor avanzado de cálculo automático de nómina
    """
    
    # Horas extras (constantes no configurables)
    HORA_ORDINARIA_DIURNA = Decimal('0.125')  # 1/8 del día
    RECARGO_HE_DIURNA = Decimal('0.25')  # 25%
    RECARGO_HE_NOCTURNA = Decimal('0.75')  # 75%
    RECARGO_HE_FESTIVA_DIURNA = Decimal('1.00')  # 100%
    RECARGO_HE_FESTIVA_NOCTURNA = Decimal('1.50')  # 150%
    RECARGO_NOCTURNO = Decimal('0.35')  # 35%
    RECARGO_FESTIVO = Decimal('0.75')  # 75%
    
    def __init__(self, period, user=None):
        self.period = period
        self.organization = period.organization
        self.user = user
        self.config = self._get_config()
        
        # Cargar valores configurables desde el modelo
        self.SALARIO_MINIMO = self.config.salario_minimo
        self.AUXILIO_TRANSPORTE = self.config.auxilio_transporte
        self.PORCENTAJE_SALUD_EMPLEADO = self.config.porcentaje_salud / Decimal('100')
        self.PORCENTAJE_PENSION_EMPLEADO = self.config.porcentaje_pension / Decimal('100')
        self.TOPE_AUXILIO_TRANSPORTE = self.SALARIO_MINIMO * Decimal('2')  # 2 SMLV
        
        self.log = None
        self.errores = []
        self.warnings = []
    
    def _get_config(self):
        """Obtiene o crea la configuración de automatización"""
        config, _ = PayrollAutomationConfig.objects.get_or_create(
            organization=self.organization
        )
        return config
    
    @transaction.atomic
    def calcular_periodo_completo(self, tipo_calculo='INICIAL'):
        """
        Calcula la nómina completa del período
        """
        tiempo_inicio = timezone.now()
        
        # Crear log
        self.log = PayrollCalculationLog.objects.create(
            organization=self.organization,
            period=self.period,
            tipo_calculo=tipo_calculo,
            usuario=self.user
        )
        
        try:
            # Obtener empleados asignados
            assignments = EmployeePeriodAssignment.objects.filter(
                organization=self.organization,
                period=self.period,
                incluido=True
            )
            
            empleados_procesados = 0
            empleados_con_errores = 0
            total_devengado = Decimal('0.00')
            total_deducciones = Decimal('0.00')
            
            for assignment in assignments:
                try:
                    resultado = self.calcular_empleado(assignment)
                    empleados_procesados += 1
                    total_devengado += resultado['total_devengado']
                    total_deducciones += resultado['total_deducciones']
                    
                    # Actualizar assignment
                    assignment.total_devengado = resultado['total_devengado']
                    assignment.total_deducido = resultado['total_deducciones']
                    assignment.neto_pagar = resultado['neto_pagar']
                    assignment.calculado_automaticamente = True
                    assignment.fecha_calculo = timezone.now()
                    assignment.requiere_recalculo = False
                    assignment.save()
                    
                except Exception as e:
                    empleados_con_errores += 1
                    self.errores.append({
                        'empleado': assignment.employee.get_full_name(),
                        'error': str(e)
                    })
            
            # Actualizar log
            tiempo_fin = timezone.now()
            self.log.empleados_procesados = empleados_procesados
            self.log.empleados_con_errores = empleados_con_errores
            self.log.total_devengado = total_devengado
            self.log.total_deducciones = total_deducciones
            self.log.total_neto = total_devengado - total_deducciones
            self.log.tiempo_fin = tiempo_fin
            self.log.duracion_segundos = (tiempo_fin - tiempo_inicio).total_seconds()
            self.log.errores = self.errores
            self.log.warnings = self.warnings
            self.log.save()
            
            return {
                'success': True,
                'empleados_procesados': empleados_procesados,
                'empleados_con_errores': empleados_con_errores,
                'total_devengado': total_devengado,
                'total_deducciones': total_deducciones,
                'total_neto': total_devengado - total_deducciones,
                'errores': self.errores,
                'warnings': self.warnings
            }
            
        except Exception as e:
            self.log.errores = [{'error_general': str(e)}]
            self.log.save()
            return {
                'success': False,
                'error': str(e)
            }
    
    def calcular_empleado(self, assignment):
        """
        Calcula la nómina de un empleado específico
        """
        employee = assignment.employee
        
        # Calcular devengados
        devengados = self._calcular_devengados(employee, assignment)
        
        # Calcular deducciones
        deducciones = self._calcular_deducciones(employee, assignment, devengados)
        
        # Calcular neto
        total_devengado = sum(d['valor'] for d in devengados)
        total_deducciones = sum(d['valor'] for d in deducciones)
        neto_pagar = total_devengado - total_deducciones
        
        # Crear o actualizar PayrollEntry
        entry, created = PayrollEntry.objects.update_or_create(
            organization=self.organization,
            period=self.period,
            employee=employee,
            defaults={
                'total_devengado': total_devengado,
                'total_deducciones': total_deducciones,
                'neto_pagar': neto_pagar,
            }
        )
        
        # Limpiar devengados y deducciones anteriores
        entry.accruals.all().delete()
        entry.deductions.all().delete()
        
        # Crear devengados
        for dev in devengados:
            Accrual.objects.create(
                organization=self.organization,
                entry=entry,
                concept=dev['concept'],
                cantidad=dev['cantidad'],
                valor_unitario=dev['valor_unitario'],
                total=dev['valor']
            )
        
        # Crear deducciones
        for ded in deducciones:
            Deduction.objects.create(
                organization=self.organization,
                entry=entry,
                concept=ded['concept'],
                base=ded['base'],
                porcentaje=ded['porcentaje'],
                total=ded['valor']
            )
        
        return {
            'total_devengado': total_devengado,
            'total_deducciones': total_deducciones,
            'neto_pagar': neto_pagar
        }
    
    def _calcular_devengados(self, employee, assignment):
        """Calcula todos los devengados del empleado"""
        devengados = []
        salario_basico = assignment.salario_periodo
        dias_trabajados = assignment.dias_trabajados
        
        # 1. Salario básico proporcional
        salario_concepto = AccrualConcept.objects.filter(
            organization=self.organization,
            codigo='SAL001',
            activo=True
        ).first()
        
        if salario_concepto:
            valor_salario = (salario_basico / 30) * dias_trabajados
            devengados.append({
                'concept': salario_concepto,
                'cantidad': dias_trabajados,
                'valor_unitario': salario_basico / 30,
                'valor': valor_salario
            })
        
        # 2. Auxilio de transporte (si aplica)
        if self.config.calcular_auxilio_transporte and salario_basico <= self.TOPE_AUXILIO_TRANSPORTE:
            auxilio_concepto = AccrualConcept.objects.filter(
                organization=self.organization,
                codigo='AUX001',
                activo=True
            ).first()
            
            if auxilio_concepto:
                valor_auxilio = (self.AUXILIO_TRANSPORTE / 30) * dias_trabajados
                devengados.append({
                    'concept': auxilio_concepto,
                    'cantidad': dias_trabajados,
                    'valor_unitario': self.AUXILIO_TRANSPORTE / 30,
                    'valor': valor_auxilio
                })
        
        # TODO: Agregar horas extras, bonificaciones, comisiones, etc.
        # Esto se puede extender con datos adicionales del empleado
        
        return devengados
    
    def _calcular_deducciones(self, employee, assignment, devengados):
        """Calcula todas las deducciones del empleado"""
        deducciones = []
        
        # Base para deducciones (solo devengados que aplican)
        base_deducciones = sum(
            d['valor'] for d in devengados
            if d['concept'].aplica_seguridad_social
        )
        
        # 1. Salud 4%
        salud_concepto = DeductionConcept.objects.filter(
            organization=self.organization,
            codigo='SALUD001',
            activo=True
        ).first()
        
        if salud_concepto:
            valor_salud = base_deducciones * self.PORCENTAJE_SALUD_EMPLEADO
            deducciones.append({
                'concept': salud_concepto,
                'base': base_deducciones,
                'porcentaje': self.PORCENTAJE_SALUD_EMPLEADO * 100,
                'valor': valor_salud
            })
        
        # 2. Pensión 4%
        pension_concepto = DeductionConcept.objects.filter(
            organization=self.organization,
            codigo='PENSION001',
            activo=True
        ).first()
        
        if pension_concepto:
            valor_pension = base_deducciones * self.PORCENTAJE_PENSION_EMPLEADO
            deducciones.append({
                'concept': pension_concepto,
                'base': base_deducciones,
                'porcentaje': self.PORCENTAJE_PENSION_EMPLEADO * 100,
                'valor': valor_pension
            })
        
        # 3. FSP (Fondo Solidaridad Pensional) - Si salario > 4 SMLV
        if base_deducciones > (self.SALARIO_MINIMO * 4):
            fsp_concepto = DeductionConcept.objects.filter(
                organization=self.organization,
                codigo='FSP001',
                activo=True
            ).first()
            
            if fsp_concepto:
                # Porcentaje según rangos configurables
                smlv = base_deducciones / self.SALARIO_MINIMO
                
                if smlv <= 16:
                    porcentaje_fsp = self.config.porcentaje_fsp_4_a_16 / Decimal('100')
                elif smlv <= 17:
                    porcentaje_fsp = self.config.porcentaje_fsp_16_a_17 / Decimal('100')
                elif smlv <= 18:
                    porcentaje_fsp = self.config.porcentaje_fsp_17_a_18 / Decimal('100')
                elif smlv <= 19:
                    porcentaje_fsp = self.config.porcentaje_fsp_18_a_19 / Decimal('100')
                elif smlv <= 20:
                    porcentaje_fsp = self.config.porcentaje_fsp_19_a_20 / Decimal('100')
                else:
                    porcentaje_fsp = self.config.porcentaje_fsp_mayor_20 / Decimal('100')
                
                valor_fsp = base_deducciones * porcentaje_fsp
                deducciones.append({
                    'concept': fsp_concepto,
                    'base': base_deducciones,
                    'porcentaje': porcentaje_fsp * 100,
                    'valor': valor_fsp
                })
        
        # TODO: Agregar retención en la fuente, préstamos, embargos, etc.
        
        return deducciones
    
    def validar_calculo(self):
        """Valida el cálculo realizado"""
        validaciones = {
            'salario_minimo': True,
            'seguridad_social': True,
            'totales': True
        }
        errores = []
        warnings = []
        
        # Validar que todos los empleados tengan salario >= mínimo
        if self.config.validar_salario_minimo:
            assignments = EmployeePeriodAssignment.objects.filter(
                period=self.period,
                incluido=True,
                salario_periodo__lt=self.SALARIO_MINIMO
            )
            if assignments.exists():
                validaciones['salario_minimo'] = False
                for assignment in assignments:
                    errores.append(
                        f"{assignment.employee.get_full_name()}: Salario menor al mínimo"
                    )
        
        return {
            'validaciones': validaciones,
            'errores': errores,
            'warnings': warnings,
            'aprobado': all(validaciones.values()) and len(errores) == 0
        }
