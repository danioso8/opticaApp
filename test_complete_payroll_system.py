"""
Script de prueba completa del sistema de nómina automatizado
Ejecutar: python test_complete_payroll_system.py
"""
import os
import django
from decimal import Decimal
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.organizations.models import Organization
from apps.payroll.models import (
    Employee, PayrollPeriod, AccrualConcept, DeductionConcept,
    PayrollEntry, Accrual, Deduction, PayrollAutomationConfig,
    PayrollPeriodWorkflow
)
from apps.payroll.services.calculation_engine import PayrollCalculationEngine
from apps.payroll.services.automation_service import PayrollAutomationService

User = get_user_model()

def print_header(text):
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_section(text):
    print(f"\n{'-'*80}")
    print(f"  {text}")
    print(f"{'-'*80}")

def test_complete_payroll_system():
    print_header("PRUEBA COMPLETA DEL SISTEMA DE NOMINA AUTOMATIZADO")
    
    # 1. Obtener organización de prueba
    print_section("1. CONFIGURACION INICIAL")
    
    try:
        org = Organization.objects.first()
        if not org:
            print("❌ No hay organizaciones. Creando una de prueba...")
            org = Organization.objects.create(
                name="Empresa de Prueba Nómina",
                slug="empresa-prueba-nomina",
                is_active=True
            )
        print(f"✅ Organización: {org.name}")
    except Exception as e:
        print(f"❌ Error obteniendo organización: {e}")
        return
    
    # 2. Configurar automatización con porcentajes personalizados
    print_section("2️⃣  CONFIGURACIÓN DE AUTOMATIZACIÓN")
    
    try:
        config, created = PayrollAutomationConfig.objects.get_or_create(
            organization=org,
            defaults={
                'activar_automatizacion': True,
                'dia_generacion': 25,
                'porcentaje_salud': Decimal('4.00'),
                'porcentaje_pension': Decimal('4.00'),
                'porcentaje_fsp_4_a_16': Decimal('1.00'),
                'porcentaje_fsp_16_a_17': Decimal('1.20'),
                'porcentaje_fsp_17_a_18': Decimal('1.40'),
                'porcentaje_fsp_18_a_19': Decimal('1.60'),
                'porcentaje_fsp_19_a_20': Decimal('1.80'),
                'porcentaje_fsp_mayor_20': Decimal('2.00'),
                'salario_minimo': Decimal('1300000'),
                'auxilio_transporte': Decimal('162000'),
            }
        )
        
        if created:
            print("✅ Configuración de automatización creada")
        else:
            print("✅ Configuración de automatización ya existe")
        
        print(f"   - Salud: {config.porcentaje_salud}%")
        print(f"   - Pensión: {config.porcentaje_pension}%")
        print(f"   - FSP 4-16 SMLV: {config.porcentaje_fsp_4_a_16}%")
        print(f"   - Salario mínimo: ${config.salario_minimo:,.0f}")
        print(f"   - Auxilio transporte: ${config.auxilio_transporte:,.0f}")
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return
    
    # 3. Crear conceptos de devengo y deducción
    print_section("3️⃣  CREACIÓN DE CONCEPTOS")
    
    try:
        # Conceptos de devengo
        salario_basico, _ = AccrualConcept.objects.get_or_create(
            organization=org,
            codigo='SAL_BAS',
            defaults={
                'nombre': 'Salario Básico',
                'tipo': 'SALARIO',
                'aplica_prestaciones': True,
                'aplica_seguridad_social': True
            }
        )
        
        aux_transporte, _ = AccrualConcept.objects.get_or_create(
            organization=org,
            codigo='AUX_TRA',
            defaults={
                'nombre': 'Auxilio de Transporte',
                'tipo': 'AUXILIO',
                'aplica_prestaciones': False,
                'aplica_seguridad_social': False
            }
        )
        
        # Conceptos de deducción
        salud, _ = DeductionConcept.objects.get_or_create(
            organization=org,
            codigo='DED_SAL',
            defaults={
                'nombre': 'Aporte Salud',
                'tipo': 'SALUD'
            }
        )
        
        pension, _ = DeductionConcept.objects.get_or_create(
            organization=org,
            codigo='DED_PEN',
            defaults={
                'nombre': 'Aporte Pensión',
                'tipo': 'PENSION'
            }
        )
        
        fsp, _ = DeductionConcept.objects.get_or_create(
            organization=org,
            codigo='DED_FSP',
            defaults={
                'nombre': 'Fondo de Solidaridad Pensional',
                'tipo': 'FSP'
            }
        )
        
        print(f"✅ Conceptos de devengo: {AccrualConcept.objects.filter(organization=org).count()}")
        print(f"✅ Conceptos de deducción: {DeductionConcept.objects.filter(organization=org).count()}")
        
    except Exception as e:
        print(f"❌ Error creando conceptos: {e}")
        return
    
    # 4. Crear empleados de prueba
    print_section("4️⃣  CREACIÓN DE EMPLEADOS")
    
    empleados_data = [
        {
            'nombre': 'Juan',
            'apellido': 'Pérez García',
            'documento': '1000000001',
            'salario': Decimal('1300000'),  # 1 SMLV
            'cargo': 'Auxiliar'
        },
        {
            'nombre': 'María',
            'apellido': 'González López',
            'documento': '1000000002',
            'salario': Decimal('3000000'),  # ~2.3 SMLV
            'cargo': 'Analista'
        },
        {
            'nombre': 'Carlos',
            'apellido': 'Rodríguez Martínez',
            'documento': '1000000003',
            'salario': Decimal('8000000'),  # ~6.15 SMLV
            'cargo': 'Coordinador'
        },
        {
            'nombre': 'Ana',
            'apellido': 'Martínez Silva',
            'documento': '1000000004',
            'salario': Decimal('25000000'),  # ~19.23 SMLV (con FSP mayor)
            'cargo': 'Gerente'
        }
    ]
    
    empleados = []
    try:
        for emp_data in empleados_data:
            empleado, created = Employee.objects.get_or_create(
                organization=org,
                numero_documento=emp_data['documento'],
                defaults={
                    'primer_nombre': emp_data['nombre'],
                    'primer_apellido': emp_data['apellido'],
                    'tipo_documento': 'CC',
                    'cargo': emp_data['cargo'],
                    'salario_basico': emp_data['salario'],
                    'activo': True,
                    'fecha_ingreso': date.today() - timedelta(days=365)
                }
            )
            empleados.append(empleado)
            status = "creado" if created else "ya existe"
            smlv = emp_data['salario'] / config.salario_minimo
            print(f"   {'✅' if created else '📋'} {emp_data['nombre']} {emp_data['apellido']}: "
                  f"${emp_data['salario']:,.0f} ({smlv:.2f} SMLV) - {status}")
        
        print(f"\n✅ Total empleados activos: {len(empleados)}")
        
    except Exception as e:
        print(f"❌ Error creando empleados: {e}")
        return
    
    # 5. Crear período de nómina
    print_section("5️⃣  CREACIÓN DE PERÍODO DE NÓMINA")
    
    try:
        hoy = date.today()
        inicio_mes = date(hoy.year, hoy.month, 1)
        if hoy.month == 12:
            fin_mes = date(hoy.year, 12, 31)
            fecha_pago = date(hoy.year + 1, 1, 5)
        else:
            siguiente_mes = hoy.month + 1
            fin_mes = date(hoy.year, siguiente_mes, 1) - timedelta(days=1)
            fecha_pago = date(hoy.year, siguiente_mes, 5)
        
        periodo, created = PayrollPeriod.objects.get_or_create(
            organization=org,
            nombre=f"Nómina {hoy.strftime('%B %Y')}",
            defaults={
                'fecha_inicio': inicio_mes,
                'fecha_fin': fin_mes,
                'fecha_pago': fecha_pago,
                'estado': 'ABIERTO'
            }
        )
        
        status = "creado" if created else "ya existe"
        print(f"✅ Período: {periodo.nombre} - {status}")
        print(f"   - Fecha inicio: {periodo.fecha_inicio.strftime('%d/%m/%Y')}")
        print(f"   - Fecha fin: {periodo.fecha_fin.strftime('%d/%m/%Y')}")
        print(f"   - Fecha pago: {periodo.fecha_pago.strftime('%d/%m/%Y')}")
        
    except Exception as e:
        print(f"❌ Error creando período: {e}")
        return
    
    # 6. Crear workflow automatizado
    print_section("6️⃣  WORKFLOW AUTOMATIZADO")
    
    try:
        workflow, created = PayrollPeriodWorkflow.objects.get_or_create(
            period=periodo,
            defaults={
                'estado': 'BORRADOR'
            }
        )
        
        status = "creado" if created else "ya existe"
        print(f"✅ Workflow: {workflow.get_estado_display()} - {status}")
        
    except Exception as e:
        print(f"❌ Error creando workflow: {e}")
        return
    
    # 7. Crear asignaciones de empleados al período
    print_section("7️⃣  ASIGNACIÓN DE EMPLEADOS AL PERÍODO")
    
    try:
        from apps.payroll.models import EmployeePeriodAssignment
        
        print(f"\n   🔄 Asignando {len(empleados)} empleados al período...")
        
        for empleado in empleados:
            assignment, created = EmployeePeriodAssignment.objects.get_or_create(
                organization=org,
                period=periodo,
                employee=empleado,
                defaults={
                    'salario_periodo': empleado.salario_basico,
                    'dias_trabajados': 30,
                    'incluido': True
                }
            )
            status = "asignado" if created else "ya asignado"
            print(f"   {'✅' if created else '📋'} {empleado.primer_nombre} {empleado.primer_apellido} - {status}")
        
        print(f"\n✅ Total asignaciones: {EmployeePeriodAssignment.objects.filter(period=periodo).count()}")
        
    except Exception as e:
        print(f"❌ Error en asignaciones: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 8. Calcular nómina automáticamente
    print_section("8️⃣  CÁLCULO AUTOMÁTICO DE NÓMINA")
    
    try:
        engine = PayrollCalculationEngine(periodo)
        
        print(f"\n   🔄 Calculando nómina para {len(empleados)} empleados...")
        resultado_calculo = engine.calcular_periodo_completo(tipo_calculo='INICIAL')
        
        if resultado_calculo['success']:
            print(f"\n   ✅ CÁLCULO COMPLETADO EXITOSAMENTE")
            print(f"      Empleados procesados: {resultado_calculo['empleados_procesados']}")
            
            # Obtener totales
            total_devengado = resultado_calculo['total_devengado']
            total_deducido = resultado_calculo['total_deducciones']
            total_neto = resultado_calculo['total_neto']
            
            print(f"\n   {'='*60}")
            print(f"   📊 DETALLE POR EMPLEADO")
            print(f"   {'='*60}")
            
            assignments = EmployeePeriodAssignment.objects.filter(period=periodo, incluido=True)
            for assignment in assignments:
                empleado = assignment.employee
                print(f"\n   👤 {empleado.primer_nombre} {empleado.primer_apellido}")
                print(f"      Salario base: ${empleado.salario_basico:,.0f}")
                print(f"      ✅ DEVENGADO: ${assignment.total_devengado:,.0f}")
                print(f"      ❌ DEDUCCIONES: ${assignment.total_deducido:,.0f}")
                print(f"      💰 NETO A PAGAR: ${assignment.neto_pagar:,.0f}")
        else:
            print(f"\n   ❌ Error en cálculo: {resultado_calculo.get('error', 'Error desconocido')}")
            total_devengado = Decimal('0')
            total_deducido = Decimal('0')
            total_neto = Decimal('0')
        
        print(f"\n   {'='*60}")
        print(f"   📊 RESUMEN GENERAL DEL PERÍODO")
        print(f"   {'='*60}")
        print(f"   Total Devengado:   ${total_devengado:,.0f}")
        print(f"   Total Deducido:    ${total_deducido:,.0f}")
        print(f"   Neto a Pagar:      ${total_neto:,.0f}")
        print(f"   Empleados:         {len(empleados)}")
        
    except Exception as e:
        print(f"❌ Error en cálculo: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 9. Probar estados del workflow
    print_section("9️⃣  PRUEBA DE ESTADOS DEL WORKFLOW")
    
    try:
        # Obtener o crear usuario de prueba
        user, _ = User.objects.get_or_create(
            username='admin_nomina',
            defaults={
                'email': 'admin@prueba.com',
                'is_staff': True
            }
        )
        
        service = PayrollAutomationService(org)
        
        print(f"   Estado actual: {workflow.get_estado_display()}")
        
        # Enviar a revisión
        print(f"\n   🔄 Enviando a revisión...")
        service.enviar_a_revision(periodo.id, user)
        workflow.refresh_from_db()
        print(f"   ✅ Estado: {workflow.get_estado_display()}")
        
        # Aprobar
        print(f"\n   🔄 Aprobando nómina...")
        service.aprobar(periodo.id, user)
        workflow.refresh_from_db()
        print(f"   ✅ Estado: {workflow.get_estado_display()}")
        
        # Procesar
        print(f"\n   🔄 Procesando nómina...")
        service.procesar(periodo.id, user)
        workflow.refresh_from_db()
        periodo.refresh_from_db()
        print(f"   ✅ Estado workflow: {workflow.get_estado_display()}")
        print(f"   ✅ Estado período: {periodo.estado}")
        
    except Exception as e:
        print(f"❌ Error en workflow: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 9. Resumen final
    print_header("✅ PRUEBA COMPLETADA EXITOSAMENTE")
    
    print(f"""
    📊 RESUMEN FINAL:
    ─────────────────────────────────────────────────────────
    • Organización:        {org.name}
    • Período:             {periodo.nombre}
    • Estado Período:      {periodo.estado}
    • Estado Workflow:     {workflow.get_estado_display()}
    • Empleados:           {len(empleados)}
    • Total Devengado:     ${total_devengado:,.0f}
    • Total Deducido:      ${total_deducido:,.0f}
    • Neto a Pagar:        ${total_neto:,.0f}
    
    🎯 PORCENTAJES CONFIGURABLES APLICADOS:
    ─────────────────────────────────────────────────────────
    • Salud:               {config.porcentaje_salud}%
    • Pensión:             {config.porcentaje_pension}%
    • FSP (4-16 SMLV):     {config.porcentaje_fsp_4_a_16}%
    • FSP (16-17 SMLV):    {config.porcentaje_fsp_16_a_17}%
    • FSP (17-18 SMLV):    {config.porcentaje_fsp_17_a_18}%
    • FSP (18-19 SMLV):    {config.porcentaje_fsp_18_a_19}%
    • FSP (19-20 SMLV):    {config.porcentaje_fsp_19_a_20}%
    • FSP (>20 SMLV):      {config.porcentaje_fsp_mayor_20}%
    
    🌐 ACCESO AL SISTEMA:
    ─────────────────────────────────────────────────────────
    Dashboard Principal:   http://127.0.0.1:8000/dashboard/payroll/
    Sistema Automatizado:  http://127.0.0.1:8000/dashboard/payroll/workflow/
    Configuración:         http://127.0.0.1:8000/dashboard/payroll/workflow/configuracion/
    Detalle Período:       http://127.0.0.1:8000/dashboard/payroll/workflow/periodo/{periodo.id}/
    """)

if __name__ == '__main__':
    test_complete_payroll_system()
