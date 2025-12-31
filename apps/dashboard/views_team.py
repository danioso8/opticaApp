"""
Vistas para gestión de equipo (usuarios y permisos)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from apps.organizations.models import (
    OrganizationMember, 
    ModulePermission, 
    MemberModulePermission,
    Organization
)


def apply_role_based_permissions(member, granted_by=None):
    """Aplica permisos automáticos según el rol del miembro"""
    # Definir permisos por rol
    role_permissions = {
        'admin': {
            # Administrador tiene acceso total a casi todo
            'all': {'view': True, 'create': True, 'edit': True, 'delete': True}
        },
        'doctor': {
            # Doctor tiene acceso a módulos clínicos y pacientes
            'patients': {'view': True, 'create': True, 'edit': True, 'delete': False},
            'appointments': {'view': True, 'create': True, 'edit': True, 'delete': False},
            'clinical': {'view': True, 'create': True, 'edit': True, 'delete': False},
            'exams': {'view': True, 'create': True, 'edit': True, 'delete': False},
            'prescriptions': {'view': True, 'create': True, 'edit': True, 'delete': False},
        },
        'cashier': {
            # Cajero tiene acceso a ventas y facturación
            'sales': {'view': True, 'create': True, 'edit': True, 'delete': False},
            'billing': {'view': True, 'create': True, 'edit': True, 'delete': False},
            'products': {'view': True, 'create': False, 'edit': False, 'delete': False},
            'customers': {'view': True, 'create': True, 'edit': True, 'delete': False},
        },
        'vendedor': {
            # Vendedor similar a cajero pero más enfocado en ventas
            'sales': {'view': True, 'create': True, 'edit': True, 'delete': False},
            'products': {'view': True, 'create': False, 'edit': False, 'delete': False},
            'customers': {'view': True, 'create': True, 'edit': True, 'delete': False},
            'billing': {'view': True, 'create': False, 'edit': False, 'delete': False},
        },
        'staff': {
            # Personal básico
            'patients': {'view': True, 'create': False, 'edit': False, 'delete': False},
            'appointments': {'view': True, 'create': True, 'edit': False, 'delete': False},
        },
        'viewer': {
            # Solo lectura
            'all': {'view': True, 'create': False, 'edit': False, 'delete': False}
        }
    }
    
    if member.role not in role_permissions:
        return
    
    role_config = role_permissions[member.role]
    
    # Eliminar permisos actuales
    MemberModulePermission.objects.filter(member=member).delete()
    
    # Obtener todos los módulos activos
    all_modules = ModulePermission.objects.filter(is_active=True)
    
    for module in all_modules:
        # Verificar si hay configuración específica para este módulo
        perms = None
        
        if 'all' in role_config:
            # Aplicar permisos para todos los módulos
            perms = role_config['all']
        else:
            # Buscar coincidencia en el código del módulo
            for key in role_config:
                if key.lower() in module.code.lower():
                    perms = role_config[key]
                    break
        
        if perms:
            MemberModulePermission.objects.create(
                member=member,
                module=module,
                can_view=perms.get('view', False),
                can_create=perms.get('create', False),
                can_edit=perms.get('edit', False),
                can_delete=perms.get('delete', False),
                granted_by=granted_by
            )


def get_user_organization(request):
    """Obtiene la organización del usuario actual desde el middleware"""
    organization = request.organization
    
    if not organization:
        return None, None
    
    # Obtener el membership para verificar permisos
    membership = OrganizationMember.objects.filter(
        user=request.user,
        organization=organization,
        is_active=True
    ).select_related('organization').first()
    
    if not membership:
        return None, None
    
    return organization, membership


@login_required
def team_list(request):
    """Lista de miembros del equipo"""
    organization, membership = get_user_organization(request)
    
    if not organization:
        messages.error(request, 'No tienes una organización asignada.')
        return redirect('dashboard:home')
    
    # Solo owner y admin pueden ver el equipo
    if membership.role not in ['owner', 'admin']:
        messages.error(request, 'No tienes permisos para gestionar el equipo.')
        return redirect('dashboard:home')
    
    members = OrganizationMember.objects.filter(
        organization=organization
    ).select_related('user').order_by('-role', 'joined_at')
    
    context = {
        'members': members,
        'organization': organization,
        'is_owner': membership.role == 'owner',
        'can_manage': membership.role in ['owner', 'admin'],
    }
    
    return render(request, 'dashboard/team/team_list.html', context)


@login_required
def team_member_add(request):
    """Agregar nuevo miembro al equipo"""
    organization, membership = get_user_organization(request)
    
    if not organization:
        messages.error(request, 'No tienes una organización asignada.')
        return redirect('dashboard:home')
    
    # Solo owner y admin pueden agregar miembros
    if membership.role not in ['owner', 'admin']:
        messages.error(request, 'No tienes permisos para agregar miembros.')
        return redirect('dashboard:team_list')
    
    if request.method == 'POST':
        # Verificar si se seleccionó un doctor
        doctor_id = request.POST.get('doctor_id', '').strip()
        
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', 'staff')
        send_email_invitation = request.POST.get('send_email') == 'on'
        activate_immediately = request.POST.get('activate_immediately') == 'on'
        
        if not email:
            messages.error(request, 'El email es obligatorio.')
            return redirect('dashboard:team_member_add')
        
        # Verificar si el usuario ya existe
        user = User.objects.filter(email__iexact=email).first()
        
        if user:
            # Verificar si ya es miembro
            existing_member = OrganizationMember.objects.filter(
                organization=organization,
                user=user
            ).first()
            
            if existing_member:
                messages.warning(request, f'{user.email} ya es miembro de tu organización.')
                return redirect('dashboard:team_list')
        else:
            # Crear nuevo usuario
            # Si no se proporcionó username, generar uno del email
            if not username:
                username = email.split('@')[0]
            
            # Asegurar username único
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Si no se proporcionó password, generar una aleatoria
            if not password:
                password = User.objects.make_random_password(length=12)
                send_email_invitation = True  # Forzar envío de email si no hay password
            
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            
            # Activar usuario si se marcó la opción
            if activate_immediately:
                user.is_active = True
                user.save()
                
                # Marcar email como verificado para evitar el middleware de verificación
                from apps.users.email_verification_models import UserProfile
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.is_email_verified = True
                profile.save()
            
            # Guardar la contraseña temporalmente para mostrarla al usuario si no se envía email
            temp_password = password if not send_email_invitation else None
        
        # Crear membresía
        new_member = OrganizationMember.objects.create(
            organization=organization,
            user=user,
            role=role,
            is_active=activate_immediately,
            invited_by=request.user
        )
        
        # Aplicar permisos automáticos según el rol
        if role not in ['owner', 'admin']:
            apply_role_based_permissions(new_member, granted_by=request.user)
        
        # Si se seleccionó un doctor, vincular
        if doctor_id:
            try:
                from apps.patients.models import Doctor
                doctor = Doctor.objects.get(id=doctor_id, organization=organization)
                # Aquí podrías agregar un campo en OrganizationMember para vincular con Doctor
                # Por ahora solo lo mencionamos en los mensajes
                messages.info(request, f'Vinculado con el doctor: {doctor.full_name}')
            except Doctor.DoesNotExist:
                pass
        
        # Enviar email de invitación solo si se solicitó
        if send_email_invitation:
            try:
                subject = f'Invitación a {organization.name}'
                context = {
                    'organization': organization,
                    'invited_by': request.user,
                    'user': user,
                    'role': new_member.get_role_display(),
                    'temp_password': password if password else None,
                }
                html_message = render_to_string('dashboard/team/email_invitation.html', context)
                send_mail(
                    subject,
                    f'Has sido invitado a {organization.name}. Por favor inicia sesión en el sistema.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_message,
                    fail_silently=True,
                )
                messages.success(request, f'{user.email} agregado. Se envió email de invitación.')
            except Exception as e:
                messages.warning(request, f'Usuario agregado pero no se pudo enviar el email: {str(e)}')
        else:
            messages.success(request, f'{user.email} ha sido agregado al equipo.')
            if temp_password:
                messages.info(request, f'📝 Credenciales: Usuario: {username} | Contraseña: {temp_password}')
                messages.warning(request, '⚠️ Guarda estas credenciales. No se envió email de confirmación.')
        
        return redirect('dashboard:team_member_permissions', member_id=new_member.id)
    
    # Obtener lista de doctores para el selector
    from apps.patients.models import Doctor
    from apps.dashboard.models_employee import Employee
    
    doctors = Doctor.objects.filter(organization=organization, is_active=True).order_by('full_name')
    employees = Employee.objects.filter(organization=organization, is_active=True).order_by('first_name', 'last_name')
    
    context = {
        'organization': organization,
        'roles': OrganizationMember.ROLES,
        'doctors': doctors,
        'employees': employees,
    }
    
    return render(request, 'dashboard/team/team_member_add.html', context)


@login_required
def team_member_edit(request, member_id):
    """Editar miembro del equipo"""
    organization, membership = get_user_organization(request)
    
    if not organization:
        messages.error(request, 'No tienes una organización asignada.')
        return redirect('dashboard:home')
    
    member = get_object_or_404(
        OrganizationMember,
        id=member_id,
        organization=organization
    )
    
    # Solo owner puede editar, o admin si no es el owner
    if membership.role == 'owner':
        can_edit = True
    elif membership.role == 'admin' and member.role != 'owner':
        can_edit = True
    else:
        can_edit = False
    
    if not can_edit:
        messages.error(request, 'No tienes permisos para editar este miembro.')
        return redirect('dashboard:team_list')
    
    if request.method == 'POST':
        role = request.POST.get('role')
        is_active = request.POST.get('is_active') == 'on'
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        email_verified = request.POST.get('email_verified') == 'on'
        
        # El owner no puede cambiar su propio rol
        if member.role == 'owner' and membership.user == member.user:
            messages.error(request, 'No puedes cambiar tu propio rol de Propietario.')
            return redirect('dashboard:team_list')
        
        # Actualizar username si se proporciona
        if username and username != member.user.username:
            # Verificar que el username no esté en uso
            if User.objects.filter(username=username).exclude(id=member.user.id).exists():
                messages.error(request, f'El nombre de usuario "{username}" ya está en uso.')
                return redirect('dashboard:team_member_edit', member_id=member_id)
            member.user.username = username
        
        # Actualizar contraseña si se proporciona
        if password:
            member.user.set_password(password)
        
        member.user.save()
        member.role = role
        member.is_active = is_active
        member.save()
        
        # Actualizar verificación de email
        from apps.users.email_verification_models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=member.user)
        profile.is_email_verified = email_verified
        profile.save()
        
        messages.success(request, f'Miembro {member.user.get_full_name() or member.user.username} actualizado.')
        return redirect('dashboard:team_list')
    
    context = {
        'member': member,
        'organization': organization,
        'roles': OrganizationMember.ROLES,
    }
    
    return render(request, 'dashboard/team/team_member_edit.html', context)


@login_required
def team_member_permissions(request, member_id):
    """Gestionar permisos de un miembro"""
    organization, membership = get_user_organization(request)
    
    if not organization:
        messages.error(request, 'No tienes una organización asignada.')
        return redirect('dashboard:home')
    
    member = get_object_or_404(
        OrganizationMember,
        id=member_id,
        organization=organization
    )
    
    # Solo owner y admin pueden gestionar permisos
    if membership.role not in ['owner', 'admin']:
        messages.error(request, 'No tienes permisos para gestionar permisos.')
        return redirect('dashboard:team_list')
    
    # Owner y Admin tienen todos los permisos por defecto
    if member.role in ['owner', 'admin']:
        messages.info(request, 'Los Propietarios y Administradores tienen acceso total a todos los módulos.')
        return redirect('dashboard:team_list')
    
    # Verificar que existan módulos
    all_modules = ModulePermission.objects.filter(is_active=True).order_by('category', 'order')
    
    if not all_modules.exists():
        messages.warning(request, 'No hay módulos configurados. Ejecuta el comando: python manage.py init_modules')
        return redirect('dashboard:team_list')
    
    if request.method == 'POST':
        with transaction.atomic():
            # Eliminar permisos actuales
            MemberModulePermission.objects.filter(member=member).delete()
            
            # Crear nuevos permisos
            for module in all_modules:
                module_key = f"module_{module.id}"
                if module_key in request.POST:
                    can_view = request.POST.get(f"view_{module.id}") == 'on'
                    can_create = request.POST.get(f"create_{module.id}") == 'on'
                    can_edit = request.POST.get(f"edit_{module.id}") == 'on'
                    can_delete = request.POST.get(f"delete_{module.id}") == 'on'
                    
                    MemberModulePermission.objects.create(
                        member=member,
                        module=module,
                        can_view=can_view,
                        can_create=can_create,
                        can_edit=can_edit,
                        can_delete=can_delete,
                        granted_by=request.user
                    )
        
        messages.success(request, f'Permisos de {member.user.get_full_name() or member.user.username} actualizados.')
        return redirect('dashboard:team_list')
    
    # Obtener permisos actuales
    current_permissions = {}
    for perm in MemberModulePermission.objects.filter(member=member).select_related('module'):
        current_permissions[perm.module.id] = {
            'can_view': perm.can_view,
            'can_create': perm.can_create,
            'can_edit': perm.can_edit,
            'can_delete': perm.can_delete,
        }
    
    # Agrupar módulos por categoría
    from collections import defaultdict
    modules_by_category = defaultdict(list)
    for module in all_modules:
        modules_by_category[module.category].append(module)
    
    context = {
        'member': member,
        'organization': organization,
        'all_modules': all_modules,
        'modules_by_category': dict(modules_by_category),
        'current_permissions': current_permissions,
    }
    
    return render(request, 'dashboard/team/team_member_permissions.html', context)


@login_required
def team_member_delete(request, member_id):
    """Eliminar miembro del equipo"""
    organization, membership = get_user_organization(request)
    
    if not organization:
        messages.error(request, 'No tienes una organización asignada.')
        return redirect('dashboard:home')
    
    member = get_object_or_404(
        OrganizationMember,
        id=member_id,
        organization=organization
    )
    
    # Solo owner puede eliminar miembros
    if membership.role != 'owner':
        messages.error(request, 'Solo el propietario puede eliminar miembros.')
        return redirect('dashboard:team_list')
    
    # No puede eliminar al owner
    if member.role == 'owner':
        messages.error(request, 'No puedes eliminar al propietario.')
        return redirect('dashboard:team_list')
    
    if request.method == 'POST':
        user_name = member.user.get_full_name() or member.user.username
        member.delete()
        messages.success(request, f'{user_name} ha sido eliminado del equipo.')
        return redirect('dashboard:team_list')
    
    context = {
        'member': member,
        'organization': organization,
    }
    
    return render(request, 'dashboard/team/team_member_delete.html', context)


@login_required
def team_modules_list(request):
    """Listar todos los módulos del sistema (para configuración)"""
    organization, membership = get_user_organization(request)
    
    if not organization:
        messages.error(request, 'No tienes una organización asignada.')
        return redirect('dashboard:home')
    
    # Solo owner puede ver módulos
    if membership.role != 'owner':
        messages.error(request, 'No tienes permisos para ver esta sección.')
        return redirect('dashboard:home')
    
    modules = ModulePermission.objects.all().order_by('category', 'order')
    
    context = {
        'modules': modules,
        'organization': organization,
    }
    
    return render(request, 'dashboard/team/modules_list.html', context)


@login_required
def get_doctor_data(request, doctor_id):
    """Obtener datos del doctor para autocompletar formulario (AJAX)"""
    organization, membership = get_user_organization(request)
    
    if not organization:
        return JsonResponse({'success': False, 'error': 'No tienes organización'}, status=403)
    
    try:
        from apps.patients.models import Doctor
        doctor = Doctor.objects.get(id=doctor_id, organization=organization)
        
        # Separar nombre completo en nombre y apellido
        name_parts = doctor.full_name.split(' ', 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        data = {
            'success': True,
            'doctor': {
                'id': doctor.id,
                'full_name': doctor.full_name,
                'first_name': first_name,
                'last_name': last_name,
                'email': doctor.email or '',
                'phone': doctor.phone or '',
                'identification': doctor.identification or '',
                'identification_type': doctor.identification_type or 'CC',
            }
        }
        return JsonResponse(data)
    except Doctor.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Doctor no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_employee_data_for_team(request, employee_id):
    """Obtener datos del empleado para autocompletar formulario (AJAX)"""
    organization, membership = get_user_organization(request)
    
    if not organization:
        return JsonResponse({'success': False, 'error': 'No tienes organización'}, status=403)
    
    try:
        from apps.dashboard.models_employee import Employee
        employee = Employee.objects.get(id=employee_id, organization=organization)
        
        data = {
            'success': True,
            'employee': {
                'id': employee.id,
                'full_name': employee.full_name,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'email': employee.email or '',
                'phone': employee.phone or '',
                'identification': employee.identification or '',
                'document_type': employee.document_type or 'CC',
            }
        }
        return JsonResponse(data)
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
