from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.text import slugify
from .models import Organization, OrganizationMember, SubscriptionPlan, Subscription
from django.db import transaction


@login_required
def organization_list(request):
    """Lista de organizaciones del usuario"""
    memberships = OrganizationMember.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('organization')
    
    # Obtener suscripción del usuario
    user_subscription = None
    can_create_more = False
    current_count = 0
    max_allowed = 0
    
    has_unlimited_access = False
    
    try:
        from apps.users.models import UserSubscription
        user_subscription = UserSubscription.objects.get(user=request.user)
        current_count = request.user.owned_organizations.filter(is_active=True).count()
        max_allowed = user_subscription.plan.max_users  # max_users usado como max_organizations
        can_create_more = user_subscription.can_create_organizations()
        
        # Detectar acceso ilimitado (año 2125)
        has_unlimited_access = user_subscription.end_date.year >= 2125
    except UserSubscription.DoesNotExist:
        pass
    
    context = {
        'memberships': memberships,
        'user_subscription': user_subscription,
        'can_create_more': can_create_more,
        'current_count': current_count,
        'max_allowed': max_allowed,
        'has_unlimited_access': has_unlimited_access,
    }
    return render(request, 'organizations/list.html', context)


@login_required
def organization_create(request):
    """Crear nueva organización (verificando límites del plan del usuario)"""
    # Verificar suscripción del usuario
    try:
        from apps.users.models import UserSubscription
        user_subscription = UserSubscription.objects.get(user=request.user)
        
        if not user_subscription.is_active or user_subscription.is_expired:
            messages.error(request, 'Tu suscripción ha expirado. Por favor renueva tu plan.')
            return redirect('organizations:subscription_plans')
        
        # Verificar si puede crear más organizaciones
        if not user_subscription.can_create_organizations():
            current_count = request.user.owned_organizations.filter(is_active=True).count()
            max_allowed = user_subscription.plan.max_users  # max_users usado como max_organizations
            messages.error(
                request, 
                f'Has alcanzado el límite de organizaciones ({current_count}/{max_allowed}). '
                f'Actualiza tu plan para crear más organizaciones.'
            )
            return redirect('organizations:subscription_plans')
            
    except UserSubscription.DoesNotExist:
        messages.error(request, 'No tienes una suscripción activa. Por favor selecciona un plan.')
        return redirect('organizations:subscription_plans')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        secondary_phone = request.POST.get('secondary_phone', '')
        address = request.POST.get('address', '')
        neighborhood = request.POST.get('neighborhood', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        country = request.POST.get('country', '')
        postal_code = request.POST.get('postal_code', '')
        legal_name = request.POST.get('legal_name', '')
        tax_id_type = request.POST.get('tax_id_type', '')
        tax_id = request.POST.get('tax_id', '')
        legal_representative = request.POST.get('legal_representative', '')
        website = request.POST.get('website', '')
        
        if not name or not email:
            messages.error(request, 'El nombre y email son requeridos')
            context = {'user_subscription': user_subscription}
            return render(request, 'organizations/create.html', context)
        
        # Generar slug único
        slug = slugify(name)
        base_slug = slug
        counter = 1
        while Organization.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        try:
            with transaction.atomic():
                # Crear organización (el signal creará automáticamente la membresía del owner)
                organization = Organization.objects.create(
                    name=name,
                    slug=slug,
                    email=email,
                    phone=phone,
                    secondary_phone=secondary_phone,
                    address=address,
                    neighborhood=neighborhood,
                    city=city,
                    state=state,
                    country=country,
                    postal_code=postal_code,
                    legal_name=legal_name,
                    tax_id_type=tax_id_type,
                    tax_id=tax_id,
                    legal_representative=legal_representative,
                    website=website,
                    owner=request.user
                )
                
                messages.success(request, f'Empresa/Sucursal "{name}" creada exitosamente')
                return redirect('organizations:list')
        except Exception as e:
            messages.error(request, f'Error al crear organización: {str(e)}')
    
    context = {
        'user_subscription': user_subscription,
    }
    return render(request, 'organizations/create.html', context)


@login_required
def organization_detail(request, org_id):
    """Detalle de organización"""
    membership = get_object_or_404(
        OrganizationMember,
        organization_id=org_id,
        user=request.user,
        is_active=True
    )
    
    organization = membership.organization
    current_subscription = organization.current_subscription
    members = organization.members.filter(is_active=True).select_related('user')
    
    context = {
        'organization': organization,
        'membership': membership,
        'current_subscription': current_subscription,
        'members': members,
        'plan_limits': organization.get_plan_limits(),
    }
    return render(request, 'organizations/detail.html', context)


@login_required
def organization_switch(request, org_id):
    """Cambiar organización activa"""
    membership = get_object_or_404(
        OrganizationMember,
        organization_id=org_id,
        user=request.user,
        is_active=True
    )
    
    request.session['current_organization_id'] = membership.organization.id
    messages.success(request, f'Ahora trabajando con: {membership.organization.name}')
    
    # Redirigir al dashboard después de seleccionar la organización
    next_url = request.GET.get('next')
    if next_url and next_url.startswith('/') and 'organizations' not in next_url:
        return redirect(next_url)
    return redirect('dashboard:home')


@login_required
def subscription_plans(request):
    """Mostrar planes de suscripción disponibles"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
    
    # Obtener suscripción actual del usuario
    current_subscription = None
    has_unlimited_access = False
    
    try:
        from apps.users.models import UserSubscription
        current_subscription = UserSubscription.objects.get(user=request.user)
        has_unlimited_access = current_subscription.end_date.year >= 2125
    except UserSubscription.DoesNotExist:
        pass
    
    context = {
        'plans': plans,
        'current_subscription': current_subscription,
        'has_unlimited_access': has_unlimited_access,
    }
    return render(request, 'organizations/plans.html', context)


@login_required
def upgrade_plan(request, plan_id):
    """Mejorar plan de suscripción del usuario"""
    if request.method == 'POST':
        plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
        
        from apps.users.models import UserSubscription
        from datetime import timedelta
        from django.utils import timezone
        
        billing_cycle = request.POST.get('billing_cycle', 'monthly')
        
        try:
            # Actualizar suscripción existente
            subscription = UserSubscription.objects.get(user=request.user)
            subscription.plan = plan
            subscription.billing_cycle = billing_cycle
            # Plan Free no requiere pago
            subscription.payment_status = 'paid' if plan.plan_type == 'free' else 'pending'
            subscription.is_active = True
            
            # Calcular nueva fecha de expiración
            if billing_cycle == 'yearly':
                subscription.end_date = timezone.now() + timedelta(days=365)
                subscription.amount_paid = plan.price_yearly
            else:
                subscription.end_date = timezone.now() + timedelta(days=30)
                subscription.amount_paid = plan.price_monthly
            
            subscription.save()
            messages.success(request, f'¡Plan actualizado a {plan.name}!')
            
        except UserSubscription.DoesNotExist:
            # Crear nueva suscripción
            if billing_cycle == 'yearly':
                end_date = timezone.now() + timedelta(days=365)
                amount = plan.price_yearly
            else:
                end_date = timezone.now() + timedelta(days=30)
                amount = plan.price_monthly
            
            # Plan Free no requiere pago
            payment_status = 'paid' if plan.plan_type == 'free' else 'pending'
            
            UserSubscription.objects.create(
                user=request.user,
                plan=plan,
                billing_cycle=billing_cycle,
                payment_status=payment_status,
                is_active=True,
                end_date=end_date,
                amount_paid=amount
            )
            messages.success(request, f'¡Suscripción activada al plan {plan.name}!')
        
        return redirect('organizations:subscription_plans')
    
    return redirect('organizations:subscription_plans')


@login_required
def subscription_expired(request):
    """Página de suscripción expirada"""
    organization = None
    if hasattr(request, 'organization'):
        organization = request.organization
    
    context = {
        'organization': organization,
    }
    return render(request, 'organizations/subscription_expired.html', context)


@login_required
def organization_settings(request, org_id):
    """Configuración de organización"""
    membership = get_object_or_404(
        OrganizationMember,
        organization_id=org_id,
        user=request.user,
        is_active=True
    )
    
    # Solo admin y owner pueden acceder
    if membership.role not in ['owner', 'admin']:
        messages.error(request, 'No tienes permisos para acceder a la configuración')
        return redirect('organizations:detail', org_id=org_id)
    
    organization = membership.organization
    
    if request.method == 'POST':
        organization.name = request.POST.get('name', organization.name)
        organization.legal_name = request.POST.get('legal_name', organization.legal_name)
        organization.tax_id_type = request.POST.get('tax_id_type', organization.tax_id_type)
        organization.tax_id = request.POST.get('tax_id', organization.tax_id)
        organization.legal_representative = request.POST.get('legal_representative', organization.legal_representative)
        organization.email = request.POST.get('email', organization.email)
        organization.website = request.POST.get('website', organization.website)
        organization.phone = request.POST.get('phone', organization.phone)
        organization.secondary_phone = request.POST.get('secondary_phone', organization.secondary_phone)
        organization.address = request.POST.get('address', organization.address)
        organization.neighborhood = request.POST.get('neighborhood', organization.neighborhood)
        organization.city = request.POST.get('city', organization.city)
        organization.state = request.POST.get('state', organization.state)
        organization.postal_code = request.POST.get('postal_code', organization.postal_code)
        organization.country = request.POST.get('country', organization.country)
        organization.primary_color = request.POST.get('primary_color', organization.primary_color)
        
        # Manejar subida de logo
        if 'logo' in request.FILES:
            # Eliminar logo anterior si existe
            if organization.logo:
                try:
                    organization.logo.delete(save=False)
                except:
                    pass
            organization.logo = request.FILES['logo']
        
        try:
            organization.save()
            messages.success(request, 'Configuración actualizada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
        
        return redirect('organizations:settings', org_id=org_id)
    
    context = {
        'organization': organization,
        'membership': membership,
    }
    return render(request, 'organizations/settings.html', context)


@login_required
def organization_delete(request, org_id):
    """Eliminar organización y todos sus datos relacionados (solo owner)"""
    membership = get_object_or_404(
        OrganizationMember,
        organization_id=org_id,
        user=request.user,
        is_active=True
    )
    
    # Solo el owner puede eliminar
    if membership.role != 'owner':
        messages.error(request, 'Solo el propietario puede eliminar la organización')
        return redirect('organizations:detail', org_id=org_id)
    
    organization = membership.organization
    org_name = organization.name
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Django eliminará automáticamente los datos relacionados con CASCADE:
                # - OrganizationMember (on_delete=CASCADE en organization)
                # - Appointment (on_delete=CASCADE en organization)
                # - Patient (on_delete=CASCADE en organization)
                # - Sale (on_delete=CASCADE en organization)
                
                organization.delete()
                
                messages.success(
                    request,
                    f'La organización "{org_name}" y todos sus datos han sido eliminados exitosamente.'
                )
                return redirect('organizations:list')
                
        except Exception as e:
            messages.error(request, f'Error al eliminar la organización: {str(e)}')
            return redirect('organizations:detail', org_id=org_id)
    
    # GET request - no se debe llegar aquí
    return redirect('organizations:detail', org_id=org_id)


def user_register(request):
    """Registro de nuevo usuario con selección de plan"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
    
    if request.method == 'POST':
        # Datos del usuario
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Plan seleccionado
        plan_id = request.POST.get('plan_id')
        billing_cycle = request.POST.get('billing_cycle', 'monthly')
        
        # Validaciones
        errors = []
        if not all([first_name, last_name, email, username, password, plan_id]):
            errors.append('Todos los campos obligatorios deben ser completados')
        
        if password != password_confirm:
            errors.append('Las contraseñas no coinciden')
        
        if len(password) < 8:
            errors.append('La contraseña debe tener al menos 8 caracteres')
        
        if User.objects.filter(username=username).exists():
            errors.append('El nombre de usuario ya está en uso')
        
        if User.objects.filter(email=email).exists():
            errors.append('El email ya está registrado')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            context = {
                'plans': plans,
                'form_data': request.POST,
            }
            return render(request, 'organizations/user_register.html', context)
        
        try:
            with transaction.atomic():
                # Crear usuario - INACTIVO hasta que verifique el email
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=False  # Usuario inactivo hasta verificar email
                )
                
                # Crear perfil de usuario
                from apps.users.email_verification_models import UserProfile
                UserProfile.objects.create(
                    user=user,
                    is_email_verified=False
                )
                
                # Crear suscripción del usuario
                plan = SubscriptionPlan.objects.get(id=plan_id)
                
                # Si es plan gratuito, marcar como pagado automáticamente
                payment_status = 'paid' if plan.plan_type == 'free' else 'pending'
                
                from apps.users.models import UserSubscription
                UserSubscription.objects.create(
                    user=user,
                    plan=plan,
                    billing_cycle=billing_cycle,
                    payment_status=payment_status
                )
                
                # Enviar email de verificación
                from apps.users.email_views import send_verification_email
                email_sent = send_verification_email(user, request)
                
                if email_sent:
                    messages.success(
                        request, 
                        f'¡Cuenta creada exitosamente! Hemos enviado un correo a {email} para verificar tu cuenta.'
                    )
                else:
                    messages.warning(
                        request,
                        'Cuenta creada, pero hubo un error al enviar el email. Por favor contacta a soporte.'
                    )
                
                # NO hacer login automático - requiere verificación de email
                # Redirigir a página de verificación pendiente
                return redirect('users:verification_pending')
                
        except SubscriptionPlan.DoesNotExist:
            messages.error(request, 'El plan seleccionado no existe')
        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {str(e)}')
    
    context = {
        'plans': plans,
    }
    return render(request, 'organizations/user_register.html', context)
