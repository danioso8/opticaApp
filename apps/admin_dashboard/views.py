from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from apps.users.models import UserSubscription
from apps.users.email_verification_models import UserProfile
from apps.organizations.models import Organization, OrganizationMember, SubscriptionPlan
from django.db import transaction


def is_superuser(user):
    """Verificar si el usuario es superusuario"""
    return user.is_superuser


def saas_admin_login(request):
    """Vista de login para el panel SaaS Admin"""
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_superuser:
                login(request, user)
                messages.success(request, f'Bienvenido al panel de administración, {user.get_full_name() or user.username}!')
                return redirect('admin_dashboard:home')
            else:
                messages.error(request, 'No tienes permisos para acceder al panel de administración.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'admin_dashboard/login.html')


@login_required
def saas_admin_logout(request):
    """Vista de logout para el panel SaaS Admin"""
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('admin_dashboard:login')


@login_required
@user_passes_test(is_superuser)
def admin_dashboard_home(request):
    """Dashboard principal de administración"""
    # Estadísticas generales
    total_users = User.objects.count()
    total_organizations = Organization.objects.count()
    total_subscriptions = UserSubscription.objects.count()
    active_subscriptions = UserSubscription.objects.filter(is_active=True, payment_status='paid').count()
    
    # Usuarios recientes (últimos 7 días)
    week_ago = timezone.now() - timedelta(days=7)
    recent_users = User.objects.filter(date_joined__gte=week_ago).count()
    
    # Suscripciones por plan
    subscriptions_by_plan = UserSubscription.objects.filter(
        is_active=True
    ).values('plan__name').annotate(count=Count('id'))
    
    # Últimos usuarios registrados
    latest_users = User.objects.order_by('-date_joined')[:10]
    
    # Suscripciones próximas a expirar (próximos 7 días)
    expiring_soon = UserSubscription.objects.filter(
        is_active=True,
        end_date__lte=timezone.now() + timedelta(days=7),
        end_date__gte=timezone.now()
    ).select_related('user', 'plan')
    
    context = {
        'total_users': total_users,
        'total_organizations': total_organizations,
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'recent_users': recent_users,
        'subscriptions_by_plan': subscriptions_by_plan,
        'latest_users': latest_users,
        'expiring_soon': expiring_soon,
    }
    return render(request, 'admin_dashboard/home.html', context)


@login_required
@user_passes_test(is_superuser)
def users_list(request):
    """Lista de todos los usuarios"""
    search = request.GET.get('search', '')
    
    users = User.objects.all().select_related('subscription').prefetch_related('owned_organizations')
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    users = users.order_by('-date_joined')
    
    context = {
        'users': users,
        'search': search,
    }
    return render(request, 'admin_dashboard/users_list.html', context)


@login_required
@user_passes_test(is_superuser)
def user_detail(request, user_id):
    """Detalle de un usuario específico"""
    user = get_object_or_404(User, id=user_id)
    
    # Obtener suscripción
    try:
        subscription = UserSubscription.objects.get(user=user)
    except UserSubscription.DoesNotExist:
        subscription = None
    
    # Organizaciones del usuario
    organizations = Organization.objects.filter(owner=user)
    
    # Membresías
    memberships = OrganizationMember.objects.filter(user=user).select_related('organization')
    
    context = {
        'user_obj': user,
        'subscription': subscription,
        'organizations': organizations,
        'memberships': memberships,
    }
    return render(request, 'admin_dashboard/user_detail.html', context)


@login_required
@user_passes_test(is_superuser)
def user_toggle_active(request, user_id):
    """Activar/Desactivar usuario"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()
        
        status = 'activado' if user.is_active else 'desactivado'
        messages.success(request, f'Usuario {user.username} {status} exitosamente')
    
    return redirect('admin_dashboard:user_detail', user_id=user_id)


@login_required
@user_passes_test(is_superuser)
def user_delete(request, user_id):
    """Eliminar usuario"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        username = user.username
        user.delete()
        messages.success(request, f'Usuario {username} eliminado exitosamente')
        return redirect('admin_dashboard:users_list')
    
    return redirect('admin_dashboard:user_detail', user_id=user_id)


@login_required
@user_passes_test(is_superuser)
def subscriptions_list(request):
    """Lista de todas las suscripciones"""
    status_filter = request.GET.get('status', '')
    plan_filter = request.GET.get('plan', '')
    
    subscriptions = UserSubscription.objects.all().select_related('user', 'plan')
    
    if status_filter:
        subscriptions = subscriptions.filter(payment_status=status_filter)
    
    if plan_filter:
        subscriptions = subscriptions.filter(plan_id=plan_filter)
    
    subscriptions = subscriptions.order_by('-created_at')
    
    plans = SubscriptionPlan.objects.all()
    
    context = {
        'subscriptions': subscriptions,
        'plans': plans,
        'status_filter': status_filter,
        'plan_filter': plan_filter,
    }
    return render(request, 'admin_dashboard/subscriptions_list.html', context)


@login_required
@user_passes_test(is_superuser)
def subscription_edit(request, subscription_id):
    """Editar suscripción"""
    subscription = get_object_or_404(UserSubscription, id=subscription_id)
    plans = SubscriptionPlan.objects.all()
    
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        billing_cycle = request.POST.get('billing_cycle')
        payment_status = request.POST.get('payment_status')
        is_active = request.POST.get('is_active') == 'on'
        end_date = request.POST.get('end_date')
        
        with transaction.atomic():
            if plan_id:
                subscription.plan_id = plan_id
            if billing_cycle:
                subscription.billing_cycle = billing_cycle
            if payment_status:
                subscription.payment_status = payment_status
            subscription.is_active = is_active
            if end_date:
                subscription.end_date = end_date
            
            subscription.save()
            messages.success(request, 'Suscripción actualizada exitosamente')
        
        return redirect('admin_dashboard:user_detail', user_id=subscription.user.id)
    
    context = {
        'subscription': subscription,
        'plans': plans,
    }
    return render(request, 'admin_dashboard/subscription_edit.html', context)


@login_required
@user_passes_test(is_superuser)
def subscription_unlimited(request, user_id):
    """Dar acceso ilimitado a un usuario"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        # Obtener o crear plan Enterprise (o el más alto)
        enterprise_plan = SubscriptionPlan.objects.filter(
            plan_type='enterprise'
        ).first()
        
        if not enterprise_plan:
            messages.error(request, 'No existe un plan empresarial configurado')
            return redirect('admin_dashboard:user_detail', user_id=user_id)
        
        try:
            subscription = UserSubscription.objects.get(user=user)
            subscription.plan = enterprise_plan
            subscription.is_active = True
            subscription.payment_status = 'paid'
            # Extender por 100 años (prácticamente ilimitado)
            subscription.end_date = timezone.now() + timedelta(days=36500)
            subscription.save()
            messages.success(request, f'Acceso ilimitado otorgado a {user.username}')
        except UserSubscription.DoesNotExist:
            UserSubscription.objects.create(
                user=user,
                plan=enterprise_plan,
                is_active=True,
                payment_status='paid',
                end_date=timezone.now() + timedelta(days=36500)
            )
            messages.success(request, f'Suscripción ilimitada creada para {user.username}')
        
        return redirect('admin_dashboard:user_detail', user_id=user_id)
    
    return redirect('admin_dashboard:user_detail', user_id=user_id)


@login_required
@user_passes_test(is_superuser)
def subscription_revoke_unlimited(request, user_id):
    """Revocar acceso ilimitado y establecer plan normal"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        try:
            subscription = UserSubscription.objects.get(user=user)
            
            # Obtener plan básico
            basic_plan = SubscriptionPlan.objects.filter(plan_type='basic').first()
            
            if not basic_plan:
                messages.error(request, 'No existe un plan básico configurado')
                return redirect('admin_dashboard:user_detail', user_id=user_id)
            
            # Cambiar a plan mensual normal (30 días)
            subscription.plan = basic_plan
            subscription.end_date = timezone.now() + timedelta(days=30)
            subscription.billing_cycle = 'monthly'
            subscription.save()
            
            messages.success(request, f'Acceso ilimitado revocado. {user.username} ahora tiene plan mensual.')
        except UserSubscription.DoesNotExist:
            messages.error(request, 'El usuario no tiene suscripción')
        
        return redirect('admin_dashboard:user_detail', user_id=user_id)
    
    return redirect('admin_dashboard:user_detail', user_id=user_id)


@login_required
@user_passes_test(is_superuser)
def organizations_list(request):
    """Lista de todas las organizaciones"""
    search = request.GET.get('search', '')
    
    organizations = Organization.objects.all().select_related('owner')
    
    if search:
        organizations = organizations.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(owner__username__icontains=search)
        )
    
    organizations = organizations.order_by('-created_at')
    
    context = {
        'organizations': organizations,
        'search': search,
    }
    return render(request, 'admin_dashboard/organizations_list.html', context)


@login_required
@user_passes_test(is_superuser)
def organization_detail(request, org_id):
    """Detalle de una organización"""
    organization = get_object_or_404(Organization, id=org_id)
    members = OrganizationMember.objects.filter(organization=organization).select_related('user')
    
    context = {
        'organization': organization,
        'members': members,
    }
    return render(request, 'admin_dashboard/organization_detail.html', context)


@login_required
@user_passes_test(is_superuser)
def organization_toggle_active(request, org_id):
    """Activar/Desactivar organización"""
    if request.method == 'POST':
        organization = get_object_or_404(Organization, id=org_id)
        organization.is_active = not organization.is_active
        organization.save()
        
        status = 'activada' if organization.is_active else 'desactivada'
        messages.success(request, f'Organización {organization.name} {status} exitosamente')
    
    return redirect('admin_dashboard:organization_detail', org_id=org_id)


@login_required
@user_passes_test(is_superuser)
def organization_delete(request, org_id):
    """Eliminar organización"""
    if request.method == 'POST':
        organization = get_object_or_404(Organization, id=org_id)
        org_name = organization.name
        organization.delete()
        
        messages.success(request, f'Organización {org_name} eliminada exitosamente')
        return redirect('admin_dashboard:organizations_list')
    
    return redirect('admin_dashboard:organization_detail', org_id=org_id)


@login_required
@user_passes_test(is_superuser)
def plans_list(request):
    """Lista de planes de suscripción"""
    plans = SubscriptionPlan.objects.all().order_by('price_monthly')
    
    context = {
        'plans': plans,
    }
    return render(request, 'admin_dashboard/plans_list.html', context)


@login_required
@user_passes_test(is_superuser)
def plan_create(request):
    """Crear nuevo plan"""
    if request.method == 'POST':
        from django.utils.text import slugify
        
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        monthly_price = request.POST.get('monthly_price')
        yearly_price = request.POST.get('yearly_price')
        max_organizations = request.POST.get('max_organizations')
        max_users = request.POST.get('max_users')
        max_appointments = request.POST.get('max_appointments')
        is_active = request.POST.get('is_active') == 'on'
        
        SubscriptionPlan.objects.create(
            name=name,
            slug=slugify(name),
            plan_type='basic',  # Por defecto
            price_monthly=monthly_price,
            price_yearly=yearly_price,
            max_users=max_users,
            max_appointments_month=max_appointments,
            max_patients=max_organizations,  # Usamos max_patients para organizaciones
            is_active=is_active,
        )
        
        messages.success(request, f'Plan {name} creado exitosamente')
        return redirect('admin_dashboard:plans_list')
    
    return render(request, 'admin_dashboard/plan_create.html')


@login_required
@user_passes_test(is_superuser)
def plan_edit(request, plan_id):
    """Editar plan existente"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    if request.method == 'POST':
        plan.name = request.POST.get('name')
        plan.description = request.POST.get('description', '')
        plan.price_monthly = request.POST.get('monthly_price')
        plan.price_yearly = request.POST.get('yearly_price')
        plan.max_users = request.POST.get('max_users')
        plan.max_appointments_month = request.POST.get('max_appointments')
        plan.max_patients = request.POST.get('max_organizations')
        plan.is_active = request.POST.get('is_active') == 'on'
        
        plan.save()
        messages.success(request, f'Plan {plan.name} actualizado exitosamente')
        return redirect('admin_dashboard:plans_list')
    
    context = {
        'plan': plan,
    }
    return render(request, 'admin_dashboard/plan_edit.html', context)


@login_required
@user_passes_test(is_superuser)
def plan_toggle_active(request, plan_id):
    """Activar/Desactivar plan"""
    if request.method == 'POST':
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        plan.is_active = not plan.is_active
        plan.save()
        
        status = 'activado' if plan.is_active else 'desactivado'
        messages.success(request, f'Plan {plan.name} {status} exitosamente')
    
    return redirect('admin_dashboard:plans_list')


@login_required
@user_passes_test(is_superuser)
def verify_user_email(request, user_id):
    """Verificar manualmente el email de un usuario"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        # Obtener o crear perfil de usuario
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.email_verified = True
        profile.save()
        
        # Activar el usuario
        user.is_active = True
        user.save()
        
        messages.success(request, f'Email de {user.username} verificado exitosamente')
    
    return redirect('admin_dashboard:user_detail', user_id=user_id)


@login_required
@user_passes_test(is_superuser)
def unverify_user_email(request, user_id):
    """Marcar como no verificado el email de un usuario"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        # Obtener o crear perfil de usuario
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.email_verified = False
        profile.save()
        
        messages.warning(request, f'Email de {user.username} marcado como no verificado')
    
    return redirect('admin_dashboard:user_detail', user_id=user_id)
