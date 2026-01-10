"""
Viewsets para el módulo de nómina
"""
from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .permissions import (
    get_user_payroll_role, 
    payroll_permission_required,
    contador_or_owner_required,
    can_approve_payroll,
    log_payroll_action
)
from .models import (
    Employee, PayrollPeriod, AccrualConcept, DeductionConcept,
    PayrollEntry, Accrual, Deduction, ElectronicPayrollDocument,
    LaborContract, SocialBenefit, VacationRequest, EmployeeLoan,
    MonthlyProvision, PILAReport, Incapacity
)
from .serializers import (
    EmployeeSerializer, EmployeeListSerializer,
    PayrollPeriodSerializer, PayrollPeriodListSerializer,
    AccrualConceptSerializer, DeductionConceptSerializer,
    PayrollEntrySerializer, PayrollEntryListSerializer,
    AccrualSerializer, DeductionSerializer,
    ElectronicPayrollDocumentSerializer
)

# Importar modelo de empleados de dashboard para sincronización
try:
    from apps.dashboard.models_employee import Employee as DashboardEmployee
    DASHBOARD_EMPLOYEE_INSTALLED = True
except ImportError:
    DASHBOARD_EMPLOYEE_INSTALLED = False


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet para empleados"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['activo', 'tipo_contrato']
    search_fields = ['numero_documento', 'primer_nombre', 'primer_apellido', 'email']
    ordering_fields = ['primer_apellido', 'fecha_ingreso', 'salario_basico']
    ordering = ['primer_apellido', 'primer_nombre']
    
    def get_queryset(self):
        return Employee.objects.filter(organization=self.request.organization)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        return EmployeeSerializer
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Retorna solo empleados activos"""
        queryset = self.get_queryset().filter(activo=True)
        serializer = EmployeeListSerializer(queryset, many=True)
        return Response(serializer.data)


class AccrualConceptViewSet(viewsets.ModelViewSet):
    """ViewSet para conceptos de devengados"""
    permission_classes = [IsAuthenticated]
    serializer_class = AccrualConceptSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tipo', 'activo']
    search_fields = ['codigo', 'nombre']
    ordering = ['codigo']
    
    def get_queryset(self):
        return AccrualConcept.objects.filter(organization=self.request.organization)
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class DeductionConceptViewSet(viewsets.ModelViewSet):
    """ViewSet para conceptos de deducciones"""
    permission_classes = [IsAuthenticated]
    serializer_class = DeductionConceptSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tipo', 'activo']
    search_fields = ['codigo', 'nombre']
    ordering = ['codigo']
    
    def get_queryset(self):
        return DeductionConcept.objects.filter(organization=self.request.organization)
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class PayrollPeriodViewSet(viewsets.ModelViewSet):
    """ViewSet para períodos de nómina"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['estado', 'tipo_periodo']
    ordering = ['-fecha_inicio']
    
    def get_queryset(self):
        return PayrollPeriod.objects.filter(
            organization=self.request.organization
        ).prefetch_related('entries')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PayrollPeriodListSerializer
        return PayrollPeriodSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def calcular(self, request, pk=None):
        """Calcula la nómina para todos los empleados del período"""
        periodo = self.get_object()
        
        if periodo.estado not in ['BORRADOR', 'CALCULADO']:
            return Response(
                {'error': 'El período debe estar en estado BORRADOR o CALCULADO'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener empleados activos
        empleados = Employee.objects.filter(
            organization=periodo.organization,
            activo=True
        )
        
        entradas_creadas = 0
        for empleado in empleados:
            # Crear o actualizar entrada de nómina
            entrada, created = PayrollEntry.objects.get_or_create(
                periodo=periodo,
                empleado=empleado,
                organization=periodo.organization,
                defaults={'dias_trabajados': 30}
            )
            
            if created:
                entradas_creadas += 1
                
                # Crear devengado de salario básico
                concepto_salario = AccrualConcept.objects.filter(
                    organization=periodo.organization,
                    tipo='BASICO',
                    activo=True
                ).first()
                
                if concepto_salario:
                    Accrual.objects.create(
                        entrada=entrada,
                        concepto=concepto_salario,
                        cantidad=1,
                        valor_unitario=empleado.salario_basico,
                        valor=empleado.salario_basico,
                        organization=periodo.organization
                    )
                
                # Crear deducciones obligatorias (salud 4%, pensión 4%)
                concepto_salud = DeductionConcept.objects.filter(
                    organization=periodo.organization,
                    tipo='SALUD',
                    activo=True
                ).first()
                
                if concepto_salud:
                    valor_salud = empleado.salario_basico * Decimal('0.04')
                    Deduction.objects.create(
                        entrada=entrada,
                        concepto=concepto_salud,
                        porcentaje=4,
                        valor=valor_salud,
                        organization=periodo.organization
                    )
                
                concepto_pension = DeductionConcept.objects.filter(
                    organization=periodo.organization,
                    tipo='PENSION',
                    activo=True
                ).first()
                
                if concepto_pension:
                    valor_pension = empleado.salario_basico * Decimal('0.04')
                    Deduction.objects.create(
                        entrada=entrada,
                        concepto=concepto_pension,
                        porcentaje=4,
                        valor=valor_pension,
                        organization=periodo.organization
                    )
        
        # Actualizar totales del período
        totales = periodo.entries.aggregate(
            total_devengado=Sum('total_devengado'),
            total_deducciones=Sum('total_deducciones'),
            total_neto=Sum('total_neto')
        )
        
        periodo.total_devengado = totales['total_devengado'] or 0
        periodo.total_deducciones = totales['total_deducciones'] or 0
        periodo.total_neto = totales['total_neto'] or 0
        periodo.estado = 'CALCULADO'
        periodo.save()
        
        return Response({
            'mensaje': f'Nómina calculada exitosamente',
            'entradas_creadas': entradas_creadas,
            'total_empleados': empleados.count(),
            'total_devengado': periodo.total_devengado,
            'total_deducciones': periodo.total_deducciones,
            'total_neto': periodo.total_neto
        })
    
    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """Aprueba el período de nómina"""
        periodo = self.get_object()
        
        if periodo.estado != 'CALCULADO':
            return Response(
                {'error': 'El período debe estar en estado CALCULADO'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        periodo.estado = 'APROBADO'
        periodo.save()
        
        return Response({'mensaje': 'Período aprobado exitosamente'})


class PayrollEntryViewSet(viewsets.ModelViewSet):
    """ViewSet para entradas de nómina"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['periodo', 'empleado']
    ordering = ['empleado__primer_apellido']
    
    def get_queryset(self):
        return PayrollEntry.objects.filter(
            organization=self.request.organization
        ).select_related('periodo', 'empleado').prefetch_related('accruals', 'deductions')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PayrollEntryListSerializer
        return PayrollEntrySerializer
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class AccrualViewSet(viewsets.ModelViewSet):
    """ViewSet para devengados"""
    permission_classes = [IsAuthenticated]
    serializer_class = AccrualSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entrada', 'concepto']
    
    def get_queryset(self):
        return Accrual.objects.filter(organization=self.request.organization)
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class DeductionViewSet(viewsets.ModelViewSet):
    """ViewSet para deducciones"""
    permission_classes = [IsAuthenticated]
    serializer_class = DeductionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entrada', 'concepto']
    
    def get_queryset(self):
        return Deduction.objects.filter(organization=self.request.organization)
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class ElectronicPayrollDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet para documentos electrónicos de nómina"""
    permission_classes = [IsAuthenticated]
    serializer_class = ElectronicPayrollDocumentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['estado', 'entrada__periodo']
    ordering = ['-fecha_generacion']
    
    def get_queryset(self):
        return ElectronicPayrollDocument.objects.filter(
            organization=self.request.organization
        ).select_related('entrada__empleado', 'entrada__periodo')
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)
    
    @action(detail=True, methods=['post'])
    def generar_xml(self, request, pk=None):
        """Genera el XML del documento electrónico"""
        documento = self.get_object()
        
        # TODO: Implementar generación de XML según especificaciones DIAN
        # Por ahora retornamos un mensaje
        
        return Response({
            'mensaje': 'Generación de XML pendiente de implementación',
            'consecutivo': documento.consecutivo
        })
    
    @action(detail=True, methods=['post'])
    def enviar_dian(self, request, pk=None):
        """Envía el documento a la DIAN"""
        documento = self.get_object()
        
        if documento.estado != 'FIRMADO':
            return Response(
                {'error': 'El documento debe estar FIRMADO antes de enviarlo a DIAN'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Implementar envío a DIAN
        # Por ahora retornamos un mensaje
        
        return Response({
            'mensaje': 'Envío a DIAN pendiente de implementación',
            'consecutivo': documento.consecutivo
        })


# ============================================
# VISTAS DEL FRONTEND
# ============================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.organizations.decorators import require_feature


@login_required
@require_feature('payroll_dian')
def payroll_dashboard(request):
    """Dashboard principal de nómina"""
    organization = request.organization
    
    # Estadísticas
    total_empleados = Employee.objects.filter(organization=organization, activo=True).count()
    periodos_activos = PayrollPeriod.objects.filter(
        organization=organization,
        estado__in=['BORRADOR', 'CALCULADO', 'APROBADO']
    ).count()
    
    # Últimos períodos
    recent_periods = PayrollPeriod.objects.filter(
        organization=organization
    ).order_by('-fecha_inicio')[:5]
    
    context = {
        'total_empleados': total_empleados,
        'periodos_activos': periodos_activos,
        'recent_periods': recent_periods,
    }
    
    return render(request, 'payroll/dashboard.html', context)


@login_required
def employee_list(request):
    """Lista de todos los empleados de nómina"""
    organization = request.organization
    
    # Mostrar TODOS los empleados de la organización
    employees = Employee.objects.filter(
        organization=organization
    ).order_by('primer_apellido', 'primer_nombre')
    
    # Filtro por estado
    status_filter = request.GET.get('status')
    if status_filter == 'activo':
        employees = employees.filter(activo=True)
    elif status_filter == 'inactivo':
        employees = employees.filter(activo=False)
    
    # Filtro por búsqueda
    search = request.GET.get('search', '').strip()
    if search:
        from django.db.models import Q
        employees = employees.filter(
            Q(primer_nombre__icontains=search) |
            Q(segundo_nombre__icontains=search) |
            Q(primer_apellido__icontains=search) |
            Q(segundo_apellido__icontains=search) |
            Q(numero_documento__icontains=search) |
            Q(email__icontains=search) |
            Q(cargo__icontains=search)
        )
    
    context = {
        'employees': employees,
        'status_filter': status_filter,
        'search': search,
        'total_activos': Employee.objects.filter(organization=organization, activo=True).count(),
        'total_inactivos': Employee.objects.filter(organization=organization, activo=False).count(),
    }
    
    return render(request, 'payroll/employee_list.html', context)


@login_required
def employee_create(request):
    """Crear empleado"""
    if request.method == 'POST':
        try:
            # Crear empleado en nómina
            employee = Employee.objects.create(
                organization=request.organization,
                tipo_documento=request.POST.get('tipo_documento'),
                numero_documento=request.POST.get('numero_documento'),
                primer_nombre=request.POST.get('primer_nombre'),
                segundo_nombre=request.POST.get('segundo_nombre', ''),
                primer_apellido=request.POST.get('primer_apellido'),
                segundo_apellido=request.POST.get('segundo_apellido', ''),
                email=request.POST.get('email'),
                telefono=request.POST.get('telefono', ''),
                direccion=request.POST.get('direccion'),
                ciudad=request.POST.get('ciudad'),
                departamento=request.POST.get('departamento'),
                tipo_contrato=request.POST.get('tipo_contrato'),
                fecha_ingreso=request.POST.get('fecha_ingreso'),
                cargo=request.POST.get('cargo'),
                salario_basico=request.POST.get('salario_basico'),
                banco=request.POST.get('banco', ''),
                tipo_cuenta=request.POST.get('tipo_cuenta', ''),
                numero_cuenta=request.POST.get('numero_cuenta', ''),
            )
            
            # Sincronizar con dashboard/employees si está instalado
            if DASHBOARD_EMPLOYEE_INSTALLED:
                try:
                    # Combinar nombres y apellidos
                    first_name = ' '.join(filter(None, [
                        request.POST.get('primer_nombre', ''),
                        request.POST.get('segundo_nombre', '')
                    ])).strip()
                    
                    last_name = ' '.join(filter(None, [
                        request.POST.get('primer_apellido', ''),
                        request.POST.get('segundo_apellido', '')
                    ])).strip()
                    
                    # Crear o actualizar en dashboard
                    DashboardEmployee.objects.update_or_create(
                        organization=request.organization,
                        identification=request.POST.get('numero_documento'),
                        defaults={
                            'first_name': first_name,
                            'last_name': last_name,
                            'document_type': request.POST.get('tipo_documento'),
                            'email': request.POST.get('email', ''),
                            'phone': request.POST.get('telefono', ''),
                            'address': request.POST.get('direccion', ''),
                            'position': request.POST.get('cargo', 'OTRO'),
                            'hire_date': request.POST.get('fecha_ingreso'),
                            'salary': request.POST.get('salario_basico'),
                            'is_active': True,
                            'incluir_en_nomina': True,  # Automáticamente incluir en nómina
                            'ciudad': request.POST.get('ciudad', 'Bogotá'),
                            'departamento_ubicacion': request.POST.get('departamento', 'Cundinamarca'),
                        }
                    )
                except Exception as sync_error:
                    print(f"Error sincronizando con dashboard/employees: {sync_error}")
            
            messages.success(request, 'Empleado creado exitosamente')
            return redirect('payroll:employee_list')
        except Exception as e:
            messages.error(request, f'Error al crear empleado: {str(e)}')
    
    return render(request, 'payroll/employee_form.html', {})


@login_required
def employee_edit(request, pk):
    """Editar empleado"""
    employee = get_object_or_404(Employee, pk=pk, organization=request.organization)
    
    if request.method == 'POST':
        try:
            employee.tipo_documento = request.POST.get('tipo_documento')
            employee.numero_documento = request.POST.get('numero_documento')
            employee.primer_nombre = request.POST.get('primer_nombre')
            employee.segundo_nombre = request.POST.get('segundo_nombre', '')
            employee.primer_apellido = request.POST.get('primer_apellido')
            employee.segundo_apellido = request.POST.get('segundo_apellido', '')
            employee.email = request.POST.get('email')
            employee.telefono = request.POST.get('telefono', '')
            employee.direccion = request.POST.get('direccion')
            employee.ciudad = request.POST.get('ciudad')
            employee.departamento = request.POST.get('departamento')
            employee.tipo_contrato = request.POST.get('tipo_contrato')
            employee.fecha_ingreso = request.POST.get('fecha_ingreso')
            employee.cargo = request.POST.get('cargo')
            employee.salario_basico = request.POST.get('salario_basico')
            employee.banco = request.POST.get('banco', '')
            employee.tipo_cuenta = request.POST.get('tipo_cuenta', '')
            employee.numero_cuenta = request.POST.get('numero_cuenta', '')
            employee.activo = request.POST.get('activo') == 'on'
            employee.save()
            
            # Sincronizar con dashboard/employees si está instalado
            if DASHBOARD_EMPLOYEE_INSTALLED:
                try:
                    # Combinar nombres y apellidos
                    first_name = ' '.join(filter(None, [
                        request.POST.get('primer_nombre', ''),
                        request.POST.get('segundo_nombre', '')
                    ])).strip()
                    
                    last_name = ' '.join(filter(None, [
                        request.POST.get('primer_apellido', ''),
                        request.POST.get('segundo_apellido', '')
                    ])).strip()
                    
                    # Actualizar en dashboard
                    DashboardEmployee.objects.update_or_create(
                        organization=request.organization,
                        identification=request.POST.get('numero_documento'),
                        defaults={
                            'first_name': first_name,
                            'last_name': last_name,
                            'document_type': request.POST.get('tipo_documento'),
                            'email': request.POST.get('email', ''),
                            'phone': request.POST.get('telefono', ''),
                            'address': request.POST.get('direccion', ''),
                            'position': request.POST.get('cargo', 'OTRO'),
                            'hire_date': request.POST.get('fecha_ingreso'),
                            'salary': request.POST.get('salario_basico'),
                            'is_active': employee.activo,
                            'incluir_en_nomina': employee.activo,  # Sincronizar estado activo
                            'ciudad': request.POST.get('ciudad', 'Bogotá'),
                            'departamento_ubicacion': request.POST.get('departamento', 'Cundinamarca'),
                        }
                    )
                except Exception as sync_error:
                    print(f"Error sincronizando con dashboard/employees: {sync_error}")
            
            messages.success(request, 'Empleado actualizado exitosamente')
            return redirect('payroll:employee_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar empleado: {str(e)}')
    
    context = {
        'employee': employee,
        'is_edit': True,
    }
    
    return render(request, 'payroll/employee_form.html', context)


@login_required
def employee_delete(request, pk):
    """Eliminar empleado"""
    employee = get_object_or_404(Employee, pk=pk, organization=request.organization)
    
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Empleado eliminado exitosamente')
        return redirect('payroll:employee_list')
    
    return render(request, 'payroll/employee_confirm_delete.html', {'employee': employee})


@login_required
def period_list(request):
    """Lista de períodos de nómina"""
    organization = request.organization
    periods = PayrollPeriod.objects.filter(organization=organization).order_by('-fecha_inicio')
    
    context = {
        'periods': periods,
    }
    
    return render(request, 'payroll/period_list.html', context)


@login_required
def period_create(request):
    """Crear período de nómina"""
    if request.method == 'POST':
        try:
            PayrollPeriod.objects.create(
                organization=request.organization,
                nombre=request.POST.get('nombre'),
                tipo_periodo=request.POST.get('tipo_periodo'),
                fecha_inicio=request.POST.get('fecha_inicio'),
                fecha_fin=request.POST.get('fecha_fin'),
                fecha_pago=request.POST.get('fecha_pago'),
                observaciones=request.POST.get('observaciones', ''),
                created_by=request.user,
            )
            messages.success(request, 'Período de nómina creado exitosamente')
            return redirect('payroll:period_list')
        except Exception as e:
            messages.error(request, f'Error al crear período: {str(e)}')
    
    return render(request, 'payroll/period_form.html', {})


@login_required
def period_detail(request, pk):
    """Detalle de período de nómina"""
    period = get_object_or_404(
        PayrollPeriod, 
        pk=pk, 
        organization=request.organization
    )
    
    entries = period.entries.select_related('empleado').prefetch_related('accruals', 'deductions')
    
    context = {
        'period': period,
        'entries': entries,
    }
    
    return render(request, 'payroll/period_detail.html', context)


@login_required
def period_calculate(request, pk):
    """Calcular nómina de un período - INCLUYE activos, liquidados e incapacidades"""
    period = get_object_or_404(
        PayrollPeriod, 
        pk=pk, 
        organization=request.organization
    )
    
    if period.estado not in ['BORRADOR', 'CALCULADO']:
        messages.error(request, 'El período debe estar en estado BORRADOR o CALCULADO')
        return redirect('payroll:period_detail', pk=pk)
    
    # Obtener empleados activos
    empleados_activos = Employee.objects.filter(
        organization=period.organization,
        activo=True,
        fecha_ingreso__lte=period.fecha_fin
    )
    
    # Obtener empleados liquidados durante el período
    empleados_liquidados = Employee.objects.filter(
        organization=period.organization,
        activo=False,
        fecha_retiro__isnull=False,
        fecha_retiro__gte=period.fecha_inicio,
        fecha_retiro__lte=period.fecha_fin
    )
    
    # Combinar todos los empleados
    empleados = list(empleados_activos) + list(empleados_liquidados)
    
    entradas_creadas = 0
    incapacidades_procesadas = 0
    dias_periodo = (period.fecha_fin - period.fecha_inicio).days + 1
    
    for empleado in empleados:
        # Calcular días trabajados
        if empleado.activo:
            # Empleado activo: trabaja todo el período
            dias_trabajados = dias_periodo
        else:
            # Empleado liquidado: días hasta fecha de retiro
            if empleado.fecha_retiro:
                dias_trabajados = (empleado.fecha_retiro - period.fecha_inicio).days + 1
            else:
                dias_trabajados = dias_periodo
        
        # Crear o actualizar entrada de nómina
        entrada, created = PayrollEntry.objects.get_or_create(
            periodo=period,
            empleado=empleado,
            organization=period.organization,
            defaults={'dias_trabajados': dias_trabajados}
        )
        
        # Actualizar días si ya existía
        if not created:
            entrada.dias_trabajados = dias_trabajados
            entrada.save()
        else:
            entradas_creadas += 1
        
        # Solo crear conceptos si es nueva entrada
        if created:
            # 1. DEVENGADOS AUTOMÁTICOS
            
            # Salario básico (proporcional si es liquidado)
            concepto_salario = AccrualConcept.objects.filter(
                organization=period.organization,
                tipo='BASICO',
                activo=True
            ).first()
            
            if concepto_salario:
                if empleado.activo:
                    valor_salario = empleado.salario_basico
                else:
                    # Pago proporcional para liquidados
                    valor_salario = (empleado.salario_basico / 30) * dias_trabajados
                
                Accrual.objects.create(
                    entrada=entrada,
                    concepto=concepto_salario,
                    cantidad=1,
                    valor_unitario=valor_salario,
                    valor=valor_salario,
                    organization=period.organization
                )
            
            # Auxilio de transporte (si aplica y salario < 2 SMMLV)
            SMMLV_2026 = Decimal('1423500')  # Actualizar según año
            if empleado.salario_basico <= (SMMLV_2026 * 2):
                concepto_auxilio = AccrualConcept.objects.filter(
                    organization=period.organization,
                    tipo='AUXILIO_TRANSPORTE',
                    activo=True
                ).first()
                
                if concepto_auxilio:
                    AUXILIO_TRANSPORTE = Decimal('200000')  # Actualizar según año
                    if empleado.activo:
                        valor_auxilio = AUXILIO_TRANSPORTE
                    else:
                        valor_auxilio = (AUXILIO_TRANSPORTE / 30) * dias_trabajados
                    
                    Accrual.objects.create(
                        entrada=entrada,
                        concepto=concepto_auxilio,
                        cantidad=1,
                        valor_unitario=valor_auxilio,
                        valor=valor_auxilio,
                        organization=period.organization
                    )
            
            # 2. INCAPACIDADES APROBADAS
            incapacidades = Incapacity.objects.filter(
                employee=empleado,
                estado='APROBADA',
                fecha_inicio__lte=period.fecha_fin,
                fecha_fin__gte=period.fecha_inicio
            )
            
            for incapacidad in incapacidades:
                # Crear concepto de devengado por incapacidad
                concepto_incapacidad = AccrualConcept.objects.filter(
                    organization=period.organization,
                    tipo='INCAPACIDAD',
                    activo=True
                ).first()
                
                # Si no existe concepto de incapacidad, crearlo automáticamente
                if not concepto_incapacidad:
                    concepto_incapacidad = AccrualConcept.objects.create(
                        organization=period.organization,
                        codigo=f'INC-{incapacidad.get_tipo_display()[:3]}',
                        nombre=f'Incapacidad {incapacidad.get_tipo_display()}',
                        tipo='INCAPACIDAD',
                        activo=True
                    )
                
                Accrual.objects.create(
                    entrada=entrada,
                    concepto=concepto_incapacidad,
                    cantidad=incapacidad.dias_incapacidad,
                    valor_unitario=incapacidad.valor_dia,
                    valor=incapacidad.total_incapacidad,
                    observaciones=f'{incapacidad.get_tipo_display()} del {incapacidad.fecha_inicio} al {incapacidad.fecha_fin}',
                    organization=period.organization
                )
                
                # Marcar incapacidad como procesada
                incapacidad.estado = 'PROCESADA'
                incapacidad.save()
                incapacidades_procesadas += 1
            
            # 3. DEDUCCIONES OBLIGATORIAS
            
            # Salud (4%)
            concepto_salud = DeductionConcept.objects.filter(
                organization=period.organization,
                tipo='SALUD',
                activo=True
            ).first()
            
            if concepto_salud:
                valor_salud = empleado.salario_basico * Decimal('0.04')
                Deduction.objects.create(
                    entrada=entrada,
                    concepto=concepto_salud,
                    porcentaje=4,
                    valor=valor_salud,
                    organization=period.organization
                )
            
            # Pensión (4%)
            concepto_pension = DeductionConcept.objects.filter(
                organization=period.organization,
                tipo='PENSION',
                activo=True
            ).first()
            
            if concepto_pension:
                valor_pension = empleado.salario_basico * Decimal('0.04')
                Deduction.objects.create(
                    entrada=entrada,
                    concepto=concepto_pension,
                    porcentaje=4,
                    valor=valor_pension,
                    organization=period.organization
                )
            
            # Retención en la fuente (si aplica - salarios altos)
            if empleado.salario_basico > (SMMLV_2026 * 4):
                concepto_retencion = DeductionConcept.objects.filter(
                    organization=period.organization,
                    tipo='RETENCION',
                    activo=True
                ).first()
                
                if concepto_retencion:
                    # Cálculo simplificado (debería usar tabla de retención)
                    valor_retencion = empleado.salario_basico * Decimal('0.01')
                    Deduction.objects.create(
                        entrada=entrada,
                        concepto=concepto_retencion,
                        porcentaje=1,
                        valor=valor_retencion,
                        organization=period.organization
                    )
            
            # Préstamos activos del empleado
            prestamos = EmployeeLoan.objects.filter(
                employee=empleado,
                estado='ACTIVO',
                saldo_pendiente__gt=0
            )
            
            for prestamo in prestamos:
                concepto_prestamo = DeductionConcept.objects.filter(
                    organization=period.organization,
                    tipo='PRESTAMO',
                    activo=True
                ).first()
                
                if concepto_prestamo and prestamo.valor_cuota:
                    Deduction.objects.create(
                        entrada=entrada,
                        concepto=concepto_prestamo,
                        valor=prestamo.valor_cuota,
                        observaciones=f'Préstamo - Cuota {prestamo.cuotas_pagadas + 1} de {prestamo.numero_cuotas}',
                        organization=period.organization
                    )
        
        # Recalcular totales de la entrada
        entrada.calculate_totals()
    
    # Actualizar totales del período
    totales = period.entries.aggregate(
        total_devengado=Sum('total_devengado'),
        total_deducciones=Sum('total_deducciones'),
        total_neto=Sum('total_neto')
    )
    
    period.total_devengado = totales['total_devengado'] or 0
    period.total_deducciones = totales['total_deducciones'] or 0
    period.total_neto = totales['total_neto'] or 0
    period.estado = 'CALCULADO'
    period.save()
    
    mensaje = f'Nómina calculada exitosamente. {entradas_creadas} nuevas entradas, {incapacidades_procesadas} incapacidades procesadas.'
    if empleados_liquidados:
        mensaje += f' Incluye {len(empleados_liquidados)} empleado(s) liquidado(s).'
    
    messages.success(request, mensaje)
    return redirect('payroll:period_detail', pk=pk)
    
    period.total_devengado = totales['total_devengado'] or 0
    period.total_deducciones = totales['total_deducciones'] or 0
    period.total_neto = totales['total_neto'] or 0
    period.estado = 'CALCULADO'
    period.save()
    
    mensaje = f'Nómina calculada exitosamente. {entradas_creadas} nuevas entradas, {incapacidades_procesadas} incapacidades procesadas.'
    if empleados_liquidados:
        mensaje += f' Incluye {len(empleados_liquidados)} empleado(s) liquidado(s).'
    
    messages.success(request, mensaje)
    return redirect('payroll:period_detail', pk=pk)


# ============================================
# EDICIÓN MANUAL DE ENTRADAS (BORRADOR)
# ============================================

@login_required
def entry_edit(request, pk):
    """Editar entrada de nómina individual - Solo en BORRADOR"""
    entry = get_object_or_404(PayrollEntry, pk=pk, organization=request.organization)
    
    if entry.periodo.estado not in ['BORRADOR', 'CALCULADO']:
        messages.error(request, 'Solo se pueden editar entradas en estado BORRADOR o CALCULADO')
        return redirect('payroll:period_detail', entry.periodo.pk)
    
    if request.method == 'POST':
        try:
            entry.dias_trabajados = int(request.POST.get('dias_trabajados', 30))
            entry.observaciones = request.POST.get('observaciones', '')
            entry.save()
            entry.calculate_totals()
            
            messages.success(request, 'Entrada actualizada exitosamente')
            return redirect('payroll:period_detail', entry.periodo.pk)
        except Exception as e:
            messages.error(request, f'Error al actualizar entrada: {str(e)}')
    
    context = {
        'entry': entry,
        'accruals': entry.accruals.all(),
        'deductions': entry.deductions.all(),
    }
    
    return render(request, 'payroll/entry_edit.html', context)


@login_required
def entry_add_accrual(request, entry_id):
    """Agregar devengado manualmente a una entrada"""
    entry = get_object_or_404(PayrollEntry, pk=entry_id, organization=request.organization)
    
    if entry.periodo.estado not in ['BORRADOR', 'CALCULADO']:
        messages.error(request, 'Solo se pueden agregar conceptos en estado BORRADOR o CALCULADO')
        return redirect('payroll:period_detail', entry.periodo.pk)
    
    if request.method == 'POST':
        try:
            concepto_id = request.POST.get('concepto')
            cantidad = Decimal(request.POST.get('cantidad', '1'))
            valor_unitario = Decimal(request.POST.get('valor_unitario', '0'))
            observaciones = request.POST.get('observaciones', '')
            
            concepto = AccrualConcept.objects.get(pk=concepto_id, organization=request.organization)
            
            Accrual.objects.create(
                entrada=entry,
                concepto=concepto,
                cantidad=cantidad,
                valor_unitario=valor_unitario,
                valor=cantidad * valor_unitario,
                observaciones=observaciones,
                organization=request.organization
            )
            
            entry.calculate_totals()
            messages.success(request, f'Devengado "{concepto.nombre}" agregado exitosamente')
            return redirect('payroll:entry_edit', entry.pk)
        except Exception as e:
            messages.error(request, f'Error al agregar devengado: {str(e)}')
    
    # Obtener conceptos disponibles
    conceptos = AccrualConcept.objects.filter(
        organization=request.organization,
        activo=True
    ).order_by('codigo')
    
    context = {
        'entry': entry,
        'conceptos': conceptos,
    }
    
    return render(request, 'payroll/entry_add_accrual.html', context)


@login_required
def entry_add_deduction(request, entry_id):
    """Agregar deducción manualmente a una entrada"""
    entry = get_object_or_404(PayrollEntry, pk=entry_id, organization=request.organization)
    
    if entry.periodo.estado not in ['BORRADOR', 'CALCULADO']:
        messages.error(request, 'Solo se pueden agregar conceptos en estado BORRADOR o CALCULADO')
        return redirect('payroll:period_detail', entry.periodo.pk)
    
    if request.method == 'POST':
        try:
            concepto_id = request.POST.get('concepto')
            valor = Decimal(request.POST.get('valor', '0'))
            porcentaje = request.POST.get('porcentaje', '')
            observaciones = request.POST.get('observaciones', '')
            
            concepto = DeductionConcept.objects.get(pk=concepto_id, organization=request.organization)
            
            Deduction.objects.create(
                entrada=entry,
                concepto=concepto,
                valor=valor,
                porcentaje=Decimal(porcentaje) if porcentaje else None,
                observaciones=observaciones,
                organization=request.organization
            )
            
            entry.calculate_totals()
            messages.success(request, f'Deducción "{concepto.nombre}" agregada exitosamente')
            return redirect('payroll:entry_edit', entry.pk)
        except Exception as e:
            messages.error(request, f'Error al agregar deducción: {str(e)}')
    
    # Obtener conceptos disponibles
    conceptos = DeductionConcept.objects.filter(
        organization=request.organization,
        activo=True
    ).order_by('codigo')
    
    context = {
        'entry': entry,
        'conceptos': conceptos,
    }
    
    return render(request, 'payroll/entry_add_deduction.html', context)


@login_required
def entry_delete_accrual(request, pk):
    """Eliminar devengado de una entrada"""
    accrual = get_object_or_404(Accrual, pk=pk, organization=request.organization)
    entry = accrual.entrada
    
    if entry.periodo.estado not in ['BORRADOR', 'CALCULADO']:
        messages.error(request, 'Solo se pueden eliminar conceptos en estado BORRADOR o CALCULADO')
        return redirect('payroll:period_detail', entry.periodo.pk)
    
    if request.method == 'POST':
        concepto_nombre = accrual.concepto.nombre
        accrual.delete()
        entry.calculate_totals()
        messages.success(request, f'Devengado "{concepto_nombre}" eliminado exitosamente')
        return redirect('payroll:entry_edit', entry.pk)
    
    context = {'accrual': accrual, 'entry': entry}
    return render(request, 'payroll/entry_confirm_delete_accrual.html', context)


@login_required
def entry_delete_deduction(request, pk):
    """Eliminar deducción de una entrada"""
    deduction = get_object_or_404(Deduction, pk=pk, organization=request.organization)
    entry = deduction.entrada
    
    if entry.periodo.estado not in ['BORRADOR', 'CALCULADO']:
        messages.error(request, 'Solo se pueden eliminar conceptos en estado BORRADOR o CALCULADO')
        return redirect('payroll:period_detail', entry.periodo.pk)
    
    if request.method == 'POST':
        concepto_nombre = deduction.concepto.nombre
        deduction.delete()
        entry.calculate_totals()
        messages.success(request, f'Deducción "{concepto_nombre}" eliminada exitosamente')
        return redirect('payroll:entry_edit', entry.pk)
    
    context = {'deduction': deduction, 'entry': entry}
    return render(request, 'payroll/entry_confirm_delete_deduction.html', context)


@login_required
@contador_or_owner_required
def period_approve(request, pk):
    """Aprobar período de nómina - Solo contador o propietario"""
    period = get_object_or_404(
        PayrollPeriod, 
        pk=pk, 
        organization=request.organization
    )
    
    if period.estado != 'CALCULADO':
        messages.error(request, 'El período debe estar en estado CALCULADO para poder aprobarlo.')
        return redirect('payroll:period_detail', pk=pk)
    
    # Verificar permisos explícitamente
    if not can_approve_payroll(request.user, request.organization):
        messages.error(request, 'No tienes permisos para aprobar nóminas. Solo propietarios y contadores.')
        return redirect('payroll:period_detail', pk=pk)
    
    # Obtener rol del usuario
    user_role = get_user_payroll_role(request.user, request.organization)
    
    # Actualizar periodo con información de auditoría
    period.estado = 'APROBADO'
    period.aprobado_por = request.user
    period.fecha_aprobacion = timezone.now()
    period.rol_aprobador = user_role
    period.save()
    
    # Registrar acción en log de auditoría
    log_payroll_action(
        user=request.user,
        organization=request.organization,
        action='APROBACION',
        description=f'Nómina {period.nombre} aprobada por {user_role}: {request.user.get_full_name() or request.user.username}',
        period=period
    )
    
    messages.success(
        request, 
        f'Período aprobado exitosamente por {user_role}: {request.user.get_full_name() or request.user.username}'
    )
    return redirect('payroll:period_detail', pk=pk)


@login_required
def concept_list(request):
    """Lista de conceptos de nómina"""
    organization = request.organization
    
    accrual_concepts = AccrualConcept.objects.filter(organization=organization).order_by('codigo')
    deduction_concepts = DeductionConcept.objects.filter(organization=organization).order_by('codigo')
    
    context = {
        'accrual_concepts': accrual_concepts,
        'deduction_concepts': deduction_concepts,
    }
    
    return render(request, 'payroll/concept_list.html', context)


@login_required
def accrual_concept_create(request):
    """Crear nuevo concepto de devengado"""
    from .forms import AccrualConceptForm
    
    if request.method == 'POST':
        form = AccrualConceptForm(request.POST)
        if form.is_valid():
            concept = form.save(commit=False)
            concept.organization = request.organization
            concept.save()
            messages.success(request, f'Concepto de devengado "{concept.nombre}" creado exitosamente.')
            return redirect('payroll:concept_list')
    else:
        form = AccrualConceptForm()
    
    context = {
        'form': form,
        'title': 'Crear Concepto de Devengado',
        'concept_type': 'accrual'
    }
    return render(request, 'payroll/concept_form.html', context)


@login_required
def deduction_concept_create(request):
    """Crear nuevo concepto de deducción"""
    from .forms import DeductionConceptForm
    
    if request.method == 'POST':
        form = DeductionConceptForm(request.POST)
        if form.is_valid():
            concept = form.save(commit=False)
            concept.organization = request.organization
            concept.save()
            messages.success(request, f'Concepto de deducción "{concept.nombre}" creado exitosamente.')
            return redirect('payroll:concept_list')
    else:
        form = DeductionConceptForm()
    
    context = {
        'form': form,
        'title': 'Crear Concepto de Deducción',
        'concept_type': 'deduction'
    }
    return render(request, 'payroll/concept_form.html', context)


@login_required
def accrual_concept_edit(request, pk):
    """Editar concepto de devengado"""
    from .forms import AccrualConceptForm
    
    concept = get_object_or_404(AccrualConcept, pk=pk, organization=request.organization)
    
    if request.method == 'POST':
        form = AccrualConceptForm(request.POST, instance=concept)
        if form.is_valid():
            form.save()
            messages.success(request, f'Concepto de devengado "{concept.nombre}" actualizado exitosamente.')
            return redirect('payroll:concept_list')
    else:
        form = AccrualConceptForm(instance=concept)
    
    context = {
        'form': form,
        'title': f'Editar Concepto: {concept.nombre}',
        'concept_type': 'accrual',
        'concept': concept
    }
    return render(request, 'payroll/concept_form.html', context)


@login_required
def deduction_concept_edit(request, pk):
    """Editar concepto de deducción"""
    from .forms import DeductionConceptForm
    
    concept = get_object_or_404(DeductionConcept, pk=pk, organization=request.organization)
    
    if request.method == 'POST':
        form = DeductionConceptForm(request.POST, instance=concept)
        if form.is_valid():
            form.save()
            messages.success(request, f'Concepto de deducción "{concept.nombre}" actualizado exitosamente.')
            return redirect('payroll:concept_list')
    else:
        form = DeductionConceptForm(instance=concept)
    
    context = {
        'form': form,
        'title': f'Editar Concepto: {concept.nombre}',
        'concept_type': 'deduction',
        'concept': concept
    }
    return render(request, 'payroll/concept_form.html', context)


@login_required
def accrual_concept_delete(request, pk):
    """Eliminar concepto de devengado"""
    concept = get_object_or_404(AccrualConcept, pk=pk, organization=request.organization)
    
    if request.method == 'POST':
        nombre = concept.nombre
        concept.delete()
        messages.success(request, f'Concepto de devengado "{nombre}" eliminado exitosamente.')
        return redirect('payroll:concept_list')
    
    context = {
        'concept': concept,
        'concept_type': 'accrual'
    }
    return render(request, 'payroll/concept_confirm_delete.html', context)


@login_required
def deduction_concept_delete(request, pk):
    """Eliminar concepto de deducción"""
    concept = get_object_or_404(DeductionConcept, pk=pk, organization=request.organization)
    
    if request.method == 'POST':
        nombre = concept.nombre
        concept.delete()
        messages.success(request, f'Concepto de deducción "{nombre}" eliminado exitosamente.')
        return redirect('payroll:concept_list')
    
    context = {
        'concept': concept,
        'concept_type': 'deduction'
    }
    return render(request, 'payroll/concept_confirm_delete.html', context)


@login_required
def download_payslip(request, entry_id):
    """Descarga desprendible de pago de un empleado"""
    from django.http import HttpResponse
    from .pdf_generator import PayslipPDFGenerator
    
    entry = get_object_or_404(
        PayrollEntry,
        pk=entry_id,
        organization=request.organization
    )
    
    # Generar PDF
    generator = PayslipPDFGenerator(entry)
    pdf_buffer = generator.generate()
    
    # Crear respuesta HTTP
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    filename = f"desprendible_{entry.empleado.numero_documento}_{entry.periodo.nombre}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
def download_payroll_report(request, period_id):
    """Descarga reporte consolidado de nómina"""
    from django.http import HttpResponse
    from .pdf_generator import PayrollReportPDFGenerator
    
    period = get_object_or_404(
        PayrollPeriod,
        pk=period_id,
        organization=request.organization
    )
    
    # Generar PDF
    generator = PayrollReportPDFGenerator(period)
    pdf_buffer = generator.generate()
    
    # Crear respuesta HTTP
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    filename = f"reporte_nomina_{period.nombre}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
def send_to_dian(request, period_id):
    """Envía un período de nómina a la DIAN"""
    from .dian_integration import PayrollDIANService
    
    period = get_object_or_404(
        PayrollPeriod,
        pk=period_id,
        organization=request.organization
    )
    
    if period.estado != 'APROBADO':
        messages.error(request, 'El período debe estar APROBADO para enviar a la DIAN')
        return redirect('payroll:period_detail', pk=period_id)
    
    # Obtener o crear documento electrónico
    electronic_doc, created = ElectronicPayrollDocument.objects.get_or_create(
        payroll_period=period,
        organization=period.organization,
        defaults={
            'tipo_documento': 'NE',  # Nómina Electrónica
            'numero_documento': f"{period.nombre.replace(' ', '_')}"
        }
    )
    
    # Procesar y enviar
    dian_service = PayrollDIANService(period.organization)
    
    try:
        result = dian_service.process_and_send_document(electronic_doc)
        
        if result['success']:
            messages.success(request, f'Documento enviado exitosamente a la DIAN. ID: {electronic_doc.dian_tracking_id}')
            
            # Mostrar pasos
            for step in result['steps']:
                if step['success']:
                    messages.info(request, f"✓ {step['step']}: {step.get('message', 'OK')}")
                else:
                    messages.warning(request, f"✗ {step['step']}: {step.get('error', 'Error')}")
        else:
            messages.error(request, 'Error al procesar el documento para la DIAN')
            
            # Mostrar errores
            for step in result['steps']:
                if not step['success']:
                    messages.error(request, f"{step['step']}: {step.get('error', 'Error desconocido')}")
    
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('payroll:period_detail', pk=period_id)


@login_required
def check_dian_status(request, period_id):
    """Consulta el estado de un documento en la DIAN"""
    from .dian_integration import PayrollDIANService
    
    period = get_object_or_404(
        PayrollPeriod,
        pk=period_id,
        organization=request.organization
    )
    
    try:
        electronic_doc = ElectronicPayrollDocument.objects.get(payroll_period=period)
        
        dian_service = PayrollDIANService(period.organization)
        result = dian_service.check_document_status(electronic_doc)
        
        if result['success']:
            messages.success(
                request,
                f"Estado: {result.get('status', 'N/A')} - {result.get('status_message', 'Sin mensaje')}"
            )
        else:
            messages.error(request, f"Error al consultar estado: {result.get('error', 'Error desconocido')}")
    
    except ElectronicPayrollDocument.DoesNotExist:
        messages.error(request, 'No existe documento electrónico para este período')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('payroll:period_detail', pk=period_id)


# ============================================================================
# VISTAS DE WORKFLOW AUTOMATIZADO
# ============================================================================

from django.views.generic import TemplateView
from django.db.models import Q, Count
from apps.payroll.models import (
    PayrollPeriodWorkflow, PayrollAutomationConfig,
    EmployeePeriodAssignment, PayrollNotification
)
from apps.payroll.services.automation_service import PayrollAutomationService
from apps.payroll.services.calculation_engine import PayrollCalculationEngine
import json


@login_required
def workflow_dashboard(request):
    """Dashboard principal del workflow de nómina"""
    organization = request.organization
    
    # Métricas generales
    borradores = PayrollPeriodWorkflow.objects.filter(
        organization=organization,
        estado='BORRADOR'
    ).count()
    
    en_revision = PayrollPeriodWorkflow.objects.filter(
        organization=organization,
        estado='EN_REVISION'
    ).count()
    
    aprobados = PayrollPeriodWorkflow.objects.filter(
        organization=organization,
        estado='APROBADO'
    ).count()
    
    procesados = PayrollPeriodWorkflow.objects.filter(
        organization=organization,
        estado='PROCESADO'
    ).count()
    
    # Períodos recientes con workflow
    periodos_recientes = PayrollPeriod.objects.filter(
        organization=organization
    ).select_related('workflow').order_by('-fecha_inicio')[:10]
    
    # Notificaciones no leídas
    notificaciones = PayrollNotification.objects.filter(
        organization=organization,
        leida=False
    ).order_by('-created_at')[:5]
    
    # Próximas fechas de pago
    config, _ = PayrollAutomationConfig.objects.get_or_create(
        organization=organization
    )
    
    context = {
        'metrics': {
            'borradores': borradores,
            'en_revision': en_revision,
            'aprobados': aprobados,
            'procesados': procesados,
        },
        'periodos': periodos_recientes,
        'notificaciones': notificaciones,
        'config': config,
    }
    
    return render(request, 'payroll/workflow/dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def workflow_enviar_revision(request, period_id):
    """Enviar período a revisión"""
    try:
        period = PayrollPeriod.objects.get(
            pk=period_id,
            organization=request.organization
        )
        
        service = PayrollAutomationService(request.organization)
        notas = request.POST.get('notas', '')
        
        result = service.enviar_a_revision(period, request.user, notas)
        
        if result['success']:
            messages.success(request, f"Período enviado a revisión. {result['message']}")
        else:
            messages.error(request, f"Error: {result['message']}")
            
    except PayrollPeriod.DoesNotExist:
        messages.error(request, 'Período no encontrado')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('payroll:workflow_dashboard')


@login_required
@require_http_methods(["POST"])
def workflow_aprobar(request, period_id):
    """Aprobar período de nómina"""
    try:
        period = PayrollPeriod.objects.get(
            pk=period_id,
            organization=request.organization
        )
        
        service = PayrollAutomationService(request.organization)
        notas = request.POST.get('notas', '')
        
        result = service.aprobar_nomina(period, request.user, notas)
        
        if result['success']:
            messages.success(request, f"Nómina aprobada exitosamente. {result['message']}")
        else:
            messages.error(request, f"Error: {result['message']}")
            
    except PayrollPeriod.DoesNotExist:
        messages.error(request, 'Período no encontrado')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('payroll:workflow_dashboard')


@login_required
@require_http_methods(["POST"])
def workflow_rechazar(request, period_id):
    """Rechazar período de nómina"""
    try:
        period = PayrollPeriod.objects.get(
            pk=period_id,
            organization=request.organization
        )
        
        service = PayrollAutomationService(request.organization)
        motivo = request.POST.get('motivo', '')
        
        if not motivo:
            messages.error(request, 'Debe proporcionar un motivo de rechazo')
            return redirect('payroll:workflow_dashboard')
        
        result = service.rechazar_nomina(period, request.user, motivo)
        
        if result['success']:
            messages.warning(request, f"Nómina rechazada. {result['message']}")
        else:
            messages.error(request, f"Error: {result['message']}")
            
    except PayrollPeriod.DoesNotExist:
        messages.error(request, 'Período no encontrado')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('payroll:workflow_dashboard')


@login_required
@require_http_methods(["POST"])
def workflow_procesar(request, period_id):
    """Procesar nómina aprobada"""
    try:
        period = PayrollPeriod.objects.get(
            pk=period_id,
            organization=request.organization
        )
        
        service = PayrollAutomationService(request.organization)
        
        result = service.procesar_nomina(period, request.user)
        
        if result['success']:
            messages.success(request, f"Nómina procesada exitosamente. {result['message']}")
        else:
            messages.error(request, f"Error: {result['message']}")
            
    except PayrollPeriod.DoesNotExist:
        messages.error(request, 'Período no encontrado')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('payroll:workflow_dashboard')


@login_required
def workflow_period_detail(request, period_id):
    """Detalle de período con workflow"""
    try:
        period = PayrollPeriod.objects.get(
            pk=period_id,
            organization=request.organization
        )
        
        # Obtener o crear workflow (solo por period, ya que es OneToOne)
        workflow, created = PayrollPeriodWorkflow.objects.get_or_create(
            period=period,
            defaults={
                'organization': request.organization,
                'usuario_creador': request.user
            }
        )
        
        # Asignaciones de empleados
        asignaciones = EmployeePeriodAssignment.objects.filter(
            period=period,
            organization=request.organization,
            incluido=True
        ).select_related('employee').order_by('employee__primer_apellido')
        
        # Calcular totales
        totales = asignaciones.aggregate(
            total_devengado=Sum('total_devengado'),
            total_deducido=Sum('total_deducido'),
            total_neto=Sum('neto_pagar')
        )
        
        context = {
            'period': period,
            'workflow': workflow,
            'asignaciones': asignaciones,
            'totales': totales,
            'puede_enviar_revision': workflow.estado == 'BORRADOR',
            'puede_aprobar': workflow.estado == 'EN_REVISION',
            'puede_rechazar': workflow.estado in ['EN_REVISION', 'APROBADO'],
            'puede_procesar': workflow.estado == 'APROBADO',
        }
        
        return render(request, 'payroll/workflow/period_detail.html', context)
        
    except PayrollPeriod.DoesNotExist:
        messages.error(request, 'Período no encontrado')
        return redirect('payroll:workflow_dashboard')


@login_required
def workflow_generar_borrador(request):
    """Vista para generar borrador manualmente"""
    if request.method == 'POST':
        try:
            service = PayrollAutomationService(request.organization)
            
            # Obtener fechas del formulario
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            fecha_pago = request.POST.get('fecha_pago')
            descripcion = request.POST.get('descripcion', '')
            
            result = service.generar_borrador_automatico(
                fecha_inicio, fecha_fin, fecha_pago, descripcion
            )
            
            if result['success']:
                messages.success(
                    request,
                    f"Borrador generado exitosamente. {result['empleados_procesados']} empleados incluidos."
                )
                return redirect('payroll:workflow_period_detail', period_id=result['period'].id)
            else:
                messages.error(request, f"Error: {result['message']}")
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'payroll/workflow/generar_borrador.html')


@login_required
def workflow_configuracion(request):
    """Vista de configuración de automatización"""
    config, created = PayrollAutomationConfig.objects.get_or_create(
        organization=request.organization
    )
    
    if request.method == 'POST':
        try:
            from decimal import Decimal
            
            config.dia_pago_mensual = int(request.POST.get('dia_pago_mensual', 30))
            config.dia_pago_quincenal_1 = int(request.POST.get('dia_pago_quincenal_1', 15))
            config.dia_pago_quincenal_2 = int(request.POST.get('dia_pago_quincenal_2', 30))
            config.dias_anticipacion_borrador = int(request.POST.get('dias_anticipacion_borrador', 5))
            
            config.auto_generar_borradores = request.POST.get('auto_generar_borradores') == 'on'
            config.enviar_notificacion_borrador = request.POST.get('enviar_notificacion_borrador') == 'on'
            config.enviar_notificacion_aprobacion = request.POST.get('enviar_notificacion_aprobacion') == 'on'
            config.enviar_notificacion_procesado = request.POST.get('enviar_notificacion_procesado') == 'on'
            
            config.validar_salario_minimo = request.POST.get('validar_salario_minimo') == 'on'
            config.validar_seguridad_social = request.POST.get('validar_seguridad_social') == 'on'
            config.validar_prestaciones = request.POST.get('validar_prestaciones') == 'on'
            
            config.calcular_horas_extras = request.POST.get('calcular_horas_extras') == 'on'
            config.calcular_auxilio_transporte = request.POST.get('calcular_auxilio_transporte') == 'on'
            config.calcular_prestaciones_sociales = request.POST.get('calcular_prestaciones_sociales') == 'on'
            
            # Porcentajes de deducciones
            config.porcentaje_salud = Decimal(request.POST.get('porcentaje_salud', '4.00'))
            config.porcentaje_pension = Decimal(request.POST.get('porcentaje_pension', '4.00'))
            config.porcentaje_fsp_4_a_16 = Decimal(request.POST.get('porcentaje_fsp_4_a_16', '1.00'))
            config.porcentaje_fsp_16_a_17 = Decimal(request.POST.get('porcentaje_fsp_16_a_17', '1.20'))
            config.porcentaje_fsp_17_a_18 = Decimal(request.POST.get('porcentaje_fsp_17_a_18', '1.40'))
            config.porcentaje_fsp_18_a_19 = Decimal(request.POST.get('porcentaje_fsp_18_a_19', '1.60'))
            config.porcentaje_fsp_19_a_20 = Decimal(request.POST.get('porcentaje_fsp_19_a_20', '1.80'))
            config.porcentaje_fsp_mayor_20 = Decimal(request.POST.get('porcentaje_fsp_mayor_20', '2.00'))
            
            # Valores legales
            config.salario_minimo = Decimal(request.POST.get('salario_minimo', '1300000'))
            config.auxilio_transporte = Decimal(request.POST.get('auxilio_transporte', '162000'))
            
            config.save()
            
            messages.success(request, 'Configuración guardada exitosamente')
            
        except Exception as e:
            messages.error(request, f'Error al guardar configuración: {str(e)}')
    
    return render(request, 'payroll/workflow/configuracion.html', {'config': config})


# ==================== VISTAS NUEVAS: PRESTACIONES SOCIALES ====================

# Contratos Laborales
def contract_list(request):
    """Lista de contratos laborales"""
    contracts = LaborContract.objects.filter(
        organization=request.organization
    ).select_related('employee').order_by('-fecha_inicio')
    
    context = {
        'contracts': contracts,
        'total_contratos': contracts.count(),
        'contratos_activos': contracts.filter(estado='ACTIVO').count(),
        'contratos_terminados': contracts.filter(estado='TERMINADO').count(),
    }
    return render(request, 'payroll/contracts/list.html', context)


def contract_create(request):
    """Crear nuevo contrato"""
    if request.method == 'POST':
        try:
            employee = get_object_or_404(Employee, pk=request.POST.get('employee'), organization=request.organization)
            
            contract = LaborContract.objects.create(
                organization=request.organization,
                employee=employee,
                numero_contrato=request.POST.get('numero_contrato'),
                tipo_contrato=request.POST.get('tipo_contrato'),
                fecha_inicio=request.POST.get('fecha_inicio'),
                fecha_fin=request.POST.get('fecha_fin') if request.POST.get('fecha_fin') else None,
                salario_contratado=Decimal(request.POST.get('salario_contratado')),
                auxilio_transporte=request.POST.get('auxilio_transporte') == 'on',
                horas_semanales=int(request.POST.get('horas_semanales', 48)),
                cargo=request.POST.get('cargo', ''),
                estado='ACTIVO'
            )
            
            messages.success(request, f'Contrato {contract.numero_contrato} creado exitosamente')
            return redirect('payroll:contract_list')
            
        except Exception as e:
            messages.error(request, f'Error al crear contrato: {str(e)}')
    
    employees = Employee.objects.filter(organization=request.organization, activo=True)
    return render(request, 'payroll/contracts/create.html', {'employees': employees})


def contract_detail(request, pk):
    """Detalle de contrato"""
    contract = get_object_or_404(LaborContract, pk=pk, organization=request.organization)
    
    # Calcular prestaciones si el contrato está terminado
    liquidacion = None
    if contract.estado in ['TERMINADO', 'LIQUIDADO']:
        from apps.payroll.services.social_benefits_calculator import SocialBenefitsCalculator
        calculator = SocialBenefitsCalculator(request.organization)
        liquidacion = calculator.liquidar_prestaciones(contract.employee, contract.fecha_terminacion or timezone.now().date())
    
    context = {
        'contract': contract,
        'liquidacion': liquidacion
    }
    return render(request, 'payroll/contracts/detail.html', context)


# Vacaciones
def vacation_list(request):
    """Lista de solicitudes de vacaciones"""
    vacations = VacationRequest.objects.filter(
        organization=request.organization
    ).select_related('employee', 'aprobado_por').order_by('-fecha_solicitud')
    
    # Filtros
    estado = request.GET.get('estado')
    if estado:
        vacations = vacations.filter(estado=estado)
    
    context = {
        'vacations': vacations,
        'total_solicitudes': vacations.count(),
        'pendientes': vacations.filter(estado='PENDIENTE').count(),
        'aprobadas': vacations.filter(estado='APROBADA').count(),
    }
    return render(request, 'payroll/vacations/list.html', context)


def vacation_create(request):
    """Crear solicitud de vacaciones"""
    if request.method == 'POST':
        try:
            employee = get_object_or_404(Employee, pk=request.POST.get('employee'), organization=request.organization)
            
            vacation = VacationRequest.objects.create(
                organization=request.organization,
                employee=employee,
                fecha_solicitud=timezone.now().date(),
                fecha_inicio=request.POST.get('fecha_inicio'),
                fecha_fin=request.POST.get('fecha_fin'),
                fecha_reintegro=request.POST.get('fecha_reintegro'),
                dias_solicitados=int(request.POST.get('dias_solicitados')),
                dias_habiles=int(request.POST.get('dias_habiles')),
                dias_calendario=int(request.POST.get('dias_calendario')),
                pago_anticipado=request.POST.get('pago_anticipado') == 'on',
                valor_pago=Decimal(request.POST.get('valor_pago', '0')),
                observaciones=request.POST.get('observaciones', ''),
                estado='PENDIENTE'
            )
            
            messages.success(request, 'Solicitud de vacaciones creada exitosamente')
            return redirect('payroll:vacation_list')
            
        except Exception as e:
            messages.error(request, f'Error al crear solicitud: {str(e)}')
    
    employees = Employee.objects.filter(organization=request.organization, activo=True)
    return render(request, 'payroll/vacations/create.html', {'employees': employees})


def vacation_approve(request, pk):
    """Aprobar vacaciones"""
    vacation = get_object_or_404(VacationRequest, pk=pk, organization=request.organization)
    
    if vacation.estado == 'PENDIENTE':
        vacation.aprobar(request.user)
        messages.success(request, f'Vacaciones aprobadas para {vacation.employee.get_full_name()}')
    else:
        messages.warning(request, 'Esta solicitud ya fue procesada')
    
    return redirect('payroll:vacation_list')


def vacation_reject(request, pk):
    """Rechazar vacaciones"""
    vacation = get_object_or_404(VacationRequest, pk=pk, organization=request.organization)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', 'Sin motivo especificado')
        vacation.rechazar(request.user, motivo)
        messages.success(request, 'Solicitud rechazada')
        return redirect('payroll:vacation_list')
    
    return render(request, 'payroll/vacations/reject.html', {'vacation': vacation})


# Préstamos
def loan_list(request):
    """Lista de préstamos"""
    loans = EmployeeLoan.objects.filter(
        organization=request.organization
    ).select_related('employee', 'aprobado_por').order_by('-fecha_solicitud')
    
    # Filtros
    estado = request.GET.get('estado')
    if estado:
        loans = loans.filter(estado=estado)
    
    context = {
        'loans': loans,
        'total_prestamos': loans.count(),
        'solicitados': loans.filter(estado='SOLICITADO').count(),
        'activos': loans.filter(estado='ACTIVO').count(),
        'total_monto': loans.filter(estado__in=['ACTIVO', 'APROBADO']).aggregate(Sum('monto_aprobado'))['monto_aprobado__sum'] or 0,
    }
    return render(request, 'payroll/loans/list.html', context)


def loan_create(request):
    """Crear solicitud de préstamo"""
    if request.method == 'POST':
        try:
            employee = get_object_or_404(Employee, pk=request.POST.get('employee'), organization=request.organization)
            
            loan = EmployeeLoan.objects.create(
                organization=request.organization,
                employee=employee,
                numero_prestamo=request.POST.get('numero_prestamo'),
                fecha_solicitud=timezone.now().date(),
                monto_solicitado=Decimal(request.POST.get('monto_solicitado')),
                numero_cuotas=int(request.POST.get('numero_cuotas')),
                tasa_interes=Decimal(request.POST.get('tasa_interes', '1.5')),
                motivo_solicitud=request.POST.get('motivo_solicitud', ''),
                estado='SOLICITADO'
            )
            
            messages.success(request, f'Préstamo {loan.numero_prestamo} solicitado exitosamente')
            return redirect('payroll:loan_list')
            
        except Exception as e:
            messages.error(request, f'Error al crear préstamo: {str(e)}')
    
    employees = Employee.objects.filter(organization=request.organization, activo=True)
    return render(request, 'payroll/loans/create.html', {'employees': employees})


def loan_approve(request, pk):
    """Aprobar préstamo"""
    loan = get_object_or_404(EmployeeLoan, pk=pk, organization=request.organization)
    
    if request.method == 'POST':
        monto_aprobado = Decimal(request.POST.get('monto_aprobado'))
        loan.aprobar(request.user, monto_aprobado)
        messages.success(request, f'Préstamo aprobado - Cuota mensual: ${loan.valor_cuota:,.0f}')
        return redirect('payroll:loan_list')
    
    return render(request, 'payroll/loans/approve.html', {'loan': loan})


def loan_disburse(request, pk):
    """Desembolsar préstamo (iniciar descuentos)"""
    loan = get_object_or_404(EmployeeLoan, pk=pk, organization=request.organization)
    
    if loan.estado == 'APROBADO':
        loan.desembolsar()
        messages.success(request, 'Préstamo desembolsado - Los descuentos iniciarán en la próxima nómina')
    else:
        messages.warning(request, 'Solo se pueden desembolsar préstamos aprobados')
    
    return redirect('payroll:loan_list')


# Dashboard de Prestaciones Sociales
def social_benefits_dashboard(request):
    """Dashboard de prestaciones sociales"""
    from apps.payroll.services.social_benefits_calculator import SocialBenefitsCalculator
    
    # Obtener empleados activos
    employees = Employee.objects.filter(organization=request.organization, activo=True)
    
    # Calcular saldo de prestaciones para cada empleado
    calculator = SocialBenefitsCalculator(request.organization)
    prestaciones_por_empleado = []
    
    for employee in employees:
        saldos = calculator.obtener_saldo_prestaciones(employee)
        prestaciones_por_empleado.append({
            'employee': employee,
            'saldos': saldos
        })
    
    # Totales
    total_cesantias = sum(emp['saldos'].get('CESANTIAS', {}).get('saldo', 0) for emp in prestaciones_por_empleado)
    total_intereses = sum(emp['saldos'].get('INTERESES_CESANTIAS', {}).get('saldo', 0) for emp in prestaciones_por_empleado)
    total_prima = sum(emp['saldos'].get('PRIMA', {}).get('saldo', 0) for emp in prestaciones_por_empleado)
    total_vacaciones = sum(emp['saldos'].get('VACACIONES', {}).get('saldo', 0) for emp in prestaciones_por_empleado)
    
    context = {
        'prestaciones_por_empleado': prestaciones_por_empleado,
        'total_cesantias': total_cesantias,
        'total_intereses': total_intereses,
        'total_prima': total_prima,
        'total_vacaciones': total_vacaciones,
        'total_general': total_cesantias + total_intereses + total_prima + total_vacaciones,
    }
    return render(request, 'payroll/social_benefits/dashboard.html', context)


# Provisiones Mensuales
def provision_list(request):
    """Lista de provisiones mensuales"""
    provisions = MonthlyProvision.objects.filter(
        organization=request.organization
    ).select_related('employee', 'period').order_by('-period__fecha_inicio')
    
    # Filtro por período
    period_id = request.GET.get('period')
    if period_id:
        provisions = provisions.filter(period_id=period_id)
    
    periods = PayrollPeriod.objects.filter(organization=request.organization).order_by('-fecha_inicio')[:12]
    
    # Calcular totales por concepto
    totals = provisions.aggregate(
        total_cesantias=Sum('cesantias'),
        total_intereses=Sum('intereses_cesantias'),
        total_prima=Sum('prima'),
        total_vacaciones=Sum('vacaciones'),
        total_general=Sum('total_provision')
    )
    
    context = {
        'provisions': provisions,
        'periods': periods,
        'years': range(2020, 2031),
        'current_year': 2026,
        'total_cesantias': totals['total_cesantias'] or 0,
        'total_intereses': totals['total_intereses'] or 0,
        'total_prima': totals['total_prima'] or 0,
        'total_vacaciones': totals['total_vacaciones'] or 0,
        'total_general': totals['total_general'] or 0,
    }
    return render(request, 'payroll/provisions/list.html', context)


# Reportes PILA
def pila_list(request):
    """Lista de reportes PILA"""
    reports = PILAReport.objects.filter(
        organization=request.organization
    ).order_by('-anio', '-mes')
    
    # Calcular totales
    totals = reports.aggregate(
        total_salud=Sum('total_salud'),
        total_pension=Sum('total_pension'),
        total_arl=Sum('total_riesgos'),
        total_aportes=Sum('total_aportes')
    )
    
    context = {
        'pila_reports': reports,
        'years': range(2020, 2031),
        'current_year': 2026,
        'total_salud': totals['total_salud'] or 0,
        'total_pension': totals['total_pension'] or 0,
        'total_arl': totals['total_arl'] or 0,
        'total_aportes': totals['total_aportes'] or 0,
    }
    return render(request, 'payroll/pila/list.html', context)


def pila_create(request):
    """Crear reporte PILA"""
    if request.method == 'POST':
        try:
            # Aquí iría la lógica de generación del archivo PILA
            report = PILAReport.objects.create(
                organization=request.organization,
                numero_planilla=request.POST.get('numero_planilla'),
                mes=int(request.POST.get('mes')),
                anio=int(request.POST.get('anio')),
                estado='BORRADOR'
            )
            
            messages.success(request, f'Reporte PILA {report.numero_planilla} creado')
            return redirect('payroll:pila_list')
            
        except Exception as e:
            messages.error(request, f'Error al crear reporte: {str(e)}')
    
    return render(request, 'payroll/pila/create.html', {})


# ============================================
# GESTIÓN DE INCAPACIDADES
# ============================================

@login_required
def incapacity_list(request):
    """Lista de incapacidades"""
    organization = request.organization
    
    # Filtros
    estado = request.GET.get('estado', '')
    employee_id = request.GET.get('employee', '')
    
    incapacidades = Incapacity.objects.filter(organization=organization)
    
    if estado:
        incapacidades = incapacidades.filter(estado=estado)
    if employee_id:
        incapacidades = incapacidades.filter(employee_id=employee_id)
    
    incapacidades = incapacidades.select_related('employee', 'created_by').order_by('-fecha_inicio')
    
    # Empleados para filtro
    employees = Employee.objects.filter(organization=organization, activo=True).order_by('primer_apellido')
    
    context = {
        'incapacidades': incapacidades,
        'employees': employees,
        'estado_actual': estado,
        'employee_actual': employee_id,
    }
    
    return render(request, 'payroll/incapacity/list.html', context)


@login_required
def incapacity_create(request):
    """Crear nueva incapacidad"""
    from .forms import IncapacityForm
    
    if request.method == 'POST':
        form = IncapacityForm(request.POST, request.FILES, organization=request.organization)
        if form.is_valid():
            incapacity = form.save(commit=False)
            incapacity.organization = request.organization
            incapacity.created_by = request.user
            incapacity.save()
            messages.success(request, f'Incapacidad registrada para {incapacity.employee.get_full_name()}.')
            return redirect('payroll:incapacity_list')
    else:
        form = IncapacityForm(organization=request.organization)
    
    context = {
        'form': form,
        'title': 'Registrar Nueva Incapacidad'
    }
    return render(request, 'payroll/incapacity/form.html', context)


@login_required
def incapacity_edit(request, pk):
    """Editar incapacidad"""
    from .forms import IncapacityForm
    
    incapacity = get_object_or_404(Incapacity, pk=pk, organization=request.organization)
    
    # Solo se pueden editar incapacidades pendientes o aprobadas
    if incapacity.estado == 'PROCESADA':
        messages.error(request, 'No se puede editar una incapacidad que ya fue procesada en nómina.')
        return redirect('payroll:incapacity_list')
    
    if request.method == 'POST':
        form = IncapacityForm(request.POST, request.FILES, instance=incapacity, organization=request.organization)
        if form.is_valid():
            form.save()
            messages.success(request, 'Incapacidad actualizada exitosamente.')
            return redirect('payroll:incapacity_list')
    else:
        form = IncapacityForm(instance=incapacity, organization=request.organization)
    
    context = {
        'form': form,
        'title': f'Editar Incapacidad - {incapacity.employee.get_full_name()}',
        'incapacity': incapacity
    }
    return render(request, 'payroll/incapacity/form.html', context)


@login_required
def incapacity_delete(request, pk):
    """Eliminar incapacidad"""
    incapacity = get_object_or_404(Incapacity, pk=pk, organization=request.organization)
    
    if incapacity.estado == 'PROCESADA':
        messages.error(request, 'No se puede eliminar una incapacidad que ya fue procesada en nómina.')
        return redirect('payroll:incapacity_list')
    
    if request.method == 'POST':
        employee_name = incapacity.employee.get_full_name()
        incapacity.delete()
        messages.success(request, f'Incapacidad de {employee_name} eliminada exitosamente.')
        return redirect('payroll:incapacity_list')
    
    context = {
        'incapacity': incapacity
    }
    return render(request, 'payroll/incapacity/confirm_delete.html', context)


@login_required
def incapacity_approve(request, pk):
    """Aprobar incapacidad"""
    incapacity = get_object_or_404(Incapacity, pk=pk, organization=request.organization)
    
    if request.method == 'POST':
        incapacity.estado = 'APROBADA'
        incapacity.aprobada_por = request.user
        incapacity.fecha_aprobacion = timezone.now()
        incapacity.save()
        
        messages.success(request, f'Incapacidad de {incapacity.employee.get_full_name()} aprobada.')
        return redirect('payroll:incapacity_list')
    
    return redirect('payroll:incapacity_list')


@login_required
def incapacity_reject(request, pk):
    """Rechazar incapacidad"""
    incapacity = get_object_or_404(Incapacity, pk=pk, organization=request.organization)
    
    if request.method == 'POST':
        incapacity.estado = 'RECHAZADA'
        incapacity.observaciones = request.POST.get('motivo_rechazo', incapacity.observaciones)
        incapacity.save()
        
        messages.warning(request, f'Incapacidad de {incapacity.employee.get_full_name()} rechazada.')
        return redirect('payroll:incapacity_list')
    
    return redirect('payroll:incapacity_list')


# ============================================
# EMPLEADOS LIQUIDADOS / NO ACTIVOS
# ============================================

@login_required
def terminated_employees(request, period_id):
    """Vista de todos los empleados del periodo: activos y liquidados"""
    period = get_object_or_404(PayrollPeriod, pk=period_id, organization=request.organization)
    
    # Empleados ACTIVOS (trabajaron todo el periodo)
    active = Employee.objects.filter(
        organization=request.organization,
        activo=True,
        fecha_ingreso__lte=period.fecha_fin
    ).order_by('primer_nombre', 'primer_apellido')
    
    # Empleados LIQUIDADOS (se retiraron durante el periodo)
    terminated = Employee.objects.filter(
        organization=request.organization,
        activo=False,
        fecha_retiro__isnull=False,
        fecha_retiro__gte=period.fecha_inicio,
        fecha_retiro__lte=period.fecha_fin
    ).order_by('fecha_retiro')
    
    # Calcular días trabajados y pagos
    active_data = []
    total_pago_activos = 0
    dias_periodo = (period.fecha_fin - period.fecha_inicio).days + 1
    
    for employee in active:
        # Empleados activos trabajan todos los días del periodo
        salario = employee.salario_basico
        total_pago_activos += salario
        
        active_data.append({
            'employee': employee,
            'dias_trabajados': dias_periodo,
            'salario_total': salario,
            'es_completo': True,
        })
    
    # Calcular pago proporcional para empleados liquidados
    terminated_data = []
    total_pago_liquidados = 0
    for employee in terminated:
        # Días trabajados en el periodo
        if employee.fecha_retiro:
            dias_trabajados = (employee.fecha_retiro - period.fecha_inicio).days + 1
        else:
            dias_trabajados = dias_periodo
        
        # Pago proporcional
        dias_mes = 30
        salario_proporcional = (employee.salario_basico / dias_mes) * dias_trabajados
        total_pago_liquidados += salario_proporcional
        
        terminated_data.append({
            'employee': employee,
            'dias_trabajados': dias_trabajados,
            'salario_total': salario_proporcional,
            'es_completo': False,
        })
    
    context = {
        'period': period,
        'active_employees': active_data,
        'terminated_employees': terminated_data,
        'total_pago_activos': total_pago_activos,
        'total_pago_liquidados': total_pago_liquidados,
        'total_pago_general': total_pago_activos + total_pago_liquidados,
        'dias_periodo': dias_periodo,
    }
    
    return render(request, 'payroll/terminated_employees.html', context)
