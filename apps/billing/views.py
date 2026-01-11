from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Q, Sum
from datetime import datetime, timedelta
from decimal import Decimal

from apps.organizations.models import Organization, OrganizationMember
from apps.patients.models import Patient
from .models import DianConfiguration, Invoice, InvoiceItem, Payment, Supplier, InvoiceProduct, InvoiceConfiguration


def get_user_organization(request):
    """Helper para obtener la organización del usuario desde el middleware"""
    organization = request.organization if hasattr(request, 'organization') else None
    
    if not organization:
        org_member = OrganizationMember.objects.filter(
            user=request.user,
            is_active=True,
            organization__is_active=True
        ).first()
        if org_member:
            organization = org_member.organization
    
    return organization


@login_required
def dian_configuration_view(request):
    """
    Vista para configurar los parámetros de la DIAN.
    Solo permite UNA configuración por organización que siempre se muestra para actualizar.
    Solo para usuarios con plan Profesional o Empresarial.
    """
    try:
        # Obtener organización del usuario
        organization = get_user_organization(request)
        if not organization:
            messages.error(request, 'No tienes una organización asignada')
            return redirect('dashboard:home')
        
        # Verificar si el plan permite facturación electrónica
        can_use, message = Invoice.puede_crear_factura_electronica(organization)
        
        # Siempre obtener o crear configuración DIAN (una sola por organización)
        dian_config, created = DianConfiguration.objects.get_or_create(
            organization=organization,
            defaults={
                'configurado_por': request.user
            }
        )
        
        if created:
            messages.info(request, 'Se ha creado la configuración DIAN para tu organización. Completa los datos requeridos.')
        
        if request.method == 'POST':
            # Validar que puede usar facturación
            if not can_use:
                messages.error(request, message)
                return redirect('billing:dian_configuration')
            
            # Actualizar campos básicos
            dian_config.razon_social = request.POST.get('razon_social', '').strip()
            dian_config.tipo_documento = request.POST.get('tipo_documento', 'NIT')
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
            return redirect('billing:dian_configuration')
        
        context = {
            'dian_config': dian_config,
            'can_use_invoicing': can_use,
            'plan_message': message,
            'organization': organization,
            'subscription': organization.subscriptions.filter(is_active=True).first(),
        }
        
        return render(request, 'billing/dian_config.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al cargar configuración DIAN: {str(e)}')
        return redirect('dashboard:home')


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


def invoice_create(request):
    """Crear nueva factura electrónica"""
    from django.utils import timezone
    
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
        try:
            import json
            from decimal import Decimal
            from django.utils import timezone
            from django.db import transaction
            
            # Obtener datos del formulario
            patient_id = request.POST.get('patient_id')
            numero_documento = request.POST.get('numero_documento', '')
            nombre_cliente = request.POST.get('nombre_cliente', '')
            email_cliente = request.POST.get('email_cliente', '')
            telefono_cliente = request.POST.get('telefono_cliente', '')
            forma_pago = request.POST.get('forma_pago', '1')
            medio_pago = request.POST.get('medio_pago', '10')
            
            # NUEVO: Tipo de facturación (electrónica o normal)
            es_factura_electronica = request.POST.get('es_factura_electronica') == 'on'
            requiere_envio_dian = request.POST.get('requiere_envio_dian') == 'on'
            
            # Items
            items_data = json.loads(request.POST.get('items', '[]'))
            
            # Pagos
            pagos_data = json.loads(request.POST.get('pagos', '[]'))
            
            if not patient_id:
                messages.error(request, 'Debe seleccionar un paciente')
                return redirect('billing:invoice_create')
            
            if not items_data:
                messages.error(request, 'Debe agregar al menos un item a la factura')
                return redirect('billing:invoice_create')
            
            patient = Patient.objects.get(id=patient_id, organization=organization)
            
            # Obtener configuración para numeración
            config = InvoiceConfiguration.get_config(organization)
            
            # Calcular totales
            subtotal = Decimal('0')
            total_descuento = Decimal('0')
            total_iva = Decimal('0')
            iva_0 = Decimal('0')
            iva_5 = Decimal('0')
            iva_19 = Decimal('0')
            
            for item in items_data:
                cantidad = Decimal(str(item.get('cantidad', 1)))
                precio = Decimal(str(item.get('precio', 0)))
                descuento_pct = Decimal(str(item.get('descuento', 0)))
                iva_pct = Decimal(str(item.get('iva', 0)))
                
                # Subtotal del item
                item_subtotal = cantidad * precio
                subtotal += item_subtotal
                
                # Descuento del item
                item_descuento = item_subtotal * (descuento_pct / 100)
                total_descuento += item_descuento
                
                # Base imponible (subtotal - descuento)
                item_base = item_subtotal - item_descuento
                
                # IVA sobre la base imponible
                item_iva = item_base * (iva_pct / 100)
                total_iva += item_iva
                
                if iva_pct == 0:
                    iva_0 += item_iva
                elif iva_pct == 5:
                    iva_5 += item_iva
                elif iva_pct == 19:
                    iva_19 += item_iva
            
            # Base imponible = subtotal - descuento
            base_imponible = subtotal - total_descuento
            total = base_imponible + total_iva
            
            # Calcular total pagado
            total_pagado = Decimal('0')
            for pago in pagos_data:
                total_pagado += Decimal(str(pago.get('monto', 0)))
            
            saldo_pendiente = total - total_pagado
            
            # Determinar estado de pago
            if total_pagado >= total:
                estado_pago = 'paid'
            elif total_pagado > 0:
                estado_pago = 'partial'
            else:
                estado_pago = 'unpaid'
            
            # TODO: Iniciar transacción atómica ANTES de generar el número
            with transaction.atomic():
                # Determinar prefijo y número según tipo de factura
                if es_factura_electronica:
                    # Factura Electrónica: Usar consecutivo DIAN
                    try:
                        dian_config = DianConfiguration.objects.get(organization=organization)
                        numero_dian = dian_config.get_next_numero(es_factura_electronica=True)
                        prefijo = dian_config.resolucion_prefijo
                        numero_completo = dian_config.get_numero_completo(numero_dian)
                        nuevo_numero = numero_dian
                    except DianConfiguration.DoesNotExist:
                        messages.error(request, '❌ No hay configuración DIAN. Configure primero la facturación electrónica.')
                        return redirect('billing:dian_configuration')
                    except ValueError as e:
                        messages.error(request, f'❌ Error en consecutivo DIAN: {str(e)}')
                        return redirect('billing:invoice_create')
                else:
                    # Factura Normal/Interna: Usar consecutivo interno
                    # Generar número de factura con lock para evitar duplicados
                    # Usar select_for_update() para bloquear la última factura durante la transacción
                    last_invoice = Invoice.objects.filter(
                        organization=organization,
                        es_factura_electronica=False  # Solo contar facturas normales
                    ).select_for_update().order_by('-numero').first()
                    
                    nuevo_numero = (last_invoice.numero + 1) if last_invoice else 1
                    prefijo = config.prefijo_factura
                    numero_completo = f"{prefijo}-{str(nuevo_numero).zfill(5)}"
                    
                    # Verificar que el número no exista (doble verificación)
                    while Invoice.objects.filter(organization=organization, numero_completo=numero_completo).exists():
                        nuevo_numero += 1
                        numero_completo = f"{prefijo}-{str(nuevo_numero).zfill(5)}"
                
                # Crear factura
                invoice = Invoice.objects.create(
                    organization=organization,
                    prefijo=prefijo,
                    numero=nuevo_numero,
                    numero_completo=numero_completo,
                    tipo='product',
                    es_factura_electronica=es_factura_electronica,
                    requiere_envio_dian=requiere_envio_dian,
                    patient=patient,
                    cliente_tipo_documento=patient.identification_type,
                    cliente_numero_documento=numero_documento or patient.identification_number,
                    cliente_nombre=nombre_cliente or f"{patient.first_name} {patient.last_name}",
                    cliente_email=email_cliente or patient.email,
                    cliente_telefono=telefono_cliente or patient.phone,
                    fecha_emision=timezone.now(),
                    forma_pago=forma_pago,
                    medio_pago=medio_pago,
                    subtotal=subtotal,
                    descuento=total_descuento,
                    base_imponible=base_imponible,
                    iva_0=iva_0,
                    iva_5=iva_5,
                    iva_19=iva_19,
                    total_iva=total_iva,
                    total=total,
                    total_pagado=total_pagado,
                    saldo_pendiente=saldo_pendiente,
                    estado_pago=estado_pago,
                    estado_dian='draft',
                    creado_por=request.user
                )
                
                # Crear items
                from apps.billing.models import InvoiceItem
                for index, item_data in enumerate(items_data, start=1):
                    descripcion = item_data.get('descripcion', '')
                    cantidad = Decimal(str(item_data.get('cantidad', 1)))
                    precio = Decimal(str(item_data.get('precio', 0)))
                    descuento_pct = Decimal(str(item_data.get('descuento', 0)))
                    iva_pct = Decimal(str(item_data.get('iva', 0)))
                    
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        numero_linea=index,
                        tipo='product',
                        codigo=f'ITEM-{index:03d}',
                        descripcion=descripcion,
                        cantidad=cantidad,
                        valor_unitario=precio,
                        descuento_porcentaje=descuento_pct,
                        iva_porcentaje=iva_pct
                    )
                
                # Crear pagos si hay
                from apps.billing.models import Payment
                payment_counter = 1
                
                # Mapeo de métodos de pago del formulario a los valores del modelo
                metodo_map = {
                    'Efectivo': 'cash',
                    'Tarjeta': 'card_credit',
                    'Transferencia': 'transfer',
                    'Cheque': 'check',
                    'Crédito': 'other',
                }
                
                for pago_data in pagos_data:
                    metodo_form = pago_data.get('metodo', 'Efectivo')
                    metodo_db = metodo_map.get(metodo_form, 'cash')
                    
                    # Generar número de pago único
                    ultimo_pago = Payment.objects.filter(
                        organization=organization,
                        payment_number__startswith='PAY-'
                    ).order_by('-payment_number').first()
                    
                    if ultimo_pago:
                        try:
                            ultimo_num = int(ultimo_pago.payment_number.split('-')[1])
                            nuevo_num = ultimo_num + 1
                        except (IndexError, ValueError):
                            nuevo_num = 1
                    else:
                        nuevo_num = 1
                    
                    # Asegurar que el número sea único
                    payment_number = f"PAY-{nuevo_num:05d}"
                    while Payment.objects.filter(payment_number=payment_number).exists():
                        nuevo_num += 1
                        payment_number = f"PAY-{nuevo_num:05d}"
                    
                    Payment.objects.create(
                        organization=organization,
                        invoice=invoice,
                        payment_number=payment_number,
                        amount=Decimal(str(pago_data.get('monto', 0))),
                        payment_method=metodo_db,
                        reference_number=pago_data.get('referencia', ''),
                        payment_date=timezone.now(),
                        processed_by=request.user
                    )
                    payment_counter += 1
                
                # ==================== CREAR VENTA EN MÓDULO DE VENTAS ====================
                # Sincronizar con el panel de ventas si el módulo está activo
                try:
                    from apps.sales.models import Sale, SaleItem
                    
                    # Generar número de venta
                    last_sale = Sale.objects.filter(organization=organization).order_by('-id').first()
                    sale_number = f"VT-{(last_sale.id + 1):05d}" if last_sale else "VT-00001"
                    
                    # Mapear método de pago a formato de ventas
                    sale_payment_method = 'cash'  # Por defecto
                    if pagos_data:
                        primer_pago = pagos_data[0].get('metodo', 'Efectivo')
                        if primer_pago == 'Tarjeta':
                            sale_payment_method = 'card'
                        elif primer_pago == 'Transferencia':
                            sale_payment_method = 'transfer'
                        elif len(pagos_data) > 1:
                            sale_payment_method = 'mixed'
                    
                    # Crear la venta
                    sale = Sale.objects.create(
                        organization=organization,
                        sale_number=sale_number,
                        patient=patient,
                        sold_by=request.user,
                        payment_method=sale_payment_method,
                        status='completed',
                        subtotal=subtotal,
                        discount=total_descuento,
                        tax=total_iva,
                        total=total,
                        notes=f'Generada desde factura {invoice.numero_completo}'
                    )
                    
                    # Vincular factura con venta
                    invoice.sale = sale
                    invoice.save()
                    
                except Exception as e:
                    # Si falla la creación de venta, solo registrar pero no detener
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f'No se pudo crear venta para factura {invoice.numero_completo}: {str(e)}')
                
                # Procesar facturación electrónica si cumple condiciones
                # 1. Es factura electrónica
                # 2. Usuario solicitó envío a DIAN
                # 3. Está completamente pagada
                if es_factura_electronica and requiere_envio_dian and config.facturacion_electronica_activa:
                    # Verificar si está completamente pagada
                    puede_enviar, mensaje_envio = invoice.puede_enviar_dian()
                    
                    if puede_enviar:
                        try:
                            from apps.billing.services import FacturacionElectronicaService
                            
                            # Usar mock si estamos en desarrollo o no hay certificado
                            usar_mock = not config.certificado_digital or config.ambiente == 'pruebas'
                            
                            servicio = FacturacionElectronicaService(
                                invoice=invoice,
                                usar_mock=usar_mock
                            )
                            
                            exito, resultado = servicio.procesar_factura_completa()
                            
                            if exito:
                                messages.success(
                                    request,
                                    f'✅ Factura Electrónica {invoice.numero_completo} creada y enviada a DIAN exitosamente'
                                )
                                if usar_mock:
                                    messages.info(request, '⚠️ Procesada en modo PRUEBA (sin envío real a DIAN)')
                                else:
                                    messages.success(request, f'📄 CUFE: {invoice.cufe[:30]}...')
                            else:
                                messages.warning(
                                    request,
                                    f'⚠️ Factura {invoice.numero_completo} creada pero hubo errores al enviar a DIAN'
                                )
                                messages.error(request, f"Error: {resultado.get('mensaje', 'Error desconocido')}")
                                
                        except Exception as e:
                            messages.warning(
                                request,
                                f'⚠️ Factura {invoice.numero_completo} creada pero no se pudo enviar a DIAN: {str(e)}'
                            )
                    else:
                        # No se puede enviar a DIAN aún
                        messages.success(request, f'✅ Factura Electrónica {invoice.numero_completo} creada exitosamente')
                        messages.info(request, f'ℹ️ {mensaje_envio}. Podrá enviarse a DIAN cuando esté completamente pagada.')
                        
                elif es_factura_electronica and not requiere_envio_dian:
                    # Es electrónica pero no se solicitó envío inmediato
                    messages.success(request, f'✅ Factura Electrónica {invoice.numero_completo} creada exitosamente')
                    messages.info(request, 'ℹ️ No se solicitó envío a DIAN. Puede enviarla posteriormente.')
                    
                else:
                    # Factura normal/interna
                    if es_factura_electronica:
                        tipo_factura = "Factura Electrónica"
                    else:
                        tipo_factura = "Factura"
                    messages.success(request, f'✅ {tipo_factura} {invoice.numero_completo} creada exitosamente')
                    if not es_factura_electronica:
                        messages.info(request, 'ℹ️ Esta es una factura normal/interna, no consume consecutivo DIAN')
                
                # Registrar en auditoría
                from apps.dashboard.audit_utils import log_action
                log_action(
                    user=request.user,
                    organization=organization,
                    action='invoice_create',
                    description=f'Creó la factura {invoice.numero_completo}',
                    content_type='Invoice',
                    object_id=invoice.id,
                    metadata={'numero': invoice.numero_completo, 'total': str(invoice.total)},
                    request=request
                )
                
                return redirect('billing:invoice_detail', invoice_id=invoice.id)
                
        except Patient.DoesNotExist:
            messages.error(request, 'Paciente no encontrado')
            return redirect('billing:invoice_create')
        except Exception as e:
            messages.error(request, f'Error creando factura: {str(e)}')
            return redirect('billing:invoice_create')
    
    # Obtener pacientes para el formulario
    patients = Patient.objects.filter(organization=organization)[:100]
    
    # Obtener productos activos para el selector
    products = InvoiceProduct.objects.filter(
        organization=organization,
        is_active=True
    ).order_by('nombre')[:200]
    
    # Obtener configuración de facturación
    config = InvoiceConfiguration.get_config(organization)
    
    context = {
        'patients': patients,
        'products': products,
        'can_create': can_create,
        'plan_message': message,
        'config': config,
        'today': timezone.localtime(timezone.now()).date(),
    }
    
    return render(request, 'billing/invoice_form.html', context)


# =====================================================
# VISTAS PARA PROVEEDORES
# =====================================================

def supplier_list(request):
    """Lista de proveedores"""
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    organization = org_member.organization
    
    # Filtros
    categoria = request.GET.get('categoria', '')
    search = request.GET.get('search', '')
    
    suppliers = Supplier.objects.filter(organization=organization)
    
    if categoria:
        suppliers = suppliers.filter(categoria=categoria)
    if search:
        suppliers = suppliers.filter(
            Q(nombre__icontains=search) | 
            Q(numero_documento__icontains=search) |
            Q(nombre_comercial__icontains=search)
        )
    
    suppliers = suppliers.order_by('-created_at')
    
    context = {
        'suppliers': suppliers,
        'search': search,
        'categoria': categoria,
    }
    
    return render(request, 'billing/supplier_list.html', context)


def supplier_create(request):
    """Crear nuevo proveedor"""
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    organization = org_member.organization
    
    if request.method == 'POST':
        try:
            supplier = Supplier.objects.create(
                organization=organization,
                codigo=request.POST.get('codigo').strip(),
                nombre=request.POST.get('nombre').strip(),
                nombre_comercial=request.POST.get('nombre_comercial', '').strip(),
                tipo_documento=request.POST.get('tipo_documento', 'NIT'),
                numero_documento=request.POST.get('numero_documento').strip(),
                categoria=request.POST.get('categoria', ''),
                email=request.POST.get('email', '').strip(),
                telefono=request.POST.get('telefono', '').strip(),
                celular=request.POST.get('celular', '').strip(),
                sitio_web=request.POST.get('sitio_web', '').strip(),
                direccion=request.POST.get('direccion', '').strip(),
                ciudad=request.POST.get('ciudad', '').strip(),
                pais=request.POST.get('pais', 'Colombia'),
                nombre_contacto=request.POST.get('nombre_contacto', '').strip(),
                cargo_contacto=request.POST.get('cargo_contacto', '').strip(),
                email_contacto=request.POST.get('email_contacto', '').strip(),
                telefono_contacto=request.POST.get('telefono_contacto', '').strip(),
                condiciones_pago=request.POST.get('condiciones_pago', '').strip(),
                notas=request.POST.get('notas', '').strip(),
            )
            messages.success(request, f'✅ Proveedor {supplier.nombre} creado exitosamente')
            return redirect('billing:supplier_list')
        except Exception as e:
            messages.error(request, f'❌ Error al crear proveedor: {str(e)}')
    
    # Obtener categorías personalizadas
    from .models import SupplierCategory
    categorias_db = SupplierCategory.objects.filter(organization=organization, activo=True)
    
    # Categorías por defecto
    categorias_default = [
        ('MONTURAS', 'Monturas'),
        ('LENTES', 'Lentes'),
        ('ACCESORIOS', 'Accesorios'),
        ('EQUIPOS', 'Equipos Ópticos'),
        ('INSUMOS', 'Insumos'),
        ('OTROS', 'Otros'),
    ]
    
    context = {
        'organization': organization,
        'categorias_db': categorias_db,
        'categorias_default': categorias_default,
    }
    
    return render(request, 'billing/supplier_form.html', context)


def supplier_edit(request, supplier_id):
    """Editar proveedor"""
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    organization = org_member.organization
    supplier = get_object_or_404(Supplier, id=supplier_id, organization=organization)
    
    if request.method == 'POST':
        try:
            supplier.codigo = request.POST.get('codigo').strip()
            supplier.nombre = request.POST.get('nombre').strip()
            supplier.nombre_comercial = request.POST.get('nombre_comercial', '').strip()
            supplier.tipo_documento = request.POST.get('tipo_documento', 'NIT')
            supplier.numero_documento = request.POST.get('numero_documento').strip()
            supplier.categoria = request.POST.get('categoria', '')
            supplier.email = request.POST.get('email', '').strip()
            supplier.telefono = request.POST.get('telefono', '').strip()
            supplier.celular = request.POST.get('celular', '').strip()
            supplier.sitio_web = request.POST.get('sitio_web', '').strip()
            supplier.direccion = request.POST.get('direccion', '').strip()
            supplier.ciudad = request.POST.get('ciudad', '').strip()
            supplier.pais = request.POST.get('pais', 'Colombia')
            supplier.nombre_contacto = request.POST.get('nombre_contacto', '').strip()
            supplier.cargo_contacto = request.POST.get('cargo_contacto', '').strip()
            supplier.email_contacto = request.POST.get('email_contacto', '').strip()
            supplier.telefono_contacto = request.POST.get('telefono_contacto', '').strip()
            supplier.condiciones_pago = request.POST.get('condiciones_pago', '').strip()
            supplier.notas = request.POST.get('notas', '').strip()
            supplier.is_active = request.POST.get('is_active') == 'on'
            supplier.save()
            
            messages.success(request, f'✅ Proveedor {supplier.nombre} actualizado exitosamente')
            return redirect('billing:supplier_list')
        except Exception as e:
            messages.error(request, f'❌ Error al actualizar proveedor: {str(e)}')
    
    # Obtener categorías personalizadas
    from .models import SupplierCategory
    categorias_db = SupplierCategory.objects.filter(organization=organization, activo=True)
    
    # Categorías por defecto
    categorias_default = [
        ('MONTURAS', 'Monturas'),
        ('LENTES', 'Lentes'),
        ('ACCESORIOS', 'Accesorios'),
        ('EQUIPOS', 'Equipos Ópticos'),
        ('INSUMOS', 'Insumos'),
        ('OTROS', 'Otros'),
    ]
    
    context = {
        'supplier': supplier,
        'organization': organization,
        'categorias_db': categorias_db,
        'categorias_default': categorias_default,
    }
    
    return render(request, 'billing/supplier_form.html', context)


@login_required
def supplier_categoria_create(request):
    """Crear nueva categoría de proveedor (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        return JsonResponse({'success': False, 'error': 'No tienes una organización asignada'}, status=403)
    
    organization = org_member.organization
    
    try:
        from .models import SupplierCategory
        
        codigo = request.POST.get('codigo', '').strip().upper()
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        if not codigo or not nombre:
            return JsonResponse({'success': False, 'error': 'Código y nombre son requeridos'})
        
        # Verificar si ya existe
        if SupplierCategory.objects.filter(organization=organization, codigo=codigo).exists():
            return JsonResponse({'success': False, 'error': f'Ya existe una categoría con el código {codigo}'})
        
        # Crear categoría
        categoria = SupplierCategory.objects.create(
            organization=organization,
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
            activo=True
        )
        
        return JsonResponse({
            'success': True,
            'categoria': {
                'id': categoria.id,
                'codigo': categoria.codigo,
                'nombre': categoria.nombre,
                'descripcion': categoria.descripcion
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def supplier_create_ajax(request):
    """Crear nuevo proveedor (AJAX) desde formulario de productos"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        return JsonResponse({'success': False, 'error': 'No tienes una organización asignada'}, status=403)
    
    organization = org_member.organization
    
    try:
        import json
        data = json.loads(request.body)
        
        tipo_documento = data.get('tipo_documento', 'NIT').strip()
        numero_documento = data.get('numero_documento', '').strip()
        nombre = data.get('nombre', '').strip()
        nombre_comercial = data.get('nombre_comercial', '').strip()
        telefono = data.get('telefono', '').strip()
        email = data.get('email', '').strip()
        
        if not numero_documento or not nombre:
            return JsonResponse({'success': False, 'error': 'Número de documento y nombre son requeridos'})
        
        # Verificar si ya existe un proveedor con ese documento
        if Supplier.objects.filter(organization=organization, numero_documento=numero_documento).exists():
            return JsonResponse({'success': False, 'error': f'Ya existe un proveedor con el documento {numero_documento}'})
        
        # Generar código automático
        codigo = f"PROV{Supplier.objects.filter(organization=organization).count() + 1:04d}"
        
        # Crear proveedor
        supplier = Supplier.objects.create(
            organization=organization,
            codigo=codigo,
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            nombre=nombre,
            nombre_comercial=nombre_comercial or nombre,
            telefono=telefono,
            email=email,
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'supplier': {
                'id': supplier.id,
                'nombre': supplier.nombre,
                'numero_documento': supplier.numero_documento,
                'tipo_documento': supplier.tipo_documento
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def product_create_ajax(request):
    """Crear nuevo producto (AJAX) desde formulario de facturas"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        return JsonResponse({'success': False, 'error': 'No tienes una organización asignada'}, status=403)
    
    organization = org_member.organization
    
    try:
        import json
        data = json.loads(request.body)
        
        codigo = data.get('codigo', '').strip()
        nombre = data.get('nombre', '').strip()
        categoria = data.get('categoria', 'OTROS').strip()
        marca = data.get('marca', '').strip()
        modelo = data.get('modelo', '').strip()
        precio_venta = data.get('precio_venta', 0)
        porcentaje_iva = data.get('porcentaje_iva', 0)
        stock_actual = data.get('stock_actual', 0)
        
        if not codigo or not nombre:
            return JsonResponse({'success': False, 'error': 'Código y nombre son requeridos'})
        
        # Verificar si ya existe un producto con ese código
        if InvoiceProduct.objects.filter(organization=organization, codigo=codigo).exists():
            return JsonResponse({'success': False, 'error': f'Ya existe un producto con el código {codigo}'})
        
        # Crear producto
        product = InvoiceProduct.objects.create(
            organization=organization,
            codigo=codigo,
            nombre=nombre,
            categoria=categoria,
            marca=marca,
            modelo=modelo,
            precio_venta=precio_venta,
            porcentaje_iva=porcentaje_iva,
            stock_actual=stock_actual,
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'product': {
                'id': product.id,
                'codigo': product.codigo,
                'nombre': product.nombre,
                'marca': product.marca or '',
                'modelo': product.modelo or '',
                'precio_venta': str(product.precio_venta),
                'porcentaje_iva': str(product.porcentaje_iva),
                'stock_actual': product.stock_actual
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def supplier_delete(request, supplier_id):
    """Eliminar proveedor"""
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    organization = org_member.organization
    supplier = get_object_or_404(Supplier, id=supplier_id, organization=organization)
    
    # Verificar si tiene productos asociados
    if supplier.products.exists():
        messages.error(request, f'❌ No se puede eliminar el proveedor {supplier.nombre} porque tiene productos asociados')
        return redirect('billing:supplier_list')
    
    nombre = supplier.nombre
    supplier.delete()
    messages.success(request, f'✅ Proveedor {nombre} eliminado exitosamente')
    return redirect('billing:supplier_list')


# =====================================================
# VISTAS PARA PRODUCTOS
# =====================================================

def product_list(request):
    """Lista de productos"""
    organization = get_user_organization(request)
    if not organization:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    # Filtros
    categoria = request.GET.get('categoria', '')
    supplier_id = request.GET.get('supplier', '')
    search = request.GET.get('search', '')
    stock = request.GET.get('stock', '')  # 'bajo', 'agotado'
    
    products = InvoiceProduct.objects.filter(organization=organization).select_related('supplier')
    
    if categoria:
        products = products.filter(categoria=categoria)
    if supplier_id:
        products = products.filter(supplier_id=supplier_id)
    if search:
        products = products.filter(
            Q(nombre__icontains=search) | 
            Q(codigo__icontains=search) |
            Q(marca__icontains=search) |
            Q(modelo__icontains=search)
        )
    if stock == 'bajo':
        # Stock bajo = stock_actual <= stock_minimo
        products = products.filter(tipo_inventario='FISICO').extra(
            where=['stock_actual <= stock_minimo']
        )
    elif stock == 'agotado':
        products = products.filter(tipo_inventario='FISICO', stock_actual=0)
    
    products = products.order_by('-created_at')
    
    # Proveedores para el filtro
    suppliers = Supplier.objects.filter(organization=organization, is_active=True)
    
    # Estadísticas
    stats = {
        'total_productos': InvoiceProduct.objects.filter(organization=organization, is_active=True).count(),
        'stock_bajo': InvoiceProduct.objects.filter(
            organization=organization,
            tipo_inventario='FISICO',
            is_active=True
        ).extra(where=['stock_actual <= stock_minimo']).count(),
        'agotados': InvoiceProduct.objects.filter(
            organization=organization,
            tipo_inventario='FISICO',
            stock_actual=0,
            is_active=True
        ).count(),
        'valor_inventario': sum([p.valor_inventario for p in InvoiceProduct.objects.filter(
            organization=organization,
            tipo_inventario='FISICO',
            is_active=True
        )]),
    }
    
    context = {
        'products': products[:100],
        'suppliers': suppliers,
        'search': search,
        'categoria': categoria,
        'supplier_id': supplier_id,
        'stock': stock,
        'stats': stats,
    }
    
    return render(request, 'billing/product_list.html', context)


def product_create(request):
    """Crear nuevo producto"""
    organization = get_user_organization(request)
    if not organization:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        try:
            # Obtener supplier si se proporcionó
            supplier = None
            supplier_id = request.POST.get('supplier')
            if supplier_id:
                supplier = Supplier.objects.get(id=supplier_id, organization=organization)
            
            # Crear producto
            product = InvoiceProduct(
                organization=organization,
                codigo=request.POST.get('codigo').strip(),
                nombre=request.POST.get('nombre').strip(),
                descripcion=request.POST.get('descripcion', '').strip(),
                categoria=request.POST.get('categoria', 'OTROS'),
                subcategoria=request.POST.get('subcategoria', '').strip(),
                supplier=supplier,
                marca=request.POST.get('marca', '').strip(),
                modelo=request.POST.get('modelo', '').strip(),
                codigo_barras=request.POST.get('codigo_barras', '').strip(),
                precio_compra=Decimal(request.POST.get('precio_compra', '0')),
                precio_venta=Decimal(request.POST.get('precio_venta', '0')),
                aplica_iva=request.POST.get('aplica_iva') == 'on',
                porcentaje_iva=Decimal(request.POST.get('porcentaje_iva', '19')),
                tipo_inventario=request.POST.get('tipo_inventario', 'FISICO'),
                stock_actual=int(request.POST.get('stock_actual', 0)),
                stock_minimo=int(request.POST.get('stock_minimo', 5)),
                stock_maximo=int(request.POST.get('stock_maximo', 100)),
                ubicacion_fisica=request.POST.get('ubicacion_fisica', '').strip(),
            )
            
            # Manejar imágenes
            if 'imagen_principal' in request.FILES:
                product.imagen_principal = request.FILES['imagen_principal']
            if 'imagen_2' in request.FILES:
                product.imagen_2 = request.FILES['imagen_2']
            if 'imagen_3' in request.FILES:
                product.imagen_3 = request.FILES['imagen_3']
            if 'imagen_4' in request.FILES:
                product.imagen_4 = request.FILES['imagen_4']
            
            product.save()
            
            # Registrar en auditoría
            from apps.dashboard.audit_utils import log_action
            log_action(
                user=request.user,
                organization=organization,
                action='product_create',
                description=f'Creó el producto: {product.nombre}',
                content_type='InvoiceProduct',
                object_id=product.id,
                metadata={'nombre': product.nombre, 'codigo': product.codigo},
                request=request
            )
            
            messages.success(request, f'✅ Producto {product.nombre} creado exitosamente')
            return redirect('billing:product_list')
        except Exception as e:
            messages.error(request, f'❌ Error al crear producto: {str(e)}')
    
    suppliers = Supplier.objects.filter(organization=organization, is_active=True)
    
    context = {
        'organization': organization,
        'suppliers': suppliers,
    }
    
    return render(request, 'billing/product_form.html', context)


def product_edit(request, product_id):
    """Editar producto"""
    organization = get_user_organization(request)
    if not organization:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    product = get_object_or_404(InvoiceProduct, id=product_id, organization=organization)
    
    if request.method == 'POST':
        try:
            # Obtener supplier si se proporcionó
            supplier = None
            supplier_id = request.POST.get('supplier')
            if supplier_id:
                supplier = Supplier.objects.get(id=supplier_id, organization=organization)
            
            product.codigo = request.POST.get('codigo').strip()
            product.nombre = request.POST.get('nombre').strip()
            product.descripcion = request.POST.get('descripcion', '').strip()
            product.categoria = request.POST.get('categoria', 'OTROS')
            product.subcategoria = request.POST.get('subcategoria', '').strip()
            product.supplier = supplier
            product.marca = request.POST.get('marca', '').strip()
            product.modelo = request.POST.get('modelo', '').strip()
            product.codigo_barras = request.POST.get('codigo_barras', '').strip()
            product.precio_compra = Decimal(request.POST.get('precio_compra', '0'))
            product.precio_venta = Decimal(request.POST.get('precio_venta', '0'))
            product.aplica_iva = request.POST.get('aplica_iva') == 'on'
            product.porcentaje_iva = Decimal(request.POST.get('porcentaje_iva', '19'))
            product.tipo_inventario = request.POST.get('tipo_inventario', 'FISICO')
            product.stock_actual = int(request.POST.get('stock_actual', 0))
            product.stock_minimo = int(request.POST.get('stock_minimo', 5))
            product.stock_maximo = int(request.POST.get('stock_maximo', 100))
            product.ubicacion_fisica = request.POST.get('ubicacion_fisica', '').strip()
            product.is_active = request.POST.get('is_active') == 'on'
            
            # Manejar imágenes
            if 'imagen_principal' in request.FILES:
                product.imagen_principal = request.FILES['imagen_principal']
            if 'imagen_2' in request.FILES:
                product.imagen_2 = request.FILES['imagen_2']
            if 'imagen_3' in request.FILES:
                product.imagen_3 = request.FILES['imagen_3']
            if 'imagen_4' in request.FILES:
                product.imagen_4 = request.FILES['imagen_4']
            
            product.save()
            
            # Registrar en auditoría
            from apps.dashboard.audit_utils import log_action
            log_action(
                user=request.user,
                organization=organization,
                action='product_edit',
                description=f'Editó el producto: {product.nombre}',
                content_type='InvoiceProduct',
                object_id=product.id,
                request=request
            )
            
            messages.success(request, f'✅ Producto {product.nombre} actualizado exitosamente')
            return redirect('billing:product_list')
        except Exception as e:
            messages.error(request, f'❌ Error al actualizar producto: {str(e)}')
    
    suppliers = Supplier.objects.filter(organization=organization, is_active=True)
    
    context = {
        'product': product,
        'organization': organization,
        'suppliers': suppliers,
    }
    
    return render(request, 'billing/product_form.html', context)


def product_delete(request, product_id):
    """Eliminar producto"""
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    organization = org_member.organization
    product = get_object_or_404(InvoiceProduct, id=product_id, organization=organization)
    
    nombre = product.nombre
    product_id = product.id
    product.delete()
    
    # Registrar en auditoría
    from apps.dashboard.audit_utils import log_action
    log_action(
        user=request.user,
        organization=organization,
        action='product_delete',
        description=f'Eliminó el producto: {nombre}',
        content_type='InvoiceProduct',
        object_id=product_id,
        request=request
    )
    
    messages.success(request, f'✅ Producto {nombre} eliminado exitosamente')
    return redirect('billing:product_list')


# =====================================================
# VISTA PARA CONFIGURACIÓN DE FACTURA
# =====================================================

@login_required
def invoice_config(request):
    """
    Configuración de facturación.
    Solo permite UNA configuración por organización que siempre se muestra para actualizar.
    """
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    organization = org_member.organization
    
    # Siempre obtener o crear configuración (una sola por organización)
    config = InvoiceConfiguration.get_config(organization)
    
    if request.method == 'POST':
        try:
            # Configuración de IVA
            config.iva_porcentaje = Decimal(request.POST.get('iva_porcentaje', '19'))
            config.aplicar_iva_automatico = request.POST.get('aplicar_iva_automatico') == 'on'
            
            # Configuración de descuentos
            config.descuento_maximo_porcentaje = Decimal(request.POST.get('descuento_maximo_porcentaje', '20'))
            config.permitir_descuento_items = request.POST.get('permitir_descuento_items') == 'on'
            
            # Retenciones
            config.aplicar_retefuente = request.POST.get('aplicar_retefuente') == 'on'
            config.retefuente_porcentaje = Decimal(request.POST.get('retefuente_porcentaje', '2.5'))
            config.aplicar_reteiva = request.POST.get('aplicar_reteiva') == 'on'
            config.reteiva_porcentaje = Decimal(request.POST.get('reteiva_porcentaje', '15'))
            
            # Numeración
            config.prefijo_factura = request.POST.get('prefijo_factura', 'FE').strip()
            
            # Notas y términos
            config.nota_predeterminada = request.POST.get('nota_predeterminada', '').strip()
            config.terminos_condiciones = request.POST.get('terminos_condiciones', '').strip()
            
            # Métodos de pago
            metodos_pago = request.POST.getlist('metodos_pago_disponibles')
            config.metodos_pago_disponibles = metodos_pago if metodos_pago else []
            config.permitir_pagos_parciales = request.POST.get('permitir_pagos_parciales') == 'on'
            
            # Configuración de Email
            config.enviar_email_factura = request.POST.get('enviar_email_factura') == 'on'
            config.email_remitente = request.POST.get('email_remitente', '').strip()
            config.email_asunto = request.POST.get('email_asunto', 'Factura Electrónica #{numero_factura}').strip()
            config.email_mensaje = request.POST.get('email_mensaje', '').strip()
            
            # Configuración SMTP
            config.smtp_host = request.POST.get('smtp_host', 'smtp.gmail.com').strip()
            config.smtp_port = int(request.POST.get('smtp_port', '587'))
            config.smtp_use_tls = request.POST.get('smtp_use_tls') == 'on'
            config.smtp_username = request.POST.get('smtp_username', '').strip()
            smtp_password = request.POST.get('smtp_password', '').strip()
            if smtp_password:  # Solo actualizar si se proporciona una nueva contraseña
                config.smtp_password = smtp_password
            
            # Configuración visual
            if 'logo_factura' in request.FILES:
                config.logo_factura = request.FILES['logo_factura']
            config.color_principal = request.POST.get('color_principal', '#3B82F6').strip()
            
            config.save()
            
            # Debug: Verificar que se guardó
            print(f"DEBUG - Config guardada:")
            print(f"  IVA: {config.iva_porcentaje}%, Auto: {config.aplicar_iva_automatico}")
            print(f"  Descuento máximo: {config.descuento_maximo_porcentaje}%, Permitir: {config.permitir_descuento_items}")
            print(f"  Retefuente: {config.aplicar_retefuente} ({config.retefuente_porcentaje}%)")
            print(f"  ReteIVA: {config.aplicar_reteiva} ({config.reteiva_porcentaje}%)")
            print(f"  Métodos pago: {config.metodos_pago_disponibles}")
            print(f"  Pagos parciales: {config.permitir_pagos_parciales}")
            print(f"  Email remitente: {config.email_remitente}")
            print(f"  SMTP Host: {config.smtp_host}")
            print(f"  SMTP Port: {config.smtp_port}")
            print(f"  SMTP Username: {config.smtp_username}")
            print(f"  SMTP TLS: {config.smtp_use_tls}")
            
            messages.success(request, '✅ Configuración de facturación actualizada exitosamente')
            return redirect('billing:invoice_config')
        except Exception as e:
            messages.error(request, f'❌ Error al actualizar configuración: {str(e)}')
    
    context = {
        'config': config,
        'organization': organization,
    }
    
    return render(request, 'billing/invoice_config.html', context)


def invoice_detail(request, invoice_id):
    """Ver detalle de factura"""
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    organization = org_member.organization
    invoice = get_object_or_404(Invoice, id=invoice_id, organization=organization)
    
    # Obtener items y pagos
    items = invoice.items.all()
    payments = Payment.objects.filter(invoice=invoice).order_by('-payment_date')
    
    context = {
        'invoice': invoice,
        'items': items,
        'payments': payments,
        'organization': organization,
        'org_member': org_member,  # Agregar org_member al contexto
    }
    
    return render(request, 'billing/invoice_detail.html', context)


@login_required
def register_payment(request, invoice_id):
    """Registrar un pago (abono) para una factura"""
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    organization = org_member.organization
    invoice = get_object_or_404(Invoice, id=invoice_id, organization=organization)
    
    if request.method == 'POST':
        # Validar que la factura tenga saldo pendiente
        if invoice.saldo_pendiente <= 0:
            messages.error(request, 'La factura no tiene saldo pendiente')
            return redirect('billing:invoice_detail', invoice_id=invoice.id)
        
        try:
            # Obtener datos del formulario
            amount = Decimal(request.POST.get('amount', '0'))
            payment_method = request.POST.get('payment_method', 'cash')
            reference_number = request.POST.get('reference_number', '').strip()
            bank_name = request.POST.get('bank_name', '').strip()
            notes = request.POST.get('notes', '').strip()
            
            # Validar monto
            if amount <= 0:
                messages.error(request, 'El monto debe ser mayor a cero')
                return redirect('billing:invoice_detail', invoice_id=invoice.id)
            
            if amount > invoice.saldo_pendiente:
                messages.error(request, f'El monto (${amount:,.0f}) no puede ser mayor al saldo pendiente (${invoice.saldo_pendiente:,.0f})')
                return redirect('billing:invoice_detail', invoice_id=invoice.id)
            
            # Determinar tipo de pago
            if amount == invoice.saldo_pendiente:
                tipo_pago = 'full'
            else:
                tipo_pago = 'partial'
            
            # Generar número de pago único
            # Buscar el número más alto existente
            ultimo_pago = Payment.objects.filter(
                organization=organization,
                payment_number__startswith='PAY-'
            ).order_by('-payment_number').first()
            
            if ultimo_pago:
                try:
                    ultimo_num = int(ultimo_pago.payment_number.split('-')[1])
                    nuevo_num = ultimo_num + 1
                except (IndexError, ValueError):
                    nuevo_num = 1
            else:
                nuevo_num = 1
            
            # Asegurar que el número sea único
            payment_number = f"PAY-{nuevo_num:05d}"
            while Payment.objects.filter(payment_number=payment_number).exists():
                nuevo_num += 1
                payment_number = f"PAY-{nuevo_num:05d}"
            
            # Crear el pago
            payment = Payment.objects.create(
                organization=organization,
                payment_number=payment_number,
                invoice=invoice,
                tipo_pago=tipo_pago,
                amount=amount,
                payment_method=payment_method,
                reference_number=reference_number,
                bank_name=bank_name,
                payment_date=timezone.now(),
                status='approved',
                processed_by=request.user,
                notes=notes
            )
            
            # Actualizar saldo de la factura
            invoice.actualizar_saldo()
            
            messages.success(request, f'✓ Pago de ${amount:,.0f} registrado exitosamente. Saldo pendiente: ${invoice.saldo_pendiente:,.0f}')
            return redirect('billing:invoice_detail', invoice_id=invoice.id)
            
        except ValueError:
            messages.error(request, 'Monto inválido')
            return redirect('billing:invoice_detail', invoice_id=invoice.id)
        except Exception as e:
            messages.error(request, f'Error al registrar el pago: {str(e)}')
            return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    return redirect('billing:invoice_detail', invoice_id=invoice.id)


@login_required
@require_http_methods(["POST"])
def send_invoice_to_dian(request, invoice_id):
    """Enviar factura electrónica a DIAN manualmente (cuando esté completamente pagada)"""
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    organization = org_member.organization
    invoice = get_object_or_404(Invoice, id=invoice_id, organization=organization)
    
    # Verificar que sea factura electrónica
    if not invoice.es_factura_electronica:
        messages.error(request, '❌ Esta es una factura normal/interna, no se puede enviar a DIAN')
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    # Verificar si puede enviarse a DIAN
    puede_enviar, mensaje = invoice.puede_enviar_dian()
    
    if not puede_enviar:
        messages.error(request, f'❌ No se puede enviar a DIAN: {mensaje}')
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    try:
        # Obtener configuración
        config = InvoiceConfiguration.get_config(organization)
        
        if not config.facturacion_electronica_activa:
            messages.error(request, '❌ La facturación electrónica no está activada')
            return redirect('billing:invoice_detail', invoice_id=invoice.id)
        
        # Procesar envío a DIAN
        from apps.billing.services import FacturacionElectronicaService
        
        # Usar mock si estamos en desarrollo o no hay certificado
        usar_mock = not config.certificado_digital or config.ambiente == 'pruebas'
        
        servicio = FacturacionElectronicaService(
            invoice=invoice,
            usar_mock=usar_mock
        )
        
        # Actualizar estado a "procesando"
        invoice.estado_dian = 'processing'
        invoice.save(update_fields=['estado_dian'])
        
        exito, resultado = servicio.procesar_factura_completa()
        
        if exito:
            messages.success(
                request,
                f'✅ Factura {invoice.numero_completo} enviada a DIAN exitosamente'
            )
            if usar_mock:
                messages.info(request, '⚠️ Procesada en modo PRUEBA (sin envío real a DIAN)')
            else:
                messages.success(request, f'📄 CUFE: {invoice.cufe[:30]}...')
        else:
            messages.error(
                request,
                f'❌ Error al enviar factura a DIAN'
            )
            messages.error(request, f"Detalle: {resultado.get('mensaje', 'Error desconocido')}")
            # Revertir estado
            invoice.estado_dian = 'draft'
            invoice.save(update_fields=['estado_dian'])
            
    except Exception as e:
        messages.error(request, f'❌ Error inesperado al enviar a DIAN: {str(e)}')
        # Revertir estado
        invoice.estado_dian = 'draft'
        invoice.save(update_fields=['estado_dian'])
    
    return redirect('billing:invoice_detail', invoice_id=invoice.id)


@login_required
def invoice_pdf(request, invoice_id):
    """Generar PDF de la factura estilo profesional y moderno"""
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
    import io
    import base64
    
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    organization = org_member.organization
    invoice = get_object_or_404(Invoice, id=invoice_id, organization=organization)
    
    # Crear buffer
    buffer = io.BytesIO()
    
    # Crear PDF con márgenes reducidos
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )
    elements = []
    
    styles = getSampleStyleSheet()
    
    # ===== ESTILOS PERSONALIZADOS =====
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1a202c'),
        spaceAfter=8,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    info_style = ParagraphStyle(
        'InfoText',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#2d3748'),
        leading=12
    )
    
    bold_style = ParagraphStyle(
        'BoldText',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a202c')
    )
    
    # ===== TÍTULO =====
    elements.append(Paragraph("Factura de Venta", title_style))
    elements.append(Spacer(1, 0.3*cm))
    
    # ===== HEADER: Empresa + Cliente + Factura en tres secciones =====
    # Obtener tax_id correctamente
    tax_id = organization.tax_id if hasattr(organization, 'tax_id') else 'N/A'
    tax_type = organization.get_tax_id_type_display() if hasattr(organization, 'tax_id_type') and organization.tax_id_type else 'NIT'
    
    empresa_info = f"""<b>{organization.name}</b><br/>
{tax_type}: {tax_id}<br/>
{organization.email if hasattr(organization, 'email') else ''}"""
    
    factura_info = f"""Factura No: <b>{invoice.numero_completo}</b><br/>
Fecha: <b>{invoice.fecha_emision.strftime('%d/%m/%Y')}</b><br/>
Estado: <b>{invoice.get_estado_dian_display()}</b>"""
    
    cliente_info = f"""<b>Cliente:</b> {invoice.cliente_nombre}<br/>
<b>{invoice.cliente_tipo_documento}:</b> {invoice.cliente_numero_documento}<br/>
{f'<b>Tel:</b> {invoice.cliente_telefono}' if invoice.cliente_telefono else ''}"""
    
    header_data = [[
        Paragraph(empresa_info, info_style),
        Paragraph(factura_info, info_style),
        Paragraph(cliente_info, info_style)
    ]]
    
    header_table = Table(header_data, colWidths=[6.5*cm, 6*cm, 6.5*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # ===== TABLA DE ITEMS =====
    items_data = [[
        Paragraph('<b>Ítem</b>', bold_style),
        Paragraph('<b>Descripción</b>', bold_style),
        Paragraph('<b>Cant.</b>', bold_style),
        Paragraph('<b>V. Unitario</b>', bold_style),
        Paragraph('<b>Desc.</b>', bold_style),
        Paragraph('<b>IVA</b>', bold_style),
        Paragraph('<b>Total</b>', bold_style)
    ]]
    
    for idx, item in enumerate(invoice.items.all(), 1):
        items_data.append([
            Paragraph(str(idx), info_style),
            Paragraph(item.descripcion[:45], info_style),
            Paragraph(f"{item.cantidad:.0f}", info_style),
            Paragraph(f"${item.valor_unitario:,.0f}", info_style),
            Paragraph(f"{item.descuento_porcentaje:.0f}%" if item.descuento_porcentaje > 0 else "-", info_style),
            Paragraph(f"{item.iva_porcentaje:.0f}%", info_style),
            Paragraph(f"${item.total_linea:,.0f}", info_style)
        ])
    
    items_table = Table(items_data, colWidths=[1*cm, 7*cm, 1.5*cm, 2.5*cm, 1.5*cm, 1.5*cm, 3*cm])
    items_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d0d0d0')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('ALIGN', (2, 0), (-1, 0), 'CENTER'),
        
        # Contenido
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        
        # Bordes y padding
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a0a0a0')),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.4*cm))
    
    # ===== TOTALES =====
    totals_data = []
    
    if invoice.descuento > 0:
        totals_data.append(['Subtotal:', f"$ {invoice.subtotal:,.2f}"])
        totals_data.append(['Descuento:', f"$ {invoice.descuento:,.2f}"])
        totals_data.append(['Base Imponible:', f"$ {invoice.base_imponible:,.2f}"])
    else:
        totals_data.append(['Subtotal:', f"$ {invoice.subtotal:,.2f}"])
    
    totals_data.append(['IVA:', f"$ {invoice.total_iva:,.2f}"])
    totals_data.append([
        Paragraph('<b>TOTAL A PAGAR:</b>', bold_style),
        Paragraph(f"<b>$ {invoice.total:,.2f}</b>", bold_style)
    ])
    
    if invoice.total_pagado > 0:
        totals_data.append(['Total Pagado:', f"$ {invoice.total_pagado:,.2f}"])
        totals_data.append([
            Paragraph('<b>Saldo Pendiente:</b>', bold_style),
            Paragraph(f"<b>$ {invoice.saldo_pendiente:,.2f}</b>", 
                     ParagraphStyle('Saldo', parent=bold_style, 
                                   textColor=colors.HexColor('#DC2626') if invoice.saldo_pendiente > 0 else colors.HexColor('#059669')))
        ])
    
    totals_table = Table(totals_data, colWidths=[12*cm, 7*cm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEABOVE', (0, -2 if invoice.total_pagado > 0 else -1), (-1, -2 if invoice.total_pagado > 0 else -1), 1, colors.HexColor('#666666')),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # ===== INFORMACIÓN DE PAGO =====
    pago_info_parts = []
    pago_info_parts.append(f"<b>Forma de Pago:</b> {'Contado' if invoice.forma_pago == '1' else 'Crédito'}")
    pago_info_parts.append(f"<b>Medio de Pago:</b> {invoice.get_medio_pago_display()}")
    
    pago_text = " | ".join(pago_info_parts)
    pago_para = Paragraph(pago_text, info_style)
    
    pago_table = Table([[pago_para]], colWidths=[19*cm])
    pago_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#a0a0a0')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(pago_table)
    
    # ===== CUFE SI EXISTE =====
    if invoice.cufe:
        elements.append(Spacer(1, 0.3*cm))
        cufe_text = f"<b>CUFE:</b> <font size=7>{invoice.cufe}</font>"
        cufe_para = Paragraph(cufe_text, ParagraphStyle('CUFE', parent=info_style, fontSize=7, textColor=colors.HexColor('#6B7280')))
        
        cufe_table = Table([[cufe_para]], colWidths=[19*cm])
        cufe_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#a0a0a0')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(cufe_table)
    
    # ===== QR CODE Y FOOTER =====
    if invoice.qr_code_base64:
        try:
            elements.append(Spacer(1, 0.3*cm))
            qr_image_data = base64.b64decode(invoice.qr_code_base64)
            qr_buffer = io.BytesIO(qr_image_data)
            img = Image(qr_buffer, width=3*cm, height=3*cm)
            
            qr_info = Paragraph(
                "<b>Código QR de Validación</b><br/><font size=7>Escanee para validar autenticidad</font>",
                ParagraphStyle('QRInfo', parent=info_style, fontSize=8, alignment=TA_CENTER)
            )
            
            qr_table = Table([[img, qr_info]], colWidths=[4*cm, 15*cm])
            qr_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(qr_table)
        except:
            pass
    
    # Footer legal
    elements.append(Spacer(1, 0.4*cm))
    legal_text = f"""<font size=7><i>Este documento fue generado por {organization.name}. 
Para consultas o aclaraciones, contacte usando la información de contacto proporcionada.</i></font>"""
    elements.append(Paragraph(legal_text, ParagraphStyle('Legal', parent=info_style, fontSize=7, textColor=colors.HexColor('#6B7280'), alignment=TA_CENTER)))
    
    # Construir PDF
    doc.build(elements)
    
    # Obtener valor del buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Retornar respuesta
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Factura_{invoice.numero_completo}.pdf"'
    response.write(pdf)
    
    return response


@login_required
def invoice_delete(request, invoice_id):
    """Eliminar una factura"""
    # Obtener organización del usuario
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        messages.error(request, 'No tienes una organización asignada')
        return redirect('dashboard:home')
    
    organization = org_member.organization
    
    # Verificar permisos (solo Owner y Admin pueden eliminar facturas)
    if org_member.role not in ['owner', 'admin']:
        messages.error(request, 'No tienes permisos para eliminar facturas')
        return redirect('billing:invoice_list')
    
    # Obtener la factura
    invoice = get_object_or_404(Invoice, id=invoice_id, organization=organization)
    
    # Verificar si la factura ya fue enviada a la DIAN
    if invoice.estado_dian == 'approved':
        messages.error(request, '❌ No se puede eliminar una factura ya aprobada por la DIAN')
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    if request.method == 'POST':
        numero_completo = invoice.numero_completo
        total_factura = invoice.total
        numero_a_liberar = invoice.numero
        es_electronica = invoice.es_factura_electronica
        
        try:
            from django.db import transaction
            
            with transaction.atomic():
                # ==================== LIBERAR CONSECUTIVO ====================
                if es_electronica:
                    # Para facturas electrónicas, liberar consecutivo DIAN
                    try:
                        dian_config = DianConfiguration.objects.get(organization=organization)
                        # Decrementar el consecutivo actual si es la última factura
                        ultima_factura = Invoice.objects.filter(
                            organization=organization,
                            es_factura_electronica=True
                        ).exclude(id=invoice.id).order_by('-numero').first()
                        
                        if ultima_factura:
                            # Si hay facturas después, no decrementar (dejar hueco)
                            if numero_a_liberar == dian_config.resolucion_numero_actual:
                                dian_config.resolucion_numero_actual -= 1
                                dian_config.save()
                                messages.info(request, f'ℹ️ Consecutivo DIAN {numero_a_liberar} liberado')
                        else:
                            # Es la única factura electrónica, resetear contador
                            dian_config.resolucion_numero_actual = dian_config.resolucion_numero_inicio - 1
                            dian_config.save()
                            messages.info(request, f'ℹ️ Consecutivo DIAN reseteado')
                    except DianConfiguration.DoesNotExist:
                        pass
                else:
                    # Para facturas normales, simplemente se puede reutilizar el número
                    # El sistema generará automáticamente el siguiente número disponible
                    messages.info(request, f'ℹ️ Consecutivo interno {numero_a_liberar} disponible para reutilizar')
                
                # ==================== SINCRONIZAR CON MÓDULO DE VENTAS ====================
                # Si la factura tiene una venta asociada, marcarla como cancelada
                if invoice.sale:
                    try:
                        from apps.sales.models import Sale
                        sale = invoice.sale
                        sale.status = 'cancelled'
                        sale.notes = f'{sale.notes}\n\nVenta cancelada por eliminación de factura {numero_completo}'.strip()
                        sale.save()
                        
                        messages.info(request, f'ℹ️ Venta {sale.sale_number} marcada como cancelada')
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f'Error al cancelar venta asociada: {str(e)}')
                
                # Eliminar la factura
                invoice.delete()
                
            messages.success(request, f'✅ Factura {numero_completo} eliminada exitosamente')
            messages.info(request, f'💰 Total descontado: ${total_factura:,.0f}')
            return redirect('billing:invoice_list')
            
        except Exception as e:
            messages.error(request, f'❌ Error al eliminar factura: {str(e)}')
            return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    # Si es GET, redirigir al detalle
    return redirect('billing:invoice_detail', invoice_id=invoice.id)


@login_required
def search_patients_ajax(request):
    """Buscar pacientes en tiempo real para autocompletado"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    org_member = OrganizationMember.objects.filter(user=request.user).first()
    if not org_member:
        return JsonResponse({'success': False, 'error': 'No tienes una organización asignada'}, status=403)
    
    organization = org_member.organization
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'success': True, 'patients': []})
    
    try:
        from apps.patients.models import Patient
        from django.db.models import Q
        
        # Buscar por nombre completo, cédula o teléfono
        patients = Patient.objects.filter(
            organization=organization,
            is_active=True
        ).filter(
            Q(full_name__icontains=query) |
            Q(identification__icontains=query) |
            Q(phone_number__icontains=query)
        )[:10]  # Limitar a 10 resultados
        
        results = []
        for patient in patients:
            results.append({
                'id': patient.id,
                'full_name': patient.full_name,
                'identification_type': patient.identification_type,
                'identification_number': patient.identification or '',
                'phone': patient.phone_number or '',
                'email': patient.email or '',
                'display': f"{patient.full_name} - {patient.identification_type}: {patient.identification or 'Sin documento'}"
            })
        
        return JsonResponse({'success': True, 'patients': results})
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error en búsqueda de pacientes: {str(e)}')
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

