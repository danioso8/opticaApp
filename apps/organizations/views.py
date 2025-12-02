from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
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
    
    context = {
        'memberships': memberships,
    }
    return render(request, 'organizations/list.html', context)


@login_required
def organization_create(request):
    """Crear nueva organización"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        
        if not name or not email:
            messages.error(request, 'El nombre y email son requeridos')
            return render(request, 'organizations/create.html')
        
        # Generar slug único
        slug = slugify(name)
        base_slug = slug
        counter = 1
        while Organization.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        try:
            with transaction.atomic():
                # Crear organización
                organization = Organization.objects.create(
                    name=name,
                    slug=slug,
                    email=email,
                    phone=phone,
                    owner=request.user
                )
                
                # Crear suscripción gratuita inicial
                free_plan = SubscriptionPlan.objects.filter(plan_type='free').first()
                if free_plan:
                    Subscription.objects.create(
                        organization=organization,
                        plan=free_plan,
                        billing_cycle='monthly',
                        payment_status='paid'
                    )
                
                messages.success(request, f'Organización {name} creada exitosamente')
                return redirect('organization_list')
        except Exception as e:
            messages.error(request, f'Error al crear organización: {str(e)}')
    
    return render(request, 'organizations/create.html')


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
    messages.success(request, f'Cambiado a {membership.organization.name}')
    
    next_url = request.GET.get('next', 'dashboard:home')
    return redirect(next_url)


@login_required
def subscription_plans(request):
    """Mostrar planes de suscripción disponibles"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_monthly')
    
    current_plan = None
    if hasattr(request, 'organization') and request.organization:
        subscription = request.organization.current_subscription
        if subscription:
            current_plan = subscription.plan
    
    context = {
        'plans': plans,
        'current_plan': current_plan,
    }
    return render(request, 'organizations/plans.html', context)


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
        return redirect('organization_detail', org_id=org_id)
    
    organization = membership.organization
    
    if request.method == 'POST':
        organization.name = request.POST.get('name', organization.name)
        organization.email = request.POST.get('email', organization.email)
        organization.phone = request.POST.get('phone', organization.phone)
        organization.address = request.POST.get('address', organization.address)
        organization.primary_color = request.POST.get('primary_color', organization.primary_color)
        
        try:
            organization.save()
            messages.success(request, 'Configuración actualizada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
        
        return redirect('organization_settings', org_id=org_id)
    
    context = {
        'organization': organization,
        'membership': membership,
    }
    return render(request, 'organizations/settings.html', context)
