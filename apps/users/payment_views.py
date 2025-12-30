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
from apps.organizations.currency_utils import usd_to_cop, usd_to_cop_cents, format_cop
from .models import UserSubscription, PaymentMethod, Transaction, SubscriptionRenewalLog
from .wompi_service import wompi_service
from datetime import timedelta


@login_required
def subscription_checkout(request, plan_id):
    """Vista de checkout para seleccionar/pagar un plan"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    
    # Determinar el ciclo de facturación (por defecto mensual)
    billing_cycle = request.GET.get('cycle', 'monthly')
    
    # Calcular el monto en USD
    if billing_cycle == 'yearly':
        amount_usd = plan.price_yearly
    else:
        amount_usd = plan.price_monthly
    
    # Convertir a COP para mostrar y cobrar
    amount_cop = usd_to_cop(amount_usd)
    amount_cop_cents = usd_to_cop_cents(amount_usd)  # Para Wompi
    
    # SI ES PLAN FREE ($0), ACTIVAR DIRECTAMENTE SIN PEDIR TARJETA
    if amount_usd == 0 or plan.plan_type == 'free':
        # Activar suscripción gratuita inmediatamente
        from apps.organizations.models import OrganizationMember
        
        org_member = OrganizationMember.objects.filter(user=request.user).first()
        if org_member:
            # Crear o actualizar suscripción
            subscription, created = UserSubscription.objects.update_or_create(
                user=request.user,
                defaults={
                    'plan': plan,
                    'organization': org_member.organization,
                    'billing_cycle': billing_cycle,
                    'status': 'active',
                    'payment_status': 'paid',  # Plan free siempre está pagado
                    'current_period_start': timezone.now(),
                    'current_period_end': timezone.now() + timedelta(days=365),  # 1 año
                }
            )
            
            messages.success(request, f'✅ ¡Bienvenido! Tu Plan Free ha sido activado exitosamente.')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'No se encontró tu organización.')
            return redirect('organizations:subscription_plans')
    
    # Para planes de pago, mostrar formulario de tarjeta
    # Obtener métodos de pago del usuario
    payment_methods = PaymentMethod.objects.filter(user=request.user, is_active=True)
    
    context = {
        'plan': plan,
        'billing_cycle': billing_cycle,
        'amount': amount_cop,  # Monto en COP para mostrar
        'amount_usd': amount_usd,  # Monto en USD para referencia
        'amount_cop_cents': amount_cop_cents,  # Para Wompi (centavos)
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
    
    # Calcular monto en USD y convertir a COP
    if billing_cycle == 'yearly':
        amount_usd = plan.price_yearly
    else:
        amount_usd = plan.price_monthly
    
    # Convertir a COP centavos para Wompi
    amount_in_cents = usd_to_cop_cents(amount_usd)
    amount_cop = usd_to_cop(amount_usd)
    
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
            user_subscription.amount_paid = amount_usd  # Guardar USD en base de datos
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
                amount_paid=amount_usd  # Guardar USD en base de datos
            )
        
        # Asociar transacción con suscripción
        transaction.subscription = user_subscription
        transaction.save()
        
        messages.success(request, f'¡Pago procesado exitosamente por {format_cop(amount_cop)}! Tu suscripción está activa.')
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
                
                # Si fue aprobada y es conversión de trial
                elif status == 'APPROVED' and transaction.metadata.get('trial_conversion'):
                    # Buscar suscripción del usuario y convertir trial
                    try:
                        subscription = UserSubscription.objects.get(user=transaction.user)
                        if subscription.is_trial:
                            subscription.convert_trial_to_paid()
                            send_subscription_confirmation_email(subscription)
                    except UserSubscription.DoesNotExist:
                        pass
                
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


@login_required
def trial_expired_checkout(request):
    """Vista de checkout específica para usuarios con trial expirado"""
    try:
        subscription = UserSubscription.objects.get(user=request.user)
    except UserSubscription.DoesNotExist:
        messages.error(request, 'No se encontró tu suscripción.')
        return redirect('organizations:subscription_plans')
    
    # Verificar que realmente necesita pago
    if not subscription.needs_payment_after_trial():
        return redirect('dashboard:home')
    
    plan = subscription.plan
    
    # El precio es mensual después del trial
    amount_usd = plan.price_monthly
    amount_cop = usd_to_cop(amount_usd)
    amount_cop_cents = usd_to_cop_cents(amount_usd)
    
    # Obtener métodos de pago del usuario
    payment_methods = PaymentMethod.objects.filter(user=request.user, is_active=True)
    
    context = {
        'plan': plan,
        'subscription': subscription,
        'amount': amount_cop,
        'amount_usd': amount_usd,
        'amount_cop_cents': amount_cop_cents,
        'payment_methods': payment_methods,
        'wompi_public_key': settings.WOMPI_PUBLIC_KEY,
    }
    
    return render(request, 'users/trial_expired_checkout.html', context)


@login_required
@require_http_methods(["POST"])
def process_trial_payment(request):
    """Procesa el pago cuando el trial ha expirado"""
    try:
        subscription = UserSubscription.objects.get(user=request.user)
    except UserSubscription.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Suscripción no encontrada'}, status=404)
    
    if not subscription.needs_payment_after_trial():
        return JsonResponse({'success': False, 'error': 'No necesita pago'}, status=400)
    
    plan = subscription.plan
    billing_cycle = request.POST.get('billing_cycle', 'monthly')
    payment_method_id = request.POST.get('payment_method_id')
    
    # Monto en USD y convertir a COP
    amount_usd = plan.price_monthly if billing_cycle == 'monthly' else plan.price_yearly
    amount_cop_cents = usd_to_cop_cents(amount_usd)
    
    # Crear transacción
    transaction = Transaction.objects.create(
        user=request.user,
        transaction_type='subscription',
        amount=amount_usd,
        currency='USD',
        status='pending',
        reference=f'trial-conversion-{request.user.id}-{uuid.uuid4().hex[:8]}',
        metadata={
            'plan_id': plan.id,
            'billing_cycle': billing_cycle,
            'trial_conversion': True,
        }
    )
    
    try:
        # Si hay método de pago guardado
        if payment_method_id:
            payment_method = PaymentMethod.objects.get(id=payment_method_id, user=request.user)
            
            # Crear transacción con Wompi usando token guardado
            success, response = wompi_service.create_transaction(
                amount_in_cents=amount_cop_cents,
                currency='COP',
                customer_email=request.user.email,
                payment_method=payment_method.wompi_token,
                reference=transaction.reference,
            )
        else:
            # Nueva tarjeta
            card_token = request.POST.get('card_token')
            
            if not card_token:
                raise ValueError('Se requiere token de tarjeta')
            
            # Crear transacción con Wompi
            success, response = wompi_service.create_transaction(
                amount_in_cents=amount_cop_cents,
                currency='COP',
                customer_email=request.user.email,
                payment_method=card_token,
                reference=transaction.reference,
            )
            
            # Guardar método de pago si la transacción fue exitosa
            if success and response.get('status') in ['APPROVED', 'PENDING']:
                PaymentMethod.objects.create(
                    user=request.user,
                    wompi_token=card_token,
                    card_type=request.POST.get('card_type', 'CARD'),
                    last_four=request.POST.get('card_last_four', '****'),
                    expiry_month=request.POST.get('expiry_month', '12'),
                    expiry_year=request.POST.get('expiry_year', '2030'),
                    is_default=not PaymentMethod.objects.filter(user=request.user).exists(),
                )
        
        # Actualizar transacción con respuesta de Wompi
        if success:
            transaction.wompi_transaction_id = response.get('id')
            transaction.status = response.get('status', '').lower()
            transaction.save()
            
            # Si el pago fue aprobado, convertir el trial
            if response.get('status') == 'APPROVED':
                subscription.convert_trial_to_paid()
                
                messages.success(request, '✅ ¡Pago exitoso! Tu suscripción ha sido activada.')
                return redirect('users:subscription_success', transaction_id=transaction.id)
            else:
                messages.info(request, 'Tu pago está siendo procesado. Te notificaremos cuando se complete.')
                return redirect('users:subscription_status')
        else:
            transaction.status = 'failed'
            transaction.save()
            messages.error(request, f'Error al procesar el pago: {response.get("message", "Error desconocido")}')
            return redirect('users:trial_expired_checkout')
            
    except Exception as e:
        transaction.status = 'failed'
        transaction.metadata['error'] = str(e)
        transaction.save()
        
        messages.error(request, f'Error al procesar el pago: {str(e)}')
        return redirect('users:trial_expired_checkout')


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


@login_required
def manage_subscription(request):
    """Vista para gestionar la suscripción del usuario"""
    try:
        subscription = UserSubscription.objects.get(user=request.user)
    except UserSubscription.DoesNotExist:
        messages.error(request, 'No tienes una suscripción activa.')
        return redirect('organizations:subscription_plans')
    
    # Obtener métodos de pago
    payment_methods = PaymentMethod.objects.filter(user=request.user, is_active=True)
    default_payment_method = payment_methods.filter(is_default=True).first()
    
    # Calcular monto de próxima renovación
    if subscription.billing_cycle == 'yearly':
        next_payment_amount = subscription.plan.price_yearly
    else:
        next_payment_amount = subscription.plan.price_monthly
    
    next_payment_cop = usd_to_cop(next_payment_amount)
    
    # Obtener logs de renovación
    renewal_logs = SubscriptionRenewalLog.objects.filter(
        subscription=subscription
    ).order_by('-attempted_at')[:5]
    
    # Calcular días hasta renovación
    days_until_renewal = (subscription.end_date - timezone.now()).days
    
    context = {
        'subscription': subscription,
        'payment_methods': payment_methods,
        'default_payment_method': default_payment_method,
        'next_payment_amount': next_payment_amount,
        'next_payment_cop': next_payment_cop,
        'renewal_logs': renewal_logs,
        'days_until_renewal': days_until_renewal,
        'page_title': 'Gestionar Suscripción',
    }
    
    return render(request, 'users/manage_subscription.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_auto_renew(request):
    """Activa o desactiva la renovación automática"""
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        
        # Cambiar estado
        subscription.auto_renew = not subscription.auto_renew
        subscription.save()
        
        if subscription.auto_renew:
            messages.success(request, '✓ Renovación automática activada. Tu suscripción se renovará automáticamente.')
        else:
            messages.warning(request, 'Renovación automática desactivada. Tu suscripción expirará el ' + 
                           subscription.end_date.strftime('%d/%m/%Y'))
        
    except UserSubscription.DoesNotExist:
        messages.error(request, 'No se encontró tu suscripción.')
    
    return redirect('users:manage_subscription')


@login_required
@require_http_methods(["POST"])
def cancel_subscription(request):
    """Cancela la suscripción (desactiva auto-renew)"""
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        
        # Solo desactivar auto_renew, no eliminar la suscripción
        subscription.auto_renew = False
        subscription.save()
        
        messages.success(request, 
            f'Tu suscripción ha sido cancelada. Seguirás teniendo acceso hasta el {subscription.end_date.strftime("%d/%m/%Y")}. '
            f'Después de esa fecha, tu cuenta será desactivada.'
        )
        
        # Enviar email de confirmación de cancelación
        send_cancellation_email(subscription)
        
    except UserSubscription.DoesNotExist:
        messages.error(request, 'No se encontró tu suscripción.')
    
    return redirect('users:manage_subscription')


def send_cancellation_email(subscription):
    """Envía email confirmando la cancelación"""
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from datetime import datetime
    
    subject = 'Confirmación de cancelación de suscripción'
    
    html_message = render_to_string('users/emails/subscription_cancelled.html', {
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
