# 📋 Módulo de Nómina Electrónica - OpticaApp

## ✅ Implementación Inicial Completada

Módulo de nómina electrónica integrado con DIAN Colombia para generar y enviar documentos soporte de pago de nómina electrónica.

---

## 🎯 Características Implementadas

### ✅ FASE 1: Estructura y Base de Datos

- [x] App Django completa (`apps/payroll`)
- [x] 8 modelos de base de datos:
  - `Employee` - Gestión de empleados
  - `AccrualConcept` - Conceptos de devengados
  - `DeductionConcept` - Conceptos de deducciones  
  - `PayrollPeriod` - Períodos de nómina
  - `PayrollEntry` - Entradas de nómina por empleado
  - `Accrual` - Devengados individuales
  - `Deduction` - Deducciones individuales
  - `ElectronicPayrollDocument` - Documentos XML DIAN
- [x] Migraciones aplicadas correctamente
- [x] Signals para cálculos automáticos de totales

### ✅ FASE 2: API REST

- [x] 8 Serializers completos
- [x] 8 ViewSets con operaciones CRUD
- [x] Endpoints REST configurados:
  - `/dashboard/payroll/api/employees/`
  - `/dashboard/payroll/api/accrual-concepts/`
  - `/dashboard/payroll/api/deduction-concepts/`
  - `/dashboard/payroll/api/periods/`
  - `/dashboard/payroll/api/entries/`
  - `/dashboard/payroll/api/accruals/`
  - `/dashboard/payroll/api/deductions/`
  - `/dashboard/payroll/api/documents/`

### ✅ FASE 3: Lógica de Negocio

- [x] Cálculo automático de nómina
- [x] Endpoint para calcular período: `POST /periods/{id}/calcular/`
- [x] Cálculo de devengados (salario básico)
- [x] Cálculo de deducciones obligatorias (salud 4%, pensión 4%)
- [x] Actualización automática de totales
- [x] Endpoint para aprobar período: `POST /periods/{id}/aprobar/`

### ✅ FASE 4: Generación XML DIAN

- [x] Generador de XML según especificaciones DIAN
- [x] Estructura completa del documento electrónico:
  - Información general
  - Datos del empleador
  - Datos del trabajador
  - Información del pago
  - Devengados detallados
  - Deducciones detalladas
- [x] Generación de CUFE (Código Único)
- [x] Uso de namespaces oficiales DIAN

### ✅ FASE 5: Herramientas Administrativas

- [x] Admin de Django configurado para todos los modelos
- [x] Comando de inicialización: `init_payroll_concepts`
  - Crea conceptos de devengados predefinidos
  - Crea conceptos de deducciones predefinidos
- [x] Filtros y búsqueda en todas las vistas

---

## 🚀 Cómo Usar

### 1. Inicializar Conceptos de Nómina

```bash
python manage.py init_payroll_concepts
```

Esto creará los conceptos básicos:
- **Devengados**: Salario básico, auxilio de transporte, horas extras, comisiones, etc.
- **Deducciones**: Salud, pensión, retención, libranzas, etc.

### 2. Crear Empleados

**Vía Admin Django:**
```
http://localhost:8000/admin/payroll/employee/
```

**Vía API:**
```bash
POST /dashboard/payroll/api/employees/
{
  "tipo_documento": "CC",
  "numero_documento": "1234567890",
  "primer_nombre": "Juan",
  "primer_apellido": "Pérez",
  "email": "juan@example.com",
  "direccion": "Calle 123",
  "ciudad": "Bogotá",
  "departamento": "Cundinamarca",
  "tipo_contrato": "INDEFINIDO",
  "fecha_ingreso": "2024-01-01",
  "cargo": "Optómetra",
  "salario_basico": 2000000
}
```

### 3. Crear Período de Nómina

```bash
POST /dashboard/payroll/api/periods/
{
  "nombre": "Nómina Enero 2026",
  "tipo_periodo": "MENSUAL",
  "fecha_inicio": "2026-01-01",
  "fecha_fin": "2026-01-31",
  "fecha_pago": "2026-02-01"
}
```

### 4. Calcular Nómina

```bash
POST /dashboard/payroll/api/periods/{id}/calcular/
```

Esto automáticamente:
- Crea entradas para todos los empleados activos
- Agrega salario básico como devengado
- Calcula salud (4%) y pensión (4%) como deducciones
- Actualiza totales

### 5. Revisar y Ajustar

Puedes agregar devengados o deducciones adicionales:

```bash
# Agregar horas extras
POST /dashboard/payroll/api/accruals/
{
  "entrada": 1,
  "concepto": 3,
  "cantidad": 10,
  "valor_unitario": 15000,
  "valor": 150000
}

# Agregar deducción
POST /dashboard/payroll/api/deductions/
{
  "entrada": 1,
  "concepto": 7,
  "valor": 100000
}
```

### 6. Aprobar Nómina

```bash
POST /dashboard/payroll/api/periods/{id}/aprobar/
```

---

## 📊 Estructura de Base de Datos

### Employee (Empleados)
- Información personal (nombres, documento, contacto)
- Información laboral (contrato, cargo, salario)
- Información bancaria (banco, cuenta)

### PayrollPeriod (Períodos)
- Fechas de nómina
- Estado del proceso
- Totales generales

### PayrollEntry (Entradas)
- Relación empleado-período
- Días trabajados
- Totales individuales

### Accrual (Devengados)
- Conceptos de ingresos
- Cantidades y valores

### Deduction (Deducciones)
- Conceptos de descuentos
- Porcentajes y valores

---

## 🔧 Próximos Pasos

### Pendientes de Implementación

#### 1. Firma Electrónica
- [ ] Integración con certificado digital (.p12)
- [ ] Firma XML usando cryptography
- [ ] Validación de firma

#### 2. Integración DIAN
- [ ] Conexión a API DIAN (habilitación/producción)
- [ ] Envío de documentos
- [ ] Recepción de respuestas
- [ ] Manejo de errores y reintentos

#### 3. Frontend Web
- [ ] Dashboard de nómina
- [ ] Gestión de empleados
- [ ] Liquidación de nómina
- [ ] Vista de desprendibles
- [ ] Reportes

#### 4. Reportes y Documentos
- [ ] Desprendibles de pago (PDF)
- [ ] Resumen de nómina
- [ ] Provisiones de seguridad social
- [ ] Certificados laborales

#### 5. Funcionalidades Avanzadas
- [ ] Cálculo de prestaciones sociales
- [ ] Liquidación de contratos
- [ ] Integración con contabilidad
- [ ] Histórico de nóminas

---

## 📦 Dependencias Requeridas

Agregar a `requirements.txt`:

```txt
lxml>=4.9.0          # Generación de XML
cryptography>=41.0.0  # Firma electrónica (próximamente)
celery>=5.3.0        # Tareas asíncronas (próximamente)
```

Instalar:
```bash
pip install lxml
```

---

## 🔐 Configuración DIAN

### Variables de Entorno (.env)

```env
# Nómina Electrónica DIAN
PAYROLL_DIAN_AMBIENTE=2  # 1: Producción, 2: Pruebas
PAYROLL_DIAN_URL_HABILITACION=https://habilitacion-catalogo-vpfe.dian.gov.co
PAYROLL_DIAN_URL_PRODUCCION=https://catalogo-vpfe.dian.gov.co
PAYROLL_CERTIFICATE_PATH=/path/to/certificate.p12
PAYROLL_CERTIFICATE_PASSWORD=secret

# Datos del Empleador
EMPLOYER_NIT=900123456
EMPLOYER_DV=7
EMPLOYER_RAZON_SOCIAL=Mi Empresa SAS
EMPLOYER_DIRECCION=Calle 123 #45-67
EMPLOYER_CIUDAD=Bogotá
EMPLOYER_DEPARTAMENTO=Cundinamarca
EMPLOYER_PAIS=CO
```

---

## 📝 Notas Técnicas

### Cálculos Automáticos

Los totales se calculan automáticamente mediante signals cuando se:
- Crea un devengado
- Actualiza un devengado
- Elimina un devengado
- Crea una deducción
- Actualiza una deducción
- Elimina una deducción

### Multi-Tenant

Todos los modelos heredan de `TenantModel`, garantizando:
- Aislamiento por organización
- Filtrado automático
- Seguridad de datos

### Estados del Proceso

1. **BORRADOR**: Período creado, sin calcular
2. **CALCULADO**: Nómina calculada, puede modificarse
3. **APROBADO**: Nómina aprobada, lista para DIAN
4. **ENVIADO_DIAN**: Documentos enviados
5. **VALIDADO_DIAN**: Aprobado por DIAN
6. **RECHAZADO_DIAN**: Rechazado por DIAN
7. **PAGADO**: Nómina pagada

---

## 🐛 Debugging

### Ver logs en desarrollo

```bash
python manage.py runserver
```

### Verificar migraciones

```bash
python manage.py showmigrations payroll
```

### Shell interactivo

```python
python manage.py shell

from apps.payroll.models import *
from apps.organizations.models import Organization

org = Organization.objects.first()
employees = Employee.objects.filter(organization=org)
print(f"Empleados: {employees.count()}")
```

---

## ✅ Testing

Próximamente se implementarán tests para:
- Modelos
- Serializers
- ViewSets
- Cálculos de nómina
- Generación de XML
- Integración DIAN

---

## 📞 Soporte

Para reportar problemas o sugerencias, contacta al equipo de desarrollo.

---

**Última actualización**: 6 de Enero de 2026
**Versión**: 1.0.0 - Beta
**Estado**: Backend Funcional ✅
