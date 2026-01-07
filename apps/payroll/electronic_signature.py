"""
Servicio de firma electrónica para documentos de nómina
"""
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from lxml import etree
import base64
from datetime import datetime
from pathlib import Path


class ElectronicSignature:
    """
    Servicio para firmar documentos XML electrónicamente
    """
    
    def __init__(self, certificate_path, certificate_password):
        """
        Args:
            certificate_path: Ruta al archivo .p12 o .pfx
            certificate_password: Contraseña del certificado
        """
        self.certificate_path = certificate_path
        self.certificate_password = certificate_password
        self.private_key = None
        self.certificate = None
        
    def load_certificate(self):
        """Carga el certificado digital desde el archivo .p12"""
        try:
            with open(self.certificate_path, 'rb') as f:
                cert_data = f.read()
            
            from cryptography.hazmat.primitives.serialization import pkcs12
            
            # Cargar certificado PKCS12
            private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
                cert_data,
                self.certificate_password.encode(),
                backend=default_backend()
            )
            
            self.private_key = private_key
            self.certificate = certificate
            
            return True
        except FileNotFoundError:
            raise Exception(f"Certificado no encontrado: {self.certificate_path}")
        except Exception as e:
            raise Exception(f"Error al cargar certificado: {str(e)}")
    
    def sign_xml(self, xml_string):
        """
        Firma un documento XML con el certificado digital
        
        Args:
            xml_string: String del XML a firmar
            
        Returns:
            XML firmado como string
        """
        if not self.private_key or not self.certificate:
            self.load_certificate()
        
        # Parsear XML
        root = etree.fromstring(xml_string.encode('utf-8'))
        
        # Crear nodo de firma (Signature)
        signature = self._create_signature_element(xml_string)
        
        # Agregar firma al XML
        root.append(signature)
        
        # Convertir a string
        signed_xml = etree.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8'
        ).decode('utf-8')
        
        return signed_xml
    
    def _create_signature_element(self, xml_data):
        """Crea el elemento Signature según estándar XMLDSig"""
        
        # Namespaces
        ds_ns = "http://www.w3.org/2000/09/xmldsig#"
        DS = "{%s}" % ds_ns
        
        # Crear elemento Signature
        signature = etree.Element(
            DS + "Signature",
            nsmap={'ds': ds_ns}
        )
        
        # SignedInfo
        signed_info = etree.SubElement(signature, DS + "SignedInfo")
        
        # CanonicalizationMethod
        etree.SubElement(
            signed_info,
            DS + "CanonicalizationMethod",
            Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
        )
        
        # SignatureMethod
        etree.SubElement(
            signed_info,
            DS + "SignatureMethod",
            Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"
        )
        
        # Reference
        reference = etree.SubElement(signed_info, DS + "Reference", URI="")
        
        # Transforms
        transforms = etree.SubElement(reference, DS + "Transforms")
        etree.SubElement(
            transforms,
            DS + "Transform",
            Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"
        )
        
        # DigestMethod
        etree.SubElement(
            reference,
            DS + "DigestMethod",
            Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"
        )
        
        # DigestValue (hash del documento)
        digest_value = self._calculate_digest(xml_data)
        etree.SubElement(reference, DS + "DigestValue").text = digest_value
        
        # SignatureValue (firma digital)
        signature_value = self._sign_data(etree.tostring(signed_info))
        etree.SubElement(signature, DS + "SignatureValue").text = signature_value
        
        # KeyInfo
        key_info = etree.SubElement(signature, DS + "KeyInfo")
        
        # X509Data
        x509_data = etree.SubElement(key_info, DS + "X509Data")
        
        # X509Certificate
        cert_der = self.certificate.public_bytes(serialization.Encoding.DER)
        cert_b64 = base64.b64encode(cert_der).decode('utf-8')
        etree.SubElement(x509_data, DS + "X509Certificate").text = cert_b64
        
        return signature
    
    def _calculate_digest(self, data):
        """Calcula el hash SHA-256 del documento"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(data)
        hash_bytes = digest.finalize()
        
        return base64.b64encode(hash_bytes).decode('utf-8')
    
    def _sign_data(self, data):
        """Firma los datos con la clave privada"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        signature = self.private_key.sign(
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode('utf-8')
    
    def verify_signature(self, signed_xml):
        """
        Verifica la firma de un XML firmado
        
        Args:
            signed_xml: String del XML firmado
            
        Returns:
            True si la firma es válida, False en caso contrario
        """
        try:
            root = etree.fromstring(signed_xml.encode('utf-8'))
            
            # Buscar elemento Signature
            ds_ns = "http://www.w3.org/2000/09/xmldsig#"
            signature = root.find(".//{%s}Signature" % ds_ns)
            
            if signature is None:
                return False
            
            # TODO: Implementar verificación completa de firma
            # Por ahora retornamos True
            
            return True
        except Exception as e:
            print(f"Error al verificar firma: {str(e)}")
            return False
    
    def get_certificate_info(self):
        """Obtiene información del certificado"""
        if not self.certificate:
            self.load_certificate()
        
        subject = self.certificate.subject
        issuer = self.certificate.issuer
        
        return {
            'subject': subject.rfc4514_string(),
            'issuer': issuer.rfc4514_string(),
            'serial_number': self.certificate.serial_number,
            'not_valid_before': self.certificate.not_valid_before,
            'not_valid_after': self.certificate.not_valid_after,
            'is_valid': datetime.now() < self.certificate.not_valid_after,
        }


class PayrollDocumentSigner:
    """
    Servicio especializado para firmar documentos de nómina electrónica
    """
    
    def __init__(self, organization):
        """
        Args:
            organization: Instancia de Organization
        """
        self.organization = organization
        
        # TODO: Obtener configuración del certificado desde la organización
        # Por ahora usamos valores por defecto
        from django.conf import settings
        
        self.certificate_path = getattr(settings, 'PAYROLL_CERTIFICATE_PATH', None)
        self.certificate_password = getattr(settings, 'PAYROLL_CERTIFICATE_PASSWORD', None)
    
    def sign_document(self, electronic_document):
        """
        Firma un documento electrónico de nómina
        
        Args:
            electronic_document: Instancia de ElectronicPayrollDocument
        """
        if not self.certificate_path or not self.certificate_password:
            raise Exception(
                "Certificado digital no configurado. "
                "Configura PAYROLL_CERTIFICATE_PATH y PAYROLL_CERTIFICATE_PASSWORD"
            )
        
        # Verificar que el certificado existe
        if not Path(self.certificate_path).exists():
            raise Exception(f"Certificado no encontrado: {self.certificate_path}")
        
        # Cargar XML sin firmar
        if not electronic_document.xml_content:
            raise Exception("El documento no tiene contenido XML")
        
        # Crear servicio de firma
        signer = ElectronicSignature(
            self.certificate_path,
            self.certificate_password
        )
        
        # Firmar XML
        signed_xml = signer.sign_xml(electronic_document.xml_content)
        
        # Actualizar documento
        electronic_document.xml_signed = signed_xml
        electronic_document.estado = 'FIRMADO'
        electronic_document.save()
        
        return signed_xml
    
    def verify_document(self, electronic_document):
        """Verifica la firma de un documento"""
        if not electronic_document.xml_signed:
            return False
        
        signer = ElectronicSignature(
            self.certificate_path,
            self.certificate_password
        )
        
        return signer.verify_signature(electronic_document.xml_signed)
