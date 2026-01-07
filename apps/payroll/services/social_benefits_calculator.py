"""
Servicio de cálculo de prestaciones sociales
Calcula: Cesantías, Intereses, Prima, Vacaciones, Provisiones
"""
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone

from apps.payroll.models import Employee, PayrollPeriod
from apps.payroll.models_extensions import (
    LaborContract,
    SocialBenefit,
    MonthlyProvision
)


class SocialBenefitsCalculator:
    """
    Calculadora de prestaciones sociales colombianas
    """
    
    # Porcentajes legales Colombia
    PORCENTAJE_CESANTIAS = Decimal('8.33')  # 8.33% mensual
    PORCENTAJE_INTERESES = Decimal('12.00')  # 12% anual
    PORCENTAJE_PRIMA = Decimal('8.33')  # 8.33% mensual
    PORCENTAJE_VACACIONES = Decimal('4.17')  # 4.17% mensual
    
    def __init__(self, organization):
        self.organization = organization
    
    def calcular_cesantias(self, employee, fecha_inicio, fecha_fin, salario_promedio):
        """
        Calcula cesantías
        Fórmula: (Salario promedio * días trabajados) / 360
        """
        dias = (fecha_fin - fecha_inicio).days
        valor_cesantias = (salario_promedio * Decimal(str(dias))) / Decimal('360')
        
        return {
            'dias': dias,
            'valor': valor_cesantias.quantize(Decimal('0.01')),
            'salario_base': salario_promedio
        }
    
    def calcular_intereses_cesantias(self, saldo_cesantias, dias):
        """
        Calcula intereses sobre cesantías
        Fórmula: (Cesantías * días * 12%) / 360
        """
        interes = (saldo_cesantias * Decimal(str(dias)) * self.PORCENTAJE_INTERESES) / (Decimal('360') * Decimal('100'))
        
        return {
            'valor': interes.quantize(Decimal('0.01')),
            'saldo_cesantias': saldo_cesantias,
            'dias': dias
        }
    
    def calcular_prima(self, employee, fecha_inicio, fecha_fin, salario_promedio):
        """
        Calcula prima de servicios
        Fórmula: (Salario promedio * días trabajados) / 360
        """
        dias = (fecha_fin - fecha_inicio).days
        valor_prima = (salario_promedio * Decimal(str(dias))) / Decimal('360')
        
        return {
            'dias': dias,
            'valor': valor_prima.quantize(Decimal('0.01')),
            'salario_base': salario_promedio
        }
    
    def calcular_vacaciones(self, employee, fecha_inicio, fecha_fin, salario_actual):
        """
        Calcula vacaciones
        Fórmula: (Salario actual * días trabajados) / 720
        15 días hábiles por año = 360 días / 24 = 15 días
        """
        dias_trabajados = (fecha_fin - fecha_inicio).days
        # 15 días de vacaciones por cada 360 días trabajados
        dias_vacaciones = (dias_trabajados * Decimal('15')) / Decimal('360')
        valor_vacaciones = (salario_actual * dias_vacaciones) / Decimal('30')
        
        return {
            'dias_trabajados': dias_trabajados,
            'dias_vacaciones': int(dias_vacaciones),
            'valor': valor_vacaciones.quantize(Decimal('0.01')),
            'salario_base': salario_actual
        }
    
    @transaction.atomic
    def calcular_provision_mensual(self, employee, period, salario_base):
        """
        Calcula y guarda la provisión mensual de prestaciones
        """
        provision, created = MonthlyProvision.objects.get_or_create(
            organization=self.organization,
            employee=employee,
            period=period,
            defaults={'salario_base': salario_base}
        )
        
        if created or not provision.calculado_automaticamente:
            provision.salario_base = salario_base
            provision.calcular()
            provision.save()
        
        return provision
    
    @transaction.atomic
    def liquidar_prestaciones(self, employee, fecha_corte=None):
        """
        Liquida todas las prestaciones sociales hasta una fecha
        Usado para liquidación de contrato
        """
        if not fecha_corte:
            fecha_corte = timezone.now().date()
        
        # Obtener contrato activo
        contrato = LaborContract.objects.filter(
            organization=self.organization,
            employee=employee,
            estado='ACTIVO'
        ).first()
        
        if not contrato:
            raise ValueError(f"No hay contrato activo para {employee.get_full_name()}")
        
        fecha_inicio = contrato.fecha_inicio
        salario_actual = employee.salario_basico
        
        # Calcular cada prestación
        resultados = {}
        
        # Cesantías
        cesantias = self.calcular_cesantias(
            employee,
            fecha_inicio,
            fecha_corte,
            salario_actual
        )
        resultados['cesantias'] = cesantias
        
        # Intereses sobre cesantías
        intereses = self.calcular_intereses_cesantias(
            cesantias['valor'],
            cesantias['dias']
        )
        resultados['intereses_cesantias'] = intereses
        
        # Prima de servicios
        # Calcular prima proporcional del semestre actual
        mes_actual = fecha_corte.month
        if mes_actual <= 6:
            # Primer semestre: enero 1 a junio 30
            inicio_semestre = datetime(fecha_corte.year, 1, 1).date()
            fin_semestre = datetime(fecha_corte.year, 6, 30).date()
        else:
            # Segundo semestre: julio 1 a diciembre 31
            inicio_semestre = datetime(fecha_corte.year, 7, 1).date()
            fin_semestre = datetime(fecha_corte.year, 12, 31).date()
        
        fecha_inicio_prima = max(fecha_inicio, inicio_semestre)
        fecha_fin_prima = min(fecha_corte, fin_semestre)
        
        prima = self.calcular_prima(
            employee,
            fecha_inicio_prima,
            fecha_fin_prima,
            salario_actual
        )
        resultados['prima'] = prima
        
        # Vacaciones
        vacaciones = self.calcular_vacaciones(
            employee,
            fecha_inicio,
            fecha_corte,
            salario_actual
        )
        resultados['vacaciones'] = vacaciones
        
        # Total liquidación
        total = (
            cesantias['valor'] +
            intereses['valor'] +
            prima['valor'] +
            vacaciones['valor']
        )
        resultados['total'] = total
        
        return resultados
    
    @transaction.atomic
    def generar_provisiones_periodo(self, period):
        """
        Genera provisiones mensuales para todos los empleados del período
        """
        from apps.payroll.models_extensions import EmployeePeriodAssignment
        
        assignments = EmployeePeriodAssignment.objects.filter(
            organization=self.organization,
            period=period,
            incluido=True
        ).select_related('employee')
        
        provisiones_creadas = 0
        
        for assignment in assignments:
            try:
                provision = self.calcular_provision_mensual(
                    assignment.employee,
                    period,
                    assignment.salario_periodo
                )
                provisiones_creadas += 1
            except Exception as e:
                print(f"Error calculando provisión para {assignment.employee.get_full_name()}: {e}")
        
        return {
            'success': True,
            'provisiones_creadas': provisiones_creadas,
            'total_empleados': assignments.count()
        }
    
    def obtener_saldo_prestaciones(self, employee):
        """
        Obtiene el saldo actual de prestaciones sociales del empleado
        """
        saldos = {}
        
        for tipo in ['CESANTIAS', 'INTERESES_CESANTIAS', 'PRIMA', 'VACACIONES']:
            prestaciones = SocialBenefit.objects.filter(
                organization=self.organization,
                employee=employee,
                tipo=tipo
            ).order_by('-fecha_fin')
            
            total_causado = sum(p.valor_causado for p in prestaciones)
            total_pagado = sum(p.valor_pagado for p in prestaciones)
            saldo = total_causado - total_pagado
            
            saldos[tipo.lower()] = {
                'causado': total_causado,
                'pagado': total_pagado,
                'saldo': saldo
            }
        
        return saldos
