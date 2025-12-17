"""
Generador de XML UBL 2.1 para facturas electrónicas DIAN Colombia
"""
from xml.etree import ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from decimal import Decimal
from typing import Dict, List


class XMLUBLGenerator:
    """
    Genera documentos XML en formato UBL 2.1 según especificaciones DIAN.
    
    Referencias:
    - UBL 2.1: http://docs.oasis-open.org/ubl/os-UBL-2.1/
    - Anexo Técnico DIAN v1.9
    """
    
    # Namespaces UBL 2.1
    NAMESPACES = {
        'xmlns': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
        'xmlns:cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'xmlns:cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'xmlns:ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'xmlns:sts': 'dian:gov:co:facturaelectronica:Structures-2-1',
        'xmlns:xades': 'http://uri.etsi.org/01903/v1.3.2#',
        'xmlns:xades141': 'http://uri.etsi.org/01903/v1.4.1#',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2 http://docs.oasis-open.org/ubl/os-UBL-2.1/xsd/maindoc/UBL-Invoice-2.1.xsd',
    }
    
    def __init__(self):
        """Inicializa el generador XML."""
        # Registrar namespaces
        for prefix, uri in self.NAMESPACES.items():
            if not prefix.startswith('xmlns'):
                ET.register_namespace(prefix.replace('xmlns:', ''), uri)
    
    def generar_xml(self, invoice_data: Dict) -> str:
        """
        Genera el XML UBL 2.1 de una factura.
        
        Args:
            invoice_data: Diccionario con los datos de la factura
            
        Returns:
            str: XML formateado
        """
        # Crear elemento raíz Invoice
        root = ET.Element('Invoice', self.NAMESPACES)
        
        # Agregar secciones del XML
        self._agregar_encabezado(root, invoice_data)
        self._agregar_emisor(root, invoice_data['emisor'])
        self._agregar_cliente(root, invoice_data['cliente'])
        self._agregar_resolucion(root, invoice_data['resolucion'])
        self._agregar_totales(root, invoice_data['totales'])
        self._agregar_items(root, invoice_data['items'])
        
        # Convertir a string y formatear
        xml_string = ET.tostring(root, encoding='unicode')
        return self._pretty_print_xml(xml_string)
    
    def _agregar_encabezado(self, root: ET.Element, data: Dict):
        """Agrega la sección de encabezado del XML."""
        # UBL Version
        ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}UBLVersionID').text = 'UBL 2.1'
        
        # Versión del documento
        ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CustomizationID').text = '10'
        
        # Perfil
        ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ProfileID').text = 'DIAN 2.1'
        
        # Profile Execution
        ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ProfileExecutionID').text = data.get('ambiente', '2')
        
        # ID de la factura
        ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID').text = data['numero_completo']
        
        # CUFE
        ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}UUID', 
                     {'schemeID': '2', 'schemeName': 'CUFE-SHA384'}).text = data['cufe']
        
        # Fecha y hora de emisión
        fecha_emision = data['fecha_emision']
        ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}IssueDate').text = fecha_emision.strftime('%Y-%m-%d')
        ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}IssueTime').text = fecha_emision.strftime('%H:%M:%S-05:00')
        
        # Fecha de vencimiento (si aplica)
        if data.get('fecha_vencimiento'):
            ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}DueDate').text = data['fecha_vencimiento'].strftime('%Y-%m-%d')
        
        # Tipo de factura (01 = Factura de Venta)
        ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}InvoiceTypeCode').text = '01'
        
        # Notas (si hay)
        if data.get('notas'):
            ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Note').text = data['notas']
        
        # Moneda
        ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}DocumentCurrencyCode').text = 'COP'
        
        # Número de líneas
        ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}LineCountNumeric').text = str(len(data['items']))
    
    def _agregar_emisor(self, root: ET.Element, emisor: Dict):
        """Agrega la información del emisor (AccountingSupplierParty)."""
        supplier_party = ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}AccountingSupplierParty')
        
        # Número de identificación adicional (si aplica)
        ET.SubElement(supplier_party, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}AdditionalAccountID').text = '1'
        
        # Party
        party = ET.SubElement(supplier_party, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Party')
        
        # Identificación
        party_id = ET.SubElement(party, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyIdentification')
        id_elem = ET.SubElement(party_id, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID',
                               {'schemeID': emisor['tipo_documento'], 
                                'schemeName': '31',
                                'schemeAgencyID': '195',
                                'schemeAgencyName': 'CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)'})
        id_elem.text = f"{emisor['nit']}"
        
        # Nombre legal
        party_name = ET.SubElement(party, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyName')
        ET.SubElement(party_name, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Name').text = emisor['razon_social']
        
        # Dirección física
        address = ET.SubElement(party, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PhysicalLocation')
        address_elem = ET.SubElement(address, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Address')
        
        ET.SubElement(address_elem, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID').text = emisor.get('ciudad_codigo', '11001')
        ET.SubElement(address_elem, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CityName').text = emisor.get('ciudad_nombre', 'Bogotá')
        ET.SubElement(address_elem, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PostalZone').text = emisor.get('codigo_postal', '110111')
        ET.SubElement(address_elem, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CountrySubentity').text = emisor.get('departamento_nombre', 'Cundinamarca')
        ET.SubElement(address_elem, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CountrySubentityCode').text = emisor.get('departamento_codigo', '11')
        
        address_line = ET.SubElement(address_elem, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}AddressLine')
        ET.SubElement(address_line, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Line').text = emisor['direccion']
        
        country = ET.SubElement(address_elem, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Country')
        ET.SubElement(country, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}IdentificationCode').text = 'CO'
        ET.SubElement(country, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Name').text = 'Colombia'
        
        # Información legal
        party_legal = ET.SubElement(party, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyLegalEntity')
        ET.SubElement(party_legal, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}RegistrationName').text = emisor['razon_social']
        ET.SubElement(party_legal, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CompanyID',
                     {'schemeID': emisor['tipo_documento'],
                      'schemeName': '31',
                      'schemeAgencyID': '195'}).text = emisor['nit']
        
        # Contacto
        if emisor.get('telefono') or emisor.get('email_facturacion'):
            contact = ET.SubElement(party, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Contact')
            if emisor.get('telefono'):
                ET.SubElement(contact, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Telephone').text = emisor['telefono']
            if emisor.get('email_facturacion'):
                ET.SubElement(contact, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ElectronicMail').text = emisor['email_facturacion']
    
    def _agregar_cliente(self, root: ET.Element, cliente: Dict):
        """Agrega la información del cliente (AccountingCustomerParty)."""
        customer_party = ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}AccountingCustomerParty')
        
        # Tipo de persona (1=Persona jurídica, 2=Persona natural)
        tipo_persona = '1' if cliente['tipo_documento'] == 'NIT' else '2'
        ET.SubElement(customer_party, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}AdditionalAccountID').text = tipo_persona
        
        # Party
        party = ET.SubElement(customer_party, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Party')
        
        # Identificación
        party_id = ET.SubElement(party, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyIdentification')
        id_elem = ET.SubElement(party_id, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID',
                               {'schemeID': cliente['tipo_documento'],
                                'schemeName': self._get_scheme_name(cliente['tipo_documento']),
                                'schemeAgencyID': '195'})
        id_elem.text = cliente['numero_documento']
        
        # Nombre
        party_name = ET.SubElement(party, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyName')
        ET.SubElement(party_name, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Name').text = cliente['nombre']
        
        # Dirección (si está disponible)
        if cliente.get('direccion'):
            address = ET.SubElement(party, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PhysicalLocation')
            address_elem = ET.SubElement(address, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Address')
            
            if cliente.get('ciudad'):
                ET.SubElement(address_elem, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CityName').text = cliente['ciudad']
            if cliente.get('departamento'):
                ET.SubElement(address_elem, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}CountrySubentity').text = cliente['departamento']
            
            address_line = ET.SubElement(address_elem, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}AddressLine')
            ET.SubElement(address_line, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Line').text = cliente['direccion']
            
            country = ET.SubElement(address_elem, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Country')
            ET.SubElement(country, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}IdentificationCode').text = 'CO'
        
        # Entidad legal
        party_legal = ET.SubElement(party, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyLegalEntity')
        ET.SubElement(party_legal, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}RegistrationName').text = cliente['nombre']
        
        # Contacto
        if cliente.get('telefono') or cliente.get('email'):
            contact = ET.SubElement(party, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Contact')
            if cliente.get('telefono'):
                ET.SubElement(contact, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Telephone').text = cliente['telefono']
            if cliente.get('email'):
                ET.SubElement(contact, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ElectronicMail').text = cliente['email']
    
    def _agregar_resolucion(self, root: ET.Element, resolucion: Dict):
        """Agrega la información de la resolución DIAN."""
        # InvoiceAuthorization
        auth_ref = ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}InvoiceDocumentReference')
        ET.SubElement(auth_ref, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID').text = resolucion['numero']
        ET.SubElement(auth_ref, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}IssueDate').text = resolucion['fecha'].strftime('%Y-%m-%d')
        
        # Prefijo y rango
        ET.SubElement(auth_ref, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}DocumentDescription').text = f"Prefijo: {resolucion['prefijo']}, Rango: {resolucion['rango_inicio']}-{resolucion['rango_fin']}"
    
    def _agregar_totales(self, root: ET.Element, totales: Dict):
        """Agrega los totales de la factura."""
        # Totales monetarios legales
        legal_total = ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}LegalMonetaryTotal')
        
        # Subtotal (antes de impuestos)
        ET.SubElement(legal_total, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}LineExtensionAmount',
                     {'currencyID': 'COP'}).text = f"{totales['subtotal']:.2f}"
        
        # Total antes de impuestos (después de descuentos)
        ET.SubElement(legal_total, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxExclusiveAmount',
                     {'currencyID': 'COP'}).text = f"{totales['base_imponible']:.2f}"
        
        # Total incluyendo impuestos
        ET.SubElement(legal_total, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxInclusiveAmount',
                     {'currencyID': 'COP'}).text = f"{totales['total']:.2f}"
        
        # Descuentos globales (si aplica)
        if totales.get('descuento', Decimal('0')) > 0:
            ET.SubElement(legal_total, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}AllowanceTotalAmount',
                         {'currencyID': 'COP'}).text = f"{totales['descuento']:.2f}"
        
        # Total a pagar
        ET.SubElement(legal_total, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PayableAmount',
                     {'currencyID': 'COP'}).text = f"{totales['total']:.2f}"
        
        # Totales de impuestos
        if totales.get('total_iva', Decimal('0')) > 0:
            tax_total = ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxTotal')
            ET.SubElement(tax_total, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxAmount',
                         {'currencyID': 'COP'}).text = f"{totales['total_iva']:.2f}"
            
            # Subtotales por tipo de IVA
            for tasa_iva, valor_iva in [(0, totales.get('iva_0', 0)), 
                                         (5, totales.get('iva_5', 0)), 
                                         (19, totales.get('iva_19', 0))]:
                if valor_iva > 0:
                    tax_subtotal = ET.SubElement(tax_total, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxSubtotal')
                    ET.SubElement(tax_subtotal, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxAmount',
                                 {'currencyID': 'COP'}).text = f"{valor_iva:.2f}"
                    
                    tax_category = ET.SubElement(tax_subtotal, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxCategory')
                    ET.SubElement(tax_category, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Percent').text = f"{tasa_iva:.2f}"
                    
                    tax_scheme = ET.SubElement(tax_category, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxScheme')
                    ET.SubElement(tax_scheme, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID').text = '01'
                    ET.SubElement(tax_scheme, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Name').text = 'IVA'
    
    def _agregar_items(self, root: ET.Element, items: List[Dict]):
        """Agrega las líneas de la factura."""
        for index, item in enumerate(items, 1):
            invoice_line = ET.SubElement(root, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}InvoiceLine')
            
            # ID de línea
            ET.SubElement(invoice_line, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID').text = str(index)
            
            # Cantidad
            ET.SubElement(invoice_line, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}InvoicedQuantity',
                         {'unitCode': item.get('unidad_medida', 'NIU')}).text = f"{item['cantidad']:.2f}"
            
            # Total de la línea
            ET.SubElement(invoice_line, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}LineExtensionAmount',
                         {'currencyID': 'COP'}).text = f"{item['subtotal']:.2f}"
            
            # Descripción del producto/servicio
            item_elem = ET.SubElement(invoice_line, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Item')
            ET.SubElement(item_elem, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Description').text = item['descripcion']
            
            # Precio unitario
            price = ET.SubElement(invoice_line, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Price')
            ET.SubElement(price, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}PriceAmount',
                         {'currencyID': 'COP'}).text = f"{item['precio_unitario']:.2f}"
            
            # Impuestos de la línea (si aplica)
            if item.get('porcentaje_iva', 0) > 0:
                tax_total = ET.SubElement(invoice_line, '{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}TaxTotal')
                ET.SubElement(tax_total, '{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}TaxAmount',
                             {'currencyID': 'COP'}).text = f"{item['valor_iva']:.2f}"
    
    def _get_scheme_name(self, tipo_documento: str) -> str:
        """Obtiene el código de esquema según el tipo de documento."""
        schemes = {
            'CC': '13',  # Cédula de ciudadanía
            'CE': '22',  # Cédula de extranjería
            'NIT': '31',  # NIT
            'PA': '41',  # Pasaporte
            'TI': '11',  # Tarjeta de identidad
        }
        return schemes.get(tipo_documento, '13')
    
    def _pretty_print_xml(self, xml_string: str) -> str:
        """Formatea el XML con indentación."""
        dom = minidom.parseString(xml_string)
        return dom.toprettyxml(indent="  ", encoding='UTF-8').decode('utf-8')
