"""
Vistas para pagos y suscripciones con Wompi
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import json
import uuid

from apps.organizations.models import SubscriptionPlan
from .models import UserSubscription, PaymentMethod, Transaction, SubscriptionRenewalLog
from .wompi_service import wompi_service
from datetime import timedelta


@login_required
def subscription_checkout(request, plan_id):
    """Vista de checkout para seleccionar/pagar un plan"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    
    # Obtener métodos de pago del usuario
    payment_methods = PaymentMethod.objects.filter(user=request.user, is_active=True)
    
    # Determinar el ciclo de facturación (por defecto mensual)
    billing_cycle = request.GET.get('cycle', 'monthly')
    
    # Calcular el monto
    if billing_cycle == 'yearly':
        amount = plan.price_yearly
    else:
        amount = plan.price_monthly
    
    # Convertir a USD (ejemplo: dividir entre 4000 para COP a USD aproximado)
    amount_usd = float(amount) / 4000
    
    context = {
        'plan': plan,
        'billing_cycle': billing_cycle,
        'amount': amount,
        'amount_usd': amount_usd,
        'payment_methods': payment_methods,
        'wompi_public_key': settings.WOMPI_PUBLIC_KEY,
    }
    
    return render(request, 'users/subscription_checkout.html', context)


@login_required
@require_http_methods(["POST"])
def process_subscription_payment(request, plan_id):
    """Procesa el pago de una suscripción"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    
    billing_cycle = request.POST.get('billing_cycle', 'monthly')
    payment_method_id = request.POST.get('payment_method_id')
    
    # Si no hay payment_method_id, es una nueva tarjeta
    if not payment_method_id:
        card_token = request.POST.get('card_token')
        card_data = {
            'last_four': request.POST.get('card_last_four'),
            'brand': request.POST.get('card_brand'),
            'holder_name': request.POST.get('card_holder_name'),
            'type': request.POST.get('card_type', 'CREDIT'),
        }
        
        success, payment_method, error = wompi_service.tokenize_card_and_save(
            user=request.user,
            card_token=card_token,
            card_data=card_data
        )
        
        if not success:
            messages.error(request, f'Error al guardar la tarjeta: {error}')
            return redirect('users:subscription_checkout', plan_id=plan_id)
        
        payment_method_id = payment_method.id
    
    # Calcular monto
    if billing_cycle == 'yearly':
        amount = plan.price_yearly
    else:
        amount = plan.price_monthly
    
    amount_in_cents = int(amount * 100)
    
    # Generar referencia única
    reference = f"SUB-{request.user.id}-{plan.id}-{uuid.uuid4().hex[:8]}"
    
    # Crear transacción
    success, transaction, error = wompi_service.create_transaction(
        amount_in_cents=amount_in_cents,
        currency='COP',
        customer_email=request.user.email,
        payment_method_id=payment_method_id,
        reference=reference,
        subscription_id=None  # Se asignará después
    )
    
    if success:
        # Crear o actualizar suscripción
        try:
            user_subscription = UserSubscription.objects.get(user=request.user)
            # Actualizar suscripción existente
            user_subscription.plan = plan
            user_subscription.billing_cycle = billing_cycle
            user_subscription.start_date = timezone.now()
            
            if billing_cycle == 'yearly':
                user_subscription.end_date = timezone.now() + timedelta(days=365)
            else:
                user_subscription.end_date = timezone.now() + timedelta(days=30)
            
            user_subscription.is_active = True
            user_subscription.payment_status = 'paid'
            user_subscription.amount_paid = amount
            user_subscription.save()
            
        except UserSubscription.DoesNotExist:
            # Crear nueva suscripción
            if billing_cycle == 'yearly':
                end_date = timezone.now() + timedelta(days=365)
            else:
                end_date = timezone.now() + timedelta(days=30)
            
            user_subscription = UserSubscription.objects.create(
                user=request.user,
                plan=plan,
                billing_cycle=billing_cycle,
                start_date=timezone.now(),
                end_date=end_date,
                is_active=True,
                payment_status='paid',
                amount_paid=amount
            )
        
        # Asociar transacción con suscripción
        transaction.subscription = user_subscription
        transaction.save()
        
        messages.success(request, '¡Pago procesado exitosamente! Tu suscripción está activa.')
        return redirect('users:subscription_success', transaction_id=transaction.id)
    else:
        messages.error(request, f'Error al procesar el pago: {error}')
        return redirect('users:subscription_checkout', plan_id=plan_id)


@login_required
def subscription_success(request, transaction_id):
    """Página de confirmación de pago exitoso"""
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    
    context = {
        'transaction': transaction,
        'subscription': transaction.subscription,
    }
    
    return render(request, 'users/subscription_success.html', context)


@login_required
def payment_methods_list(request):
    """Lista de métodos de pago del usuario"""
    payment_methods = PaymentMethod.objects.filter(user=request.user, is_active=True)
    
    context = {
        'payment_methods': payment_methods,
        'wompi_public_key': settings.WOMPI_PUBLIC_KEY,
    }
    
    return render(request, 'users/payment_methods.html', context)


@login_required
@require_http_methods(["POST"])
def add_payment_method(request):
    """Añade un nuevo método de pago"""
    card_token = request.POST.get('card_token')
    card_data = {
        'last_four': request.POST.get('card_last_four'),
        'brand': request.POST.get('card_brand'),
        'holder_name': request.POST.get('card_holder_name'),
        'type': request.POST.get('card_type', 'CREDIT'),
    }
    
    success, payment_method, error = wompi_service.tokenize_card_and_save(
        user=request.user,
        card_token=card_token,
        card_data=card_data
    )
    
    if success:
        messages.success(request, 'Tarjeta añadida exitosamente')
    else:
        messages.error(request, f'Error al añadir la tarjeta: {error}')
    
    return redirect('users:payment_methods')


@login_required
@require_http_methods(["POST"])
def delete_payment_method(request, method_id):
    """Elimina un método de pago"""
    payment_method = get_object_or_404(PaymentMethod, id=method_id, user=request.user)
    
    payment_method.is_active = False
    payment_method.save()
    
    messages.success(request, 'Método de pago eliminado')
    return redirect('users:payment_methods')


@login_required
@require_http_methods(["POST"])
def set_default_payment_method(request, method_id):
    """Establece un método de pago como predeterminado"""
    payment_method = get_object_or_404(PaymentMethod, id=method_id, user=request.user)
    
    # Desactivar otros como predeterminados
    PaymentMethod.objects.filter(user=request.user).update(is_default=False)
    
    payment_method.is_default = True
    payment_method.save()
    
    messages.success(request, 'Método de pago predeterminado actualizado')
    return redirect('users:payment_methods')


@csrf_exempt
@require_http_methods(["POST"])
def wompi_webhook(request):
    """
    Webhook para recibir eventos de Wompi
    
    Eventos importantes:
    - transaction.updated: Actualización de estado de transacción
    """
    try:
        # Obtener el payload
        payload = json.loads(request.body)
        
        # Verificar la firma
        if not wompi_service.verify_signature(payload):
            return HttpResponse('Invalid signature', status=401)
        
        # Obtener el evento
        event = payload.get('event')
        data = payload.get('data', {})
        transaction_data = data.get('transaction', {})
        
        if event == 'transaction.updated':
            transaction_id = transaction_data.get('id')
            status = transaction_data.get('status')
            
            # Buscar la transacción en BD
            try:
                transaction = Transaction.objects.get(wompi_transaction_id=transaction_id)
                
                # Actualizar estado
                transaction.status = status.upper()
                transaction.metadata = payload
                transaction.processed_at = timezone.now()
                transaction.save()
                
                # Si fue aprobada, activar suscripción
                if status == 'APPROVED' and transaction.subscription:
                    subscription = transaction.subscription
                    subscription.is_active = True
                    subscription.payment_status = 'paid'
                    subscription.save()
                    
                    # Enviar email de confirmación
                    send_subscription_confirmation_email(subscription)
                
                # Si fue rechazada, enviar email
                elif status == 'DECLINED' and transaction.subscription:
                    send_payment_failed_email(transaction)
                
            except Transaction.DoesNotExist:
                pass
        
        return HttpResponse('OK', status=200)
        
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)


@login_required
def subscription_status(request):
    """Vista del estado de la suscripción del usuario"""
    try:
        subscription = UserSubscription.objects.get(user=request.user)
    except UserSubscription.DoesNotExist:
        subscription = None
    
    # Obtener historial de transacciones
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Obtener método de pago predeterminado
    default_payment_method = PaymentMethod.objects.filter(
        user=request.user,
        is_active=True,
        is_default=True
    ).first()
    
    context = {
        'subscription': subscription,
        'transactions': transactions,
        'default_payment_method': default_payment_method,
    }
    
    return render(request, 'users/subscription_status.html', context)


def send_subscription_confirmation_email(subscription):
    """Envía email de confirmación de suscripción"""
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from datetime import datetime
    
    subject = f'Suscripción activada - {subscription.plan.name}'
    
    html_message = render_to_string('users/emails/subscription_confirmed.html', {
        'subscription': subscription,
        'user': subscription.user,
        'current_year': datetime.now().year,
    })
    
    send_mail(
        subject=subject,
        message='',
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[subscription.user.email],
        fail_silently=True,
    )


def send_payment_failed_email(transaction):
    """Envía email cuando falla un pago"""
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from datetime import datetime
    
    subject = 'Error en el pago de tu suscripción'
    
    html_message = render_to_string('users/emails/payment_failed.html', {
        'transaction': transaction,
        'user': transaction.user,
        'current_year': datetime.now().year,
    })
    
    send_mail(
        subject=subject,
        message='',
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[transaction.user.email],
        fail_silently=True,
    )


def send_subscription_renewal_failed_email(subscription, error_message):
    """Envía email cuando falla la renovación automática"""
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from datetime import datetime
    
    subject = 'No se pudo renovar tu suscripción'
    
    html_message = render_to_string('users/emails/renewal_failed.html', {
        'subscription': subscription,
        'user': subscription.user,
        'error_message': error_message,
        'current_year': datetime.now().year,
    })
    
    send_mail(
        subject=subject,
        message='',
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[subscription.user.email],
        fail_silently=True,
    )
