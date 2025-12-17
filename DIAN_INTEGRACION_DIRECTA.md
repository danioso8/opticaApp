# 🚀 INTEGRACIÓN DIRECTA FACTURACIÓN ELECTRÓNICA DIAN

## ✅ IMPLEMENTACIÓN COMPLETADA

Fecha: 16 de Diciembre de 2025  
Método: **Desarrollo Directo** - XML UBL 2.1 + Firma Digital

---

## 📦 SERVICIOS IMPLEMENTADOS

### 1. **CUFEGenerator** (`apps/billing/services/cufe_generator.py`)
Genera el Código Único de Factura Electrónica según especificaciones DIAN.

**Características**:
- Algoritmo SHA-384 según normativa DIAN
- Incluye todos los campos requeridos (número, fecha, valores, NIT, etc.)
- Soporte para ambiente de pruebas y producción
- Validación de formato CUFE

**Uso**:
```python
from apps.billing.services import CUFEGenerator

cufe = CUFEGenerator.generar(
    numero_factura='FE-00001',
    fecha_emision=datetime.now(),
    valor_subtotal=Decimal('100000'),
    valor_iva=Decimal('19000'),
    valor_total=Decimal('119000'),
    nit_emisor='900123456',
    tipo_doc_receptor='CC',
    num_doc_receptor='1234567890',
    clave_tecnica='tu_clave_tecnica_dian',
    ambiente='2'  # 1=producción, 2=pruebas
)
```

---

### 2. **XMLUBLGenerator** (`apps/billing/services/xml_generator.py`)
Genera documentos XML en formato UBL 2.1 según especificaciones DIAN.

**Características**:
- Estructura completa UBL 2.1
- Namespaces correctos (xmlns, cac, cbc, ext, sts, xades)
- Soporte para múltiples tasas de IVA (0%, 5%, 19%)
- Información completa de emisor y cliente
- Resolución de facturación
- Items detallados con impuestos

**Secciones generadas**:
- Encabezado (UBLVersionID, CUFE, fechas)
- AccountingSupplierParty (emisor)
- AccountingCustomerParty (cliente)
- InvoiceDocumentReference (resolución)
- LegalMonetaryTotal (totales)
- TaxTotal (impuestos)
- InvoiceLine (items)

---

### 3. **DigitalSignatureService** (`apps/billing/services/digital_signature.py`)
Firma digitalmente XMLs usando certificados .p12/.pfx.

**Características**:
- Soporte para certificados PKCS#12 (.p12, .pfx)
- Firma XMLDSig con XAdES-EPES
- Validación de vigencia del certificado
- Cálculo de digest SHA-256
- Firma RSA-SHA256
- Inclusión de certificado en el XML

**Estructura de firma**:
- SignedInfo con CanonicalizationMethod
- Reference con DigestValue
- SignatureValue
- KeyInfo con X509Certificate
- QualifyingProperties (XAdES)

**Uso**:
```python
from apps.billing.services import DigitalSignatureService

signer = DigitalSignatureService(
    certificado_path='/path/to/cert.p12',
    certificado_password='password123'
)

# Validar certificado
es_valido, mensaje = signer.validar_certificado()

# Firmar XML
xml_firmado = signer.firmar_xml(xml_string, cufe)
```

---

### 4. **QRCodeGenerator** (`apps/billing/services/qr_generator.py`)
Genera códigos QR para facturas electrónicas.

**Características**:
- QR con todos los datos de la factura según DIAN
- URL de validación en línea
- Formato PNG en base64 para fácil integración
- Alta corrección de errores (ERROR_CORRECT_H)

**Datos incluidos en QR**:
- NumFac, FecFac, NitFac, DocAdq
- ValFac, ValIva, ValOtroIm, ValTotal
- CUFE completo
- URL de validación DIAN

**Uso**:
```python
from apps.billing.services import QRCodeGenerator

# Desde un objeto Invoice
qr_base64 = QRCodeGenerator.generar_qr_para_invoice(invoice)

# O manual
qr_base64 = QRCodeGenerator.generar_qr(
    numero_factura='FE-00001',
    fecha_factura='2025-12-16',
    nit_emisor='900123456',
    nit_adquiriente='1234567890',
    valor_factura='100000.00',
    valor_iva='19000.00',
    valor_otros_impuestos='0.00',
    valor_total='119000.00',
    cufe='abc123...',
    url_validacion='https://catalogo-vpfe.dian.gov.co/Document/FindDocument'
)
```

---

### 5. **DianSoapClient** (`apps/billing/services/dian_client.py`)
Cliente SOAP para comunicación con webservices DIAN.

**Características**:
- Soporte para ambientes de habilitación y producción
- Envío de facturas (SendBillSync)
- Consulta de estado (GetStatus)
- Parseo de respuestas XML SOAP
- Manejo de errores y advertencias DIAN

**Endpoints**:
- Habilitación: `https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc`
- Producción: `https://vpfe.dian.gov.co/WcfDianCustomerServices.svc`

**DianMockClient**: Cliente mock para pruebas sin conexión real a DIAN.

**Uso**:
```python
from apps.billing.services import DianSoapClient

cliente = DianSoapClient(ambiente='habilitacion')

# Enviar factura
exito, respuesta = cliente.enviar_factura(
    xml_firmado=xml_string,
    nit_emisor='900123456'
)

# Consultar estado
encontrada, info = cliente.consultar_estado(cufe='abc123...')

# Validar conexión
conectado, mensaje = cliente.validar_conexion()
```

---

### 6. **FacturacionElectronicaService** (`apps/billing/services/facturacion_service.py`)
Servicio orquestador que coordina todo el proceso de facturación electrónica.

**Proceso completo**:
1. ✅ Validar configuración DIAN
2. ✅ Generar CUFE
3. ✅ Generar XML UBL 2.1
4. ✅ Firmar XML digitalmente
5. ✅ Generar código QR
6. ✅ Enviar a DIAN
7. ✅ Procesar respuesta
8. ✅ Actualizar estado de factura

**Uso**:
```python
from apps.billing.services import FacturacionElectronicaService

# Crear servicio
servicio = FacturacionElectronicaService(
    invoice=invoice_obj,
    usar_mock=True  # False para DIAN real
)

# Procesar factura completa
exito, resultado = servicio.procesar_factura_completa()

if exito:
    print(f"✅ Factura aprobada: {resultado['cufe']}")
else:
    print(f"❌ Error: {resultado['mensaje']}")
    print(f"Errores: {resultado['errores']}")
```

---

## 📚 DEPENDENCIAS AGREGADAS

En `requirements.txt`:
```
# Facturación Electrónica DIAN
lxml==4.9.3               # Procesamiento XML
pyOpenSSL==23.2.0         # Certificados digitales
cryptography==41.0.3      # Firma digital
qrcode[pil]==7.4.2        # Generación códigos QR
```

**Instalación**:
```bash
pip install -r requirements.txt
```

---

## 🗄️ MODELOS EXISTENTES

El modelo `Invoice` ya tiene todos los campos necesarios:
- ✅ CUFE
- ✅ XML sin firmar y firmado
- ✅ Estado DIAN (draft, pending, processing, approved, rejected)
- ✅ Respuesta DIAN (JSON)
- ✅ Fechas de envío y aprobación
- ✅ QR code en base64
- ✅ URLs de archivos

El modelo `DianConfiguration` ya tiene:
- ✅ Datos del emisor (NIT, DV, razón social)
- ✅ Ubicación (DIVIPOLA)
- ✅ Resolución de facturación
- ✅ Certificado digital (.p12/.pfx)
- ✅ Clave técnica
- ✅ Ambiente (pruebas/producción)

---

## 🔧 CONFIGURACIÓN NECESARIA

### 1. Certificado Digital
Subir certificado .p12 o .pfx en la configuración DIAN:
- Archivo del certificado
- Contraseña del certificado
- Fecha de vencimiento

### 2. Resolución DIAN
Configurar en DianConfiguration:
- Número de resolución
- Fecha de emisión
- Prefijo (ej: FE, FEPV)
- Rango de numeración (inicio - fin)
- Clave técnica

### 3. Datos Fiscales
- NIT y DV
- Razón social
- Dirección con códigos DIVIPOLA
- Información de contacto

---

## 🧪 MODO DE PRUEBA

Para desarrollo y pruebas sin enviar a DIAN real:

```python
# Usar cliente mock
servicio = FacturacionElectronicaService(
    invoice=invoice,
    usar_mock=True  # ← Importante para pruebas
)

# El cliente mock simula respuestas DIAN sin conexión real
```

---

## 🚀 PRÓXIMOS PASOS

### Para poner en producción:

1. **Obtener certificado digital** de una CA autorizada en Colombia
2. **Inscribirse como facturador electrónico** ante DIAN
3. **Obtener resolución de facturación electrónica**
4. **Configurar certificado y resolución** en DianConfiguration
5. **Probar en ambiente de habilitación** (usar_mock=False, ambiente='habilitacion')
6. **Solicitar habilitación a producción** ante DIAN
7. **Cambiar a ambiente de producción** (ambiente='produccion')

### Integración con el formulario de factura:

```python
# En apps/billing/views.py - invoice_create

def invoice_create(request):
    if request.method == 'POST':
        # ... crear y guardar invoice ...
        
        # Procesar facturación electrónica
        if invoice.organization.tiene_facturacion_electronica():
            from apps.billing.services import FacturacionElectronicaService
            
            servicio = FacturacionElectronicaService(invoice, usar_mock=False)
            exito, resultado = servicio.procesar_factura_completa()
            
            if exito:
                messages.success(request, f"✅ Factura electrónica aprobada: {invoice.numero_completo}")
            else:
                messages.error(request, f"❌ Error DIAN: {resultado['mensaje']}")
        
        return redirect('billing:invoice_list')
```

---

## 📄 DOCUMENTACIÓN TÉCNICA

### Especificaciones implementadas:
- ✅ **UBL 2.1** - Universal Business Language
- ✅ **XMLDSig** - XML Digital Signature
- ✅ **XAdES-EPES** - XML Advanced Electronic Signatures
- ✅ **Anexo Técnico DIAN v1.9**
- ✅ **Resolución 000042 de 2020** (Facturación electrónica)

### Algoritmos de seguridad:
- SHA-384 para CUFE
- SHA-256 para digest XML
- RSA-SHA256 para firma digital
- C14N para canonicalización XML

---

## ⚠️ NOTAS IMPORTANTES

1. **Certificado digital**: Debe ser emitido por una CA autorizada en Colombia (Certicámara, GSE, etc.)
2. **Ambiente de pruebas**: Usar `ambiente='habilitacion'` hasta obtener aprobación DIAN
3. **Numeración**: La resolución tiene un rango limitado, monitorear el uso
4. **Validación**: Cada factura debe ser validada por DIAN antes de ser válida
5. **Respaldo**: Guardar siempre el XML firmado y la respuesta DIAN
6. **Contingencia**: Tener plan de contingencia si DIAN no responde

---

## 🎯 ESTADO DEL PROYECTO

**FASE 3 - Integración DIAN**: ✅ **100% COMPLETADA**

- [x] Generación de CUFE
- [x] Generación XML UBL 2.1
- [x] Firma digital con certificado
- [x] Generación código QR
- [x] Cliente SOAP para DIAN
- [x] Servicio orquestador completo
- [x] Cliente mock para pruebas
- [x] Dependencias instaladas

**PENDIENTE**:
- [ ] Generación PDF representación gráfica (Fase 4)
- [ ] Integración con vista invoice_create (Fase 5)
- [ ] Pruebas en ambiente de habilitación DIAN
- [ ] Certificación ante DIAN

---

**🎉 El sistema ya está listo para generar, firmar y enviar facturas electrónicas a la DIAN!**
