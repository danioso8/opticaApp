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
from apps.organizations.models import Organization, OrganizationMember, SubscriptionPlan, Subscription
from django.db import transaction
from functools import wraps


def is_superuser(user):
    """Verificar si el usuario es superusuario"""
    return user.is_authenticated and user.is_superuser


def superuser_required(view_func):
    """Decorador personalizado que requiere superusuario y redirige correctamente"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/saas-admin/login/')
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para acceder al panel de administración.')
            return redirect('/dashboard/')
        return view_func(request, *args, **kwargs)
    return wrapper


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


@superuser_required
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
    """Eliminar usuario y sus organizaciones asociadas"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        username = user.username
        
        # Verificar si el usuario es owner de organizaciones
        from apps.organizations.models import Organization
        owned_orgs = Organization.objects.filter(owner=user)
        
        if owned_orgs.exists():
            org_count = owned_orgs.count()
            org_names = ', '.join([org.name for org in owned_orgs[:3]])
            if org_count > 3:
                org_names += f' y {org_count - 3} más'
            
            # Eliminar las organizaciones primero (esto eliminará en cascada todo lo relacionado)
            owned_orgs.delete()
            messages.warning(
                request, 
                f'{org_count} organización(es) eliminada(s): {org_names}'
            )
        
        try:
            user.delete()
            messages.success(request, f'Usuario {username} eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar el usuario: {str(e)}')
            return redirect('admin_dashboard:user_detail', user_id=user_id)
        
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
        # El template envía 'plan' no 'plan_id'
        plan_id = request.POST.get('plan')
        billing_cycle = request.POST.get('billing_cycle')
        payment_status = request.POST.get('payment_status')
        end_date = request.POST.get('end_date')
        
        print(f"\n{'='*70}")
        print(f"🔧 EDITANDO SUSCRIPCIÓN DEL USUARIO: {subscription.user.username}")
        print(f"{'='*70}")
        print(f"Plan anterior: {subscription.plan.name} (ID: {subscription.plan.id})")
        print(f"Plan nuevo ID recibido: {plan_id}")
        print(f"Billing cycle: {billing_cycle}")
        print(f"Payment status: {payment_status}")
        
        with transaction.atomic():
            # Actualizar UserSubscription
            old_plan_name = subscription.plan.name
            
            if plan_id:
                subscription.plan_id = int(plan_id)
            if billing_cycle:
                subscription.billing_cycle = billing_cycle
            if payment_status:
                subscription.payment_status = payment_status
            
            # Activar automáticamente si el pago está confirmado
            subscription.is_active = (payment_status == 'paid')
            
            if end_date:
                subscription.end_date = end_date
            
            subscription.save()
            subscription.refresh_from_db()
            print(f"✅ UserSubscription guardada: {subscription.plan.name}")
            print(f"   is_active: {subscription.is_active} (payment_status: {payment_status})")
            
            # También actualizar la suscripción de la organización
            org_member = OrganizationMember.objects.filter(user=subscription.user).first()
            if org_member and org_member.organization:
                org = org_member.organization
                print(f"📋 Organización encontrada: {org.name}")
                
                # IMPORTANTE: Desactivar TODAS las suscripciones anteriores
                old_subs_count = Subscription.objects.filter(
                    organization=org,
                    is_active=True
                ).count()
                
                Subscription.objects.filter(
                    organization=org
                ).update(is_active=False)
                
                print(f"🔴 Desactivadas {old_subs_count} suscripciones anteriores")
                
                # Crear nueva suscripción con el plan actualizado
                new_plan = subscription.plan
                new_sub = Subscription.objects.create(
                    organization=org,
                    plan=new_plan,
                    billing_cycle=billing_cycle or subscription.billing_cycle,
                    payment_status=payment_status or subscription.payment_status,
                    is_active=True,
                    end_date=end_date or subscription.end_date,
                    start_date=timezone.now(),
                    amount_paid=0 if new_plan.plan_type == 'free' else (
                        new_plan.price_yearly if (billing_cycle or subscription.billing_cycle) == 'yearly' 
                        else new_plan.price_monthly
                    )
                )
                print(f"✅ Nueva Subscription de organización creada: {new_sub.plan.name} (ID: {new_sub.id})")
                print(f"📅 End date: {new_sub.end_date}")
            else:
                print(f"⚠️ Usuario no tiene organización")
            
            print(f"{'='*70}\n")
            
            messages.success(request, f'✅ Suscripción actualizada de {old_plan_name} a {subscription.plan.name}')
        
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
        
        # Intentar obtener plan Enterprise (case insensitive)
        enterprise_plan = SubscriptionPlan.objects.filter(
            plan_type__iexact='enterprise'
        ).first()
        
        # Si no existe, buscar por nombre que contenga "empresarial"
        if not enterprise_plan:
            enterprise_plan = SubscriptionPlan.objects.filter(
                name__icontains='empresarial'
            ).first()
        
        # Si aún no existe, obtener el plan más caro (el de mayor precio)
        if not enterprise_plan:
            enterprise_plan = SubscriptionPlan.objects.order_by('-price_monthly').first()
        
        # Si no hay ningún plan configurado, mostrar error
        if not enterprise_plan:
            messages.error(request, 'No existe ningún plan de suscripción configurado. Por favor, crea al menos un plan.')
            return redirect('admin_dashboard:user_detail', user_id=user_id)
        
        try:
            subscription = UserSubscription.objects.get(user=user)
            subscription.plan = enterprise_plan
            subscription.is_active = True
            subscription.payment_status = 'paid'
            # Extender por 100 años (prácticamente ilimitado)
            subscription.end_date = timezone.now() + timedelta(days=36500)
            subscription.save()
            messages.success(request, f'Acceso ilimitado otorgado a {user.username} con plan {enterprise_plan.name}')
        except UserSubscription.DoesNotExist:
            UserSubscription.objects.create(
                user=user,
                plan=enterprise_plan,
                is_active=True,
                payment_status='paid',
                end_date=timezone.now() + timedelta(days=36500)
            )
            messages.success(request, f'Suscripción ilimitada creada para {user.username} con plan {enterprise_plan.name}')
        
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
    from apps.organizations.models import PlanFeature
    
    if request.method == 'POST':
        from django.utils.text import slugify
        
        name = request.POST.get('name')
        plan_type = request.POST.get('plan_type', 'basic')
        description = request.POST.get('description', '')
        monthly_price = request.POST.get('monthly_price')
        yearly_price = request.POST.get('yearly_price')
        max_users = request.POST.get('max_users')
        max_appointments = request.POST.get('max_appointments')
        max_patients = request.POST.get('max_patients')
        max_storage_mb = request.POST.get('max_storage_mb', 500)
        is_active = request.POST.get('is_active') == 'on'
        
        # Características (checkboxes - legacy)
        whatsapp_integration = request.POST.get('whatsapp_integration') == '1'
        custom_branding = request.POST.get('custom_branding') == '1'
        api_access = request.POST.get('api_access') == '1'
        priority_support = request.POST.get('priority_support') == '1'
        analytics = request.POST.get('analytics') == '1'
        multi_location = request.POST.get('multi_location') == '1'
        
        # Nuevos campos de marketing
        coverage_description = request.POST.get('coverage_description', '')
        ideal_for = request.POST.get('ideal_for', '')
        plan_badge = request.POST.get('plan_badge', '')
        highlighted_features = request.POST.get('highlighted_features', '')
        main_benefits = request.POST.get('main_benefits', '')
        additional_features = request.POST.get('additional_features', '')
        
        # Nuevos campos de límites ilimitados
        unlimited_users = request.POST.get('unlimited_users') == '1'
        unlimited_patients = request.POST.get('unlimited_patients') == '1'
        unlimited_appointments = request.POST.get('unlimited_appointments') == '1'
        unlimited_organizations = request.POST.get('unlimited_organizations') == '1'
        unlimited_storage = request.POST.get('unlimited_storage') == '1'
        
        # Módulos seleccionados
        selected_features = request.POST.getlist('features')
        
        plan = SubscriptionPlan.objects.create(
            name=name,
            slug=slugify(name),
            plan_type=plan_type,
            price_monthly=monthly_price,
            price_yearly=yearly_price,
            max_users=max_users,
            max_appointments_month=max_appointments,
            max_patients=max_patients,
            max_storage_mb=max_storage_mb,
            whatsapp_integration=whatsapp_integration,
            custom_branding=custom_branding,
            api_access=api_access,
            priority_support=priority_support,
            analytics=analytics,
            multi_location=multi_location,
            # Nuevos campos de marketing
            coverage_description=coverage_description,
            ideal_for=ideal_for,
            plan_badge=plan_badge,
            highlighted_features=highlighted_features,
            main_benefits=main_benefits,
            additional_features=additional_features,
            includes_landing_page=True,
            # Nuevos campos de límites ilimitados
            unlimited_users=unlimited_users,
            unlimited_patients=unlimited_patients,
            unlimited_appointments=unlimited_appointments,
            unlimited_organizations=unlimited_organizations,
            unlimited_storage=unlimited_storage,
            is_active=is_active,
        )
        
        # Asignar módulos al plan
        if selected_features:
            plan.features.set(selected_features)
        
        messages.success(request, f'Plan {name} creado exitosamente con {len(selected_features)} módulo(s)')
        return redirect('admin_dashboard:plans_list')
    
    # GET - Mostrar formulario
    available_features = PlanFeature.objects.filter(is_active=True).order_by('category', 'name')
    
    context = {
        'available_features': available_features,
    }
    return render(request, 'admin_dashboard/plan_create.html', context)


@login_required
@user_passes_test(is_superuser)
def plan_edit(request, plan_id):
    """Editar plan existente"""
    from apps.organizations.models import PlanFeature
    
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    if request.method == 'POST':
        from django.utils.text import slugify
        from decimal import Decimal
        
        print("\n" + "="*70)
        print("🔧 EDITANDO PLAN")
        print("="*70)
        print(f"Plan ID: {plan_id}")
        print(f"Datos POST recibidos:")
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                print(f"   {key}: {value}")
        
        plan.name = request.POST.get('name')
        plan.slug = slugify(plan.name)
        plan.plan_type = request.POST.get('plan_type', plan.plan_type)
        plan.price_monthly = Decimal(request.POST.get('monthly_price', '0'))
        plan.price_yearly = Decimal(request.POST.get('yearly_price', '0'))
        
        # Límites básicos
        plan.max_users = int(request.POST.get('max_users', 1))
        plan.max_organizations = int(request.POST.get('max_organizations', 1))
        plan.max_appointments_month = int(request.POST.get('max_appointments', 50))
        plan.max_patients = int(request.POST.get('max_patients', 100))
        plan.max_storage_mb = int(request.POST.get('max_storage_mb', 500))
        
        # Facturación Electrónica
        plan.allow_electronic_invoicing = request.POST.get('allow_electronic_invoicing') == '1'
        plan.max_invoices_month = int(request.POST.get('max_invoices_month', 0))
        
        # Características (checkboxes - legacy)
        plan.whatsapp_integration = request.POST.get('whatsapp_integration') == '1'
        plan.custom_branding = request.POST.get('custom_branding') == '1'
        plan.api_access = request.POST.get('api_access') == '1'
        plan.priority_support = request.POST.get('priority_support') == '1'
        plan.analytics = request.POST.get('analytics') == '1'
        plan.multi_location = request.POST.get('multi_location') == '1'
        
        # NUEVOS CAMPOS DE MARKETING
        plan.coverage_description = request.POST.get('coverage_description', '')
        plan.ideal_for = request.POST.get('ideal_for', '')
        plan.plan_badge = request.POST.get('plan_badge', '')
        plan.highlighted_features = request.POST.get('highlighted_features', '')
        plan.main_benefits = request.POST.get('main_benefits', '')
        plan.additional_features = request.POST.get('additional_features', '')
        plan.includes_landing_page = True  # Siempre True por defecto
        
        # NUEVOS CAMPOS DE LÍMITES ILIMITADOS
        plan.unlimited_users = request.POST.get('unlimited_users') == '1'
        plan.unlimited_patients = request.POST.get('unlimited_patients') == '1'
        plan.unlimited_appointments = request.POST.get('unlimited_appointments') == '1'
        plan.unlimited_organizations = request.POST.get('unlimited_organizations') == '1'
        plan.unlimited_storage = request.POST.get('unlimited_storage') == '1'
        
        plan.is_active = request.POST.get('is_active') == 'on'
        
        # Módulos seleccionados
        selected_features = request.POST.getlist('features')
        plan.features.set(selected_features)
        
        plan.save()
        
        print(f"\n✅ Plan guardado:")
        print(f"   Nombre: {plan.name}")
        print(f"   Max usuarios: {plan.max_users}")
        print(f"   Max organizaciones: {plan.max_organizations}")
        print(f"   Max citas/mes: {plan.max_appointments_month}")
        print(f"   Max pacientes: {plan.max_patients}")
        print(f"   Max storage: {plan.max_storage_mb} MB")
        print(f"   Facturación: {plan.allow_electronic_invoicing}")
        print(f"   Max facturas/mes: {plan.max_invoices_month}")
        print(f"   Activo: {plan.is_active}")
        print("="*70 + "\n")
        
        messages.success(request, f'Plan {plan.name} actualizado correctamente')
        return redirect('admin_dashboard:plans_list')
    
    # GET - Mostrar formulario
    available_features = PlanFeature.objects.filter(is_active=True).order_by('category', 'name')
    plan_feature_ids = list(plan.features.values_list('id', flat=True))
    
    context = {
        'plan': plan,
        'available_features': available_features,
        'plan_feature_ids': plan_feature_ids,
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
def plan_delete(request, plan_id):
    """Eliminar plan de suscripción"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    if request.method == 'POST':
        # Verificar si hay suscripciones activas
        active_subscriptions = Subscription.objects.filter(plan=plan, is_active=True).count()
        
        if active_subscriptions > 0:
            messages.error(request, f'No se puede eliminar el plan "{plan.name}". Tiene {active_subscriptions} suscripción(es) activa(s).')
            return redirect('admin_dashboard:plans_list')
        
        plan_name = plan.name
        plan.delete()
        messages.success(request, f'Plan "{plan_name}" eliminado exitosamente.')
        return redirect('admin_dashboard:plans_list')
    
    # GET request - mostrar página de confirmación
    active_subscriptions = Subscription.objects.filter(plan=plan, is_active=True).count()
    total_subscriptions = Subscription.objects.filter(plan=plan).count()
    
    context = {
        'plan': plan,
        'active_subscriptions': active_subscriptions,
        'total_subscriptions': total_subscriptions,
    }
    return render(request, 'admin_dashboard/plan_delete.html', context)


@login_required
@user_passes_test(is_superuser)
def verify_user_email(request, user_id):
    """Verificar manualmente el email de un usuario"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        # Obtener o crear perfil de usuario
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.is_email_verified = True
        profile.email_verified_at = timezone.now()
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
        profile.is_email_verified = False
        profile.email_verified_at = None
        profile.save()
        
        messages.warning(request, f'Email de {user.username} marcado como no verificado')
    
    return redirect('admin_dashboard:user_detail', user_id=user_id)


# ==================== GESTIÓN DE MÓDULOS/CARACTERÍSTICAS ====================

@login_required
@user_passes_test(is_superuser)
def features_list(request):
    """Listar todos los módulos/características"""
    from apps.organizations.models import PlanFeature
    from django.db.models import Count
    
    category_filter = request.GET.get('category')
    
    features = PlanFeature.objects.annotate(
        plans_count=Count('plans')
    ).order_by('category', 'name')
    
    if category_filter:
        features = features.filter(category=category_filter)
    
    # Contar por categoría con nombres
    category_counts = []
    for cat_code, cat_name in PlanFeature.FEATURE_CATEGORIES:
        count = PlanFeature.objects.filter(category=cat_code).count()
        category_counts.append({
            'code': cat_code,
            'name': cat_name,
            'count': count
        })
    
    context = {
        'features': features,
        'categories': PlanFeature.FEATURE_CATEGORIES,
        'category_filter': category_filter,
        'category_counts': category_counts,
    }
    return render(request, 'admin_dashboard/features_list.html', context)


@login_required
@user_passes_test(is_superuser)
def feature_create(request):
    """Crear nuevo módulo/característica"""
    from apps.organizations.models import PlanFeature
    from django.utils.text import slugify
    
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        category = request.POST.get('category')
        icon = request.POST.get('icon', '')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            feature = PlanFeature.objects.create(
                name=name,
                code=code,
                category=category,
                icon=icon,
                description=description,
                is_active=is_active
            )
            messages.success(request, f'Módulo "{name}" creado exitosamente')
            return redirect('admin_dashboard:features_list')
        except Exception as e:
            messages.error(request, f'Error al crear módulo: {str(e)}')
    
    return render(request, 'admin_dashboard/feature_create.html')


@login_required
@user_passes_test(is_superuser)
def feature_edit(request, feature_id):
    """Editar módulo/característica"""
    from apps.organizations.models import PlanFeature
    
    feature = get_object_or_404(PlanFeature, id=feature_id)
    
    if request.method == 'POST':
        feature.name = request.POST.get('name')
        feature.code = request.POST.get('code')
        feature.category = request.POST.get('category')
        feature.icon = request.POST.get('icon', '')
        feature.description = request.POST.get('description', '')
        feature.is_active = request.POST.get('is_active') == 'on'
        
        try:
            feature.save()
            messages.success(request, f'Módulo "{feature.name}" actualizado exitosamente')
            return redirect('admin_dashboard:features_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar módulo: {str(e)}')
    
    context = {
        'feature': feature,
        'categories': PlanFeature.FEATURE_CATEGORIES,
    }
    return render(request, 'admin_dashboard/feature_edit.html', context)


@login_required
@user_passes_test(is_superuser)
def feature_delete(request, feature_id):
    """Eliminar módulo/característica"""
    from apps.organizations.models import PlanFeature
    
    if request.method == 'POST':
        feature = get_object_or_404(PlanFeature, id=feature_id)
        feature_name = feature.name
        feature.delete()
        messages.success(request, f'Módulo "{feature_name}" eliminado exitosamente')
    
    return redirect('admin_dashboard:features_list')


# ==================== GESTIÓN DE MÓDULOS POR ORGANIZACIÓN ====================

@login_required
@user_passes_test(is_superuser)
def organization_features(request, org_id):
    """Gestionar módulos de una organización específica"""
    from apps.organizations.models import PlanFeature, OrganizationFeature
    
    organization = get_object_or_404(Organization, id=org_id)
    
    # Obtener todos los módulos disponibles
    all_features = PlanFeature.objects.filter(is_active=True).order_by('category', 'name')
    
    # Obtener módulos habilitados para esta organización
    enabled_features = OrganizationFeature.objects.filter(
        organization=organization
    ).select_related('feature')
    
    # Crear diccionario para fácil acceso
    enabled_dict = {ef.feature.id: ef for ef in enabled_features}
    
    # Obtener módulos del plan actual
    plan_features = set()
    if organization.current_subscription:
        plan_features = set(organization.current_subscription.plan.features.values_list('id', flat=True))
    
    context = {
        'organization': organization,
        'all_features': all_features,
        'enabled_dict': enabled_dict,
        'plan_features': plan_features,
    }
    return render(request, 'admin_dashboard/organization_features.html', context)


@login_required
@user_passes_test(is_superuser)
def organization_feature_toggle(request, org_id):
    """Habilitar/deshabilitar módulo para una organización"""
    from apps.organizations.models import PlanFeature, OrganizationFeature
    
    if request.method == 'POST':
        organization = get_object_or_404(Organization, id=org_id)
        feature_id = request.POST.get('feature_id')
        is_enabled = request.POST.get('is_enabled') == 'true'
        
        try:
            feature = PlanFeature.objects.get(id=feature_id)
            org_feature, created = OrganizationFeature.objects.get_or_create(
                organization=organization,
                feature=feature,
                defaults={
                    'is_enabled': is_enabled,
                    'granted_by_plan': False,  # Habilitado manualmente por admin
                }
            )
            
            if not created:
                org_feature.is_enabled = is_enabled
                org_feature.save()
            
            status = 'habilitado' if is_enabled else 'deshabilitado'
            messages.success(request, f'Módulo "{feature.name}" {status} para {organization.name}')
            
        except PlanFeature.DoesNotExist:
            messages.error(request, 'Módulo no encontrado')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return redirect('admin_dashboard:organization_features', org_id=org_id)


@login_required
@user_passes_test(is_superuser)
def organization_sync_plan_features(request, org_id):
    """Sincronizar módulos del plan con la organización"""
    from apps.organizations.models import OrganizationFeature
    
    if request.method == 'POST':
        organization = get_object_or_404(Organization, id=org_id)
        
        if not organization.current_subscription:
            messages.error(request, 'La organización no tiene suscripción activa')
            return redirect('admin_dashboard:organization_features', org_id=org_id)
        
        plan = organization.current_subscription.plan
        plan_features = plan.features.all()
        
        # Marcar módulos del plan como habilitados
        for feature in plan_features:
            org_feature, created = OrganizationFeature.objects.get_or_create(
                organization=organization,
                feature=feature,
                defaults={
                    'is_enabled': True,
                    'granted_by_plan': True,
                }
            )
            
            if not created:
                org_feature.is_enabled = True
                org_feature.granted_by_plan = True
                org_feature.save()
        
        messages.success(request, f'{plan_features.count()} módulos sincronizados desde el plan {plan.name}')
    
    return redirect('admin_dashboard:organization_features', org_id=org_id)


# ==================== GESTIÓN DE PAQUETES DE FACTURAS ====================

@login_required
@user_passes_test(is_superuser)
def invoice_packages_list(request):
    """Listar todas las compras de paquetes de facturas"""
    from apps.organizations.models import InvoicePackagePurchase
    
    org_filter = request.GET.get('organization')
    status_filter = request.GET.get('status')
    
    packages = InvoicePackagePurchase.objects.all().select_related('organization')
    
    if org_filter:
        packages = packages.filter(organization_id=org_filter)
    
    if status_filter:
        packages = packages.filter(payment_status=status_filter)
    
    packages = packages.order_by('-purchased_at')
    
    # Organizaciones para el filtro
    organizations = Organization.objects.all().order_by('name')
    
    context = {
        'packages': packages,
        'organizations': organizations,
        'org_filter': org_filter,
        'status_filter': status_filter,
    }
    return render(request, 'admin_dashboard/invoice_packages_list.html', context)


@login_required
@user_passes_test(is_superuser)
def invoice_package_create(request, org_id):
    """Crear paquete de facturas para una organización"""
    from apps.organizations.models import InvoicePackagePurchase
    from decimal import Decimal
    
    organization = get_object_or_404(Organization, id=org_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        payment_status = request.POST.get('payment_status', 'paid')
        
        # Obtener precio del paquete
        price = Decimal(InvoicePackagePurchase.PACKAGE_PRICES.get(quantity, 0))
        
        package = InvoicePackagePurchase.objects.create(
            organization=organization,
            quantity=quantity,
            price=price,
            payment_status=payment_status,
            payment_date=timezone.now() if payment_status == 'paid' else None
        )
        
        messages.success(request, f'Paquete de {quantity} facturas creado para {organization.name}')
        return redirect('admin_dashboard:organization_detail', org_id=org_id)
    
    # GET - Mostrar formulario
    context = {
        'organization': organization,
        'package_sizes': InvoicePackagePurchase.PACKAGE_SIZES,
        'package_prices': InvoicePackagePurchase.PACKAGE_PRICES,
    }
    return render(request, 'admin_dashboard/invoice_package_create.html', context)


# ==================== GESTIÓN DE COMPRAS DE MÓDULOS ADICIONALES ====================

@login_required
@user_passes_test(is_superuser)
def addon_purchases_list(request):
    """Listar todas las compras de módulos adicionales"""
    from apps.organizations.models import AddonPurchase
    
    org_filter = request.GET.get('organization')
    status_filter = request.GET.get('status')
    
    addons = AddonPurchase.objects.all().select_related('organization', 'feature')
    
    if org_filter:
        addons = addons.filter(organization_id=org_filter)
    
    if status_filter:
        addons = addons.filter(payment_status=status_filter)
    
    addons = addons.order_by('-purchased_at')
    
    # Organizaciones para el filtro
    organizations = Organization.objects.all().order_by('name')
    
    context = {
        'addons': addons,
        'organizations': organizations,
        'org_filter': org_filter,
        'status_filter': status_filter,
    }
    return render(request, 'admin_dashboard/addon_purchases_list.html', context)


@login_required
@user_passes_test(is_superuser)
def addon_purchase_create(request, org_id):
    """Crear compra de módulo adicional para una organización"""
    from apps.organizations.models import AddonPurchase, PlanFeature, OrganizationFeature
    from decimal import Decimal
    
    organization = get_object_or_404(Organization, id=org_id)
    
    if request.method == 'POST':
        feature_id = request.POST.get('feature_id')
        billing_cycle = request.POST.get('billing_cycle', 'monthly')
        payment_status = request.POST.get('payment_status', 'paid')
        price = Decimal(request.POST.get('price', 0))
        
        feature = get_object_or_404(PlanFeature, id=feature_id)
        
        # Crear la compra
        addon = AddonPurchase.objects.create(
            organization=organization,
            feature=feature,
            billing_cycle=billing_cycle,
            price=price,
            payment_status=payment_status,
            is_active=True,
            payment_date=timezone.now() if payment_status == 'paid' else None
        )
        
        # Habilitar el módulo para la organización
        org_feature, created = OrganizationFeature.objects.get_or_create(
            organization=organization,
            feature=feature,
            defaults={
                'is_enabled': True,
                'granted_by_plan': False,
                'purchased_at': timezone.now(),
                'expires_at': addon.end_date,
                'amount_paid': price
            }
        )
        
        if not created:
            org_feature.is_enabled = True
            org_feature.granted_by_plan = False
            org_feature.purchased_at = timezone.now()
            org_feature.expires_at = addon.end_date
            org_feature.amount_paid = price
            org_feature.save()
        
        messages.success(request, f'Módulo "{feature.name}" agregado a {organization.name}')
        return redirect('admin_dashboard:organization_detail', org_id=org_id)
    
    # GET - Mostrar formulario
    # Solo módulos que se pueden comprar por separado
    available_features = PlanFeature.objects.filter(
        is_active=True,
        can_purchase_separately=True
    ).order_by('category', 'name')
    
    context = {
        'organization': organization,
        'available_features': available_features,
    }
    return render(request, 'admin_dashboard/addon_purchase_create.html', context)


@superuser_required
def error_monitoring(request):
    """
    Dashboard de Monitoreo de Errores del Sistema
    
    Esta vista proporciona un panel de control completo para monitorear y analizar
    todos los errores capturados automáticamente en la aplicación.
    
    Características:
    - Errores JavaScript capturados automáticamente desde el frontend
    - Errores de red (HTTP 400, 500) interceptados por fetch
    - Errores de backend (excepciones Python, Django)
    - Estadísticas en tiempo real (total, sin resolver, críticos)
    - Gráficos de tendencias (últimos 7 días)
    - Distribución por severidad
    - Top 10 errores más frecuentes
    - Filtros avanzados (severidad, estado, búsqueda)
    
    Filtros disponibles:
    - severity: DEBUG, INFO, WARNING, ERROR, CRITICAL
    - resolved: 'resolved' (resueltos) o 'unresolved' (pendientes)
    - search: busca en tipo de error, mensaje y URL
    
    Contexto retornado:
    - total_errors: Total de errores en el sistema
    - unresolved_errors: Errores pendientes de resolver
    - critical_errors: Errores críticos activos
    - recent_errors: Errores en las últimas 24 horas
    - errors_by_severity: Distribución por nivel de severidad
    - top_errors: Los 10 errores más frecuentes (últimos 7 días)
    - errors_by_day: Tendencia diaria (últimos 7 días)
    - errors_list: Lista paginada de errores (últimos 100)
    """
    from apps.audit.models import ErrorLog
    from django.db.models import Count
    from datetime import datetime, timedelta
    
    # Filtros
    severity_filter = request.GET.get('severity')
    resolved_filter = request.GET.get('resolved')
    search_query = request.GET.get('search')
    
    # Query base
    errors = ErrorLog.objects.all()
    
    # Aplicar filtros
    if severity_filter:
        errors = errors.filter(severity=severity_filter)
    
    if resolved_filter:
        is_resolved = resolved_filter == 'resolved'
        errors = errors.filter(is_resolved=is_resolved)
    
    if search_query:
        errors = errors.filter(
            Q(error_type__icontains=search_query) |
            Q(error_message__icontains=search_query) |
            Q(url__icontains=search_query)
        )
    
    # Estadísticas generales
    total_errors = ErrorLog.objects.count()
    unresolved_errors = ErrorLog.objects.filter(is_resolved=False).count()
    critical_errors = ErrorLog.objects.filter(severity='CRITICAL', is_resolved=False).count()
    
    # Errores por severidad
    errors_by_severity = ErrorLog.objects.values('severity').annotate(
        count=Count('id')
    ).order_by('severity')
    
    # Errores recientes (últimas 24 horas)
    yesterday = timezone.now() - timedelta(days=1)
    recent_errors = ErrorLog.objects.filter(timestamp__gte=yesterday).count()
    
    # Errores más frecuentes (últimos 7 días)
    week_ago = timezone.now() - timedelta(days=7)
    top_errors = ErrorLog.objects.filter(
        timestamp__gte=week_ago
    ).values('error_type', 'error_message').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Errores por día (últimos 7 días)
    errors_by_day = []
    for i in range(6, -1, -1):
        day = timezone.now() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        count = ErrorLog.objects.filter(
            timestamp__gte=day_start,
            timestamp__lt=day_end
        ).count()
        
        errors_by_day.append({
            'date': day_start.strftime('%d/%m'),
            'count': count
        })
    
    # Lista de errores (paginado)
    errors_list = errors.select_related('user', 'organization').order_by('-timestamp')[:100]
    
    context = {
        'total_errors': total_errors,
        'unresolved_errors': unresolved_errors,
        'critical_errors': critical_errors,
        'recent_errors': recent_errors,
        'errors_by_severity': errors_by_severity,
        'top_errors': top_errors,
        'errors_by_day': errors_by_day,
        'errors_list': errors_list,
        'severity_filter': severity_filter,
        'resolved_filter': resolved_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin_dashboard/error_monitoring.html', context)


@superuser_required
def error_resolve(request, error_id):
    """
    Marca un error como resuelto.
    Útil cuando ya se corrigió el problema en el código.
    """
    from apps.audit.models import ErrorLog
    
    error = get_object_or_404(ErrorLog, id=error_id)
    error.is_resolved = True
    error.save()
    
    messages.success(request, f'✅ Error #{error_id} marcado como RESUELTO')
    
    return redirect('admin_dashboard:error_monitoring')


@superuser_required
def error_unresolve(request, error_id):
    """
    Marca un error como NO resuelto.
    Útil si el error vuelve a ocurrir después de creer que se solucionó.
    """
    from apps.audit.models import ErrorLog
    
    error = get_object_or_404(ErrorLog, id=error_id)
    error.is_resolved = False
    error.save()
    
    messages.warning(request, f'⚠️ Error #{error_id} marcado como NO RESUELTO')
    
    return redirect('admin_dashboard:error_monitoring')
