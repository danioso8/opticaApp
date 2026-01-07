# Configuración de Nómina Electrónica - DIAN Colombia

Este documento describe los pasos necesarios para configurar y utilizar el módulo de Nómina Electrónica compatible con la DIAN (Dirección de Impuestos y Aduanas Nacionales de Colombia).

## 📋 Requisitos Previos

### 1. Registro ante la DIAN

Para poder generar nóminas electrónicas, tu organización debe:

1. **Estar registrada en el RUT** (Registro Único Tributario)
2. **Solicitar habilitación** para nómina electrónica en la DIAN
3. **Obtener certificado digital** (.p12 o .pfx) de una entidad certificadora autorizada

### 2. Entidades Certificadoras Autorizadas en Colombia

- **Certicámara**: https://www.certicamara.com/
- **GSE**: https://www.gse.com.co/
- **Andes SCD**: https://www.andesscd.com.co/

El certificado digital debe ser de tipo **persona jurídica** y debe incluir firma electrónica.

## 🔧 Configuración del Sistema

### 1. Obtener Credenciales de la DIAN

Después de registrarte en la DIAN para nómina electrónica, recibirás:

- **Software ID**: Identificador único de tu software
- **Software PIN**: Clave para firmar documentos
- **Test Set ID**: ID para pruebas en ambiente de habilitación (opcional)

### 2. Configurar Variables de Entorno

Edita tu archivo `.env` y agrega:

```env
# ==================== NOMINA ELECTRONICA - DIAN ====================

# Ruta al certificado digital (.p12 o .pfx)
# Ejemplo Windows: C:\certificados\mi_empresa.p12
# Ejemplo Linux: /opt/certificados/mi_empresa.p12
PAYROLL_CERTIFICATE_PATH=ruta/al/certificado.p12
PAYROLL_CERTIFICATE_PASSWORD=tu_password_del_certificado

# Credenciales DIAN
DIAN_SOFTWARE_ID=tu_software_id_de_dian
DIAN_SOFTWARE_PIN=tu_pin_de_dian
DIAN_TEST_SET_ID=tu_test_set_id  # Solo para ambiente de pruebas

# Modo de operación
# True = Ambiente de Habilitación (pruebas)
# False = Ambiente de Producción
DIAN_TEST_MODE=True
```

### 3. Proteger el Certificado Digital

⚠️ **IMPORTANTE**: El certificado digital es como la llave de tu empresa. Debes:

1. **Guardarlo en un lugar seguro** fuera del repositorio de código
2. **Hacer backup** en múltiples ubicaciones seguras
3. **Usar permisos restrictivos** en el archivo:
   - Windows: Propiedades → Seguridad → Solo lectura para administradores
   - Linux: `chmod 600 /ruta/al/certificado.p12`
4. **Nunca subirlo a GitHub** u otro repositorio público
5. **Añadirlo al .gitignore**

```gitignore
# Certificados digitales
*.p12
*.pfx
certificados/
```

## 📝 Configuración Inicial

### 1. Ejecutar Migraciones

```bash
python manage.py migrate
```

### 2. Inicializar Conceptos de Nómina

Este comando crea los conceptos básicos de devengos y deducciones:

```bash
python manage.py init_payroll_concepts
```

Conceptos creados automáticamente:

**Devengos:**
- Salario Básico
- Horas Extras
- Auxilio de Transporte
- Comisiones
- Bonificaciones
- Viáticos
- Incapacidades
- Licencias

**Deducciones:**
- Salud (4%)
- Pensión (4%)
- Fondo de Solidaridad Pensional
- Retención en la Fuente
- Préstamos
- Embargo
- Cooperativas

### 3. Crear Empleados

Accede a **Dashboard → Nómina Electrónica → Empleados** y registra:

- Información personal (nombres, apellidos, documento)
- Información laboral (cargo, salario, tipo de contrato)
- Información bancaria (para pagos)

## 🚀 Uso del Sistema

### Flujo de Trabajo de Nómina

```
1. BORRADOR → 2. CALCULADO → 3. APROBADO → 4. VALIDADO_DIAN
```

#### 1. Crear Período de Nómina

1. Ve a **Nómina Electrónica → Períodos**
2. Haz clic en **Nuevo Período**
3. Completa:
   - Nombre (ej: "Enero 2024")
   - Fecha inicio, fin y pago
   - Tipo de nómina (Mensual, Quincenal, etc.)
4. Guarda

#### 2. Calcular Nómina

1. Entra al período creado
2. Haz clic en **Calcular**
3. El sistema:
   - Genera entradas para todos los empleados activos
   - Calcula devengos (salario, horas extras, etc.)
   - Aplica deducciones automáticas (salud 4%, pensión 4%)
   - Calcula neto a pagar

#### 3. Aprobar Nómina

1. Revisa los cálculos
2. Descarga el **Reporte PDF** para verificar
3. Haz clic en **Aprobar**

#### 4. Enviar a la DIAN

⚠️ **Solo en Producción** o **Ambiente de Habilitación**

1. Asegúrate de tener configurado el certificado digital
2. Haz clic en **Enviar a DIAN**
3. El sistema:
   - Genera el XML según especificaciones DIAN
   - Firma digitalmente el documento
   - Envía a los servicios web de la DIAN
   - Recibe respuesta de validación

#### 5. Generar Desprendibles de Pago

- En la tabla de empleados del período, haz clic en el ícono PDF
- Descarga desprendible individual para cada empleado
- Los empleados pueden usar este documento como comprobante de pago

## 🧪 Pruebas (Ambiente de Habilitación)

La DIAN requiere que pruebes tu sistema antes de pasar a producción:

1. **Configura modo de pruebas**: `DIAN_TEST_MODE=True`
2. **Usa el Test Set ID** proporcionado por la DIAN
3. **Envía documentos de prueba** y verifica respuestas
4. **Corrige errores** si los hay
5. **Solicita habilitación definitiva** cuando todas las pruebas pasen

URLs de servicios DIAN:
- **Habilitación (Pruebas)**: https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc
- **Producción**: https://vpfe.dian.gov.co/WcfDianCustomerServices.svc

## 📊 Reportes y Documentos

### Reporte Consolidado de Nómina (PDF)

Descarga un reporte completo del período con:
- Resumen general
- Detalle por empleado
- Totales de devengos, deducciones y neto

### Desprendibles de Pago (PDF)

Documento individual para cada empleado con:
- Datos del empleado
- Detalle de devengos
- Detalle de deducciones
- Neto a pagar
- Información bancaria

### XML Electrónico (DIAN)

Documento firmado digitalmente según estándar DIAN con:
- Información del empleador
- Datos del trabajador
- Periodo de pago
- Devengos y deducciones
- Firma digital XMLDSig
- CUFE (Código Único de Factura Electrónica)

## 🔍 Consultar Estado en DIAN

Para verificar el estado de un documento enviado:

1. Ve al detalle del período
2. Haz clic en **Consultar Estado**
3. El sistema muestra:
   - Estado actual (Aceptado, Rechazado, etc.)
   - Código de respuesta
   - Mensaje de la DIAN

## ⚠️ Solución de Problemas

### Error: "Certificado no encontrado"

- Verifica que la ruta en `PAYROLL_CERTIFICATE_PATH` sea correcta
- Verifica que el archivo existe y tienes permisos de lectura

### Error: "Error al cargar certificado"

- Verifica que la contraseña en `PAYROLL_CERTIFICATE_PASSWORD` sea correcta
- Asegúrate de que el certificado esté en formato .p12 o .pfx

### Error: "Documento debe estar firmado"

- Verifica que el certificado digital esté configurado correctamente
- Revisa los logs para errores específicos de firma

### Error al enviar a DIAN: "SOAP Fault"

- Verifica tus credenciales DIAN (SOFTWARE_ID, PIN)
- Asegúrate de estar en el modo correcto (TEST_MODE)
- Revisa que el XML cumpla con el esquema DIAN

### Error: "Certificado vencido"

- Los certificados digitales tienen vigencia limitada (1-3 años)
- Renueva tu certificado con la entidad certificadora
- Actualiza `PAYROLL_CERTIFICATE_PATH` con el nuevo certificado

## 📚 Referencias

- **DIAN Nómina Electrónica**: https://www.dian.gov.co/fizcalizacioncontrol/herramienconsulta/FacturaElectronica/Nomina/Paginas/default.aspx
- **Especificación Técnica**: Anexo técnico de nómina electrónica versión 1.0
- **Validación Pre-RUT**: https://muisca.dian.gov.co/
- **Soporte DIAN**: 01 8000 910 300

## 🔐 Seguridad

1. **Nunca compartas** tu certificado digital
2. **Usa HTTPS** en producción para todas las comunicaciones
3. **Realiza backups** regulares de la base de datos
4. **Audita** los accesos al módulo de nómina
5. **Limita permisos** solo a usuarios autorizados (owner/admin)

## 📞 Soporte

Para problemas técnicos con el módulo:
- Revisa los logs de Django: `python manage.py runserver --verbosity 2`
- Consulta la documentación de la DIAN
- Contacta a tu proveedor de certificados digitales

---

**Última actualización**: Enero 2025
**Versión del módulo**: 1.0.0
