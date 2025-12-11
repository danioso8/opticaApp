"""
Servicio de integración con Wompi API
Documentación: https://docs.wompi.co/docs/
"""

import requests
import hashlib
import logging
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from typing import Dict, Optional, Tuple
from .models import Transaction, PaymentMethod, UserSubscription
import json as json_module

logger = logging.getLogger(__name__)


class WompiService:
    """Servicio para interactuar con la API de Wompi"""
    
    def __init__(self):
        self.public_key = getattr(settings, 'WOMPI_PUBLIC_KEY', '')
        self.private_key = getattr(settings, 'WOMPI_PRIVATE_KEY', '')
        self.events_secret = getattr(settings, 'WOMPI_EVENTS_SECRET', '')
        self.integrity_secret = getattr(settings, 'WOMPI_INTEGRITY_SECRET', '')
        self.base_url = getattr(settings, 'WOMPI_BASE_URL', 'https://production.wompi.co/v1')
        self.test_mode = getattr(settings, 'WOMPI_TEST_MODE', True)
        
        if self.test_mode:
            self.base_url = 'https://sandbox.wompi.co/v1'
    
    def _get_headers(self, use_private_key=False):
        """Obtiene los headers para las peticiones"""
        # Las llaves ya vienen con el prefijo (pub_test_, prv_prod_, etc)
        auth_key = self.private_key if use_private_key else self.public_key
        
        return {
            'Authorization': f'Bearer {auth_key}',
            'Content-Type': 'application/json',
        }
    
    def get_acceptance_token(self) -> Optional[str]:
        """
        Obtiene el token de aceptación de términos y condiciones
        
        Returns:
            Token de aceptación o None si falla
        """
        try:
            url = f"{self.base_url}/merchants/{self.public_key}"
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                data = response.json()
                presigned_acceptance = data.get('data', {}).get('presigned_acceptance', {})
                return presigned_acceptance.get('acceptance_token')
            else:
                logger.error(f"Error al obtener acceptance token: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Excepción al obtener acceptance token: {str(e)}")
            return None
    
    def create_payment_source(self, token_card: str) -> Optional[Dict]:
        """
        Crea una fuente de pago (tokeniza tarjeta)
        
        Args:
            token_card: Token de la tarjeta obtenida del widget de Wompi
            
        Returns:
            Dict con la información de la fuente de pago o None si falla
        """
        try:
            url = f"{self.base_url}/payment_sources"
            data = {
                "type": "CARD",
                "token": token_card,
                "customer_email": "",  # Opcional
                "acceptance_token": ""  # Token de aceptación de términos
            }
            
            response = requests.post(
                url,
                json=data,
                headers=self._get_headers(use_private_key=True)
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                logger.error(f"Error al crear payment source: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Excepción al crear payment source: {str(e)}")
            return None
    
    def create_transaction(
        self,
        amount_in_cents: int,
        currency: str,
        customer_email: str,
        payment_method_id: int,
        reference: str,
        subscription_id: Optional[int] = None
    ) -> Tuple[bool, Optional[Transaction], Optional[str]]:
        """
        Crea una transacción de pago
        
        Args:
            amount_in_cents: Monto en centavos
            currency: Moneda (COP, USD, etc.)
            customer_email: Email del cliente
            payment_method_id: ID del método de pago guardado
            reference: Referencia única de la transacción
            subscription_id: ID de la suscripción (opcional)
            
        Returns:
            Tuple (success, transaction_obj, error_message)
        """
        try:
            # Obtener el payment method
            payment_method = PaymentMethod.objects.get(id=payment_method_id)
            
            # Crear la transacción en BD
            transaction = Transaction.objects.create(
                user=payment_method.user,
                subscription_id=subscription_id,
                payment_method=payment_method,
                transaction_type='subscription_payment' if subscription_id else 'subscription_payment',
                amount=Decimal(amount_in_cents) / 100,
                currency=currency,
                status='PENDING',
                wompi_reference=reference
            )
            
            # Crear la transacción en Wompi
            url = f"{self.base_url}/transactions"
            
            # Obtener acceptance token
            acceptance_token = self.get_acceptance_token()
            if not acceptance_token:
                return False, None, "No se pudo obtener el token de aceptación"
            
            # Generar signature
            integrity = self._generate_integrity_signature(
                reference=reference,
                amount_in_cents=amount_in_cents,
                currency=currency
            )
            
            data = {
                "acceptance_token": acceptance_token,
                "amount_in_cents": amount_in_cents,
                "currency": currency,
                "customer_email": customer_email,
                "payment_method": {
                    "type": "CARD",
                    "token": payment_method.wompi_token_id,
                    "installments": 1
                },
                "reference": reference,
                "signature": integrity
            }
            
            response = requests.post(
                url,
                json=data,
                headers=self._get_headers(use_private_key=True)
            )
            
            response_data = response.json()
            
            if response.status_code in [200, 201]:
                transaction.wompi_transaction_id = response_data.get('data', {}).get('id')
                transaction.status = response_data.get('data', {}).get('status', 'PENDING')
                transaction.metadata = json_module.dumps(response_data)  # Convertir a JSON string
                transaction.save()
                
                return True, transaction, None
            else:
                error_msg = response_data.get('error', {}).get('messages', {})
                transaction.mark_as_declined(str(error_msg))
                return False, transaction, str(error_msg)
                
        except PaymentMethod.DoesNotExist:
            return False, None, "Método de pago no encontrado"
        except Exception as e:
            logger.error(f"Error al crear transacción: {str(e)}")
            if 'transaction' in locals():
                transaction.mark_as_declined(str(e))
            return False, None, str(e)
    
    def get_transaction(self, transaction_id: str) -> Optional[Dict]:
        """
        Consulta el estado de una transacción
        
        Args:
            transaction_id: ID de la transacción en Wompi
            
        Returns:
            Dict con la información de la transacción
        """
        try:
            url = f"{self.base_url}/transactions/{transaction_id}"
            response = requests.get(
                url,
                headers=self._get_headers(use_private_key=True)
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error al consultar transacción: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Excepción al consultar transacción: {str(e)}")
            return None
    
    def create_payment_link(
        self,
        amount_in_cents: int,
        currency: str,
        customer_email: str,
        reference: str,
        redirect_url: str,
        description: str = "Pago de suscripción"
    ) -> Optional[Dict]:
        """
        Crea un link de pago
        
        Args:
            amount_in_cents: Monto en centavos
            currency: Moneda
            customer_email: Email del cliente
            reference: Referencia única
            redirect_url: URL de redirección después del pago
            description: Descripción del pago
            
        Returns:
            Dict con la información del link de pago
        """
        try:
            url = f"{self.base_url}/payment_links"
            
            # Generar signature
            integrity = self._generate_integrity_signature(
                reference=reference,
                amount_in_cents=amount_in_cents,
                currency=currency
            )
            
            data = {
                "name": description,
                "description": description,
                "single_use": True,
                "collect_shipping": False,
                "currency": currency,
                "amount_in_cents": amount_in_cents,
                "reference": reference,
                "customer_email": customer_email,
                "redirect_url": redirect_url,
                "signature:integrity": integrity
            }
            
            response = requests.post(
                url,
                json=data,
                headers=self._get_headers(use_private_key=True)
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Error al crear payment link: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Excepción al crear payment link: {str(e)}")
            return None
    
    def verify_signature(self, event_data: Dict) -> bool:
        """
        Verifica la firma de un evento de webhook
        
        Args:
            event_data: Datos del evento
            
        Returns:
            True si la firma es válida
        """
        try:
            signature = event_data.get('signature', {})
            checksum = signature.get('checksum', '')
            properties = signature.get('properties', [])
            
            # Construir string para verificar
            values = []
            for prop in properties:
                value = self._get_nested_value(event_data, prop)
                values.append(str(value))
            
            concat_values = ''.join(values)
            concat_with_secret = concat_values + self.events_secret
            
            # Calcular hash
            calculated_checksum = hashlib.sha256(concat_with_secret.encode()).hexdigest()
            
            return calculated_checksum == checksum
            
        except Exception as e:
            logger.error(f"Error al verificar firma: {str(e)}")
            return False
    
    def _generate_integrity_signature(
        self,
        reference: str,
        amount_in_cents: int,
        currency: str
    ) -> str:
        """
        Genera la firma de integridad para transacciones
        
        Args:
            reference: Referencia de la transacción
            amount_in_cents: Monto en centavos
            currency: Moneda
            
        Returns:
            Firma SHA256
        """
        concat_string = f"{reference}{amount_in_cents}{currency}{self.integrity_secret}"
        return hashlib.sha256(concat_string.encode()).hexdigest()
    
    def _get_nested_value(self, data: Dict, key_path: str):
        """
        Obtiene un valor anidado de un diccionario usando punto como separador
        
        Args:
            data: Diccionario
            key_path: Ruta del valor (ej: "data.transaction.id")
            
        Returns:
            Valor encontrado o None
        """
        keys = key_path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        
        return value
    
    def tokenize_card_and_save(
        self,
        user,
        card_token: str,
        card_data: Dict
    ) -> Tuple[bool, Optional[PaymentMethod], Optional[str]]:
        """
        Tokeniza una tarjeta y la guarda en BD
        
        Args:
            user: Usuario
            card_token: Token de la tarjeta de Wompi
            card_data: Información de la tarjeta (last_four, brand, holder_name)
            
        Returns:
            Tuple (success, payment_method, error_message)
        """
        try:
            # Verificar si ya existe una tarjeta con este token
            if PaymentMethod.objects.filter(wompi_token_id=card_token).exists():
                return False, None, "Esta tarjeta ya está registrada"
            
            # Crear el método de pago
            payment_method = PaymentMethod.objects.create(
                user=user,
                wompi_token_id=card_token,
                card_last_four=card_data.get('last_four', ''),
                card_brand=card_data.get('brand', '').upper(),
                card_type=card_data.get('type', 'CREDIT').upper(),
                card_holder_name=card_data.get('holder_name', ''),
                is_default=not PaymentMethod.objects.filter(user=user).exists()
            )
            
            return True, payment_method, None
            
        except Exception as e:
            logger.error(f"Error al guardar método de pago: {str(e)}")
            return False, None, str(e)


# Instancia global del servicio
wompi_service = WompiService()
