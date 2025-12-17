"""
Cliente SOAP para comunicación con webservices de la DIAN
"""
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, Tuple, Optional
from xml.etree import ElementTree as ET
import base64
from datetime import datetime


class DianSoapClient:
    """
    Cliente para interactuar con los servicios web SOAP de la DIAN.
    
    Endpoints DIAN:
    - Habilitación (Pruebas): https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc
    - Producción: https://vpfe.dian.gov.co/WcfDianCustomerServices.svc
    """
    
    # URLs de los servicios DIAN
    URL_HABILITACION = "https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc"
    URL_PRODUCCION = "https://vpfe.dian.gov.co/WcfDianCustomerServices.svc"
    
    # Namespaces SOAP
    SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
    DIAN_NS = "http://wcf.dian.colombia"
    
    def __init__(self, ambiente: str = 'habilitacion', usuario: Optional[str] = None, password: Optional[str] = None):
        """
        Inicializa el cliente SOAP.
        
        Args:
            ambiente: 'habilitacion' o 'produccion'
            usuario: Usuario DIAN (opcional, para algunos servicios)
            password: Contraseña DIAN (opcional)
        """
        self.ambiente = ambiente
        self.url = self.URL_HABILITACION if ambiente == 'habilitacion' else self.URL_PRODUCCION
        self.usuario = usuario
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': ''
        })
    
    def enviar_factura(self, xml_firmado: str, nit_emisor: str) -> Tuple[bool, Dict]:
        """
        Envía una factura electrónica a la DIAN.
        
        Args:
            xml_firmado: XML de la factura firmado digitalmente
            nit_emisor: NIT del emisor
            
        Returns:
            Tuple[bool, Dict]: (exito, respuesta_parseada)
        """
        # Convertir XML a base64
        xml_base64 = base64.b64encode(xml_firmado.encode('utf-8')).decode('utf-8')
        
        # Construir envelope SOAP
        soap_envelope = self._construir_envelope_envio(xml_base64, nit_emisor)
        
        try:
            # Enviar request
            response = self.session.post(
                self.url,
                data=soap_envelope,
                timeout=60
            )
            response.raise_for_status()
            
            # Parsear respuesta
            resultado = self._parsear_respuesta_envio(response.text)
            
            return resultado['exitoso'], resultado
            
        except requests.exceptions.RequestException as e:
            return False, {
                'exitoso': False,
                'error': f'Error de conexión con DIAN: {str(e)}',
                'codigo_error': 'CONNECTION_ERROR'
            }
        except Exception as e:
            return False, {
                'exitoso': False,
                'error': f'Error procesando respuesta: {str(e)}',
                'codigo_error': 'PARSE_ERROR'
            }
    
    def consultar_estado(self, cufe: str) -> Tuple[bool, Dict]:
        """
        Consulta el estado de una factura en la DIAN.
        
        Args:
            cufe: CUFE de la factura
            
        Returns:
            Tuple[bool, Dict]: (encontrada, info_estado)
        """
        soap_envelope = self._construir_envelope_consulta(cufe)
        
        try:
            response = self.session.post(
                self.url,
                data=soap_envelope,
                timeout=30
            )
            response.raise_for_status()
            
            resultado = self._parsear_respuesta_consulta(response.text)
            return resultado['encontrada'], resultado
            
        except requests.exceptions.RequestException as e:
            return False, {
                'encontrada': False,
                'error': f'Error de conexión: {str(e)}'
            }
    
    def _construir_envelope_envio(self, xml_base64: str, nit_emisor: str) -> str:
        """Construye el envelope SOAP para envío de factura."""
        envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="{self.SOAP_NS}" xmlns:wcf="{self.DIAN_NS}">
    <soap:Header/>
    <soap:Body>
        <wcf:SendBillSync>
            <wcf:fileName>face_{nit_emisor}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xml</wcf:fileName>
            <wcf:contentFile>{xml_base64}</wcf:contentFile>
        </wcf:SendBillSync>
    </soap:Body>
</soap:Envelope>"""
        return envelope
    
    def _construir_envelope_consulta(self, cufe: str) -> str:
        """Construye el envelope SOAP para consulta de estado."""
        envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="{self.SOAP_NS}" xmlns:wcf="{self.DIAN_NS}">
    <soap:Header/>
    <soap:Body>
        <wcf:GetStatus>
            <wcf:trackId>{cufe}</wcf:trackId>
        </wcf:GetStatus>
    </soap:Body>
</soap:Envelope>"""
        return envelope
    
    def _parsear_respuesta_envio(self, xml_response: str) -> Dict:
        """
        Parsea la respuesta SOAP del envío de factura.
        
        Returns:
            Dict con estructura:
            {
                'exitoso': bool,
                'codigo_respuesta': str,
                'mensaje': str,
                'errores': list,
                'advertencias': list,
                'cufe': str,
                'fecha_validacion': datetime
            }
        """
        try:
            root = ET.fromstring(xml_response)
            
            # Buscar el resultado
            ns = {'s': self.SOAP_NS, 'wcf': self.DIAN_NS}
            result = root.find('.//wcf:SendBillSyncResult', ns)
            
            if result is None:
                return {
                    'exitoso': False,
                    'error': 'Respuesta inválida de DIAN',
                    'xml_respuesta': xml_response
                }
            
            # Extraer información
            is_valid = result.find('.//wcf:IsValid', ns)
            status_code = result.find('.//wcf:StatusCode', ns)
            status_description = result.find('.//wcf:StatusDescription', ns)
            status_message = result.find('.//wcf:StatusMessage', ns)
            
            # Errores y advertencias
            errores = []
            advertencias = []
            
            error_messages = result.findall('.//wcf:ErrorMessage', ns)
            for error in error_messages:
                errores.append(error.text)
            
            return {
                'exitoso': is_valid.text.lower() == 'true' if is_valid is not None else False,
                'codigo_respuesta': status_code.text if status_code is not None else '',
                'descripcion': status_description.text if status_description is not None else '',
                'mensaje': status_message.text if status_message is not None else '',
                'errores': errores,
                'advertencias': advertencias,
                'xml_respuesta': xml_response,
                'fecha_validacion': datetime.now()
            }
            
        except ET.ParseError as e:
            return {
                'exitoso': False,
                'error': f'Error parseando XML de respuesta: {str(e)}',
                'xml_respuesta': xml_response
            }
    
    def _parsear_respuesta_consulta(self, xml_response: str) -> Dict:
        """Parsea la respuesta de consulta de estado."""
        try:
            root = ET.fromstring(xml_response)
            ns = {'s': self.SOAP_NS, 'wcf': self.DIAN_NS}
            
            result = root.find('.//wcf:GetStatusResult', ns)
            
            if result is None:
                return {'encontrada': False, 'error': 'No se encontró la factura'}
            
            status = result.find('.//wcf:Status', ns)
            status_message = result.find('.//wcf:StatusMessage', ns)
            
            return {
                'encontrada': True,
                'estado': status.text if status is not None else 'Desconocido',
                'mensaje': status_message.text if status_message is not None else '',
                'xml_respuesta': xml_response
            }
            
        except ET.ParseError:
            return {'encontrada': False, 'error': 'Error parseando respuesta'}
    
    def validar_conexion(self) -> Tuple[bool, str]:
        """
        Valida que se pueda conectar con los servicios DIAN.
        
        Returns:
            Tuple[bool, str]: (conectado, mensaje)
        """
        try:
            # Hacer un request simple para verificar conectividad
            response = requests.get(
                self.url + '?wsdl',
                timeout=10
            )
            
            if response.status_code == 200:
                return True, f"✅ Conectado a DIAN ({self.ambiente})"
            else:
                return False, f"❌ Error de conexión: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return False, f"❌ No se pudo conectar con DIAN: {str(e)}"


class DianMockClient(DianSoapClient):
    """
    Cliente mock para pruebas sin conectar a DIAN real.
    Simula respuestas de DIAN para desarrollo.
    """
    
    def __init__(self):
        super().__init__(ambiente='habilitacion')
        self.facturas_enviadas = {}
    
    def enviar_factura(self, xml_firmado: str, nit_emisor: str) -> Tuple[bool, Dict]:
        """Simula envío de factura."""
        # Extraer CUFE del XML
        try:
            root = ET.fromstring(xml_firmado)
            cufe_elem = root.find('.//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}UUID')
            cufe = cufe_elem.text if cufe_elem is not None else 'CUFE-MOCK-123456'
            
            # Guardar en memoria
            self.facturas_enviadas[cufe] = {
                'xml': xml_firmado,
                'nit_emisor': nit_emisor,
                'fecha_envio': datetime.now(),
                'estado': 'Aprobada'
            }
            
            return True, {
                'exitoso': True,
                'codigo_respuesta': '00',
                'descripcion': 'Procesamiento exitoso',
                'mensaje': '✅ Factura aprobada por DIAN (MODO PRUEBA)',
                'errores': [],
                'advertencias': [],
                'cufe': cufe,
                'fecha_validacion': datetime.now()
            }
            
        except Exception as e:
            return False, {
                'exitoso': False,
                'error': f'Error en mock: {str(e)}'
            }
    
    def consultar_estado(self, cufe: str) -> Tuple[bool, Dict]:
        """Simula consulta de estado."""
        if cufe in self.facturas_enviadas:
            factura = self.facturas_enviadas[cufe]
            return True, {
                'encontrada': True,
                'estado': factura['estado'],
                'mensaje': 'Factura encontrada en sistema mock',
                'fecha_envio': factura['fecha_envio'].isoformat()
            }
        else:
            return False, {
                'encontrada': False,
                'error': 'Factura no encontrada en sistema mock'
            }
    
    def validar_conexion(self) -> Tuple[bool, str]:
        """Simula validación de conexión."""
        return True, "✅ Cliente Mock activado (sin conexión real a DIAN)"
