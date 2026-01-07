# 📊 PLAN DE DESARROLLO Y MEJORAS - OpticaApp

**Fecha de Análisis:** 6 de enero de 2026  
**Versión Actual:** 1.0 (Con módulo de Nómina implementado)  
**Objetivo:** Completar funcionalidades empresariales críticas por fases

---

## 📈 ESTADO ACTUAL DEL SISTEMA

### ✅ MÓDULOS IMPLEMENTADOS Y FUNCIONALES

#### 1. **Core Multi-Tenant**
- ✅ Sistema SaaS con arquitectura multi-tenant
- ✅ Modelo `TenantModel` base para aislamiento de datos
- ✅ Organizaciones con suscripciones y planes
- ✅ Sistema de permisos por módulos (`ModulePermission`)
- ✅ Landing pages personalizadas por organización
- ✅ Gestión de miembros y roles

#### 2. **Gestión de Pacientes** (`apps.patients`)
- ✅ Registro completo de pacientes
- ✅ Historia clínica digital
- ✅ Adjuntos de historia clínica
- ✅ Gestión de doctores
- ✅ Parámetros clínicos configurables
- ✅ Templates de medicación
- ✅ Protocolos de tratamiento
- ✅ Exámenes especiales:
  - Tonometría
  - Campo visual
  - Retinografía
  - OCT
  - Topografía corneal
  - Paquimetría
  - Queratometría
  - Visión de colores
  - Examen de motilidad

#### 3. **Sistema de Citas** (`apps.appointments`)
- ✅ Agendamiento de citas
- ✅ Configuración de horarios por día
- ✅ Horarios específicos por fecha
- ✅ Notificaciones automáticas (WhatsApp, Email)
- ✅ Estados de citas (pendiente, confirmada, completada, cancelada)
- ✅ Vista pública para agendamiento
- ✅ Configuración de disponibilidad

#### 4. **Ventas e Inventario Básico** (`apps.sales`)
- ✅ Punto de venta (POS)
- ✅ Gestión de productos
- ✅ Categorías de productos
- ✅ Control básico de stock
- ✅ Métodos de pago múltiples
- ✅ Ventas a pacientes o clientes anónimos
- ✅ Estadísticas básicas (diarias, semanales, mensuales)

#### 5. **Facturación Electrónica** (`apps.billing`)
- ✅ Integración con DIAN Colombia
- ✅ Generación de facturas electrónicas
- ✅ Notas crédito y débito
- ✅ Firma digital de documentos
- ✅ Envío automático por email
- ✅ Estados de facturas
- ✅ Paquetes de facturación
- ✅ Control de cupos de facturación

#### 6. **Nómina Electrónica** (`apps.payroll`) - ✨ RECIÉN IMPLEMENTADO
- ✅ Gestión de empleados
- ✅ Períodos de nómina
- ✅ Conceptos de devengos y deducciones
- ✅ Cálculo automático de nómina
- ✅ Workflow de aprobación
- ✅ Generación XML DIAN
- ✅ Envío a DIAN
- ✅ Desprendibles de pago en PDF
- ✅ **Contratos laborales** (indefinido, fijo, obra/labor, prestación servicios)
- ✅ **Vacaciones** (solicitud, aprobación, rechazo, cálculo automático)
- ✅ **Préstamos a empleados** (solicitud, aprobación, desembolso, cuotas)
- ✅ **Prestaciones sociales** (cesantías, intereses, prima, vacaciones)
- ✅ **Provisiones mensuales** (cálculo automático)
- ✅ **PILA** (Planilla Integrada de Liquidación de Aportes)

#### 7. **Promociones y Marketing** (`apps.promotions`)
- ✅ Gestión de promociones
- ✅ Campañas de marketing
- ✅ Integración WhatsApp Business (Twilio)
- ✅ Envío masivo de mensajes
- ✅ Seguimiento de campañas
- ✅ Estadísticas de campañas

#### 8. **Usuarios y Suscripciones** (`apps.users`)
- ✅ Sistema de suscripciones
- ✅ Métodos de pago
- ✅ Transacciones
- ✅ Logs de renovación
- ✅ Gestión de planes

#### 9. **Dashboard y Administración**
- ✅ Dashboard principal (`apps.dashboard`)
- ✅ Dashboard administrativo (`apps.admin_dashboard`)
- ✅ Vistas públicas (`apps.public`)
- ✅ Landing pages personalizadas

#### 10. **Infraestructura Técnica**
- ✅ Django 3.2.25 + Python 3.7.9
- ✅ WebSockets (Channels + Daphne)
- ✅ REST API (Django REST Framework)
- ✅ CORS habilitado
- ✅ Tailwind CSS para frontend
- ✅ PostgreSQL como base de datos
- ✅ Servidor Contabo en producción
- ✅ django.contrib.humanize (formateo de números)

---

## 🎉 IMPLEMENTACIONES DEL DÍA - 6 Enero 2026

### **Módulo de Prestaciones Sociales y PILA** (apps.payroll)

#### Modelos Creados:
1. **LaborContract** - Contratos laborales con todos los tipos colombianos
2. **VacationRequest** - Solicitudes de vacaciones con cálculo automático
3. **EmployeeLoan** - Préstamos con cuotas y seguimiento
4. **SocialBenefit** - Cálculo de prestaciones sociales
5. **MonthlyProvision** - Provisiones mensuales automáticas
6. **PILAReport** - Reportes PILA para seguridad social

#### Vistas Implementadas (15 nuevas):
- `contract_list`, `contract_create`, `contract_detail`
- `vacation_list`, `vacation_create`, `vacation_approve`, `vacation_reject`
- `loan_list`, `loan_create`, `loan_approve`, `loan_disburse`
- `social_benefits_dashboard`, `provision_list`
- `pila_list`, `pila_create`

#### Templates Creados (13 archivos):
**Contratos:**
- [contracts/list.html](apps/payroll/templates/payroll/contracts/list.html) - Lista con 3 stat cards y tabla
- [contracts/create.html](apps/payroll/templates/payroll/contracts/create.html) - Formulario con auto-generación de número
- [contracts/detail.html](apps/payroll/templates/payroll/contracts/detail.html) - Vista detallada con liquidación automática

**Vacaciones:**
- [vacations/list.html](apps/payroll/templates/payroll/vacations/list.html) - Lista con filtros y aprobación inline
- [vacations/create.html](apps/payroll/templates/payroll/vacations/create.html) - Formulario con calculadora de días automática
- [vacations/reject.html](apps/payroll/templates/payroll/vacations/reject.html) - Modal de rechazo con motivos predefinidos

**Préstamos:**
- [loans/list.html](apps/payroll/templates/payroll/loans/list.html) - Lista con 4 stat cards y barras de progreso
- [loans/create.html](apps/payroll/templates/payroll/loans/create.html) - Formulario con calculadora de cuotas en tiempo real
- [loans/approve.html](apps/payroll/templates/payroll/loans/approve.html) - Aprobación con recalculación de cuotas

**Prestaciones Sociales:**
- [social_benefits/dashboard.html](apps/payroll/templates/payroll/social_benefits/dashboard.html) - Dashboard con 5 cards de resumen y tabla completa

**Provisiones:**
- [provisions/list.html](apps/payroll/templates/payroll/provisions/list.html) - Lista con 4 cards y tabla mensual

**PILA:**
- [pila/list.html](apps/payroll/templates/payroll/pila/list.html) - Lista de reportes PILA con 4 cards de totales
- [pila/create.html](apps/payroll/templates/payroll/pila/create.html) - Generación de PILA con configuración completa

#### Servicios Creados:
- **SocialBenefitsCalculator** - Cálculo de prestaciones sociales según ley colombiana:
  - Cesantías: `(Salario × Días) / 360`
  - Intereses cesantías: `Cesantías × 12% × (Días/360)`
  - Prima de servicios: `(Salario × Días) / 360`
  - Vacaciones: `(Salario × 15) / 360`
  - Liquidación completa al terminar contrato

#### URLs Registradas (20+):
```python
# Contratos
path('contratos/', contract_list, name='contract_list')
path('contratos/crear/', contract_create, name='contract_create')
path('contratos/<int:pk>/', contract_detail, name='contract_detail')

# Vacaciones
path('vacaciones/', vacation_list, name='vacation_list')
path('vacaciones/crear/', vacation_create, name='vacation_create')
path('vacaciones/<int:pk>/aprobar/', vacation_approve, name='vacation_approve')
path('vacaciones/<int:pk>/rechazar/', vacation_reject, name='vacation_reject')

# Préstamos
path('prestamos/', loan_list, name='loan_list')
path('prestamos/crear/', loan_create, name='loan_create')
path('prestamos/<int:pk>/aprobar/', loan_approve, name='loan_approve')
path('prestamos/<int:pk>/desembolsar/', loan_disburse, name='loan_disburse')

# Prestaciones, Provisiones, PILA
path('prestaciones/', social_benefits_dashboard, name='social_benefits_dashboard')
path('provisiones/', provision_list, name='provision_list')
path('pila/', pila_list, name='pila_list')
path('pila/crear/', pila_create, name='pila_create')
```

#### Navegación Actualizada:
**Sidebar** (`apps/dashboard/templates/dashboard/base.html`):
- ✅ Agregado dropdown "Nómina y Empleados" con 6 nuevas opciones:
  1. 📄 Contratos Laborales
  2. 🏖️ Vacaciones
  3. 💰 Préstamos
  4. 🐷 Prestaciones Sociales
  5. 🧮 Provisiones
  6. 🏥 PILA

**Dashboard Principal** (`apps/payroll/templates/payroll/dashboard.html`):
- ✅ Nueva sección "Prestaciones Sociales" con 6 cards de acceso rápido

#### Características Técnicas Implementadas:

**JavaScript Calculadoras:**
1. **Vacaciones** - Cálculo automático de:
   - Días totales (calendario)
   - Días hábiles (aproximación 5/7)
   - Pago anticipado: `(Salario × Días) / 30`
   - Auto-set fecha de reintegro

2. **Préstamos** - Calculadora en tiempo real:
   - Cuota mensual con interés compuesto: `P × (r × (1+r)^n) / ((1+r)^n - 1)`
   - Total a pagar
   - Total intereses
   - **Capacidad de pago** con semáforo (verde/amarillo/rojo)
   - Validación si cuota > 50% salario

3. **Contratos** - Auto-generación:
   - Número de contrato: `CON-2026-XXX`
   - Mostrar/ocultar campos según tipo
   - Validaciones de fechas

4. **Liquidación** - Cálculo automático al terminar contrato:
   - Fetch AJAX para calcular prestaciones
   - Desglose completo en modal
   - Totales automáticos

**Formularios con Tailwind CSS:**
- ✅ Diseño responsive (mobile-first)
- ✅ Validaciones del lado del cliente
- ✅ Feedback visual (badges, progress bars)
- ✅ Auto-completado de campos
- ✅ Mensajes de confirmación
- ✅ Estados de carga

**Correcciones Realizadas:**
1. ✅ Agregado `django.contrib.humanize` a INSTALLED_APPS
2. ✅ Agregado `{% load humanize %}` a todos los templates con `intcomma`
3. ✅ Corregido campo `prima_servicios` → `prima` en provisiones
4. ✅ Corregido campo `total_arl` → `total_riesgos` en PILA
5. ✅ Cambiado grids de `md:grid-cols-2` a `sm:grid-cols-2` para mejor visualización
6. ✅ Cambiado colores de cards (amarillo/rojo a naranja/rosa) para mejor contraste

#### Totales del Día:
- **6 modelos** nuevos
- **15 vistas** nuevas
- **13 templates** completos
- **20+ URLs** registradas
- **4 calculadoras** JavaScript
- **1 servicio** de cálculos (SocialBenefitsCalculator)
- **~3000 líneas** de código

---

## ❌ MÓDULOS CRÍTICOS FALTANTES

### 🔴 FASE 1 - OPERACIONES CRÍTICAS (Prioridad Alta)
**Tiempo estimado: 6-8 semanas**  
**Impacto: Operativo inmediato**

#### 1.1 **INVENTARIO AVANZADO** ⭐⭐⭐⭐⭐
**Problema actual:** Solo hay stock básico, sin trazabilidad ni control real.

**Modelos a crear:**
```python
# apps/inventory/models.py

class InventoryMovement(TenantModel):
    """Movimientos de inventario trazables"""
    MOVEMENT_TYPES = [
        ('IN_PURCHASE', 'Entrada por compra'),
        ('IN_RETURN', 'Entrada por devolución'),
        ('IN_ADJUSTMENT', 'Entrada por ajuste'),
        ('OUT_SALE', 'Salida por venta'),
        ('OUT_LOSS', 'Salida por pérdida'),
        ('OUT_DAMAGE', 'Salida por daño'),
        ('OUT_ADJUSTMENT', 'Salida por ajuste'),
        ('TRANSFER_OUT', 'Transferencia salida'),
        ('TRANSFER_IN', 'Transferencia entrada'),
    ]
    product = ForeignKey('sales.Product')
    movement_type = CharField(choices=MOVEMENT_TYPES)
    quantity = IntegerField()
    cost_unit = DecimalField()
    reference_document = CharField()  # OC, Factura, etc
    reason = TextField()
    created_by = ForeignKey(User)
    created_at = DateTimeField(auto_now_add=True)

class ProductLot(TenantModel):
    """Lotes de productos con vencimiento"""
    product = ForeignKey('sales.Product')
    lot_number = CharField()
    expiration_date = DateField(null=True)
    quantity = IntegerField()
    cost = DecimalField()
    supplier = ForeignKey('Supplier')

class StockAlert(TenantModel):
    """Alertas de stock bajo"""
    product = ForeignKey('sales.Product')
    alert_type = CharField()  # low_stock, out_of_stock, near_expiry
    is_resolved = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)

class InventoryAdjustment(TenantModel):
    """Ajustes de inventario"""
    product = ForeignKey('sales.Product')
    quantity_before = IntegerField()
    quantity_after = IntegerField()
    reason = TextField()
    approved_by = ForeignKey(User)
    created_at = DateTimeField(auto_now_add=True)
```

**Funcionalidades:**
- Kardex completo por producto
- Control de lotes y vencimientos
- Alertas automáticas de stock bajo
- Ajustes de inventario con razones
- Transferencias entre sucursales
- Costo promedio ponderado
- Reportes de rotación de inventario
- Dashboard de inventario

#### 1.2 **CAJA Y TESORERÍA** ⭐⭐⭐⭐⭐
**Problema actual:** No hay control de efectivo ni cuadre de caja.

**Modelos a crear:**
```python
# apps/treasury/models.py

class CashRegister(TenantModel):
    """Cajas registradoras"""
    name = CharField()
    code = CharField()
    location = CharField()
    is_active = BooleanField(default=True)

class CashSession(TenantModel):
    """Sesiones de caja (turnos)"""
    cash_register = ForeignKey(CashRegister)
    opened_by = ForeignKey(User)
    closed_by = ForeignKey(User, null=True)
    opening_amount = DecimalField()
    closing_amount = DecimalField(null=True)
    expected_amount = DecimalField(null=True)
    difference = DecimalField(null=True)
    opened_at = DateTimeField()
    closed_at = DateTimeField(null=True)
    status = CharField()  # open, closed, reconciled

class CashMovement(TenantModel):
    """Movimientos de caja"""
    MOVEMENT_TYPES = [
        ('SALE', 'Venta'),
        ('EXPENSE', 'Egreso'),
        ('INITIAL', 'Base inicial'),
        ('DEPOSIT', 'Depósito bancario'),
        ('WITHDRAWAL', 'Retiro'),
    ]
    session = ForeignKey(CashSession)
    movement_type = CharField(choices=MOVEMENT_TYPES)
    amount = DecimalField()
    description = TextField()
    reference = CharField()  # Venta ID, Factura, etc
    created_by = ForeignKey(User)
    created_at = DateTimeField(auto_now_add=True)

class Expense(TenantModel):
    """Gastos menores"""
    CATEGORIES = [
        ('SUPPLIES', 'Insumos'),
        ('SERVICES', 'Servicios'),
        ('MAINTENANCE', 'Mantenimiento'),
        ('TRANSPORT', 'Transporte'),
        ('OTHER', 'Otros'),
    ]
    category = CharField(choices=CATEGORIES)
    amount = DecimalField()
    description = TextField()
    receipt_number = CharField()
    approved_by = ForeignKey(User)
    session = ForeignKey(CashSession, null=True)
    created_at = DateTimeField(auto_now_add=True)
```

**Funcionalidades:**
- Apertura/cierre de caja
- Cuadre automático
- Control de faltantes/sobrantes
- Egresos (gastos menores)
- Depósitos bancarios
- Arqueos de caja
- Reportes de movimientos
- Auditoría completa

#### 1.3 **COMPRAS Y PROVEEDORES** ⭐⭐⭐⭐⭐
**Problema actual:** No hay forma de gestionar compras a proveedores.

**Modelos a crear:**
```python
# apps/purchases/models.py

class Supplier(TenantModel):
    """Proveedores"""
    name = CharField()
    tax_id = CharField()  # NIT
    contact_name = CharField()
    phone = CharField()
    email = EmailField()
    address = TextField()
    payment_terms = IntegerField()  # días
    is_active = BooleanField(default=True)

class PurchaseOrder(TenantModel):
    """Órdenes de compra"""
    STATUS = [
        ('DRAFT', 'Borrador'),
        ('SENT', 'Enviada'),
        ('PARTIAL', 'Recibida parcial'),
        ('RECEIVED', 'Recibida completa'),
        ('CANCELLED', 'Cancelada'),
    ]
    order_number = CharField()
    supplier = ForeignKey(Supplier)
    order_date = DateField()
    expected_date = DateField()
    status = CharField(choices=STATUS, default='DRAFT')
    subtotal = DecimalField()
    tax = DecimalField()
    total = DecimalField()
    notes = TextField()
    created_by = ForeignKey(User)

class PurchaseOrderItem(TenantModel):
    """Items de orden de compra"""
    purchase_order = ForeignKey(PurchaseOrder)
    product = ForeignKey('sales.Product')
    quantity_ordered = IntegerField()
    quantity_received = IntegerField(default=0)
    unit_cost = DecimalField()
    subtotal = DecimalField()

class GoodsReceipt(TenantModel):
    """Recepción de mercancía"""
    purchase_order = ForeignKey(PurchaseOrder)
    receipt_number = CharField()
    received_date = DateField()
    received_by = ForeignKey(User)
    notes = TextField()

class GoodsReceiptItem(TenantModel):
    """Items recibidos"""
    goods_receipt = ForeignKey(GoodsReceipt)
    purchase_order_item = ForeignKey(PurchaseOrderItem)
    quantity_received = IntegerField()
    lot_number = CharField(null=True)
    expiration_date = DateField(null=True)
```

**Funcionalidades:**
- Catálogo de proveedores
- Órdenes de compra
- Recepción de mercancía
- Integración con inventario
- Control de compras pendientes
- Reportes de compras
- Evaluación de proveedores

#### 1.4 **GESTIÓN DE RECETAS Y LABORATORIO** ⭐⭐⭐⭐⭐
**Específico para ópticas - Core business**

**Modelos a crear:**
```python
# apps/laboratory/models.py

class LaboratorySupplier(TenantModel):
    """Laboratorios ópticos"""
    name = CharField()
    contact = CharField()
    phone = CharField()
    email = EmailField()
    delivery_days = IntegerField()  # días promedio
    is_active = BooleanField(default=True)

class LensOrder(TenantModel):
    """Órdenes a laboratorio"""
    STATUS = [
        ('DRAFT', 'Borrador'),
        ('SENT', 'Enviada'),
        ('PROCESSING', 'En proceso'),
        ('READY', 'Lista'),
        ('DELIVERED', 'Entregada'),
        ('CANCELLED', 'Cancelada'),
    ]
    order_number = CharField()
    patient = ForeignKey('patients.Patient')
    sale = ForeignKey('sales.Sale', null=True)
    laboratory = ForeignKey(LaboratorySupplier)
    order_date = DateField()
    expected_date = DateField()
    delivery_date = DateField(null=True)
    status = CharField(choices=STATUS, default='DRAFT')
    
    # Ojo derecho
    od_sphere = DecimalField()
    od_cylinder = DecimalField()
    od_axis = IntegerField()
    od_add = DecimalField(null=True)
    
    # Ojo izquierdo
    oi_sphere = DecimalField()
    oi_cylinder = DecimalField()
    oi_axis = IntegerField()
    oi_add = DecimalField(null=True)
    
    # Tipo de lentes
    lens_type = CharField()  # monofocal, bifocal, progresivo
    lens_material = CharField()  # CR39, policarbonato, high-index
    coating = CharField()  # antirreflejante, transitions, blue-block
    
    # Medidas
    pupillary_distance = DecimalField()
    frame_type = CharField()
    
    notes = TextField()
    cost = DecimalField()
    created_by = ForeignKey(User)

class LensQualityCheck(TenantModel):
    """Control de calidad de lentes"""
    lens_order = ForeignKey(LensOrder)
    checked_by = ForeignKey(User)
    check_date = DateField()
    is_approved = BooleanField()
    issues_found = TextField()
    action_taken = CharField()  # accepted, returned, adjusted
```

**Funcionalidades:**
- Gestión de laboratorios
- Órdenes a laboratorio
- Tracking de estado
- Control de calidad
- Integración con ventas
- Cálculo automático de precios
- Alertas de retrasos
- Reportes de tiempos de entrega

---

### 🟡 FASE 2 - GESTIÓN FINANCIERA (Prioridad Media-Alta)
**Tiempo estimado: 6-8 semanas**  
**Impacto: Financiero y administrativo**

#### 2.1 **CONTABILIDAD BÁSICA** ⭐⭐⭐⭐
**Problema actual:** No hay registro contable, solo transacciones sueltas.

**Modelos a crear:**
```python
# apps/accounting/models.py

class ChartOfAccounts(TenantModel):
    """Plan de cuentas (PUC Colombia)"""
    code = CharField()  # 110505
    name = CharField()  # Caja general
    account_type = CharField()  # ASSET, LIABILITY, EQUITY, INCOME, EXPENSE
    parent = ForeignKey('self', null=True)
    is_active = BooleanField(default=True)

class JournalEntry(TenantModel):
    """Asientos contables"""
    entry_number = CharField()
    entry_date = DateField()
    description = TextField()
    reference = CharField()  # Factura, Nómina, etc
    created_by = ForeignKey(User)
    is_posted = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)

class JournalEntryLine(TenantModel):
    """Líneas de asiento"""
    journal_entry = ForeignKey(JournalEntry)
    account = ForeignKey(ChartOfAccounts)
    debit = DecimalField(default=0)
    credit = DecimalField(default=0)
    description = TextField()

class FiscalPeriod(TenantModel):
    """Períodos fiscales"""
    name = CharField()  # "2026-01"
    start_date = DateField()
    end_date = DateField()
    is_closed = BooleanField(default=False)

class TaxWithholding(TenantModel):
    """Retenciones"""
    TYPES = [
        ('RETEFTE', 'Retención en la fuente'),
        ('RETEIVA', 'Retención IVA'),
        ('RETEICA', 'Retención ICA'),
    ]
    type = CharField(choices=TYPES)
    percentage = DecimalField()
    base_amount = DecimalField()
    amount = DecimalField()
    document = CharField()  # Factura
    created_at = DateTimeField(auto_now_add=True)
```

**Funcionalidades:**
- Plan de cuentas PUC Colombia
- Asientos contables automáticos
- Libro diario
- Libro mayor
- Balance general
- Estado de resultados (P&L)
- Flujo de caja
- Retenciones automáticas
- Cierre de períodos

#### 2.2 **REPORTES Y ANALYTICS AVANZADOS** ⭐⭐⭐⭐
**Problema actual:** Solo hay stats básicas, sin análisis profundo.

**Módulos a crear:**
```python
# apps/analytics/

class KPIDashboard:
    """Dashboard ejecutivo"""
    - Revenue (MRR, ARR)
    - Profit margins
    - Growth rate
    - Customer acquisition cost
    - Lifetime value
    - Churn rate

class ProductAnalytics:
    """Análisis de productos"""
    - Análisis ABC
    - Rotación de inventario
    - Productos más vendidos
    - Margen por producto
    - Stock vs ventas

class CustomerAnalytics:
    """Análisis de clientes"""
    - RFM (Recency, Frequency, Monetary)
    - Segmentación
    - CLV (Customer Lifetime Value)
    - Tasa de retención
    - NPS (Net Promoter Score)

class SalesForecasting:
    """Pronóstico de ventas"""
    - Tendencias históricas
    - Estacionalidad
    - Predicción ML
    - Metas vs realidad

class FinancialReports:
    """Reportes financieros"""
    - Flujo de caja proyectado
    - Punto de equilibrio
    - Rentabilidad por servicio
    - Costos operativos
    - Reportes fiscales (IVA, Retefte)
```

**Funcionalidades:**
- Dashboard ejecutivo con KPIs
- Análisis de rentabilidad
- Segmentación de clientes
- Forecast de ventas
- Exportación a Excel/PDF
- Gráficos interactivos
- Alertas automáticas
- Reportes personalizables

#### 2.3 **GARANTÍAS Y DEVOLUCIONES** ⭐⭐⭐⭐
**Específico para ópticas**

**Modelos a crear:**
```python
# apps/warranty/models.py

class Warranty(TenantModel):
    """Garantías"""
    WARRANTY_TYPES = [
        ('MANUFACTURER', 'Fabricante'),
        ('STORE', 'Tienda'),
        ('LABORATORY', 'Laboratorio'),
    ]
    sale = ForeignKey('sales.Sale')
    product = ForeignKey('sales.Product', null=True)
    lens_order = ForeignKey('laboratory.LensOrder', null=True)
    warranty_type = CharField(choices=WARRANTY_TYPES)
    start_date = DateField()
    end_date = DateField()
    terms = TextField()
    status = CharField()  # active, expired, claimed

class Return(TenantModel):
    """Devoluciones"""
    REASONS = [
        ('DEFECT', 'Producto defectuoso'),
        ('WRONG_RX', 'Prescripción incorrecta'),
        ('DISCOMFORT', 'Incomodidad'),
        ('CHANGE_MIND', 'Cambio de opinión'),
        ('LABORATORY_ERROR', 'Error de laboratorio'),
    ]
    ACTIONS = [
        ('REFUND', 'Reembolso'),
        ('EXCHANGE', 'Cambio'),
        ('REPAIR', 'Reparación'),
        ('CREDIT', 'Nota crédito'),
    ]
    sale = ForeignKey('sales.Sale')
    return_number = CharField()
    reason = CharField(choices=REASONS)
    action_taken = CharField(choices=ACTIONS)
    amount = DecimalField()
    notes = TextField()
    processed_by = ForeignKey(User)
    created_at = DateTimeField(auto_now_add=True)

class WarrantyClaim(TenantModel):
    """Reclamos de garantía"""
    warranty = ForeignKey(Warranty)
    claim_date = DateField()
    issue_description = TextField()
    resolution = TextField()
    is_approved = BooleanField()
    processed_by = ForeignKey(User)
```

**Funcionalidades:**
- Registro de garantías
- Tracking de vencimientos
- Proceso de devoluciones
- Cambios y reembolsos
- Notas crédito automáticas
- Reportes de devoluciones
- Análisis de causas

---

### 🟢 FASE 3 - VALOR AGREGADO (Prioridad Media)
**Tiempo estimado: 8-10 semanas**  
**Impacto: Competitivo y experiencia**

#### 3.1 **CRM AVANZADO** ⭐⭐⭐
**Mejora del módulo de pacientes existente**

**Funcionalidades a agregar:**
```python
# apps/crm/models.py

class Lead(TenantModel):
    """Prospectos"""
    SOURCE = [
        ('WEBSITE', 'Sitio web'),
        ('REFERRAL', 'Referido'),
        ('WALK_IN', 'Walk-in'),
        ('SOCIAL', 'Redes sociales'),
        ('CAMPAIGN', 'Campaña'),
    ]
    STATUS = [
        ('NEW', 'Nuevo'),
        ('CONTACTED', 'Contactado'),
        ('QUALIFIED', 'Calificado'),
        ('CONVERTED', 'Convertido'),
        ('LOST', 'Perdido'),
    ]
    name = CharField()
    phone = CharField()
    email = EmailField()
    source = CharField(choices=SOURCE)
    status = CharField(choices=STATUS)
    assigned_to = ForeignKey(User)
    notes = TextField()

class Opportunity(TenantModel):
    """Oportunidades de venta"""
    lead = ForeignKey(Lead, null=True)
    patient = ForeignKey('patients.Patient', null=True)
    title = CharField()
    estimated_value = DecimalField()
    probability = IntegerField()  # 0-100
    expected_close_date = DateField()
    stage = CharField()
    assigned_to = ForeignKey(User)

class CustomerInteraction(TenantModel):
    """Historial de interacciones"""
    TYPES = [
        ('CALL', 'Llamada'),
        ('EMAIL', 'Email'),
        ('WHATSAPP', 'WhatsApp'),
        ('VISIT', 'Visita'),
        ('NOTE', 'Nota'),
    ]
    patient = ForeignKey('patients.Patient')
    interaction_type = CharField(choices=TYPES)
    description = TextField()
    created_by = ForeignKey(User)
    created_at = DateTimeField(auto_now_add=True)

class LoyaltyProgram(TenantModel):
    """Programa de lealtad"""
    patient = ForeignKey('patients.Patient')
    points_balance = IntegerField(default=0)
    tier = CharField()  # bronze, silver, gold, platinum
    
class LoyaltyTransaction(TenantModel):
    """Movimientos de puntos"""
    program = ForeignKey(LoyaltyProgram)
    points = IntegerField()  # positivo=ganó, negativo=redimió
    description = TextField()
    sale = ForeignKey('sales.Sale', null=True)
    created_at = DateTimeField(auto_now_add=True)
```

**Funcionalidades:**
- Pipeline de ventas
- Gestión de leads
- Seguimiento de oportunidades
- Historial completo 360°
- Programa de lealtad con puntos
- Segmentación avanzada
- Email marketing
- SMS/WhatsApp marketing
- NPS automático

#### 3.2 **MEJORAS DE SEGURIDAD** ⭐⭐⭐

**Implementaciones:**
```python
# apps/security/

1. Autenticación 2FA
   - django-otp
   - TOTP (Google Authenticator)
   - SMS backup

2. Auditoría completa
   - django-auditlog
   - Logs de cambios en BD
   - Logs de accesos
   - IP tracking

3. Políticas de contraseña
   - Complejidad mínima
   - Rotación obligatoria
   - Historial de contraseñas
   - Bloqueo por intentos

4. Sesiones seguras
   - Timeout automático
   - Logout en múltiples dispositivos
   - Detección de sesiones sospechosas

5. Rate limiting
   - django-ratelimit
   - Límites por IP
   - Límites por usuario
   - API throttling

6. Encriptación
   - Datos sensibles encriptados
   - django-encrypted-model-fields
   - SSL/TLS obligatorio

7. Backup automático
   - django-dbbackup
   - Backup diario
   - Retención 30 días
   - Restauración fácil

8. GDPR/LOPD Compliance
   - Consentimiento explícito
   - Derecho al olvido
   - Exportación de datos
   - Políticas de privacidad
```

#### 3.3 **CONFIGURACIONES GLOBALES** ⭐⭐⭐

**Módulo de configuración centralizado:**
```python
# apps/settings/models.py

class TaxConfiguration(TenantModel):
    """Configuración de impuestos"""
    iva_rate = DecimalField(default=19)
    retention_rate = DecimalField(default=2.5)
    ica_rate = DecimalField(default=0.966)
    is_tax_responsible = BooleanField(default=True)

class InvoiceConfiguration(TenantModel):
    """Configuración de facturación"""
    resolution_number = CharField()
    resolution_date = DateField()
    valid_from = IntegerField()
    valid_to = IntegerField()
    current_number = IntegerField()
    prefix = CharField()

class EmailConfiguration(TenantModel):
    """Configuración SMTP"""
    smtp_host = CharField()
    smtp_port = IntegerField()
    smtp_user = CharField()
    smtp_password = CharField()
    from_email = EmailField()
    from_name = CharField()

class DocumentTemplate(TenantModel):
    """Plantillas de documentos"""
    TYPES = [
        ('INVOICE', 'Factura'),
        ('PAYSLIP', 'Desprendible'),
        ('CONTRACT', 'Contrato'),
        ('PRESCRIPTION', 'Receta'),
    ]
    template_type = CharField(choices=TYPES)
    name = CharField()
    html_content = TextField()
    css_styles = TextField()
    variables = JSONField()

class DocumentNumbering(TenantModel):
    """Numeración de documentos"""
    document_type = CharField()
    prefix = CharField()
    current_number = IntegerField()
    padding = IntegerField(default=6)

class Currency(TenantModel):
    """Monedas"""
    code = CharField()  # USD, EUR, COP
    name = CharField()
    symbol = CharField()
    exchange_rate = DecimalField()
    is_default = BooleanField(default=False)

class WebhookEndpoint(TenantModel):
    """Webhooks para integraciones"""
    name = CharField()
    url = URLField()
    events = JSONField()  # ['sale.created', 'appointment.confirmed']
    is_active = BooleanField(default=True)
    secret = CharField()
```

---

## 🎯 CRONOGRAMA DE IMPLEMENTACIÓN

### **FASE 1: Operaciones Críticas** (Semanas 1-8)

#### Semana 1-2: Inventario Avanzado
- [ ] Crear modelos de inventario
- [ ] Migrar datos existentes
- [ ] Implementar trazabilidad
- [ ] Dashboard de inventario
- [ ] Alertas de stock

#### Semana 3-4: Caja y Tesorería
- [ ] Crear modelos de caja
- [ ] Implementar apertura/cierre
- [ ] Cuadre automático
- [ ] Reportes de caja
- [ ] Integración con ventas

#### Semana 5-6: Compras y Proveedores
- [ ] Crear modelos de compras
- [ ] Catálogo de proveedores
- [ ] Órdenes de compra
- [ ] Recepción de mercancía
- [ ] Integración con inventario

#### Semana 7-8: Recetas y Laboratorio
- [ ] Crear modelos de laboratorio
- [ ] Órdenes a laboratorio
- [ ] Tracking de estado
- [ ] Control de calidad
- [ ] Integración con ventas

**Entregable:** Sistema operativo completo para gestión diaria

---

### **FASE 2: Gestión Financiera** (Semanas 9-16)

#### Semana 9-11: Contabilidad Básica
- [ ] Plan de cuentas PUC
- [ ] Asientos automáticos
- [ ] Libros contables
- [ ] Balance general
- [ ] Estado de resultados

#### Semana 12-14: Reportes Avanzados
- [ ] Dashboard ejecutivo
- [ ] KPIs automáticos
- [ ] Análisis de productos
- [ ] Análisis de clientes
- [ ] Forecast de ventas

#### Semana 15-16: Garantías y Devoluciones
- [ ] Sistema de garantías
- [ ] Proceso de devoluciones
- [ ] Notas crédito
- [ ] Reportes de devoluciones

**Entregable:** Sistema financiero completo con reportes

---

### **FASE 3: Valor Agregado** (Semanas 17-26)

#### Semana 17-20: CRM Avanzado
- [ ] Pipeline de ventas
- [ ] Gestión de leads
- [ ] Programa de lealtad
- [ ] Email marketing
- [ ] Segmentación avanzada

#### Semana 21-23: Seguridad
- [ ] 2FA
- [ ] Auditoría completa
- [ ] Políticas de contraseña
- [ ] Backup automático
- [ ] GDPR compliance

#### Semana 24-26: Configuraciones
- [ ] Módulo de configuración
- [ ] Plantillas de documentos
- [ ] Webhooks
- [ ] API mejorada

**Entregable:** Sistema empresarial completo

---

## 📝 MEJORAS TÉCNICAS REQUERIDAS

### Testing
```python
# Crear estructura de tests
tests/
├── unit/
│   ├── test_models.py
│   ├── test_views.py
│   └── test_services.py
├── integration/
│   ├── test_sales_flow.py
│   ├── test_payroll_flow.py
│   └── test_billing_flow.py
└── e2e/
    ├── test_checkout.py
    └── test_appointment.py
```

**Coverage objetivo: 80%**

### Documentación
```markdown
docs/
├── api/
│   ├── openapi.yaml
│   └── postman_collection.json
├── user_manual/
│   ├── getting_started.md
│   ├── sales.md
│   ├── appointments.md
│   └── payroll.md
├── admin_guide/
│   ├── installation.md
│   ├── configuration.md
│   └── maintenance.md
└── developer/
    ├── architecture.md
    ├── models_diagram.png
    └── api_reference.md
```

### Performance
```python
# Optimizaciones
1. Índices en BD
   - organization_id en todas las tablas
   - foreign keys
   - campos de búsqueda frecuente

2. Caching (Redis)
   - Sesiones
   - Datos de configuración
   - Consultas frecuentes
   - Cache de plantillas

3. Paginación
   - Todas las listas
   - API endpoints
   - Django Paginator

4. Query optimization
   - select_related() para FKs
   - prefetch_related() para M2M
   - only() para campos específicos
   - Evitar N+1 queries

5. CDN para estáticos
   - CloudFlare
   - Amazon CloudFront
   - DigitalOcean Spaces
```

### Monitoreo
```python
# Herramientas
1. Sentry
   - Error tracking
   - Performance monitoring
   - Release tracking

2. New Relic / DataDog
   - APM
   - Infrastructure monitoring
   - Custom dashboards

3. ELK Stack
   - Logs centralizados
   - Elasticsearch
   - Kibana dashboards

4. Alertas
   - Errores críticos
   - Performance degradation
   - Disk space
   - Memory usage
```

---

## 🚀 DESPLIEGUE A CONTABO

### Checklist Pre-Deploy

#### 1. Preparación de Código
- [ ] Todas las migraciones creadas
- [ ] Tests pasando (>80% coverage)
- [ ] Linting (flake8, black)
- [ ] Security check (bandit)
- [ ] Dependencies actualizadas (pip freeze)
- [ ] .env.production configurado
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configurado
- [ ] SECRET_KEY segura

#### 2. Base de Datos
- [ ] Backup de BD actual
- [ ] Plan de rollback
- [ ] Migraciones probadas en staging
- [ ] Índices creados
- [ ] Vacuum/Analyze ejecutado

#### 3. Archivos Estáticos
- [ ] collectstatic ejecutado
- [ ] CSS/JS minificado
- [ ] Imágenes optimizadas
- [ ] CDN configurado (opcional)

#### 4. Servidor
- [ ] Supervisor configurado
- [ ] Nginx configurado
- [ ] SSL/TLS activo
- [ ] Firewall configurado
- [ ] Backup automático configurado
- [ ] Monitoreo activo

### Comandos de Deploy

```bash
# En servidor Contabo
cd /var/www/OpticaApp

# 1. Backup
pg_dump opticaapp_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Pull código
git pull origin main

# 3. Activar virtualenv
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Migraciones
python manage.py migrate --no-input

# 6. Estáticos
python manage.py collectstatic --no-input

# 7. Reiniciar servicios
sudo supervisorctl restart opticaapp
sudo systemctl restart nginx

# 8. Verificar
python manage.py check --deploy
curl https://tu-dominio.com/health/
```

### Plan de Rollback

```bash
# Si algo falla:
# 1. Restaurar código
git reset --hard HEAD~1

# 2. Restaurar BD
psql opticaapp_db < backup_YYYYMMDD_HHMMSS.sql

# 3. Reiniciar
sudo supervisorctl restart opticaapp
```

---

## 💡 OPORTUNIDADES DE NEGOCIO FUTURAS

### Fase 4 (Opcional - 6 meses)

#### 1. App Móvil
- React Native / Flutter
- Agendamiento de citas
- Ver recetas
- Historial de compras
- Notificaciones push
- Pago desde app

#### 2. Telemedicina
- Videoconsultas
- Recetas digitales
- Chat con doctor
- Seguimiento remoto

#### 3. Integraciones
- Laboratorios (API directa)
- POS físicos
- Bancos (PSE, pagos online)
- Marketplaces (Mercado Libre, Amazon)
- ERP externo (SAP, Odoo)

#### 4. AI/ML
- Recomendaciones de productos
- Predicción de demanda
- Detección de fraudes
- Análisis de sentimientos
- Chatbot de atención

#### 5. Marketplace
- Tienda online pública
- Catálogo de productos
- Carrito de compras
- Pasarela de pagos
- Envíos a domicilio

#### 6. Suscripciones
- Plan de mantenimiento anual
- Revisiones periódicas
- Descuentos exclusivos
- Seguro de lentes

---

## 📊 MÉTRICAS DE ÉXITO

### KPIs por Fase

#### Fase 1
- ✅ 100% trazabilidad de inventario
- ✅ 0 faltantes/sobrantes sin explicación
- ✅ Tiempo de orden a laboratorio: <24h
- ✅ 100% compras documentadas

#### Fase 2
- ✅ Balance general generado automáticamente
- ✅ Reportes en <5 segundos
- ✅ 100% transacciones contabilizadas
- ✅ Tasa de devoluciones <5%

#### Fase 3
- ✅ 2FA activo para todos
- ✅ Backup automático diario
- ✅ 0 vulnerabilidades críticas
- ✅ CLV calculado para todos los clientes

### Métricas Técnicas
- **Uptime:** >99.5%
- **Response time:** <500ms (p95)
- **Error rate:** <0.1%
- **Test coverage:** >80%
- **Security score:** A+ (SSL Labs)

---

## 🔧 STACK TECNOLÓGICO RECOMENDADO

### Backend (Actual + Nuevos)
- Django 4.2 LTS (actualizar de 3.2)
- PostgreSQL 14+
- Redis 7 (caching + Celery)
- Celery (tareas async)
- Django REST Framework
- django-filter
- django-cors-headers

### Frontend
- Tailwind CSS 3 ✅
- Alpine.js (reemplazar jQuery)
- Chart.js (gráficos)
- DataTables (tablas)
- Select2 (dropdowns)

### Testing
- pytest
- pytest-django
- factory_boy
- coverage

### DevOps
- Docker (containerización)
- docker-compose
- GitHub Actions (CI/CD)
- Sentry (errores)
- New Relic (monitoring)

### Seguridad
- django-otp (2FA)
- django-auditlog
- django-ratelimit
- django-cors-headers
- django-csp

---

## 📞 PRÓXIMOS PASOS INMEDIATOS

### Mañana (7 enero 2026)
1. ✅ Revisar documentación
2. ⏳ Priorizar módulos de Fase 1
3. ⏳ Crear rama `feature/inventory-module`
4. ⏳ Diseñar modelos de inventario
5. ⏳ Crear migraciones iniciales

### Esta Semana
1. ⏳ Implementar módulo de inventario (80%)
2. ⏳ Tests del módulo
3. ⏳ Documentación de API
4. ⏳ Deploy a staging para pruebas

### Este Mes
1. ⏳ Completar Fase 1 (100%)
2. ⏳ Training a usuarios
3. ⏳ Deploy a producción
4. ⏳ Iniciar Fase 2

---

## 📚 RECURSOS Y REFERENCIAS

### Documentación
- [Django 4.2 Docs](https://docs.djangoproject.com/en/4.2/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Celery Documentation](https://docs.celeryproject.org/)

### Contabilidad Colombia
- [Plan Único de Cuentas PUC](https://actualicese.com/plan-unico-de-cuentas-puc/)
- [DIAN - Facturación Electrónica](https://www.dian.gov.co/)
- [Retenciones en Colombia](https://www.dian.gov.co/impuestos/retencion)

### Best Practices
- [Django Best Practices](https://django-best-practices.readthedocs.io/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)
- [12 Factor App](https://12factor.net/)

---

**Última actualización:** 6 de enero de 2026  
**Autor:** Equipo de Desarrollo OpticaApp  
**Versión:** 1.0

---

## ✅ CHECKLIST DE VALIDACIÓN

Antes de cada deploy a producción:

### Pre-Deploy
- [ ] Tests pasando (>80% coverage)
- [ ] Migraciones probadas en staging
- [ ] Backup de BD realizado
- [ ] .env.production verificado
- [ ] Logs de errores revisados
- [ ] Performance test ejecutado
- [ ] Security scan realizado
- [ ] Documentación actualizada

### Post-Deploy
- [ ] Health check OK
- [ ] Migraciones aplicadas
- [ ] Servicios corriendo
- [ ] Logs sin errores críticos
- [ ] Funcionalidades críticas verificadas
- [ ] Notificación a usuarios (si aplica)
- [ ] Monitoring activo
- [ ] Backup post-deploy

---

**¡Listo para iniciar la implementación mañana! 🚀**
