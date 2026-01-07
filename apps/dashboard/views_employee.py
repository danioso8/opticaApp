from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from apps.dashboard.models_employee import Employee
from apps.organizations.models import OrganizationMember
from datetime import datetime

# Importar modelo de nómina para sincronización
try:
    from apps.payroll.models import Employee as PayrollEmployee
    PAYROLL_INSTALLED = True
except ImportError:
    PAYROLL_INSTALLED = False


@login_required
def employee_list(request):
    """Vista para listar empleados"""
    organization = request.organization
    
    if not organization:
        messages.error(request, 'No tienes una organización asignada.')
        return redirect('dashboard:home')
    
    # Obtener empleados de la organización
    employees = Employee.objects.filter(organization=organization)
    
    # Filtros
    search = request.GET.get('search', '')
    position = request.GET.get('position', '')
    status = request.GET.get('status', '')
    
    if search:
        employees = employees.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(identification__icontains=search) |
            Q(email__icontains=search)
        )
    
    if position:
        employees = employees.filter(position=position)
    
    if status == 'active':
        employees = employees.filter(is_active=True)
    elif status == 'inactive':
        employees = employees.filter(is_active=False)
    
    # Agregar información de sincronización con nómina
    employees_with_sync = []
    for emp in employees:
        emp_data = emp
        emp_data.in_payroll = False
        if PAYROLL_INSTALLED:
            try:
                payroll_emp = PayrollEmployee.objects.filter(
                    organization=organization,
                    numero_documento=emp.identification
                ).first()
                emp_data.in_payroll = payroll_emp is not None
            except:
                pass
        employees_with_sync.append(emp_data)
    
    context = {
        'employees': employees_with_sync,
        'position_choices': Employee.POSITION_CHOICES,
        'search': search,
        'selected_position': position,
        'selected_status': status,
        'payroll_installed': PAYROLL_INSTALLED,
    }
    
    return render(request, 'dashboard/employees/employee_list.html', context)


@login_required
def employee_create(request):
    """Vista para crear empleado vía AJAX"""
    if request.method == 'POST':
        try:
            organization = request.organization
            
            if not organization:
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes una organización asignada.'
                })
            
            # Validar que no exista otro empleado con el mismo número de identificación
            identification = request.POST.get('identification')
            if Employee.objects.filter(organization=organization, identification=identification).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Ya existe un empleado con este número de identificación.'
                })
            
            # Crear empleado
            employee = Employee.objects.create(
                organization=organization,
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                document_type=request.POST.get('document_type', 'CC'),
                identification=identification,
                birth_date=request.POST.get('birth_date') or None,
                gender=request.POST.get('gender') or None,
                email=request.POST.get('email', ''),
                phone=request.POST.get('phone', ''),
                address=request.POST.get('address', ''),
                position=request.POST.get('position'),
                department=request.POST.get('department', ''),
                hire_date=request.POST.get('hire_date'),
                salary=request.POST.get('salary') or None,
                is_active=request.POST.get('is_active') == 'true',
                incluir_en_nomina=request.POST.get('incluir_en_nomina') == 'true',
                ciudad=request.POST.get('ciudad', 'Bogotá'),
                departamento_ubicacion=request.POST.get('departamento_ubicacion', 'Cundinamarca'),
            )
            
            # Sincronizar con nómina solo si está marcado para incluir en nómina
            if PAYROLL_INSTALLED and employee.incluir_en_nomina:
                try:
                    # Crear o actualizar empleado en nómina
                    PayrollEmployee.objects.update_or_create(
                        organization=organization,
                        numero_documento=identification,
                        defaults={
                            'tipo_documento': request.POST.get('document_type', 'CC'),
                            'primer_nombre': request.POST.get('first_name').split()[0] if request.POST.get('first_name') else '',
                            'segundo_nombre': ' '.join(request.POST.get('first_name').split()[1:]) if len(request.POST.get('first_name', '').split()) > 1 else '',
                            'primer_apellido': request.POST.get('last_name').split()[0] if request.POST.get('last_name') else '',
                            'segundo_apellido': ' '.join(request.POST.get('last_name').split()[1:]) if len(request.POST.get('last_name', '').split()) > 1 else '',
                            'email': request.POST.get('email', ''),
                            'telefono': request.POST.get('phone', ''),
                            'direccion': request.POST.get('address', ''),
                            'ciudad': 'Bogotá',  # Valor por defecto
                            'departamento': 'Cundinamarca',  # Valor por defecto
                            'cargo': request.POST.get('position', 'OTRO'),
                            'fecha_ingreso': request.POST.get('hire_date'),
                            'salario_basico': request.POST.get('salary') or 1300000,
                            'activo': request.POST.get('is_active') == 'true',
                        }
                    )
                except Exception as sync_error:
                    # Log error pero no fallar la creación del empleado
                    print(f"Error sincronizando con nómina: {sync_error}")
            
            return JsonResponse({
                'success': True,
                'message': 'Empleado creado exitosamente.',
                'employee_id': employee.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al crear empleado: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


@login_required
def employee_update(request, pk):
    """Vista para actualizar empleado vía AJAX"""
    if request.method == 'POST':
        try:
            organization = request.organization
            
            if not organization:
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes una organización asignada.'
                })
            
            employee = get_object_or_404(Employee, pk=pk, organization=organization)
            
            # Validar que no exista otro empleado con el mismo número de identificación
            identification = request.POST.get('identification')
            if Employee.objects.filter(
                organization=organization, 
                identification=identification
            ).exclude(pk=pk).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Ya existe otro empleado con este número de identificación.'
                })
            
            # Actualizar empleado
            employee.first_name = request.POST.get('first_name')
            employee.last_name = request.POST.get('last_name')
            employee.document_type = request.POST.get('document_type', 'CC')
            employee.identification = identification
            employee.birth_date = request.POST.get('birth_date') or None
            employee.gender = request.POST.get('gender') or None
            employee.email = request.POST.get('email', '')
            employee.phone = request.POST.get('phone', '')
            employee.address = request.POST.get('address', '')
            employee.position = request.POST.get('position')
            employee.department = request.POST.get('department', '')
            employee.hire_date = request.POST.get('hire_date')
            employee.salary = request.POST.get('salary') or None
            employee.is_active = request.POST.get('is_active') == 'true'
            employee.incluir_en_nomina = request.POST.get('incluir_en_nomina') == 'true'
            employee.ciudad = request.POST.get('ciudad', 'Bogotá')
            employee.departamento_ubicacion = request.POST.get('departamento_ubicacion', 'Cundinamarca')
            employee.save()
            
            # Sincronizar con nómina solo si está marcado
            if PAYROLL_INSTALLED and employee.incluir_en_nomina:
                try:
                    # Actualizar empleado en nómina
                    PayrollEmployee.objects.update_or_create(
                        organization=organization,
                        numero_documento=identification,
                        defaults={
                            'tipo_documento': request.POST.get('document_type', 'CC'),
                            'primer_nombre': request.POST.get('first_name').split()[0] if request.POST.get('first_name') else '',
                            'segundo_nombre': ' '.join(request.POST.get('first_name').split()[1:]) if len(request.POST.get('first_name', '').split()) > 1 else '',
                            'primer_apellido': request.POST.get('last_name').split()[0] if request.POST.get('last_name') else '',
                            'segundo_apellido': ' '.join(request.POST.get('last_name').split()[1:]) if len(request.POST.get('last_name', '').split()) > 1 else '',
                            'email': request.POST.get('email', ''),
                            'telefono': request.POST.get('phone', ''),
                            'direccion': request.POST.get('address', ''),
                            'ciudad': 'Bogotá',
                            'departamento': 'Cundinamarca',
                            'cargo': request.POST.get('position', 'OTRO'),
                            'fecha_ingreso': request.POST.get('hire_date'),
                            'salario_basico': request.POST.get('salary') or 1300000,
                            'activo': request.POST.get('is_active') == 'true',
                        }
                    )
                except Exception as sync_error:
                    print(f"Error sincronizando con nómina: {sync_error}")
            
            return JsonResponse({
                'success': True,
                'message': 'Empleado actualizado exitosamente.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar empleado: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


@login_required
def employee_delete(request, pk):
    """Vista para eliminar empleado"""
    if request.method == 'POST':
        try:
            organization = request.organization
            
            if not organization:
                return JsonResponse({
                    'success': False,
                    'message': 'No tienes una organización asignada.'
                })
            
            employee = get_object_or_404(Employee, pk=pk, organization=organization)
            
            employee_name = employee.full_name
            employee.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Empleado {employee_name} eliminado exitosamente.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar empleado: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


@login_required
def get_employee_data(request, pk):
    """Vista para obtener datos de un empleado en formato JSON"""
    try:
        organization = request.organization
        
        if not organization:
            return JsonResponse({
                'success': False,
                'message': 'No tienes una organización asignada.'
            })
        
        employee = get_object_or_404(Employee, pk=pk, organization=organization)
        
        data = {
            'id': employee.id,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'full_name': employee.full_name,
            'document_type': employee.document_type,
            'identification': employee.identification,
            'birth_date': employee.birth_date.strftime('%Y-%m-%d') if employee.birth_date else '',
            'gender': employee.gender or '',
            'email': employee.email,
            'phone': employee.phone,
            'address': employee.address,
            'position': employee.position,
            'position_display': employee.get_position_display(),
            'department': employee.department,
            'hire_date': employee.hire_date.strftime('%Y-%m-%d'),
            'salary': str(employee.salary) if employee.salary else '',
            'is_active': employee.is_active,
            'incluir_en_nomina': employee.incluir_en_nomina,
            'ciudad': employee.ciudad or 'Bogotá',
            'departamento_ubicacion': employee.departamento_ubicacion or 'Cundinamarca',
        }
        
        return JsonResponse({'success': True, 'data': data})
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener datos: {str(e)}'
        })
