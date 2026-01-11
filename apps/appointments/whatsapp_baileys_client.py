"""
Cliente Python para comunicarse con el servidor WhatsApp (Baileys)
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class WhatsAppBaileysClient:
    """Cliente para el servidor WhatsApp con Baileys"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'WHATSAPP_SERVER_URL', 'http://localhost:3000')
        self.api_key = getattr(settings, 'WHATSAPP_SERVER_API_KEY', '')
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }
    
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
    
    def send_message(self, organization_id, phone, message):
        """Enviar mensaje de WhatsApp"""
        data = {
            'organization_id': str(organization_id),
            'phone': phone,
            'message': message
        }
        return self._make_request('POST', '/api/send-message', data)
    
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
