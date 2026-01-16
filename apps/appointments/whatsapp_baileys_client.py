"""
Cliente Python para comunicarse con el servidor WhatsApp (Baileys)
Con sistema de auto-recuperación de sesiones corruptas
"""
import requests
import logging
import time
from django.conf import settings

logger = logging.getLogger(__name__)


class WhatsAppBaileysClient:
    """Cliente para el servidor WhatsApp con Baileys y auto-recuperación"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'WHATSAPP_SERVER_URL', 'http://localhost:3000')
        self.api_key = getattr(settings, 'WHATSAPP_SERVER_API_KEY', '')
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }
        self.auto_recovery_enabled = True  # Habilitar auto-recuperación por defecto
    
    def _make_request(self, method, endpoint, data=None):
        """Hacer petición HTTP al servidor"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=self.headers, timeout=10)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición a WhatsApp server: {e}")
            return None
    
    def start_session(self, organization_id):
        """Iniciar sesión de WhatsApp para una organización"""
        data = {'organization_id': str(organization_id)}
        return self._make_request('POST', '/api/start-session', data)
    
    def get_qr(self, organization_id):
        """Obtener código QR para escanear"""
        return self._make_request('GET', f'/api/qr/{organization_id}')
    
    def get_status(self, organization_id):
        """Obtener estado de la conexión"""
        return self._make_request('GET', f'/api/status/{organization_id}')
    
    def force_clean_session(self, organization_id):
        """Forzar limpieza de sesión corrupta"""
        data = {'organization_id': str(organization_id)}
        result = self._make_request('POST', '/api/force-clean-session', data)
        logger.info(f"🔧 Sesión limpiada para org {organization_id}: {result}")
        return result
    
    def verify_and_recover_connection(self, organization_id, max_retries=2):
        """
        Verificar conexión WhatsApp y auto-recuperar si está desconectado
        
        Args:
            organization_id: ID de la organización
            max_retries: Número máximo de intentos de recuperación
            
        Returns:
            tuple: (is_connected, phone_number or None)
        """
        try:
            # Verificar estado actual
            status = self.get_status(organization_id)
            
            if not status:
                logger.warning(f"❌ No se pudo obtener estado de WhatsApp para org {organization_id}")
                return False, None
            
            current_status = status.get('status', 'unknown')
            phone = status.get('phone_number') or status.get('phone')  # Soportar ambos nombres de campo
            
            # Si está conectado, retornar OK
            if current_status == 'connected' and phone:
                logger.info(f"✅ WhatsApp conectado para org {organization_id}: {phone}")
                return True, phone
            
            # Si no está conectado y auto-recuperación está habilitada
            if self.auto_recovery_enabled and current_status in ['disconnected', 'qr_required', 'connecting']:
                logger.warning(f"⚠️  WhatsApp desconectado para org {organization_id}. Estado: {current_status}")
                logger.info(f"🔄 Iniciando auto-recuperación de sesión...")
                
                for attempt in range(max_retries):
                    try:
                        # Limpiar sesión corrupta
                        clean_result = self.force_clean_session(organization_id)
                        
                        if clean_result and clean_result.get('success'):
                            logger.info(f"✨ Sesión limpiada exitosamente. Esperando regeneración...")
                            
                            # Esperar a que se genere nuevo QR y potencial reconexión
                            time.sleep(3)
                            
                            # Verificar si se reconectó automáticamente
                            new_status = self.get_status(organization_id)
                            if new_status and new_status.get('status') == 'connected':
                                logger.info(f"🎉 Auto-recuperación exitosa para org {organization_id}")
                                return True, new_status.get('phone')
                            else:
                                logger.warning(f"⏳ Sesión limpiada pero requiere escaneo de QR para org {organization_id}")
                                return False, None
                        else:
                            logger.error(f"❌ Fallo en limpieza de sesión. Intento {attempt + 1}/{max_retries}")
                            
                    except Exception as e:
                        logger.error(f"Error en auto-recuperación (intento {attempt + 1}): {str(e)}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Esperar antes del siguiente intento
                
                logger.error(f"❌ Auto-recuperación fallida después de {max_retries} intentos")
                return False, None
            
            # No está conectado y no se puede auto-recuperar
            logger.warning(f"❌ WhatsApp no conectado para org {organization_id}. Estado: {current_status}")
            return False, None
            
        except Exception as e:
            logger.error(f"Error verificando conexión WhatsApp: {str(e)}")
            return False, None
    
    def send_message(self, organization_id, phone, message, auto_recover=True):
        """
        Enviar mensaje de WhatsApp con verificación y auto-recuperación
        
        Args:
            organization_id: ID de la organización
            phone: Número de teléfono destino
            message: Mensaje a enviar
            auto_recover: Si True, intenta auto-recuperar conexión si falla
            
        Returns:
            dict: Resultado del envío o None si falla
        """
        # Verificar y recuperar conexión si es necesario
        if auto_recover:
            is_connected, org_phone = self.verify_and_recover_connection(organization_id)
            
            if not is_connected:
                logger.error(f"❌ No se puede enviar mensaje: WhatsApp no conectado para org {organization_id}")
                logger.info(f"💡 El usuario debe escanear el código QR en el módulo de WhatsApp")
                return None
        
        # Intentar enviar mensaje
        data = {
            'organization_id': str(organization_id),
            'phone': phone,
            'message': message
        }
        
        result = self._make_request('POST', '/api/send-message', data)
        
        if result and result.get('success'):
            logger.info(f"✅ Mensaje enviado exitosamente a {phone}")
        else:
            logger.error(f"❌ Error enviando mensaje a {phone}: {result}")
        
        return result
    
    def logout(self, organization_id):
        """Cerrar sesión de WhatsApp"""
        data = {'organization_id': str(organization_id)}
        return self._make_request('POST', '/api/logout', data)
    
    def clear_session(self, organization_id):
        """Limpiar sesión corrupta de WhatsApp"""
        data = {'organization_id': str(organization_id)}
        return self._make_request('POST', '/api/clear-session', data)
    
    def list_sessions(self):
        """Listar todas las sesiones activas"""
        return self._make_request('GET', '/api/sessions')
    
    def healthcheck(self):
        """Verificar si el servidor está activo"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False


# Instancia global
whatsapp_baileys_client = WhatsAppBaileysClient()
