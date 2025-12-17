"""
Servicio de firma digital XML usando certificado digital .p12/.pfx
para facturas electrónicas DIAN Colombia
"""
from lxml import etree
from OpenSSL import crypto
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography import x509
import base64
from datetime import datetime
from typing import Tuple, Optional


class DigitalSignatureService:
    """
    Servicio para firmar digitalmente XMLs de facturas electrónicas.
    
    Utiliza certificados digitales en formato .p12 o .pfx para crear
    firmas XMLDSig según especificaciones DIAN.
    """
    
    def __init__(self, certificado_path: str, certificado_password: str):
        """
        Inicializa el servicio de firma digital.
        
        Args:
            certificado_path: Ruta al archivo .p12 o .pfx
            certificado_password: Contraseña del certificado
        """
        self.certificado_path = certificado_path
        self.certificado_password = certificado_password
        self._cargar_certificado()
    
    def _cargar_certificado(self):
        """Carga el certificado digital y la clave privada."""
        try:
            # Leer el archivo del certificado
            with open(self.certificado_path, 'rb') as f:
                certificado_data = f.read()
            
            # Cargar el certificado PKCS#12
            p12 = crypto.load_pkcs12(certificado_data, self.certificado_password.encode())
            
            # Extraer componentes
            self.private_key = p12.get_privatekey()
            self.certificate = p12.get_certificate()
            self.ca_certs = p12.get_ca_certificates() or []
            
            # Información del certificado
            self.cert_subject = self.certificate.get_subject()
            self.cert_issuer = self.certificate.get_issuer()
            self.cert_serial = self.certificate.get_serial_number()
            self.cert_not_before = datetime.strptime(
                self.certificate.get_notBefore().decode('ascii'),
                '%Y%m%d%H%M%SZ'
            )
            self.cert_not_after = datetime.strptime(
                self.certificate.get_notAfter().decode('ascii'),
                '%Y%m%d%H%M%SZ'
            )
            
        except FileNotFoundError:
            raise ValueError(f"No se encontró el certificado en: {self.certificado_path}")
        except Exception as e:
            raise ValueError(f"Error al cargar el certificado: {str(e)}")
    
    def validar_certificado(self) -> Tuple[bool, str]:
        """
        Valida que el certificado sea válido y no haya expirado.
        
        Returns:
            Tuple[bool, str]: (es_valido, mensaje)
        """
        ahora = datetime.now()
        
        if ahora < self.cert_not_before:
            return False, f"El certificado aún no es válido. Válido desde: {self.cert_not_before}"
        
        if ahora > self.cert_not_after:
            return False, f"El certificado ha expirado. Expiró el: {self.cert_not_after}"
        
        # Calcular días restantes
        dias_restantes = (self.cert_not_after - ahora).days
        
        if dias_restantes < 30:
            return True, f"⚠️ Certificado válido pero expira en {dias_restantes} días"
        
        return True, f"✅ Certificado válido hasta {self.cert_not_after.strftime('%Y-%m-%d')}"
    
    def firmar_xml(self, xml_string: str, cufe: str) -> str:
        """
        Firma digitalmente un XML de factura electrónica.
        
        Args:
            xml_string: XML sin firmar
            cufe: CUFE de la factura
            
        Returns:
            str: XML firmado con XMLDSig
        """
        # Validar certificado antes de firmar
        es_valido, mensaje = self.validar_certificado()
        if not es_valido:
            raise ValueError(f"Certificado inválido: {mensaje}")
        
        # Parse del XML
        parser = etree.XMLParser(remove_blank_text=True)
        doc = etree.fromstring(xml_string.encode('utf-8'), parser)
        
        # Crear la sección de firma XAdES
        signature = self._crear_estructura_firma(cufe)
        
        # Agregar la firma al documento
        # La firma debe ir en UBLExtensions > UBLExtension > ExtensionContent
        extensions = doc.find('.//{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}UBLExtensions')
        if extensions is None:
            extensions = etree.Element('{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}UBLExtensions')
            doc.insert(0, extensions)
        
        extension = etree.SubElement(extensions, '{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}UBLExtension')
        content = etree.SubElement(extension, '{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}ExtensionContent')
        content.append(signature)
        
        # Calcular el digest del documento
        canonical_doc = etree.tostring(doc, method='c14n', exclusive=True)
        digest = self._calcular_digest(canonical_doc)
        
        # Insertar el digest en la firma
        digest_value = signature.find('.//{http://www.w3.org/2000/09/xmldsig#}DigestValue')
        digest_value.text = digest
        
        # Calcular la firma de SignedInfo
        signed_info = signature.find('.//{http://www.w3.org/2000/09/xmldsig#}SignedInfo')
        canonical_signed_info = etree.tostring(signed_info, method='c14n', exclusive=True)
        signature_value = self._calcular_firma(canonical_signed_info)
        
        # Insertar el valor de la firma
        sig_value = signature.find('.//{http://www.w3.org/2000/09/xmldsig#}SignatureValue')
        sig_value.text = signature_value
        
        # Insertar el certificado
        x509_cert = signature.find('.//{http://www.w3.org/2000/09/xmldsig#}X509Certificate')
        cert_pem = crypto.dump_certificate(crypto.FILETYPE_PEM, self.certificate)
        cert_base64 = cert_pem.decode('utf-8').replace('-----BEGIN CERTIFICATE-----\n', '').replace('\n-----END CERTIFICATE-----\n', '')
        x509_cert.text = cert_base64
        
        # Convertir a string
        return etree.tostring(doc, encoding='unicode', pretty_print=True)
    
    def _crear_estructura_firma(self, cufe: str) -> etree.Element:
        """Crea la estructura XMLDSig con XAdES-EPES."""
        # Namespace declarations
        ns_ds = "http://www.w3.org/2000/09/xmldsig#"
        ns_xades = "http://uri.etsi.org/01903/v1.3.2#"
        
        # Crear elemento Signature
        signature = etree.Element(f"{{{ns_ds}}}Signature", nsmap={
            'ds': ns_ds,
            'xades': ns_xades
        })
        signature.set('Id', f'xmldsig-{cufe}')
        
        # SignedInfo
        signed_info = etree.SubElement(signature, f"{{{ns_ds}}}SignedInfo")
        
        # CanonicalizationMethod
        canon_method = etree.SubElement(signed_info, f"{{{ns_ds}}}CanonicalizationMethod")
        canon_method.set('Algorithm', 'http://www.w3.org/TR/2001/REC-xml-c14n-20010315')
        
        # SignatureMethod
        sig_method = etree.SubElement(signed_info, f"{{{ns_ds}}}SignatureMethod")
        sig_method.set('Algorithm', 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256')
        
        # Reference al documento
        reference = etree.SubElement(signed_info, f"{{{ns_ds}}}Reference")
        reference.set('Id', f'xmldsig-ref-{cufe}')
        reference.set('URI', '')
        
        # Transforms
        transforms = etree.SubElement(reference, f"{{{ns_ds}}}Transforms")
        transform = etree.SubElement(transforms, f"{{{ns_ds}}}Transform")
        transform.set('Algorithm', 'http://www.w3.org/2000/09/xmldsig#enveloped-signature')
        
        # DigestMethod
        digest_method = etree.SubElement(reference, f"{{{ns_ds}}}DigestMethod")
        digest_method.set('Algorithm', 'http://www.w3.org/2001/04/xmlenc#sha256')
        
        # DigestValue (se llenará después)
        etree.SubElement(reference, f"{{{ns_ds}}}DigestValue")
        
        # SignatureValue (se llenará después)
        etree.SubElement(signature, f"{{{ns_ds}}}SignatureValue")
        
        # KeyInfo
        key_info = etree.SubElement(signature, f"{{{ns_ds}}}KeyInfo")
        x509_data = etree.SubElement(key_info, f"{{{ns_ds}}}X509Data")
        etree.SubElement(x509_data, f"{{{ns_ds}}}X509Certificate")  # Se llenará después
        
        # Object con QualifyingProperties (XAdES)
        obj = etree.SubElement(signature, f"{{{ns_ds}}}Object")
        qualifying = etree.SubElement(obj, f"{{{ns_xades}}}QualifyingProperties")
        qualifying.set('Target', f'#xmldsig-{cufe}')
        
        # SignedProperties
        signed_props = etree.SubElement(qualifying, f"{{{ns_xades}}}SignedProperties")
        signed_props.set('Id', f'xmldsig-{cufe}-signedprops')
        
        # SignedSignatureProperties
        sig_props = etree.SubElement(signed_props, f"{{{ns_xades}}}SignedSignatureProperties")
        
        # SigningTime
        signing_time = etree.SubElement(sig_props, f"{{{ns_xades}}}SigningTime")
        signing_time.text = datetime.now().strftime('%Y-%m-%dT%H:%M:%S-05:00')
        
        # SigningCertificate
        signing_cert = etree.SubElement(sig_props, f"{{{ns_xades}}}SigningCertificate")
        cert = etree.SubElement(signing_cert, f"{{{ns_xades}}}Cert")
        cert_digest = etree.SubElement(cert, f"{{{ns_xades}}}CertDigest")
        
        digest_method = etree.SubElement(cert_digest, f"{{{ns_ds}}}DigestMethod")
        digest_method.set('Algorithm', 'http://www.w3.org/2001/04/xmlenc#sha256')
        
        digest_value = etree.SubElement(cert_digest, f"{{{ns_ds}}}DigestValue")
        # Calcular digest del certificado
        cert_der = crypto.dump_certificate(crypto.FILETYPE_ASN1, self.certificate)
        cert_digest_value = base64.b64encode(hashes.Hash(hashes.SHA256(), backend=default_backend()).update(cert_der).finalize()).decode()
        digest_value.text = cert_digest_value
        
        issuer_serial = etree.SubElement(cert, f"{{{ns_xades}}}IssuerSerial")
        x509_issuer = etree.SubElement(issuer_serial, f"{{{ns_ds}}}X509IssuerName")
        x509_issuer.text = f"CN={self.cert_issuer.CN}"
        x509_serial = etree.SubElement(issuer_serial, f"{{{ns_ds}}}X509SerialNumber")
        x509_serial.text = str(self.cert_serial)
        
        return signature
    
    def _calcular_digest(self, data: bytes) -> str:
        """Calcula el digest SHA-256 en base64."""
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(data)
        return base64.b64encode(digest.finalize()).decode()
    
    def _calcular_firma(self, data: bytes) -> str:
        """Calcula la firma RSA-SHA256."""
        # Convertir la clave privada de OpenSSL a cryptography
        private_key_pem = crypto.dump_privatekey(crypto.FILETYPE_PEM, self.private_key)
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )
        
        # Firmar
        signature = private_key.sign(
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode()
    
    def obtener_info_certificado(self) -> dict:
        """Obtiene información del certificado cargado."""
        return {
            'subject': {
                'CN': self.cert_subject.CN,
                'O': getattr(self.cert_subject, 'O', ''),
                'C': getattr(self.cert_subject, 'C', ''),
            },
            'issuer': {
                'CN': self.cert_issuer.CN,
                'O': getattr(self.cert_issuer, 'O', ''),
            },
            'serial_number': self.cert_serial,
            'valid_from': self.cert_not_before.strftime('%Y-%m-%d'),
            'valid_until': self.cert_not_after.strftime('%Y-%m-%d'),
            'days_remaining': (self.cert_not_after - datetime.now()).days
        }
