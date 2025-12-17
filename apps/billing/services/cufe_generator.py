"""
Generador de CUFE (Código Único de Factura Electrónica)
según especificaciones DIAN Colombia
"""
import hashlib
from datetime import datetime
from decimal import Decimal


class CUFEGenerator:
    """
    Genera el CUFE según el algoritmo DIAN usando SHA-384.
    
    El CUFE es un hash SHA-384 de la concatenación de:
    1. Número de factura
    2. Fecha de emisión
    3. Valor total de la factura (sin decimales)
    4. Códigos y valores de impuestos
    5. Valor total con impuestos
    6. NIT emisor
    7. Tipo y número de documento receptor
    8. Clave técnica (de la resolución)
    9. Ambiente (1=producción, 2=pruebas)
    """
    
    @staticmethod
    def generar(
        numero_factura: str,
        fecha_emision: datetime,
        valor_subtotal: Decimal,
        valor_iva: Decimal,
        valor_total: Decimal,
        nit_emisor: str,
        tipo_doc_receptor: str,
        num_doc_receptor: str,
        clave_tecnica: str,
        ambiente: str = '2'  # 1=producción, 2=pruebas
    ) -> str:
        """
        Genera el CUFE según especificaciones DIAN.
        
        Args:
            numero_factura: Número completo con prefijo (ej: FE-00001)
            fecha_emision: Fecha y hora de emisión
            valor_subtotal: Subtotal de la factura
            valor_iva: Total de IVA
            valor_total: Total de la factura
            nit_emisor: NIT del emisor sin DV
            tipo_doc_receptor: Tipo de documento del cliente (CC, NIT, etc)
            num_doc_receptor: Número de documento del cliente
            clave_tecnica: Clave técnica de la resolución DIAN
            ambiente: 1 para producción, 2 para pruebas
            
        Returns:
            str: CUFE (hash SHA-384 en hexadecimal)
        """
        
        # Formatear fecha según especificación DIAN: YYYY-MM-DD HH:MM:SS-05:00
        fecha_formateada = fecha_emision.strftime('%Y-%m-%d %H:%M:%S-05:00')
        
        # Convertir valores a enteros sin decimales (multiplicar por 100)
        subtotal_sin_decimales = str(int(valor_subtotal * 100)).zfill(15)
        iva_sin_decimales = str(int(valor_iva * 100)).zfill(15)
        total_sin_decimales = str(int(valor_total * 100)).zfill(15)
        
        # Construir cadena para el hash según especificación DIAN
        # Formato: NumFac + Fecha + ValorBase + CodImp1 + ValorImp1 + ... + ValorTotal + NitEmisor + TipoDocReceptor + NumDocReceptor + ClaveTecnica + Ambiente
        cadena = (
            f"{numero_factura}"
            f"{fecha_formateada}"
            f"{subtotal_sin_decimales}"
            f"01{iva_sin_decimales}"  # 01 = Código para IVA
            f"{total_sin_decimales}"
            f"{nit_emisor}"
            f"{tipo_doc_receptor}"
            f"{num_doc_receptor}"
            f"{clave_tecnica}"
            f"{ambiente}"
        )
        
        # Generar hash SHA-384
        cufe = hashlib.sha384(cadena.encode('utf-8')).hexdigest()
        
        return cufe
    
    @staticmethod
    def validar_cufe(cufe: str) -> bool:
        """
        Valida que el CUFE tenga el formato correcto.
        
        Args:
            cufe: CUFE a validar
            
        Returns:
            bool: True si el CUFE es válido
        """
        # El CUFE debe ser un hash SHA-384 en hexadecimal (96 caracteres)
        if not cufe:
            return False
            
        if len(cufe) != 96:
            return False
            
        # Verificar que solo contenga caracteres hexadecimales
        try:
            int(cufe, 16)
            return True
        except ValueError:
            return False
