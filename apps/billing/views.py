from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q, Sum
from datetime import datetime, timedelta
from decimal import Decimal

from apps.organizations.models import Organization, OrganizationMember
from apps.patients.models import Patient
from .models import DianConfiguration, Invoice, InvoiceItem, Payment


@login_required
def dian_configuration_view(request):
    """
    Vista para configurar los parámetros de la DIAN.
    Solo para usuarios con plan Profesional o Empresarial.
    """
    # Obtener organización del usuario
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    organization = org_member.organization
    
    # Verificar si el plan permite facturación electrónica
    can_use, message = Invoice.puede_crear_factura_electronica(organization)
    
    if not can_use and not hasattr(organization, 'dianconfiguration'):
        messages.error(request, message)
        return redirect('dashboard:home')
    
    # Obtener o crear configuración DIAN
    dian_config, created = DianConfiguration.objects.get_or_create(
        organization=organization,
        defaults={
            'configurado_por': request.user
        }
    )
    
    if request.method == 'POST':
        # Validar que puede usar facturación
        if not can_use:
            messages.error(request, message)
            return redirect('billing:dian_config')
        
        # Actualizar campos básicos
        dian_config.razon_social = request.POST.get('razon_social', '').strip()
        dian_config.nit = request.POST.get('nit', '').strip()
        dian_config.dv = request.POST.get('dv', '').strip()
        dian_config.tipo_organizacion = request.POST.get('tipo_organizacion', '2')
        
        # Dirección
        dian_config.direccion = request.POST.get('direccion', '').strip()
        dian_config.ciudad_codigo = request.POST.get('ciudad_codigo', '').strip()
        dian_config.departamento_codigo = request.POST.get('departamento_codigo', '').strip()
        dian_config.pais_codigo = request.POST.get('pais_codigo', 'CO')
        dian_config.codigo_postal = request.POST.get('codigo_postal', '').strip()
        
        # Contacto
        dian_config.telefono = request.POST.get('telefono', '').strip()
        dian_config.email_facturacion = request.POST.get('email_facturacion', '').strip()
        
        # Resolución DIAN
        dian_config.resolucion_numero = request.POST.get('resolucion_numero', '').strip()
        dian_config.resolucion_fecha = request.POST.get('resolucion_fecha')
        dian_config.resolucion_prefijo = request.POST.get('resolucion_prefijo', 'FE').strip()
        dian_config.resolucion_numero_inicio = int(request.POST.get('resolucion_numero_inicio', 1))
        dian_config.resolucion_numero_fin = int(request.POST.get('resolucion_numero_fin', 1000))
        
        # Estado
        dian_config.is_active = request.POST.get('is_active') == 'on'
        dian_config.habilitado_dian = request.POST.get('habilitado_dian') == 'on'
        
        dian_config.configurado_por = request.user
        dian_config.save()
        
        messages.success(request, '✅ Configuración DIAN actualizada correctamente')
        return redirect('billing:dian_config')
    
    context = {
        'dian_config': dian_config,
        'can_use_invoicing': can_use,
        'plan_message': message,
        'organization': organization,
        'subscription': organization.subscriptions.filter(is_active=True).first(),
    }
    
    return render(request, 'billing/dian_config.html', context)


@login_required
def invoice_list(request):
    """Lista de facturas electrónicas"""
    # Obtener organización del usuario
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    organization = org_member.organization
    
    # Verificar acceso
    can_use, message = Invoice.puede_crear_factura_electronica(organization)
    
    # Filtros
    estado_pago = request.GET.get('estado_pago', '')
    estado_dian = request.GET.get('estado_dian', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    
    invoices = Invoice.objects.filter(organization=organization).select_related('patient')
    
    if estado_pago:
        invoices = invoices.filter(estado_pago=estado_pago)
    if estado_dian:
        invoices = invoices.filter(estado_dian=estado_dian)
    if fecha_inicio:
        invoices = invoices.filter(created_at__gte=fecha_inicio)
    if fecha_fin:
        invoices = invoices.filter(created_at__lte=fecha_fin)
    
    # Estadísticas
    stats = {
        'total_facturas': invoices.count(),
        'total_monto': invoices.aggregate(total=Sum('total'))['total'] or Decimal('0'),
        'total_pagado': invoices.aggregate(total=Sum('total_pagado'))['total'] or Decimal('0'),
        'pendiente_pago': invoices.filter(estado_pago__in=['unpaid', 'partial']).count(),
        'pendiente_dian': invoices.filter(estado_dian='draft').count(),
    }
    
    # Límite mensual (si aplica)
    subscription = organization.subscriptions.filter(is_active=True).first()
    plan = subscription.plan if subscription else None
    
    if plan and plan.allow_electronic_invoicing and plan.max_invoices_month > 0:
        # Contar facturas del mes actual
        inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        facturas_mes = Invoice.objects.filter(
            organization=organization,
            created_at__gte=inicio_mes
        ).count()
        
        stats['facturas_mes'] = facturas_mes
        stats['limite_mes'] = plan.max_invoices_month
        stats['restantes_mes'] = plan.max_invoices_month - facturas_mes
    else:
        stats['facturas_mes'] = None
        stats['limite_mes'] = 0
        stats['restantes_mes'] = None
    
    context = {
        'invoices': invoices[:100],  # Limitar a 100 registros
        'stats': stats,
        'can_create': can_use,
        'plan_message': message,
        'filters': {
            'estado_pago': estado_pago,
            'estado_dian': estado_dian,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
        }
    }
    
    return render(request, 'billing/invoice_list.html', context)


@login_required
def invoice_create(request):
    """Crear nueva factura electrónica"""
    # Obtener organización del usuario
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    organization = org_member.organization
    
    # Verificar límites del plan
    can_create, message = Invoice.puede_crear_factura_electronica(organization)
    
    if not can_create:
        messages.error(request, message)
        return redirect('billing:invoice_list')
    
    if request.method == 'POST':
        # TODO: Implementar creación de factura
        messages.info(request, '🚧 Función en desarrollo - Fase 1')
        return redirect('billing:invoice_list')
    
    # Obtener pacientes para el formulario
    patients = Patient.objects.filter(organization=organization)[:100]
    
    context = {
        'patients': patients,
        'can_create': can_create,
        'plan_message': message,
    }
    
    return render(request, 'billing/invoice_form.html', context)

