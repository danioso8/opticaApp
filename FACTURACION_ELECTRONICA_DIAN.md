# 📋 FACTURACIÓN ELECTRÓNICA DIAN - COLOMBIA
## Análisis de Requisitos e Implementación

---

## 🏢 REQUISITOS LEGALES Y TÉCNICOS

### 1. **Requisitos Previos (Antes de Facturar Electrónicamente)**

#### A. Requisitos ante la DIAN:
- ✅ **RUT actualizado** con la actividad económica de prestación de servicios de salud/venta de productos ópticos
- ✅ **Inscripción como facturador electrónico** ante la DIAN
- ✅ **Resolución de facturación electrónica** (autorización de numeración)
- ✅ **Certificado digital** de firma electrónica (persona jurídica o representante legal)
- ✅ **Registro del software** (habilitación ante DIAN)

#### B. Opciones de Implementación:
1. **Proveedor Tecnológico Autorizado (PTA)** - RECOMENDADO
   - Empresas certificadas por la DIAN
   - Manejan todo el proceso técnico
   - Ejemplos: Alegra, Siigo, Factus, Asesor Electrónico, etc.
   
2. **Desarrollo Directo** - COMPLEJO
   - Requiere certificación del software
   - Implementación de XML UBL 2.1
   - Firma electrónica con certificado digital
   - Validación DIAN en tiempo real

---

## 📄 DATOS OBLIGATORIOS EN LA FACTURA ELECTRÓNICA

### 2. **Información del Emisor (Tu Óptica)**

```python
EMISOR = {
    # Identificación
    'nit': '900123456-1',  # NIT de la óptica
    'tipo_documento': '31',  # 31 = NIT
    'dv': '1',  # Dígito de verificación
    
    # Datos comerciales
    'razon_social': 'ÓPTICA EJEMPLO S.A.S',
    'nombre_comercial': 'Óptica Ejemplo',
    
    # Ubicación
    'direccion': 'Calle 123 #45-67',
    'ciudad': 'Bogotá D.C.',
    'departamento': 'Cundinamarca',
    'codigo_postal': '110111',
    'pais': 'CO',
    
    # Contacto
    'telefono': '+57 1 234 5678',
    'email': 'facturacion@opticaejemplo.com',
    
    # Fiscal
    'responsabilidad_fiscal': ['O-13', 'O-15'],  # Régimen simplificado, etc.
    'tipo_regimen': '49',  # 49 = No responsable de IVA (si aplica)
}
```

### 3. **Información del Cliente/Paciente**

```python
CLIENTE = {
    # Identificación (OBLIGATORIO)
    'tipo_documento': 'CC',  # CC, CE, NIT, PA, TI, etc.
    'numero_documento': '1234567890',
    'nombre_completo': 'Juan Pérez López',
    
    # Ubicación (OPCIONAL pero recomendado)
    'direccion': 'Calle 45 #12-34',
    'ciudad': 'Medellín',
    'departamento': 'Antioquia',
    'pais': 'CO',
    
    # Contacto (OPCIONAL)
    'telefono': '+57 300 123 4567',
    'email': 'juan.perez@email.com',
    
    # Fiscal (SI ES EMPRESA)
    'responsabilidad_fiscal': ['R-99-PN'],  # Persona natural
}
```

### 4. **Datos de la Factura**

```python
FACTURA = {
    # Numeración (CRÍTICO)
    'prefijo': 'FE',  # Ej: FE, FEPV, etc. (según resolución)
    'numero': '00001',  # Número consecutivo
    'numero_completo': 'FE-00001',
    
    # Resolución DIAN (OBLIGATORIO)
    'resolucion_numero': '18760000001',  # # de resolución
    'resolucion_fecha': '2024-01-15',
    'rango_inicio': 1,
    'rango_fin': 5000,
    'prefijo_resolucion': 'FE',
    'clave_tecnica': 'abc123...',  # Clave técnica de la resolución
    
    # Fechas
    'fecha_emision': '2024-12-15T14:30:00-05:00',  # ISO 8601
    'fecha_vencimiento': '2024-12-30T23:59:59-05:00',
    
    # Tipo de operación
    'tipo_operacion': '10',  # 10 = Venta, 20 = Devolución, etc.
    'forma_pago': '1',  # 1 = Contado, 2 = Crédito
    'medio_pago': '10',  # 10 = Efectivo, 48 = Tarjeta, etc.
    
    # Moneda
    'moneda': 'COP',
    'trm': 1,  # Tasa representativa del mercado (1 si es COP)
}
```

### 5. **Items/Líneas de la Factura**

```python
ITEMS = [
    {
        # Descripción
        'numero_linea': 1,
        'descripcion': 'Examen visual completo',
        'cantidad': 1,
        'unidad_medida': '94',  # 94 = Servicio
        
        # Precios
        'valor_unitario': 50000,  # Sin IVA
        'valor_total': 50000,  # cantidad * valor_unitario
        
        # Impuestos
        'impuesto_tipo': '01',  # 01 = IVA
        'impuesto_porcentaje': 0,  # 0%, 5%, 19%, etc.
        'impuesto_valor': 0,
        
        # Descuentos (opcional)
        'descuento_porcentaje': 0,
        'descuento_valor': 0,
        
        # Códigos (opcional)
        'codigo_producto': 'EXA-001',
        'codigo_estandar': 'GTIN',  # GTIN, EAN, UPC, etc.
    },
    {
        'numero_linea': 2,
        'descripcion': 'Montura Ray-Ban RB3025',
        'cantidad': 1,
        'unidad_medida': '94',
        'valor_unitario': 200000,
        'valor_total': 200000,
        'impuesto_tipo': '01',
        'impuesto_porcentaje': 19,  # IVA 19%
        'impuesto_valor': 38000,
        'codigo_producto': 'MON-RB3025',
    },
]
```

### 6. **Totales de la Factura**

```python
TOTALES = {
    # Base gravable
    'base_imponible': 250000,  # Suma de items sin IVA
    
    # Impuestos
    'total_iva': 38000,
    'total_impuesto_consumo': 0,
    'total_retefuente': 0,
    'total_reteiva': 0,
    'total_reteica': 0,
    
    # Descuentos
    'descuento_total': 0,
    
    # Cargos adicionales
    'cargos_adicionales': 0,
    
    # TOTAL FINAL
    'subtotal': 250000,  # Base antes de impuestos
    'total_impuestos': 38000,
    'total_factura': 288000,  # A PAGAR
    
    # Anticipos (si hay pagos parciales)
    'anticipos': [
        {
            'numero_recibo': 'ANT-001',
            'fecha': '2024-12-10',
            'valor': 100000,
        }
    ],
    'total_anticipos': 100000,
    'saldo_pendiente': 188000,  # total_factura - anticipos
}
```

### 7. **CUFE - Código Único de Factura Electrónica**

El **CUFE** es la huella digital única de cada factura:

```python
# Algoritmo de generación CUFE
def generar_cufe():
    """
    El CUFE se genera con SHA-384 de la concatenación de:
    1. Número de factura
    2. Fecha de emisión (YYYYMMDD HH:MM:SS-05:00)
    3. Valor total de la factura (sin decimales)
    4. Código impuestos (01 para IVA, 04 para INC, 03 para ICA, etc.)
    5. Valor impuestos (sin decimales)
    6. Valor total factura con impuestos (sin decimales)
    7. NIT emisor
    8. Tipo documento receptor
    9. Número documento receptor
    10. Clave técnica (de la resolución DIAN)
    11. Ambiente (1 = producción, 2 = pruebas)
    """
    
    cadena = (
        f"{numero_factura}"
        f"{fecha_emision}"
        f"{str(valor_base).zfill(15)}"
        f"01{str(valor_iva).zfill(15)}"
        f"04{str(valor_consumo).zfill(15)}"
        f"03{str(valor_ica).zfill(15)}"
        f"{str(valor_total).zfill(15)}"
        f"{nit_emisor}"
        f"{tipo_doc_receptor}"
        f"{num_doc_receptor}"
        f"{clave_tecnica}"
        f"{ambiente}"
    )
    
    cufe = hashlib.sha384(cadena.encode()).hexdigest()
    return cufe

# Ejemplo:
CUFE = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6..."
```

---

## 🔐 PROCESO DE FIRMA Y ENVÍO

### 8. **Flujo Completo**

```
1. Generar XML UBL 2.1
   └─> Factura con todos los campos obligatorios
   
2. Calcular CUFE
   └─> Incluir en el XML
   
3. Firmar XML Digitalmente
   └─> Con certificado digital (.p12 o .pfx)
   
4. Generar QR Code
   └─> Con URL de validación DIAN + CUFE
   
5. Enviar a DIAN (Web Service SOAP)
   └─> Validación en tiempo real
   
6. Recibir Respuesta DIAN
   ├─> Aprobada: Guardar XML firmado + PDF
   ├─> Rechazada: Mostrar errores y corregir
   └─> Pendiente: Esperar validación asíncrona
   
7. Enviar PDF al Cliente
   └─> Con representación gráfica + QR + XML adjunto
```

---

## 💾 CAMPOS A AGREGAR EN LA BASE DE DATOS

### 9. **Modelo Invoice (Factura)**

```python
# Nuevos campos necesarios para DIAN
class Invoice(TenantModel):
    # Campos existentes...
    
    # ===== CAMPOS DIAN =====
    
    # Numeración oficial
    prefijo = models.CharField(max_length=10, default='FE')
    numero_dian = models.PositiveIntegerField()  # Número consecutivo
    numero_completo = models.CharField(max_length=50, unique=True)  # FE-00001
    
    # Resolución de facturación
    resolucion_numero = models.CharField(max_length=50)
    resolucion_fecha = models.DateField()
    resolucion_rango_inicio = models.PositiveIntegerField()
    resolucion_rango_fin = models.PositiveIntegerField()
    resolucion_clave_tecnica = models.CharField(max_length=500)
    
    # Estado ante la DIAN
    estado_dian = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Borrador'),
            ('pending', 'Pendiente de envío'),
            ('sent', 'Enviada a DIAN'),
            ('approved', 'Aprobada por DIAN'),
            ('rejected', 'Rechazada por DIAN'),
        ],
        default='draft'
    )
    
    # CUFE (Código Único)
    cufe = models.CharField(max_length=200, blank=True)
    
    # QR Code
    qr_code = models.TextField(blank=True)  # Base64 o URL
    
    # Archivos
    xml_content = models.TextField(blank=True)  # XML UBL
    xml_signed = models.TextField(blank=True)  # XML firmado
    xml_url = models.URLField(blank=True)  # URL pública del XML
    pdf_url = models.URLField(blank=True)  # URL pública del PDF
    
    # Respuesta DIAN
    dian_response = models.JSONField(null=True, blank=True)
    dian_sent_at = models.DateTimeField(null=True, blank=True)
    dian_approved_at = models.DateTimeField(null=True, blank=True)
    
    # Tipo de operación
    tipo_operacion = models.CharField(
        max_length=2,
        choices=[
            ('10', 'Venta estándar'),
            ('20', 'Nota débito'),
            ('30', 'Nota crédito'),
        ],
        default='10'
    )
    
    # Forma y medio de pago
    forma_pago = models.CharField(
        max_length=1,
        choices=[
            ('1', 'Contado'),
            ('2', 'Crédito'),
        ],
        default='1'
    )
    
    medio_pago = models.CharField(
        max_length=2,
        choices=[
            ('10', 'Efectivo'),
            ('42', 'Consignación bancaria'),
            ('47', 'Transferencia débito bancaria'),
            ('48', 'Tarjeta crédito'),
            ('49', 'Tarjeta débito'),
        ],
        default='10'
    )
    
    # Vencimiento (para crédito)
    fecha_vencimiento = models.DateTimeField(null=True, blank=True)
```

### 10. **Modelo OrganizationDianConfig**

```python
class OrganizationDianConfig(TenantModel):
    """Configuración DIAN por organización"""
    
    # Datos del emisor
    nit = models.CharField(max_length=20)
    dv = models.CharField(max_length=1)
    razon_social = models.CharField(max_length=300)
    nombre_comercial = models.CharField(max_length=300)
    
    # Ubicación
    direccion = models.CharField(max_length=500)
    ciudad = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20)
    
    # Contacto
    telefono = models.CharField(max_length=50)
    email_facturacion = models.EmailField()
    
    # Responsabilidad fiscal
    responsabilidad_fiscal = models.JSONField(default=list)  # ['O-13', 'O-15']
    tipo_regimen = models.CharField(max_length=2, default='49')
    
    # Resolución vigente
    resolucion_actual = models.CharField(max_length=50)
    resolucion_fecha = models.DateField()
    prefijo = models.CharField(max_length=10, default='FE')
    numero_actual = models.PositiveIntegerField(default=0)  # Último usado
    numero_inicio = models.PositiveIntegerField()
    numero_fin = models.PositiveIntegerField()
    clave_tecnica = models.CharField(max_length=500)
    
    # Certificado digital
    certificado_digital = models.FileField(upload_to='certificates/')  # .p12/.pfx
    certificado_password = models.CharField(max_length=200)  # Encriptado
    certificado_valido_hasta = models.DateField()
    
    # Proveedor tecnológico (si se usa)
    usa_proveedor = models.BooleanField(default=True)
    proveedor_nombre = models.CharField(max_length=100, blank=True)  # Alegra, Siigo, etc.
    proveedor_api_key = models.CharField(max_length=500, blank=True)
    proveedor_api_url = models.URLField(blank=True)
    
    # Ambiente
    ambiente = models.CharField(
        max_length=10,
        choices=[
            ('pruebas', 'Pruebas'),
            ('produccion', 'Producción'),
        ],
        default='pruebas'
    )
    
    # Estado
    is_active = models.BooleanField(default=False)
    habilitado_dian = models.BooleanField(default=False)
    fecha_habilitacion = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Configuración DIAN"
        verbose_name_plural = "Configuraciones DIAN"
    
    def get_next_numero(self):
        """Obtiene el siguiente número disponible"""
        self.numero_actual += 1
        if self.numero_actual > self.numero_fin:
            raise ValueError("Se agotó la numeración de la resolución")
        self.save()
        return self.numero_actual
    
    def get_numero_completo(self):
        """Retorna número con prefijo: FE-00001"""
        return f"{self.prefijo}-{str(self.numero_actual).zfill(5)}"
```

---

## 🚀 RECOMENDACIÓN DE IMPLEMENTACIÓN

### FASE 1: Preparación Legal (2-4 semanas)
1. Inscribirse como facturador electrónico ante DIAN
2. Obtener resolución de facturación
3. Contratar proveedor tecnológico autorizado (RECOMENDADO)

### FASE 2: Integración Técnica (1-2 semanas)
1. Implementar modelos de BD con campos DIAN
2. Integrar API del proveedor tecnológico
3. Configurar generación de PDF con QR

### FASE 3: Pruebas (1 semana)
1. Ambiente de pruebas DIAN
2. Validar facturas de prueba
3. Ajustar errores

### FASE 4: Producción
1. Habilitar en producción
2. Facturar electrónicamente

---

## 📌 PROVEEDORES TECNOLÓGICOS RECOMENDADOS

| Proveedor | Precio Aprox. | Características |
|-----------|---------------|-----------------|
| **Alegra** | $49.000/mes | API REST, fácil integración, soporte |
| **Siigo** | $60.000/mes | Completo, contabilidad integrada |
| **Factus** | $35.000/mes | Económico, API REST |
| **Asesor Electrónico** | $40.000/mes | Especializado en salud |

**VENTAJAS DE USAR PROVEEDOR:**
- ✅ No necesitas certificado digital propio
- ✅ Ellos manejan XML, firma, envío DIAN
- ✅ Soporte técnico
- ✅ Solo envías JSON por API y ellos devuelven factura aprobada

---

## 💡 RECOMENDACIÓN FINAL

Para tu óptica, lo mejor es:

1. **Usar Proveedor Tecnológico** (Alegra, Factus, etc.)
2. **Tu sistema solo genera el JSON** con los datos de la factura
3. **El proveedor genera XML, firma, envía DIAN y te devuelve PDF + XML**
4. **Guardas el resultado en tu BD**

**NO intentes desarrollo directo a menos que tengas un equipo técnico especializado.**

---

## 📞 PRÓXIMOS PASOS

1. ¿Ya tienes resolución DIAN o necesitas tramitarla?
2. ¿Prefieres contratar proveedor o desarrollo directo?
3. ¿Quieres que implemente la integración con algún proveedor específico?

**Responde estas preguntas para continuar con la implementación** 🚀
