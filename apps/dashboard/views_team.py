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


def get_user_organization(request):
    """Obtiene la organización del usuario actual"""
    membership = OrganizationMember.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('organization').first()
    
    if not membership:
        return None, None
    
    return membership.organization, membership


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
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        role = request.POST.get('role', 'staff')
        
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
            username = email.split('@')[0]
            # Asegurar username único
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=User.objects.make_random_password()
            )
        
        # Crear membresía
        new_member = OrganizationMember.objects.create(
            organization=organization,
            user=user,
            role=role,
            invited_by=request.user
        )
        
        # Enviar email de invitación
        try:
            subject = f'Invitación a {organization.name}'
            context = {
                'organization': organization,
                'invited_by': request.user,
                'user': user,
                'role': new_member.get_role_display(),
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
        except Exception as e:
            print(f"Error enviando email: {e}")
        
        messages.success(request, f'{user.email} ha sido agregado al equipo como {new_member.get_role_display()}.')
        return redirect('dashboard:team_member_permissions', member_id=new_member.id)
    
    context = {
        'organization': organization,
        'roles': OrganizationMember.ROLES,
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
        
        # El owner no puede cambiar su propio rol
        if member.role == 'owner' and membership.user == member.user:
            messages.error(request, 'No puedes cambiar tu propio rol de Propietario.')
            return redirect('dashboard:team_list')
        
        member.role = role
        member.is_active = is_active
        member.save()
        
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
