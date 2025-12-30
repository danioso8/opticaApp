# Sistema de Facturación Electrónica Mejorado

## Mejoras Implementadas

### 1. **Distinción entre Factura Electrónica (DIAN) y Factura Normal (Interna)**

Se agregaron dos nuevos campos al modelo `Invoice`:

- **`es_factura_electronica`** (Boolean): 
  - `True`: Factura electrónica que consume consecutivo DIAN
  - `False`: Factura normal/interna que usa consecutivo interno

- **`requiere_envio_dian`** (Boolean):
  - Indica si el usuario solicitó que la factura sea enviada a la DIAN
  - Permite crear facturas electrónicas sin enviarlas inmediatamente

### 2. **Gestión Inteligente de Consecutivos**

#### Factura Electrónica (DIAN)
- Consume el consecutivo autorizado por la DIAN
- Usa el prefijo de la resolución DIAN (ej: `FE001`)
- Se valida que no se agote el rango autorizado
- **Método**: `DianConfiguration.get_next_numero(es_factura_electronica=True)`

#### Factura Normal (Interna)
- Usa consecutivo interno de la organización
- No consume números de la DIAN
- Prefijo configurable por organización (ej: `INV-00001`)
- Útil para cotizaciones, facturas de prueba, etc.

### 3. **Envío a DIAN Solo Cuando Esté Completamente Pagada**

#### Flujo Mejorado:

1. **Creación de Factura**:
   - Usuario elige si es factura electrónica o normal
   - Si es electrónica, puede marcar "Enviar a DIAN"
   - Se registran los datos y pagos iniciales

2. **Validación Automática**:
   - La factura solo se envía a DIAN si:
     - ✅ Es factura electrónica (`es_factura_electronica = True`)
     - ✅ Se solicitó envío (`requiere_envio_dian = True`)
     - ✅ Está 100% pagada (`estado_pago = 'paid'`)
     - ✅ Configuración DIAN válida y vigente

3. **Envío Manual Posterior**:
   - Nueva vista: `send_invoice_to_dian`
   - Permite enviar facturas electrónicas cuando se completen los pagos
   - Botón disponible en detalle de factura
   - URL: `/billing/invoices/<id>/send-to-dian/`

### 4. **Actualización del Método `puede_enviar_dian()`**

```python
def puede_enviar_dian(self):
    """Valida si la factura puede enviarse a DIAN"""
    # 1. Verificar que sea factura electrónica
    if not self.es_factura_electronica:
        return False, "Esta es una factura normal, no electrónica"
    
    # 2. Verificar que se haya solicitado envío
    if not self.requiere_envio_dian:
        return False, "No se solicitó envío a DIAN"
    
    # 3. Verificar pago completo
    if self.estado_pago != 'paid':
        return False, "La factura debe estar completamente pagada"
    
    # 4. Verificar estado DIAN
    if self.estado_dian not in ['draft', 'rejected']:
        return False, f"Estado actual: {self.estado_dian}"
    
    # 5. Verificar configuración
    try:
        config = self.organization.dianconfiguration
        if not config.puede_facturar():
            return False, "Configuración DIAN no válida"
    except:
        return False, "No hay configuración DIAN"
    
    return True, "OK"
```

## Casos de Uso

### Caso 1: Factura de Prueba / Cotización
```
✅ es_factura_electronica = False
✅ requiere_envio_dian = False
→ Usa consecutivo interno (INV-00001)
→ No consume consecutivo DIAN
→ Ideal para cotizaciones, estimados, facturas de prueba
```

### Caso 2: Factura Electrónica con Pago Parcial
```
✅ es_factura_electronica = True
✅ requiere_envio_dian = True
❌ estado_pago = 'partial' (50% pagado)
→ Factura creada con consecutivo DIAN (FE001)
→ NO se envía a DIAN aún
→ Mensaje: "Podrá enviarse cuando esté completamente pagada"
→ Cuando se completa el pago → Envío automático o manual
```

### Caso 3: Factura Electrónica Pagada al Contado
```
✅ es_factura_electronica = True
✅ requiere_envio_dian = True
✅ estado_pago = 'paid' (100% pagado)
→ Factura creada con consecutivo DIAN (FE001)
→ Se envía INMEDIATAMENTE a DIAN
→ Genera CUFE, XML, QR, etc.
```

### Caso 4: Factura Electrónica sin Envío Inmediato
```
✅ es_factura_electronica = True
❌ requiere_envio_dian = False
→ Factura creada con consecutivo DIAN (FE001)
→ NO se envía a DIAN (aunque esté pagada)
→ Usuario puede enviarla manualmente después
```

## Migración de Datos Existentes

Para facturas existentes, se recomienda ejecutar:

```python
# Script para actualizar facturas existentes
from apps.billing.models import Invoice

# Marcar facturas con CUFE como electrónicas enviadas
Invoice.objects.filter(cufe__isnull=False).exclude(cufe='').update(
    es_factura_electronica=True,
    requiere_envio_dian=True
)

# Facturas sin CUFE son normales
Invoice.objects.filter(Q(cufe__isnull=True) | Q(cufe='')).update(
    es_factura_electronica=False,
    requiere_envio_dian=False
)
```

## Interfaz de Usuario

### Formulario de Creación de Factura

Agregar checkboxes:

```html
<div class="form-check">
    <input type="checkbox" name="es_factura_electronica" id="es_factura_electronica" 
           class="form-check-input" {% if plan.allow_electronic_invoicing %}{% endif %}>
    <label for="es_factura_electronica">
        📄 Factura Electrónica DIAN (consume consecutivo autorizado)
    </label>
</div>

<div class="form-check" id="envio-dian-option" style="display:none;">
    <input type="checkbox" name="requiere_envio_dian" id="requiere_envio_dian" 
           class="form-check-input">
    <label for="requiere_envio_dian">
        🚀 Enviar a DIAN cuando esté completamente pagada
    </label>
</div>

<script>
document.getElementById('es_factura_electronica').addEventListener('change', function() {
    document.getElementById('envio-dian-option').style.display = 
        this.checked ? 'block' : 'none';
});
</script>
```

### Detalle de Factura

Mostrar botón de envío a DIAN:

```html
{% if invoice.es_factura_electronica and invoice.estado_pago == 'paid' %}
    {% if invoice.estado_dian in 'draft,rejected' %}
    <form method="post" action="{% url 'billing:send_invoice_to_dian' invoice.id %}">
        {% csrf_token %}
        <button type="submit" class="btn btn-success">
            <i class="fas fa-paper-plane"></i> Enviar a DIAN
        </button>
    </form>
    {% endif %}
{% endif %}
```

## Ventajas del Sistema

1. **Flexibilidad**: Permite facturas normales sin consumir consecutivos DIAN
2. **Control de Costos**: Solo se envía a DIAN cuando está pagado
3. **Cumplimiento**: Garantiza que facturas electrónicas tengan pago completo
4. **Trazabilidad**: Clara distinción entre factura normal y electrónica
5. **Ahorro de Consecutivos**: Cotizaciones y pruebas no gastan números DIAN

## Validaciones Importantes

✅ **Validación de Plan**: Solo planes Profesional y Empresarial pueden usar facturación electrónica  
✅ **Validación de Configuración**: DIAN debe estar configurada y vigente  
✅ **Validación de Consecutivo**: No permite agotar rango autorizado  
✅ **Validación de Pago**: Solo facturas 100% pagadas se envían a DIAN  
✅ **Validación de Estado**: Solo estados 'draft' o 'rejected' pueden enviarse  

## Pruebas Recomendadas

1. Crear factura normal (sin checkbox electrónica) → Verificar consecutivo interno
2. Crear factura electrónica sin pago → Verificar que NO se envía a DIAN
3. Crear factura electrónica con pago parcial → Completar pago → Enviar manual
4. Crear factura electrónica 100% pagada → Verificar envío automático
5. Verificar que consecutivos DIAN y normales sean independientes
