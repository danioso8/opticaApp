# -*- coding: utf-8 -*-
"""
Servicio de integración con Wompi (Colombia)
https://docs.wompi.co/docs/
"""
import requests
from django.conf import settings
from decimal import Decimal
from apps.payments.models import Transaction
from apps.organizations.models import OrganizationModule


class WompiService:
    """
    Servicio para procesar pagos con Wompi
    Compatible con pagos en Colombia (PSE, Nequi, Tarjetas)
    """
    
    def __init__(self):
        self.public_key = getattr(settings, 'WOMPI_PUBLIC_KEY', '')
        self.private_key = getattr(settings, 'WOMPI_PRIVATE_KEY', '')
        self.base_url = 'https://production.wompi.co/v1'
        self.sandbox_url = 'https://sandbox.wompi.co/v1'
        self.is_sandbox = getattr(settings, 'WOMPI_SANDBOX', True)
        self.api_url = self.sandbox_url if self.is_sandbox else self.base_url
    
    def create_transaction(self, organization, amount, currency='COP', reference=None, metadata=None):
        """
        Crear una transacción en Wompi
        
        Args:
            organization: Organization instance
            amount: Decimal - Monto en centavos (Wompi usa centavos)
            currency: str - COP por defecto
            reference: str - Referencia única
            metadata: dict - Metadata adicional
        
        Returns:
            dict con datos de la transacción
        """
        # Convertir a centavos
        amount_cents = int(amount * 100)
        
        # Generar referencia única si no se proporciona
        if not reference:
            from apps.payments.models import Transaction as TransactionModel
            import uuid
            reference = f"ORG-{organization.id}-{uuid.uuid4().hex[:8]}"
        
        payload = {
            'amount_in_cents': amount_cents,
            'currency': currency,
            'customer_email': organization.owner.email if organization.owner else 'noreply@optikaapp.com',
            'reference': reference,
            'redirect_url': f"{settings.SITE_URL}/dashboard/payments/success/",
            'metadata': {
                'organization_id': str(organization.id),
                'organization_name': organization.name,
                **(metadata or {})
            }
        }
        
        headers = {
            'Authorization': f'Bearer {self.public_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                f'{self.api_url}/transactions',
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                'id': data['data']['id'],
                'reference': reference,
                'amount': amount,
                'currency': currency,
                'payment_link': data['data'].get('payment_link_url'),
                'status': data['data'].get('status'),
            }
        
        except requests.RequestException as e:
            raise Exception(f"Error en Wompi: {str(e)}")
    
    def verify_transaction(self, transaction_id):
        """
        Verificar el estado de una transacción
        
        Args:
            transaction_id: str - ID de la transacción en Wompi
        
        Returns:
            dict con status y detalles
        """
        headers = {
            'Authorization': f'Bearer {self.private_key}',
        }
        
        try:
            response = requests.get(
                f'{self.api_url}/transactions/{transaction_id}',
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            transaction_data = data['data']
            
            return {
                'status': transaction_data['status'],  # APPROVED, DECLINED, PENDING
                'amount': Decimal(transaction_data['amount_in_cents']) / 100,
                'currency': transaction_data['currency'],
                'reference': transaction_data['reference'],
                'payment_method': transaction_data.get('payment_method_type'),
                'payment_method_info': transaction_data.get('payment_method'),
            }
        
        except requests.RequestException as e:
            raise Exception(f"Error al verificar transacción: {str(e)}")
    
    def process_module_purchase(self, organization, module_ids):
        """
        Procesar compra de módulos con Wompi
        
        Args:
            organization: Organization instance
            module_ids: list of int - IDs de módulos
        
        Returns:
            dict con transaction y payment_link
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
        
        # Convertir USD a COP (tasa aproximada - debería obtenerse de una API)
        # Por ahora, tasa fija de 1 USD = 4000 COP
        total_cop = total * Decimal('4000')
        
        # Crear transacción local
        transaction = Transaction.objects.create(
            organization=organization,
            transaction_type='module_purchase',
            status='pending',
            amount=total,
            currency='COP',
            payment_gateway='wompi',
            metadata={
                'module_ids': module_ids,
                'subtotal': float(subtotal),
                'discount_percent': discount_percent,
                'discount_amount': float(discount_amount),
                'amount_cop': float(total_cop),
            }
        )
        
        # Agregar módulos
        transaction.modules.set(modules)
        
        # Crear transacción en Wompi
        wompi_transaction = self.create_transaction(
            organization=organization,
            amount=total_cop,
            currency='COP',
            reference=transaction.transaction_number,
            metadata={
                'transaction_id': str(transaction.id),
                'module_count': module_count,
            }
        )
        
        # Guardar ID de Wompi
        transaction.gateway_transaction_id = wompi_transaction['id']
        transaction.save()
        
        return {
            'transaction': transaction,
            'wompi_transaction_id': wompi_transaction['id'],
            'payment_link': wompi_transaction['payment_link'],
            'total_usd': total,
            'total_cop': total_cop,
            'modules': list(modules.values('id', 'name', 'price_monthly')),
        }
    
    def activate_purchased_modules(self, transaction_id):
        """
        Activar módulos después de pago exitoso
        Igual que en Stripe
        """
        transaction = Transaction.objects.get(id=transaction_id)
        
        if transaction.status != 'completed':
            raise Exception("La transacción no está completada")
        
        modules = transaction.modules.all()
        
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
        
        # Actualizar trial
        from apps.organizations.models import TrialStatus
        try:
            trial = TrialStatus.objects.get(organization=transaction.organization)
            trial.state = 'converted'
            trial.save()
        except TrialStatus.DoesNotExist:
            pass
        
        return modules
    
    def create_payment_source(self, organization, token, customer_email):
        """
        Crear una fuente de pago tokenizada
        
        Args:
            organization: Organization instance
            token: str - Token de la tarjeta
            customer_email: str - Email del cliente
        
        Returns:
            dict con datos de la fuente de pago
        """
        payload = {
            'type': 'CARD',
            'token': token,
            'customer_email': customer_email,
            'acceptance_token': self.get_acceptance_token(),
        }
        
        headers = {
            'Authorization': f'Bearer {self.private_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                f'{self.api_url}/payment_sources',
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            return data['data']
        
        except requests.RequestException as e:
            raise Exception(f"Error al crear fuente de pago: {str(e)}")
    
    def get_acceptance_token(self):
        """
        Obtener token de aceptación de términos y condiciones
        Requerido por Wompi para Colombia
        """
        headers = {
            'Authorization': f'Bearer {self.public_key}',
        }
        
        try:
            response = requests.get(
                f'{self.api_url}/merchants/{self.public_key}',
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            return data['data']['presigned_acceptance']['acceptance_token']
        
        except requests.RequestException as e:
            # Retornar vacío si falla (solo para sandbox)
            return ''
