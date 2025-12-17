"""
Generador de códigos QR para facturas electrónicas DIAN
"""
import qrcode
import base64
from io import BytesIO
from typing import Optional


class QRCodeGenerator:
    """
    Genera códigos QR para facturas electrónicas según especificaciones DIAN.
    
    El QR contiene:
    - NumFac: Número de factura
    - FecFac: Fecha de factura
    - NitFac: NIT del emisor
    - DocAdq: Documento del adquiriente
    - ValFac: Valor total de la factura
    - ValIva: Valor del IVA
    - ValOtroIm: Otros impuestos
    - ValTotal: Valor total con impuestos
    - CUFE: Código único de factura electrónica
    """
    
    @staticmethod
    def generar_qr(
        numero_factura: str,
        fecha_factura: str,
        nit_emisor: str,
        nit_adquiriente: str,
        valor_factura: str,
        valor_iva: str,
        valor_otros_impuestos: str,
        valor_total: str,
        cufe: str,
        url_validacion: Optional[str] = None
    ) -> str:
        """
        Genera un código QR en formato base64.
        
        Args:
            numero_factura: Número completo de la factura (ej: FE-00001)
            fecha_factura: Fecha en formato YYYY-MM-DD
            nit_emisor: NIT del emisor sin DV
            nit_adquiriente: Documento del cliente
            valor_factura: Valor antes de impuestos
            valor_iva: Valor del IVA
            valor_otros_impuestos: Otros impuestos (consumo, ICA, etc)
            valor_total: Valor total con impuestos
            cufe: CUFE de la factura
            url_validacion: URL opcional para validación en línea
            
        Returns:
            str: Imagen QR en base64
        """
        # Construir el texto del QR según especificaciones DIAN
        qr_data = (
            f"NumFac: {numero_factura}\n"
            f"FecFac: {fecha_factura}\n"
            f"NitFac: {nit_emisor}\n"
            f"DocAdq: {nit_adquiriente}\n"
            f"ValFac: {valor_factura}\n"
            f"ValIva: {valor_iva}\n"
            f"ValOtroIm: {valor_otros_impuestos}\n"
            f"ValTotal: {valor_total}\n"
            f"CUFE: {cufe}"
        )
        
        # Agregar URL de validación si está disponible
        if url_validacion:
            qr_data += f"\n{url_validacion}/consulta/{cufe}"
        
        # Generar el código QR
        qr = qrcode.QRCode(
            version=None,  # Auto ajustar tamaño
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Alta corrección de errores
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Crear la imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return img_base64
    
    @staticmethod
    def generar_qr_simple(cufe: str, url_validacion: str = "https://catalogo-vpfe.dian.gov.co/Document/FindDocument") -> str:
        """
        Genera un QR simple solo con el CUFE y URL de validación DIAN.
        
        Args:
            cufe: CUFE de la factura
            url_validacion: URL del servicio de validación DIAN
            
        Returns:
            str: Imagen QR en base64
        """
        # URL de consulta DIAN
        qr_data = f"{url_validacion}?documentkey={cufe}"
        
        # Generar QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return img_base64
    
    @staticmethod
    def generar_qr_para_invoice(invoice) -> str:
        """
        Genera el QR a partir de un objeto Invoice del modelo.
        
        Args:
            invoice: Instancia del modelo Invoice
            
        Returns:
            str: Imagen QR en base64
        """
        # Obtener configuración DIAN de la organización
        from apps.billing.models import DianConfiguration
        dian_config = DianConfiguration.objects.filter(
            organization=invoice.organization,
            is_active=True
        ).first()
        
        if not dian_config:
            raise ValueError("No hay configuración DIAN activa para esta organización")
        
        # Generar QR con todos los datos
        return QRCodeGenerator.generar_qr(
            numero_factura=invoice.numero_completo,
            fecha_factura=invoice.fecha_emision.strftime('%Y-%m-%d'),
            nit_emisor=dian_config.nit,
            nit_adquiriente=invoice.cliente_numero_documento,
            valor_factura=str(invoice.base_imponible),
            valor_iva=str(invoice.total_iva),
            valor_otros_impuestos='0.00',  # Por ahora solo IVA
            valor_total=str(invoice.total),
            cufe=invoice.cufe,
            url_validacion='https://catalogo-vpfe.dian.gov.co/Document/FindDocument'
        )
