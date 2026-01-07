"""
Integración con los servicios web de la DIAN para nómina electrónica
"""
import requests
from datetime import datetime
from lxml import etree
import base64
from django.conf import settings


class DIANService:
    """
    Servicio para interactuar con la API de la DIAN
    """
    
    # URLs de servicios DIAN (Habilitación)
    DIAN_TEST_URL = "https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc"
    DIAN_PROD_URL = "https://vpfe.dian.gov.co/WcfDianCustomerServices.svc"
    
    def __init__(self, organization, test_mode=True):
        """
        Args:
            organization: Instancia de Organization
            test_mode: Si True usa ambiente de pruebas, si False producción
        """
        self.organization = organization
        self.test_mode = test_mode
        self.base_url = self.DIAN_TEST_URL if test_mode else self.DIAN_PROD_URL
        
        # Credenciales (deben estar en configuración de organización)
        self.software_id = getattr(settings, 'DIAN_SOFTWARE_ID', '')
        self.software_pin = getattr(settings, 'DIAN_SOFTWARE_PIN', '')
        self.test_set_id = getattr(settings, 'DIAN_TEST_SET_ID', '') if test_mode else None
    
    def send_document(self, electronic_document):
        """
        Envía un documento de nómina electrónica a la DIAN
        
        Args:
            electronic_document: Instancia de ElectronicPayrollDocument
            
        Returns:
            dict con respuesta de la DIAN
        """
        if not electronic_document.xml_signed:
            raise Exception("El documento debe estar firmado antes de enviarlo a la DIAN")
        
        # Preparar sobre SOAP
        soap_envelope = self._create_soap_envelope(electronic_document)
        
        # Enviar a DIAN
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://wcf.dian.colombia/IWcfDianCustomerServices/SendNominaElectronica'
        }
        
        try:
            response = requests.post(
                f"{self.base_url}?wsdl",
                data=soap_envelope,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            # Parsear respuesta
            result = self._parse_dian_response(response.text)
            
            # Actualizar documento con respuesta
            electronic_document.response_code = result.get('status_code')
            electronic_document.response_message = result.get('status_message')
            electronic_document.dian_tracking_id = result.get('tracking_id')
            
            if result.get('success'):
                electronic_document.estado = 'VALIDADO_DIAN'
            else:
                electronic_document.estado = 'RECHAZADO_DIAN'
            
            electronic_document.save()
            
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error al comunicarse con la DIAN: {str(e)}"
            electronic_document.estado = 'ERROR_ENVIO'
            electronic_document.response_message = error_msg
            electronic_document.save()
            
            return {
                'success': False,
                'error': error_msg
            }
    
    def _create_soap_envelope(self, electronic_document):
        """Crea el sobre SOAP para enviar a la DIAN"""
        
        # Base64 del XML firmado
        xml_b64 = base64.b64encode(
            electronic_document.xml_signed.encode('utf-8')
        ).decode('utf-8')
        
        # Namespace SOAP
        soap_ns = "http://schemas.xmlsoap.org/soap/envelope/"
        wcf_ns = "http://wcf.dian.colombia"
        
        # Crear sobre SOAP
        envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="{soap_ns}" xmlns:wcf="{wcf_ns}">
    <soap:Header/>
    <soap:Body>
        <wcf:SendNominaElectronica>
            <wcf:fileName>{electronic_document.cufe}.xml</wcf:fileName>
            <wcf:contentFile>{xml_b64}</wcf:contentFile>
            <wcf:testSetId>{self.test_set_id or ''}</wcf:testSetId>
        </wcf:SendNominaElectronica>
    </soap:Body>
</soap:Envelope>"""
        
        return envelope.encode('utf-8')
    
    def _parse_dian_response(self, response_xml):
        """Parsea la respuesta SOAP de la DIAN"""
        try:
            root = etree.fromstring(response_xml.encode('utf-8'))
            
            # Namespaces
            ns = {
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                's': 'http://schemas.xmlsoap.org/soap/envelope/',
                'b': 'http://wcf.dian.colombia'
            }
            
            # Buscar respuesta
            response = root.find('.//b:SendNominaElectronicaResponse', ns)
            
            if response is None:
                # Buscar fallas SOAP
                fault = root.find('.//soap:Fault', ns) or root.find('.//s:Fault', ns)
                if fault is not None:
                    fault_string = fault.find('.//faultstring')
                    error_msg = fault_string.text if fault_string is not None else "Error desconocido"
                    return {
                        'success': False,
                        'error': error_msg,
                        'status_code': 'FAULT',
                        'status_message': error_msg
                    }
            
            # Extraer campos de respuesta
            result = response.find('.//b:SendNominaElectronicaResult', ns)
            
            if result is None:
                return {
                    'success': False,
                    'error': 'Respuesta inválida de la DIAN'
                }
            
            status_code = result.findtext('.//b:StatusCode', default='', namespaces=ns)
            status_message = result.findtext('.//b:StatusMessage', default='', namespaces=ns)
            tracking_id = result.findtext('.//b:XmlDocumentKey', default='', namespaces=ns)
            
            # Códigos de éxito: 00 (Aceptado), 66 (Validación pendiente)
            success = status_code in ['00', '66']
            
            return {
                'success': success,
                'status_code': status_code,
                'status_message': status_message,
                'tracking_id': tracking_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error al parsear respuesta: {str(e)}"
            }
    
    def query_document_status(self, tracking_id):
        """
        Consulta el estado de un documento en la DIAN
        
        Args:
            tracking_id: ID de seguimiento retornado por la DIAN
            
        Returns:
            dict con estado del documento
        """
        soap_envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
               xmlns:wcf="http://wcf.dian.colombia">
    <soap:Header/>
    <soap:Body>
        <wcf:GetStatus>
            <wcf:trackId>{tracking_id}</wcf:trackId>
        </wcf:GetStatus>
    </soap:Body>
</soap:Envelope>"""
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://wcf.dian.colombia/IWcfDianCustomerServices/GetStatus'
        }
        
        try:
            response = requests.post(
                f"{self.base_url}?wsdl",
                data=soap_envelope.encode('utf-8'),
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            return self._parse_status_response(response.text)
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Error al consultar estado: {str(e)}"
            }
    
    def _parse_status_response(self, response_xml):
        """Parsea la respuesta de consulta de estado"""
        try:
            root = etree.fromstring(response_xml.encode('utf-8'))
            
            ns = {
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'b': 'http://wcf.dian.colombia'
            }
            
            result = root.find('.//b:GetStatusResult', ns)
            
            if result is None:
                return {
                    'success': False,
                    'error': 'Respuesta inválida'
                }
            
            status = result.findtext('.//b:Status', default='', namespaces=ns)
            status_code = result.findtext('.//b:StatusCode', default='', namespaces=ns)
            status_message = result.findtext('.//b:StatusMessage', default='', namespaces=ns)
            
            return {
                'success': True,
                'status': status,
                'status_code': status_code,
                'status_message': status_message
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error al parsear respuesta: {str(e)}"
            }
    
    def validate_numbering_range(self, prefix, from_number, to_number):
        """
        Solicita rango de numeración a la DIAN (solo en producción)
        
        Args:
            prefix: Prefijo de numeración (ej: 'NE')
            from_number: Número inicial
            to_number: Número final
            
        Returns:
            dict con respuesta de solicitud
        """
        if self.test_mode:
            return {
                'success': True,
                'message': 'En modo pruebas no se requiere solicitar rangos'
            }
        
        # TODO: Implementar solicitud de rango de numeración
        # Esta funcionalidad requiere un proceso adicional con la DIAN
        
        return {
            'success': False,
            'error': 'Funcionalidad no implementada'
        }


class PayrollDIANService:
    """
    Servicio de alto nivel para gestionar documentos de nómina con la DIAN
    """
    
    def __init__(self, organization):
        self.organization = organization
        self.dian_service = DIANService(organization, test_mode=True)
    
    def process_and_send_document(self, electronic_document):
        """
        Procesa un documento completo: genera XML, firma y envía a DIAN
        
        Args:
            electronic_document: Instancia de ElectronicPayrollDocument
            
        Returns:
            dict con resultado del proceso
        """
        from .xml_generator import PayrollXMLGenerator
        from .electronic_signature import PayrollDocumentSigner
        
        results = {
            'steps': [],
            'success': False
        }
        
        # Paso 1: Generar XML
        try:
            generator = PayrollXMLGenerator(electronic_document.payroll_period)
            xml_content = generator.generate()
            cufe = generator.generate_cufe(
                self.organization.nit,
                electronic_document.numero_documento,
                electronic_document.payroll_period.fecha_inicio,
                electronic_document.payroll_period.total_devengos,
                electronic_document.payroll_period.total_deducciones,
                electronic_document.payroll_period.total_neto
            )
            
            electronic_document.xml_content = xml_content
            electronic_document.cufe = cufe
            electronic_document.save()
            
            results['steps'].append({
                'step': 'Generar XML',
                'success': True,
                'message': 'XML generado correctamente'
            })
            
        except Exception as e:
            results['steps'].append({
                'step': 'Generar XML',
                'success': False,
                'error': str(e)
            })
            return results
        
        # Paso 2: Firmar XML
        try:
            signer = PayrollDocumentSigner(self.organization)
            signed_xml = signer.sign_document(electronic_document)
            
            results['steps'].append({
                'step': 'Firmar XML',
                'success': True,
                'message': 'Documento firmado correctamente'
            })
            
        except Exception as e:
            results['steps'].append({
                'step': 'Firmar XML',
                'success': False,
                'error': str(e)
            })
            return results
        
        # Paso 3: Enviar a DIAN
        try:
            dian_result = self.dian_service.send_document(electronic_document)
            
            results['steps'].append({
                'step': 'Enviar a DIAN',
                'success': dian_result.get('success', False),
                'message': dian_result.get('status_message', ''),
                'tracking_id': dian_result.get('tracking_id')
            })
            
            results['success'] = dian_result.get('success', False)
            
        except Exception as e:
            results['steps'].append({
                'step': 'Enviar a DIAN',
                'success': False,
                'error': str(e)
            })
            return results
        
        return results
    
    def check_document_status(self, electronic_document):
        """Consulta el estado de un documento en la DIAN"""
        if not electronic_document.dian_tracking_id:
            return {
                'success': False,
                'error': 'El documento no tiene ID de seguimiento'
            }
        
        return self.dian_service.query_document_status(
            electronic_document.dian_tracking_id
        )
