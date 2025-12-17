"""
Servicio orquestador para el proceso completo de facturación electrónica DIAN.

Este servicio coordina todos los pasos necesarios para generar, firmar y
enviar una factura electrónica a la DIAN.
"""
from typing import Tuple, Dict
from decimal import Decimal
from datetime import datetime
from django.utils import timezone

from apps.billing.models import Invoice, DianConfiguration
from .cufe_generator import CUFEGenerator
from .xml_generator import XMLUBLGenerator
from .digital_signature import DigitalSignatureService
from .qr_generator import QRCodeGenerator
from .dian_client import DianSoapClient, DianMockClient


class FacturacionElectronicaService:
    """
    Servicio principal para gestionar el ciclo completo de facturación electrónica.
    
    Pasos del proceso:
    1. Validar configuración DIAN
    2. Generar CUFE
    3. Generar XML UBL 2.1
    4. Firmar XML digitalmente
    5. Generar código QR
    6. Enviar a DIAN
    7. Procesar respuesta
    8. Actualizar estado de la factura
    """
    
    def __init__(self, invoice: Invoice, usar_mock: bool = False):
        """
        Inicializa el servicio de facturación electrónica.
        
        Args:
            invoice: Instancia del modelo Invoice
            usar_mock: Si True, usa cliente mock en lugar de DIAN real (para desarrollo)
        """
        self.invoice = invoice
        self.organization = invoice.organization
        self.usar_mock = usar_mock
        self.errores = []
        self.advertencias = []
        
        # Cargar configuración DIAN
        self.dian_config = DianConfiguration.objects.filter(
            organization=self.organization,
            is_active=True
        ).first()
        
        if not self.dian_config:
            raise ValueError("No hay configuración DIAN activa para esta organización")
    
    def procesar_factura_completa(self) -> Tuple[bool, Dict]:
        """
        Ejecuta el proceso completo de facturación electrónica.
        
        Returns:
            Tuple[bool, Dict]: (exitoso, resultado_detallado)
        """
        try:
            # PASO 1: Validar configuración
            if not self._validar_configuracion():
                return False, {
                    'paso': 'validacion',
                    'errores': self.errores,
                    'mensaje': 'Error en la configuración DIAN'
                }
            
            # PASO 2: Generar CUFE
            cufe = self._generar_cufe()
            if not cufe:
                return False, {
                    'paso': 'cufe',
                    'errores': self.errores,
                    'mensaje': 'Error generando CUFE'
                }
            
            self.invoice.cufe = cufe
            self.invoice.save(update_fields=['cufe'])
            
            # PASO 3: Generar XML UBL 2.1
            xml_sin_firmar = self._generar_xml()
            if not xml_sin_firmar:
                return False, {
                    'paso': 'xml',
                    'errores': self.errores,
                    'mensaje': 'Error generando XML'
                }
            
            self.invoice.xml_sin_firmar = xml_sin_firmar
            self.invoice.save(update_fields=['xml_sin_firmar'])
            
            # PASO 4: Firmar XML
            xml_firmado = self._firmar_xml(xml_sin_firmar)
            if not xml_firmado:
                return False, {
                    'paso': 'firma',
                    'errores': self.errores,
                    'mensaje': 'Error firmando XML'
                }
            
            self.invoice.xml_firmado = xml_firmado
            self.invoice.save(update_fields=['xml_firmado'])
            
            # PASO 5: Generar código QR
            qr_base64 = self._generar_qr()
            if qr_base64:
                self.invoice.qr_code_base64 = qr_base64
                self.invoice.save(update_fields=['qr_code_base64'])
            
            # PASO 6: Enviar a DIAN
            self.invoice.estado_dian = 'processing'
            self.invoice.dian_enviado_en = timezone.now()
            self.invoice.save(update_fields=['estado_dian', 'dian_enviado_en'])
            
            exito, respuesta_dian = self._enviar_a_dian(xml_firmado)
            
            # PASO 7: Procesar respuesta
            self._procesar_respuesta_dian(exito, respuesta_dian)
            
            if exito:
                return True, {
                    'paso': 'completado',
                    'cufe': cufe,
                    'mensaje': '✅ Factura electrónica procesada exitosamente',
                    'respuesta_dian': respuesta_dian,
                    'advertencias': self.advertencias
                }
            else:
                return False, {
                    'paso': 'envio_dian',
                    'errores': self.errores,
                    'mensaje': respuesta_dian.get('mensaje', 'Error enviando a DIAN'),
                    'respuesta_dian': respuesta_dian
                }
                
        except Exception as e:
            self.errores.append(str(e))
            return False, {
                'paso': 'exception',
                'errores': self.errores,
                'mensaje': f'Error inesperado: {str(e)}'
            }
    
    def _validar_configuracion(self) -> bool:
        """Valida que la configuración DIAN esté completa."""
        # Verificar campos obligatorios
        campos_requeridos = {
            'nit': self.dian_config.nit,
            'dv': self.dian_config.dv,
            'razon_social': self.dian_config.razon_social,
            'resolucion_numero': self.dian_config.resolucion_numero,
            'resolucion_fecha': self.dian_config.resolucion_fecha,
            'prefijo': self.dian_config.resolucion_prefijo,
            'numero_inicio': self.dian_config.resolucion_numero_inicio,
            'numero_fin': self.dian_config.resolucion_numero_fin,
            'clave_tecnica': self.dian_config.resolucion_clave_tecnica,
        }
        
        for campo, valor in campos_requeridos.items():
            if not valor:
                self.errores.append(f"Campo obligatorio '{campo}' no configurado")
                return False
        
        # Verificar que haya numeración disponible
        if self.dian_config.resolucion_numero_actual >= self.dian_config.resolucion_numero_fin:
            self.errores.append("Se agotó la numeración de la resolución DIAN")
            return False
        
        # Verificar certificado digital (si no es mock)
        if not self.usar_mock:
            if not self.dian_config.certificado_archivo:
                self.errores.append("No hay certificado digital configurado")
                return False
            
            if not self.dian_config.certificado_password:
                self.errores.append("No hay contraseña de certificado configurada")
                return False
        
        return True
    
    def _generar_cufe(self) -> str:
        """Genera el CUFE de la factura."""
        try:
            cufe = CUFEGenerator.generar(
                numero_factura=self.invoice.numero_completo,
                fecha_emision=self.invoice.fecha_emision,
                valor_subtotal=self.invoice.base_imponible,
                valor_iva=self.invoice.total_iva,
                valor_total=self.invoice.total,
                nit_emisor=self.dian_config.nit,
                tipo_doc_receptor=self.invoice.cliente_tipo_documento,
                num_doc_receptor=self.invoice.cliente_numero_documento,
                clave_tecnica=self.dian_config.resolucion_clave_tecnica,
                ambiente='2' if self.dian_config.ambiente == '2' else '1'
            )
            return cufe
        except Exception as e:
            self.errores.append(f"Error generando CUFE: {str(e)}")
            return None
    
    def _generar_xml(self) -> str:
        """Genera el XML UBL 2.1 de la factura."""
        try:
            # Preparar datos para el generador
            # Convertir fechas a string si son objetos datetime
            def fecha_a_str(fecha):
                if fecha is None:
                    return None
                if hasattr(fecha, 'strftime'):
                    return fecha.strftime('%Y-%m-%d')
                return str(fecha)
            
            # DEBUG: imprimir tipo de fecha_emision
            print(f"DEBUG fecha_emision type: {type(self.invoice.fecha_emision)}")
            print(f"DEBUG fecha_emision value: {self.invoice.fecha_emision}")
            
            invoice_data = {
                'numero_completo': self.invoice.numero_completo,
                'cufe': self.invoice.cufe,
                'fecha_emision': fecha_a_str(self.invoice.fecha_emision),
                'fecha_vencimiento': fecha_a_str(self.invoice.fecha_vencimiento),
                'ambiente': '2' if self.dian_config.ambiente == '2' else '1',
                'emisor': {
                    'tipo_documento': self.dian_config.tipo_documento,
                    'nit': self.dian_config.nit,
                    'dv': self.dian_config.dv,
                    'razon_social': self.dian_config.razon_social,
                    'nombre_comercial': self.dian_config.nombre_comercial or self.dian_config.razon_social,
                    'direccion': self.dian_config.direccion,
                    'ciudad_codigo': self.dian_config.ciudad_codigo,
                    'ciudad_nombre': self.dian_config.ciudad_nombre,
                    'departamento_codigo': self.dian_config.departamento_codigo,
                    'departamento_nombre': self.dian_config.departamento_nombre,
                    'codigo_postal': self.dian_config.codigo_postal,
                    'telefono': self.dian_config.telefono,
                    'email_facturacion': self.dian_config.email_facturacion,
                },
                'cliente': {
                    'tipo_documento': self.invoice.cliente_tipo_documento,
                    'numero_documento': self.invoice.cliente_numero_documento,
                    'nombre': self.invoice.cliente_nombre,
                    'email': self.invoice.cliente_email,
                    'telefono': self.invoice.cliente_telefono,
                    'direccion': self.invoice.cliente_direccion,
                    'ciudad': self.invoice.cliente_ciudad,
                    'departamento': self.invoice.cliente_departamento,
                },
                'resolucion': {
                    'numero': self.dian_config.resolucion_numero,
                    'fecha': fecha_a_str(self.dian_config.resolucion_fecha),
                    'prefijo': self.dian_config.resolucion_prefijo,
                    'rango_inicio': self.dian_config.resolucion_numero_inicio,
                    'rango_fin': self.dian_config.resolucion_numero_fin,
                },
                'totales': {
                    'subtotal': self.invoice.subtotal,
                    'descuento': self.invoice.descuento,
                    'base_imponible': self.invoice.base_imponible,
                    'iva_0': self.invoice.iva_0,
                    'iva_5': self.invoice.iva_5,
                    'iva_19': self.invoice.iva_19,
                    'total_iva': self.invoice.total_iva,
                    'total': self.invoice.total,
                },
                'items': []
            }
            
            # Agregar items de la factura
            for item in self.invoice.items.all():
                invoice_data['items'].append({
                    'descripcion': item.descripcion,
                    'cantidad': item.cantidad,
                    'precio_unitario': item.valor_unitario,
                    'subtotal': item.subtotal,
                    'porcentaje_iva': item.iva_porcentaje,
                    'valor_iva': item.valor_iva,
                    'total': item.total_linea,
                    'unidad_medida': item.unidad_medida or 'NIU'
                })
            
            # Generar XML
            generator = XMLUBLGenerator()
            xml_string = generator.generar_xml(invoice_data)
            
            return xml_string
            
        except Exception as e:
            self.errores.append(f"Error generando XML: {str(e)}")
            return None
    
    def _firmar_xml(self, xml_string: str) -> str:
        """Firma digitalmente el XML."""
        if self.usar_mock:
            # En modo mock, retornar el XML sin firmar
            self.advertencias.append("⚠️ Modo mock: XML no firmado digitalmente")
            return xml_string
        
        try:
            # Cargar servicio de firma
            signer = DigitalSignatureService(
                certificado_path=self.dian_config.certificado_archivo.path,
                certificado_password=self.dian_config.certificado_password
            )
            
            # Validar certificado
            es_valido, mensaje = signer.validar_certificado()
            if not es_valido:
                self.errores.append(f"Certificado inválido: {mensaje}")
                return None
            
            if '⚠️' in mensaje:
                self.advertencias.append(mensaje)
            
            # Firmar
            xml_firmado = signer.firmar_xml(xml_string, self.invoice.cufe)
            return xml_firmado
            
        except Exception as e:
            self.errores.append(f"Error firmando XML: {str(e)}")
            return None
    
    def _generar_qr(self) -> str:
        """Genera el código QR de la factura."""
        try:
            qr_base64 = QRCodeGenerator.generar_qr_para_invoice(self.invoice)
            return qr_base64
        except Exception as e:
            self.advertencias.append(f"No se pudo generar QR: {str(e)}")
            return None
    
    def _enviar_a_dian(self, xml_firmado: str) -> Tuple[bool, Dict]:
        """Envía el XML firmado a la DIAN."""
        try:
            # Elegir cliente
            if self.usar_mock:
                cliente = DianMockClient()
            else:
                cliente = DianSoapClient(
                    ambiente='habilitacion' if self.dian_config.ambiente == 'pruebas' else 'produccion'
                )
            
            # Enviar factura
            exito, respuesta = cliente.enviar_factura(
                xml_firmado=xml_firmado,
                nit_emisor=self.dian_config.nit
            )
            
            return exito, respuesta
            
        except Exception as e:
            return False, {
                'exitoso': False,
                'error': f'Error enviando a DIAN: {str(e)}'
            }
    
    def _procesar_respuesta_dian(self, exito: bool, respuesta: Dict):
        """Procesa la respuesta de la DIAN y actualiza la factura."""
        # Guardar respuesta completa
        self.invoice.dian_response = respuesta
        
        if exito:
            self.invoice.estado_dian = 'approved'
            self.invoice.dian_aprobado_en = timezone.now()
            self.invoice.dian_error_mensaje = ''
        else:
            self.invoice.estado_dian = 'rejected'
            error_msg = respuesta.get('mensaje', 'Error desconocido')
            
            # Agregar errores si los hay
            if 'errores' in respuesta and respuesta['errores']:
                error_msg += '\nErrores: ' + ', '.join(respuesta['errores'])
            
            self.invoice.dian_error_mensaje = error_msg
            self.errores.append(error_msg)
        
        self.invoice.save(update_fields=[
            'dian_response',
            'estado_dian',
            'dian_aprobado_en',
            'dian_error_mensaje'
        ])
    
    @staticmethod
    def consultar_estado_factura(invoice: Invoice) -> Tuple[bool, Dict]:
        """
        Consulta el estado de una factura en la DIAN.
        
        Args:
            invoice: Instancia de Invoice con CUFE
            
        Returns:
            Tuple[bool, Dict]: (encontrada, info)
        """
        if not invoice.cufe:
            return False, {'error': 'La factura no tiene CUFE'}
        
        dian_config = DianConfiguration.objects.filter(
            organization=invoice.organization,
            is_active=True
        ).first()
        
        if not dian_config:
            return False, {'error': 'No hay configuración DIAN'}
        
        try:
            cliente = DianSoapClient(
                ambiente='habilitacion' if dian_config.ambiente == 'pruebas' else 'produccion'
            )
            
            encontrada, info = cliente.consultar_estado(invoice.cufe)
            return encontrada, info
            
        except Exception as e:
            return False, {'error': str(e)}
