"""
Servicio de automatización y workflow de nómina
"""
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
import json
from apps.payroll.models import (
    PayrollPeriod, Employee,
    PayrollAutomationConfig, PayrollPeriodWorkflow,
    EmployeePeriodAssignment, PayrollNotification
)
from .calculation_engine import PayrollCalculationEngine


class PayrollAutomationService:
    """
    Servicio para automatizar la generación y procesamiento de nómina
    """
    
    def __init__(self, organization):
        self.organization = organization
        self.config = self._get_config()
    
    def _get_config(self):
        config, _ = PayrollAutomationConfig.objects.get_or_create(
            organization=self.organization
        )
        return config
    
    @transaction.atomic
    def generar_borrador_automatico(self, tipo_periodo='MENSUAL'):
        """
        Genera automáticamente un borrador de nómina
        """
        # Calcular fechas del período
        hoy = timezone.now().date()
        
        if tipo_periodo == 'MENSUAL':
            fecha_inicio = hoy.replace(day=1)
            if hoy.month == 12:
                fecha_fin = hoy.replace(day=31)
            else:
                fecha_fin = (hoy.replace(month=hoy.month + 1, day=1) - timedelta(days=1))
            fecha_pago = hoy.replace(day=self.config.dia_pago_mensual)
        elif tipo_periodo == 'QUINCENAL':
            if hoy.day <= 15:
                fecha_inicio = hoy.replace(day=1)
                fecha_fin = hoy.replace(day=15)
                fecha_pago = hoy.replace(day=self.config.dia_pago_quincenal_1)
            else:
                fecha_inicio = hoy.replace(day=16)
                if hoy.month == 12:
                    fecha_fin = hoy.replace(day=31)
                else:
                    fecha_fin = (hoy.replace(month=hoy.month + 1, day=1) - timedelta(days=1))
                fecha_pago = hoy.replace(day=self.config.dia_pago_quincenal_2)
        
        # Crear período
        period = PayrollPeriod.objects.create(
            organization=self.organization,
            nombre=f"Nómina {tipo_periodo.title()} - {fecha_inicio.strftime('%b %Y')}",
            tipo_periodo=tipo_periodo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            fecha_pago=fecha_pago,
            estado='BORRADOR'
        )
        
        # Crear workflow
        workflow = PayrollPeriodWorkflow.objects.create(
            organization=self.organization,
            period=period,
            estado='BORRADOR',
            notas_borrador=f"Borrador generado automáticamente el {timezone.now()}"
        )
        
        # Asignar empleados activos
        self.asignar_empleados_automaticamente(period)
        
        # Calcular nómina inicial
        engine = PayrollCalculationEngine(period)
        resultado = engine.calcular_periodo_completo(tipo_calculo='AUTOMATICO')
        
        # Crear notificación
        if self.config.enviar_notificacion_borrador:
            self._crear_notificacion(
                period,
                'BORRADOR_GENERADO',
                f'Borrador de nómina generado: {period.nombre}',
                f'Se ha generado automáticamente un borrador de nómina para el período {fecha_inicio} - {fecha_fin}. '
                f'Total empleados: {resultado["empleados_procesados"]}. '
                f'Total a pagar: ${resultado["total_neto"]:,.2f}'
            )
        
        return {
            'success': True,
            'period': period,
            'workflow': workflow,
            'calculo': resultado
        }
    
    def asignar_empleados_automaticamente(self, period):
        """
        Asigna automáticamente todos los empleados activos al período
        """
        # Obtener empleados activos que están marcados para nómina
        try:
            from apps.dashboard.models_employee import Employee as DashboardEmployee
            dashboard_employees = DashboardEmployee.objects.filter(
                organization=self.organization,
                is_active=True,
                incluir_en_nomina=True
            ).values_list('identification', flat=True)
            
            employees = Employee.objects.filter(
                organization=self.organization,
                activo=True,
                numero_documento__in=dashboard_employees
            )
        except:
            employees = Employee.objects.filter(
                organization=self.organization,
                activo=True
            )
        
        assignments_creados = 0
        for employee in employees:
            # Calcular días trabajados
            dias_trabajados = self._calcular_dias_trabajados(employee, period)
            
            assignment, created = EmployeePeriodAssignment.objects.get_or_create(
                organization=self.organization,
                period=period,
                employee=employee,
                defaults={
                    'salario_periodo': employee.salario_basico,
                    'dias_trabajados': dias_trabajados,
                    'incluido': True
                }
            )
            if created:
                assignments_creados += 1
        
        return assignments_creados
    
    def _calcular_dias_trabajados(self, employee, period):
        """Calcula los días efectivamente trabajados en el período"""
        # Por defecto, usar la diferencia de días entre inicio y fin
        dias = (period.fecha_fin - period.fecha_inicio).days + 1
        
        # Si el empleado ingresó durante el período, ajustar
        if employee.fecha_ingreso > period.fecha_inicio:
            dias = (period.fecha_fin - employee.fecha_ingreso).days + 1
        
        # Si el empleado se retiró durante el período, ajustar
        if employee.fecha_retiro and employee.fecha_retiro < period.fecha_fin:
            dias = (employee.fecha_retiro - period.fecha_inicio).days + 1
        
        return max(0, dias)
    
    @transaction.atomic
    def enviar_a_revision(self, period, usuario, notas=''):
        """
        Envía el borrador a revisión
        """
        workflow = PayrollPeriodWorkflow.objects.get(period=period)
        
        if not workflow.puede_enviar_a_revision():
            return {
                'success': False,
                'error': 'El período no está en estado borrador'
            }
        
        # Validar cálculos
        engine = PayrollCalculationEngine(period, usuario)
        validacion = engine.validar_calculo()
        
        if not validacion['aprobado']:
            return {
                'success': False,
                'error': 'La nómina tiene errores de validación',
                'validacion': validacion
            }
        
        # Cambiar estado
        workflow.estado = 'EN_REVISION'
        workflow.fecha_revision = timezone.now()
        workflow.usuario_revisor = usuario
        workflow.notas_revision = notas
        workflow.validaciones_pasadas = validacion['validaciones']
        workflow.save()
        
        period.estado = 'EN_REVISION'
        period.save()
        
        # Notificar
        if self.config.enviar_notificacion_aprobacion:
            self._crear_notificacion(
                period,
                'REVISION_PENDIENTE',
                f'Nómina en revisión: {period.nombre}',
                f'La nómina ha sido enviada a revisión y requiere aprobación. '
                f'Revisor: {usuario.get_full_name()}'
            )
        
        return {'success': True, 'workflow': workflow}
    
    @transaction.atomic
    def aprobar_nomina(self, period, usuario, notas=''):
        """
        Aprueba la nómina para ser procesada
        """
        workflow = PayrollPeriodWorkflow.objects.get(period=period)
        
        if not workflow.puede_aprobar():
            return {
                'success': False,
                'error': 'El período no está en estado de revisión'
            }
        
        # Cambiar estado
        workflow.estado = 'APROBADO'
        workflow.fecha_aprobacion = timezone.now()
        workflow.usuario_aprobador = usuario
        workflow.notas_aprobacion = notas
        workflow.save()
        
        period.estado = 'APROBADO'
        period.save()
        
        # Notificar
        if self.config.enviar_notificacion_aprobacion:
            self._crear_notificacion(
                period,
                'NOMINA_APROBADA',
                f'Nómina aprobada: {period.nombre}',
                f'La nómina ha sido aprobada por {usuario.get_full_name()} y está lista para procesar.'
            )
        
        return {'success': True, 'workflow': workflow}
    
    @transaction.atomic
    def rechazar_nomina(self, period, usuario, motivo):
        """
        Rechaza la nómina y la devuelve a borrador
        """
        workflow = PayrollPeriodWorkflow.objects.get(period=period)
        
        if not workflow.puede_rechazar():
            return {
                'success': False,
                'error': 'El período no puede ser rechazado en su estado actual'
            }
        
        # Cambiar estado
        workflow.estado = 'RECHAZADO'
        workflow.fecha_rechazo = timezone.now()
        workflow.motivo_rechazo = motivo
        workflow.save()
        
        period.estado = 'RECHAZADO'
        period.save()
        
        # Notificar
        self._crear_notificacion(
            period,
            'NOMINA_RECHAZADA',
            f'Nómina rechazada: {period.nombre}',
            f'La nómina ha sido rechazada. Motivo: {motivo}'
        )
        
        return {'success': True, 'workflow': workflow}
    
    @transaction.atomic
    def procesar_nomina(self, period, usuario):
        """
        Procesa la nómina aprobada (genera XMLs, firma, etc.)
        """
        workflow = PayrollPeriodWorkflow.objects.get(period=period)
        
        if not workflow.puede_procesar():
            return {
                'success': False,
                'error': 'El período no está aprobado para procesar'
            }
        
        # Cambiar estado
        workflow.estado = 'PROCESADO'
        workflow.fecha_procesado = timezone.now()
        workflow.save()
        
        period.estado = 'PROCESADO'
        period.save()
        
        # Notificar
        if self.config.enviar_notificacion_procesado:
            self._crear_notificacion(
                period,
                'NOMINA_PROCESADA',
                f'Nómina procesada: {period.nombre}',
                f'La nómina ha sido procesada exitosamente y está lista para enviar a la DIAN.'
            )
        
        return {'success': True, 'workflow': workflow}
    
    def _crear_notificacion(self, period, tipo, titulo, mensaje):
        """Crea una notificación del sistema"""
        notificacion = PayrollNotification.objects.create(
            organization=self.organization,
            period=period,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            requiere_accion=tipo in ['REVISION_PENDIENTE', 'APROBACION_REQUERIDA']
        )
        
        # TODO: Asignar usuarios destinatarios (administradores, contadores, etc.)
        
        return notificacion
