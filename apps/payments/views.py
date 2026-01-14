# -*- coding: utf-8 -*-
"""
Vistas para procesamiento de pagos
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib import messages
from decimal import Decimal
import json
import stripe

from apps.payments.models import Transaction, PaymentMethod, Invoice
from apps.payments.services.stripe_service import StripeService
from apps.payments.services.wompi_service import WompiService
from apps.organizations.models import PlanFeature


@login_required
def checkout(request):
    """
    Página de checkout - procesar pago de módulos
    """
    organization = request.user.organization
    
    # Obtener módulos desde sesión
    module_ids = request.session.get('checkout_modules', [])
    
    if not module_ids:
        messages.warning(request, 'No hay módulos seleccionados para comprar.')
        return redirect('dashboard:module_selector')
    
    # Obtener módulos
    modules = PlanFeature.objects.filter(id__in=module_ids, is_active=True)
    
    if not modules.exists():
        messages.error(request, 'No se encontraron módulos válidos.')
        return redirect('dashboard:module_selector')
    
    # Calcular precios (igual que en el selector)
    from apps.organizations.models import ModulePricing
    
    subtotal = sum(m.price_monthly or Decimal('0.00') for m in modules)
    
    try:
        pricing = ModulePricing.objects.first()
        discount_4 = pricing.discount_4_modules if pricing else 10
        discount_7 = pricing.discount_7_modules if pricing else 20
    except:
        discount_4 = 10
        discount_7 = 20
    
    module_count = len(module_ids)
    discount_percent = 0
    discount_amount = Decimal('0.00')
    
    if module_count >= 7:
        discount_percent = discount_7
        discount_amount = subtotal * Decimal(str(discount_7)) / Decimal('100')
    elif module_count >= 4:
        discount_percent = discount_4
        discount_amount = subtotal * Decimal(str(discount_4)) / Decimal('100')
    
    total = subtotal - discount_amount
    
    # Obtener métodos de pago guardados
    payment_methods = PaymentMethod.objects.filter(
        organization=organization,
        is_active=True
    )
    
    context = {
        'organization': organization,
        'modules': modules,
        'module_count': module_count,
        'subtotal': subtotal,
        'discount_percent': discount_percent,
        'discount_amount': discount_amount,
        'total': total,
        'payment_methods': payment_methods,
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLIC_KEY', ''),
        'wompi_public_key': getattr(settings, 'WOMPI_PUBLIC_KEY', ''),
    }
    
    return render(request, 'payments/checkout.html', context)


@login_required
@require_POST
def create_payment_intent(request):
    """
    Crear un Payment Intent con Stripe
    """
    organization = request.user.organization
    
    try:
        data = json.loads(request.body)
        module_ids = data.get('module_ids', [])
        
        if not module_ids:
            return JsonResponse({'error': 'No se especificaron módulos'}, status=400)
        
        # Usar servicio de Stripe
        stripe_service = StripeService()
        result = stripe_service.process_module_purchase(
            organization=organization,
            module_ids=module_ids
        )
        
        return JsonResponse({
            'client_secret': result['payment_intent']['client_secret'],
            'transaction_id': str(result['transaction'].id),
            'total': float(result['total']),
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def create_wompi_transaction(request):
    """
    Crear transacción con Wompi
    """
    organization = request.user.organization
    
    try:
        data = json.loads(request.body)
        module_ids = data.get('module_ids', [])
        
        if not module_ids:
            return JsonResponse({'error': 'No se especificaron módulos'}, status=400)
        
        # Usar servicio de Wompi
        wompi_service = WompiService()
        result = wompi_service.process_module_purchase(
            organization=organization,
            module_ids=module_ids
        )
        
        return JsonResponse({
            'payment_link': result['payment_link'],
            'transaction_id': str(result['transaction'].id),
            'total_usd': float(result['total_usd']),
            'total_cop': float(result['total_cop']),
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def payment_success(request):
    """
    Página de éxito después del pago
    """
    transaction_id = request.GET.get('transaction_id')
    
    if transaction_id:
        try:
            transaction = Transaction.objects.get(
                id=transaction_id,
                organization=request.user.organization
            )
            
            context = {
                'transaction': transaction,
                'modules': transaction.modules.all(),
            }
            
            return render(request, 'payments/success.html', context)
        
        except Transaction.DoesNotExist:
            messages.error(request, 'Transacción no encontrada.')
    
    return redirect('dashboard:my_plan')


@login_required
def payment_failed(request):
    """
    Página de error en el pago
    """
    transaction_id = request.GET.get('transaction_id')
    
    context = {
        'transaction_id': transaction_id,
    }
    
    return render(request, 'payments/failed.html', context)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Webhook para eventos de Stripe
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Manejar el evento
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_successful_payment_intent(payment_intent)
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_failed_payment_intent(payment_intent)
    
    return HttpResponse(status=200)


def handle_successful_payment_intent(payment_intent):
    """
    Procesar payment intent exitoso
    """
    try:
        # Buscar transacción
        transaction = Transaction.objects.get(
            gateway_transaction_id=payment_intent['id']
        )
        
        # Marcar como completada
        transaction.mark_as_completed()
        
        # Activar módulos
        stripe_service = StripeService()
        stripe_service.activate_purchased_modules(transaction.id)
        
        # TODO: Enviar email de confirmación
        
    except Transaction.DoesNotExist:
        pass  # Log error


def handle_failed_payment_intent(payment_intent):
    """
    Procesar payment intent fallido
    """
    try:
        transaction = Transaction.objects.get(
            gateway_transaction_id=payment_intent['id']
        )
        
        transaction.mark_as_failed(
            reason=payment_intent.get('last_payment_error', {}).get('message')
        )
        
    except Transaction.DoesNotExist:
        pass


@csrf_exempt
@require_POST
def wompi_webhook(request):
    """
    Webhook para eventos de Wompi
    """
    try:
        data = json.loads(request.body)
        event = data.get('event')
        
        if event == 'transaction.updated':
            transaction_data = data.get('data', {}).get('transaction', {})
            handle_wompi_transaction_update(transaction_data)
        
        return HttpResponse(status=200)
    
    except Exception as e:
        return HttpResponse(status=400)


def handle_wompi_transaction_update(transaction_data):
    """
    Procesar actualización de transacción de Wompi
    """
    try:
        transaction = Transaction.objects.get(
            gateway_transaction_id=transaction_data['id']
        )
        
        status = transaction_data['status']
        
        if status == 'APPROVED':
            transaction.mark_as_completed()
            
            # Activar módulos
            wompi_service = WompiService()
            wompi_service.activate_purchased_modules(transaction.id)
        
        elif status in ['DECLINED', 'ERROR']:
            transaction.mark_as_failed(
                reason=transaction_data.get('status_message')
            )
    
    except Transaction.DoesNotExist:
        pass


@login_required
def transaction_history(request):
    """
    Historial de transacciones de la organización
    """
    organization = request.user.organization
    
    transactions = Transaction.objects.filter(
        organization=organization
    ).order_by('-created_at')[:50]
    
    context = {
        'transactions': transactions,
    }
    
    return render(request, 'payments/transaction_history.html', context)


@login_required
def invoice_list(request):
    """
    Lista de facturas de la organización
    """
    organization = request.user.organization
    
    invoices = Invoice.objects.filter(
        organization=organization
    ).order_by('-created_at')
    
    context = {
        'invoices': invoices,
    }
    
    return render(request, 'payments/invoice_list.html', context)


@login_required
def invoice_detail(request, invoice_id):
    """
    Detalle de una factura
    """
    invoice = get_object_or_404(
        Invoice,
        id=invoice_id,
        organization=request.user.organization
    )
    
    context = {
        'invoice': invoice,
        'items': invoice.items.all(),
    }
    
    return render(request, 'payments/invoice_detail.html', context)
