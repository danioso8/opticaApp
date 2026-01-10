"""
Ejemplo de vista usando módulos compartidos
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from shared.utils import format_currency, get_client_ip, truncate_text
from shared.services import EmailService, FileService
from shared.core import validate_phone

from .models import Cliente, Factura, Producto
from .forms import ClienteForm, FacturaForm


@login_required
def crear_cliente(request):
    """Crea un nuevo cliente usando utilidades compartidas"""
    
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        
        if form.is_valid():
            # Crear cliente
            cliente = form.save(commit=False)
            cliente.organization = request.user.organization
            cliente.save()
            
            # Obtener IP del cliente
            ip = get_client_ip(request)
            
            # Registrar en log (ejemplo)
            print(f"Cliente {cliente.nombre} creado desde IP: {ip}")
            
            # Enviar email de bienvenida
            EmailService.send_template_email(
                to_emails=cliente.email,
                template_key='welcome',
                context={
                    'cliente': cliente,
                    'empresa': request.user.organization.name,
                },
                organization=request.user.organization
            )
            
            messages.success(request, f'Cliente {cliente.nombre} creado exitosamente')
            return redirect('clientes:detalle', pk=cliente.pk)
    else:
        form = ClienteForm()
    
    return render(request, 'clientes/crear.html', {'form': form})


@login_required
def detalle_factura(request, pk):
    """Detalle de factura con formateo de datos"""
    
    factura = get_object_or_404(
        Factura,
        pk=pk,
        organization=request.user.organization
    )
    
    # Formatear montos usando utilidades compartidas
    context = {
        'factura': factura,
        'subtotal_formateado': format_currency(factura.subtotal),
        'impuestos_formateados': format_currency(factura.impuestos),
        'total_formateado': format_currency(factura.total),
        'cliente': factura.cliente,
        'detalles': factura.detalles.all(),
    }
    
    return render(request, 'facturas/detalle.html', context)


@login_required
def enviar_factura_email(request, pk):
    """Envía la factura por email"""
    
    factura = get_object_or_404(
        Factura,
        pk=pk,
        organization=request.user.organization
    )
    
    # Formatear datos
    total_formateado = format_currency(factura.total)
    
    # Enviar email
    success = EmailService.send_template_email(
        to_emails=factura.cliente.email,
        template_key='invoice_sent',
        context={
            'factura': factura,
            'total': total_formateado,
            'cliente': factura.cliente,
            'empresa': request.user.organization.name,
        },
        organization=request.user.organization
    )
    
    if success:
        messages.success(request, f'Factura enviada a {factura.cliente.email}')
    else:
        messages.error(request, 'Error al enviar el email')
    
    return redirect('facturas:detalle', pk=factura.pk)


@login_required
def productos_bajo_stock(request):
    """Lista productos que requieren reorden"""
    
    productos = Producto.objects.filter(
        organization=request.user.organization,
        is_active=True
    )
    
    # Filtrar productos bajo stock
    productos_criticos = [p for p in productos if p.requiere_reorden]
    
    # Preparar datos para la vista
    productos_data = []
    for producto in productos_criticos:
        productos_data.append({
            'producto': producto,
            'stock_actual': producto.stock,
            'stock_minimo': producto.stock_minimo,
            'margen': f"{producto.margen_ganancia:.2f}%",
        })
    
    context = {
        'productos': productos_data,
        'total_criticos': len(productos_criticos),
    }
    
    return render(request, 'productos/bajo_stock.html', context)


@login_required
def exportar_clientes(request):
    """Exporta clientes a CSV usando FileService"""
    import csv
    from django.http import HttpResponse
    
    # Obtener clientes
    clientes = Cliente.objects.filter(
        organization=request.user.organization,
        is_deleted=False
    )
    
    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="clientes.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Nombre', 'Email', 'Teléfono', 'Documento', 'Ciudad', 'Fecha Creación'])
    
    for cliente in clientes:
        writer.writerow([
            cliente.nombre,
            cliente.email,
            cliente.telefono,
            cliente.numero_documento,
            cliente.ciudad or '',
            cliente.created_at.strftime('%Y-%m-%d'),
        ])
    
    return response


@login_required
def eliminar_cliente(request, pk):
    """Elimina un cliente de forma suave"""
    
    cliente = get_object_or_404(
        Cliente,
        pk=pk,
        organization=request.user.organization
    )
    
    if request.method == 'POST':
        # Eliminar de forma suave (usando el mixin)
        cliente.eliminar(usuario=request.user)
        
        messages.success(request, f'Cliente {cliente.nombre} eliminado')
        return redirect('clientes:lista')
    
    return render(request, 'clientes/confirmar_eliminar.html', {'cliente': cliente})


@login_required
def restaurar_cliente(request, pk):
    """Restaura un cliente eliminado"""
    
    cliente = get_object_or_404(
        Cliente,
        pk=pk,
        organization=request.user.organization,
        is_deleted=True
    )
    
    # Restaurar (usando el mixin)
    cliente.restaurar()
    
    messages.success(request, f'Cliente {cliente.nombre} restaurado')
    return redirect('clientes:detalle', pk=cliente.pk)


# ============================================================================
# EJEMPLO DE API VIEW (usando Django REST Framework)
# ============================================================================

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
def crear_cliente_api(request):
    """
    API endpoint para crear cliente
    Usa validadores compartidos
    """
    from shared.core import validate_phone, validate_email_custom
    from django.core.exceptions import ValidationError
    
    data = request.data
    
    # Validar teléfono
    try:
        validate_phone(data.get('telefono', ''))
    except ValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validar email
    try:
        validate_email_custom(data.get('email', ''))
    except ValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Crear cliente
    cliente = Cliente.objects.create(
        nombre=data['nombre'],
        email=data['email'],
        telefono=data['telefono'],
        numero_documento=data.get('numero_documento', ''),
        organization=request.user.organization
    )
    
    return Response(
        {
            'id': cliente.id,
            'nombre': cliente.nombre,
            'email': cliente.email,
            'created_at': cliente.created_at,
        },
        status=status.HTTP_201_CREATED
    )
