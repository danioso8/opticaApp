# -*- coding: utf-8 -*-
"""
Servicio de integración con Stripe
https://stripe.com/docs/api
"""
import stripe
from django.conf import settings
from decimal import Decimal
from apps.payments.models import Transaction, PaymentMethod
from apps.organizations.models import OrganizationModule


class StripeService:
    """
    Servicio para procesar pagos con Stripe
    """
    
    def __init__(self):
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
        self.publishable_key = getattr(settings, 'STRIPE_PUBLIC_KEY', '')
    
    def create_payment_intent(self, organization, amount, currency='usd', metadata=None):
        """
        Crear un Payment Intent en Stripe
        
        Args:
            organization: Organization instance
            amount: Decimal - Monto en la moneda especificada
            currency: str - Código de moneda (usd, cop, etc.)
            metadata: dict - Metadata adicional
        
        Returns:
            dict con client_secret y payment_intent_id
        """
        try:
            # Convertir a centavos (Stripe usa centavos)
            amount_cents = int(amount * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata={
                    'organization_id': str(organization.id),
                    'organization_name': organization.name,
                    **(metadata or {})
                },
                automatic_payment_methods={'enabled': True},
            )
            
            return {
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'amount': amount,
                'currency': currency,
            }
        
        except stripe.error.StripeError as e:
            raise Exception(f"Error en Stripe: {str(e)}")
    
    def confirm_payment(self, payment_intent_id):
        """
        Confirmar un pago y obtener el status
        
        Returns:
            dict con status y detalles del pago
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'status': payment_intent.status,
                'amount': Decimal(payment_intent.amount) / 100,
                'currency': payment_intent.currency,
                'payment_method': payment_intent.payment_method,
                'metadata': payment_intent.metadata,
            }
        
        except stripe.error.StripeError as e:
            raise Exception(f"Error al confirmar pago: {str(e)}")
    
    def save_payment_method(self, organization, payment_method_id):
        """
        Guardar un método de pago para uso futuro
        
        Args:
            organization: Organization instance
            payment_method_id: str - ID del PaymentMethod de Stripe
        
        Returns:
            PaymentMethod instance
        """
        try:
            # Obtener detalles del payment method desde Stripe
            pm = stripe.PaymentMethod.retrieve(payment_method_id)
            
            # Determinar tipo de tarjeta
            card_brand_map = {
                'visa': 'visa',
                'mastercard': 'mastercard',
                'amex': 'amex',
                'diners': 'diners',
            }
            
            # Crear registro local
            payment_method = PaymentMethod.objects.create(
                organization=organization,
                payment_type='card',
                card_brand=card_brand_map.get(pm.card.brand, 'visa'),
                last_four=pm.card.last4,
                expiry_month=pm.card.exp_month,
                expiry_year=pm.card.exp_year,
                stripe_payment_method_id=payment_method_id,
            )
            
            return payment_method
        
        except stripe.error.StripeError as e:
            raise Exception(f"Error al guardar método de pago: {str(e)}")
    
    def process_module_purchase(self, organization, module_ids, payment_method_id=None):
        """
        Procesar compra de módulos
        
        Args:
            organization: Organization instance
            module_ids: list of int - IDs de módulos a comprar
            payment_method_id: str - ID del payment method (opcional)
        
        Returns:
            dict con transaction y payment_intent
        """
        from apps.organizations.models import PlanFeature, ModulePricing
        
        # Obtener módulos
        modules = PlanFeature.objects.filter(id__in=module_ids, is_active=True)
        
        # Calcular total
        subtotal = sum(m.price_monthly or Decimal('0.00') for m in modules)
        
        # Aplicar descuentos
        pricing = ModulePricing.objects.first()
        module_count = len(module_ids)
        discount_percent = 0
        
        if module_count >= 7 and pricing:
            discount_percent = pricing.discount_7_modules
        elif module_count >= 4 and pricing:
            discount_percent = pricing.discount_4_modules
        
        discount_amount = subtotal * Decimal(str(discount_percent)) / Decimal('100')
        total = subtotal - discount_amount
        
        # Crear transacción
        transaction = Transaction.objects.create(
            organization=organization,
            transaction_type='module_purchase',
            status='pending',
            amount=total,
            currency='USD',
            payment_gateway='stripe',
            metadata={
                'module_ids': module_ids,
                'subtotal': float(subtotal),
                'discount_percent': discount_percent,
                'discount_amount': float(discount_amount),
            }
        )
        
        # Agregar módulos a la transacción
        transaction.modules.set(modules)
        
        # Crear payment intent
        payment_intent = self.create_payment_intent(
            organization=organization,
            amount=total,
            currency='usd',
            metadata={
                'transaction_id': str(transaction.id),
                'transaction_number': transaction.transaction_number,
                'module_count': module_count,
            }
        )
        
        # Guardar payment intent ID
        transaction.gateway_transaction_id = payment_intent['payment_intent_id']
        transaction.save()
        
        return {
            'transaction': transaction,
            'payment_intent': payment_intent,
            'total': total,
            'modules': list(modules.values('id', 'name', 'price_monthly')),
        }
    
    def activate_purchased_modules(self, transaction_id):
        """
        Activar módulos después de un pago exitoso
        
        Args:
            transaction_id: UUID - ID de la transacción
        """
        transaction = Transaction.objects.get(id=transaction_id)
        
        if transaction.status != 'completed':
            raise Exception("La transacción no está completada")
        
        # Obtener módulos de la transacción
        modules = transaction.modules.all()
        
        # Activar cada módulo
        for module in modules:
            OrganizationModule.objects.update_or_create(
                organization=transaction.organization,
                module=module,
                defaults={
                    'is_active': True,
                    'price_paid': module.price_monthly,
                    'auto_renew': True,
                }
            )
        
        # Actualizar estado del trial si existe
        from apps.organizations.models import TrialStatus
        try:
            trial = TrialStatus.objects.get(organization=transaction.organization)
            trial.state = 'converted'
            trial.save()
        except TrialStatus.DoesNotExist:
            pass
        
        return modules
    
    def create_refund(self, transaction_id, amount=None, reason=None):
        """
        Crear un reembolso
        
        Args:
            transaction_id: UUID - ID de la transacción original
            amount: Decimal - Monto a reembolsar (None = total)
            reason: str - Razón del reembolso
        
        Returns:
            Transaction instance del reembolso
        """
        original_transaction = Transaction.objects.get(id=transaction_id)
        
        if not original_transaction.gateway_transaction_id:
            raise Exception("Transacción no tiene ID de pasarela")
        
        try:
            # Crear refund en Stripe
            refund_amount = amount or original_transaction.amount
            refund_cents = int(refund_amount * 100)
            
            refund = stripe.Refund.create(
                payment_intent=original_transaction.gateway_transaction_id,
                amount=refund_cents,
                reason=reason or 'requested_by_customer',
            )
            
            # Crear transacción de reembolso
            refund_transaction = Transaction.objects.create(
                organization=original_transaction.organization,
                transaction_type='refund',
                status='completed',
                amount=refund_amount,
                currency=original_transaction.currency,
                payment_gateway='stripe',
                gateway_transaction_id=refund.id,
                metadata={
                    'original_transaction_id': str(original_transaction.id),
                    'reason': reason,
                }
            )
            
            return refund_transaction
        
        except stripe.error.StripeError as e:
            raise Exception(f"Error al crear reembolso: {str(e)}")
