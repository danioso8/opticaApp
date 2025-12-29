# Sistema de Conversión de Moneda USD a COP

## Resumen de Implementación

Se ha implementado un sistema completo de conversión de moneda que permite:
- **Almacenar precios en USD** en la base de datos
- **Mostrar precios en COP** a los usuarios colombianos
- **Cobrar en COP** a través de Wompi

## Archivos Modificados/Creados

### 1. `apps/organizations/currency_utils.py` (NUEVO)
Archivo de utilidades con funciones de conversión:
- `get_exchange_rate()`: Obtiene la tasa de cambio (4000 COP/USD por defecto)
- `usd_to_cop(amount)`: Convierte USD a COP
- `usd_to_cop_cents(amount)`: Convierte USD a centavos COP (para Wompi)
- `format_cop(amount)`: Formatea cantidad en COP con símbolo ($159.960 COP)
- `get_plan_price_cop(plan)`: Obtiene precios COP de un plan
- `get_plan_prices_display(plan)`: Obtiene todos los precios formateados

### 2. `config/settings.py`
Configuración añadida:
```python
# Tasa de cambio USD a COP
USD_TO_COP_RATE = 4000.00  # 1 USD = 4000 COP

# Moneda para mostrar
CURRENCY_DISPLAY = 'COP'
```

### 3. `apps/users/payment_views.py`
Modificaciones en vistas de pago:
- **subscription_checkout()**: Convierte precios USD a COP antes de mostrar
- **process_subscription_payment()**: Convierte USD a centavos COP para Wompi
- Importa funciones de currency_utils

### 4. `apps/organizations/views.py`
Modificaciones:
- **user_register()**: Añade precios COP a cada plan
- **subscription_plans()**: Añade precios COP a cada plan

### 5. Templates Actualizados

#### `apps/organizations/templates/organizations/user_register.html`
- Muestra precios en COP como principal
- Muestra USD como referencia (≈ $39.99 USD)
- Formato: "$159.960 COP/mes"

#### `apps/users/templates/users/subscription_checkout.html`
- Banner de plan muestra precio en COP
- Incluye referencia en USD
- Formato mejorado para checkout

#### `apps/organizations/templates/organizations/plans.html`
- Precios principales en COP
- USD como referencia
- Toggle mensual/anual actualizado

## Tasa de Cambio

**Actual: 1 USD = 4,000 COP**

Para actualizar la tasa de cambio, modificar en `config/settings.py`:
```python
USD_TO_COP_RATE = 4200.00  # Nueva tasa
```

## Ejemplos de Conversión

| Plan           | Precio USD | Precio COP    | Centavos Wompi |
|----------------|------------|---------------|----------------|
| Free           | $0.00      | $0 COP        | 0              |
| Basic (Mes)    | $39.99     | $159.960 COP  | 15,996,000     |
| Basic (Año)    | $399.99    | $1.599.960 COP| 159,996,000    |
| Professional (Mes)| $89.99  | $359.960 COP  | 35,996,000     |
| Professional (Año)| $899.99 | $3.599.960 COP| 359,996,000    |
| Enterprise (Mes)| $179.99   | $719.960 COP  | 71,996,000     |
| Enterprise (Año)| $1,799.99 | $7.199.960 COP| 719,996,000    |

## Flujo de Conversión

### 1. Almacenamiento (Base de Datos)
```python
# SubscriptionPlan model
price_monthly = Decimal('39.99')  # USD
price_yearly = Decimal('399.99')  # USD
```

### 2. Visualización (Templates)
```python
# En la vista
plan.cop_prices = get_plan_prices_display(plan)

# En el template
{{ plan.cop_prices.monthly_cop|floatformat:0 }} COP
≈ ${{ plan.price_monthly|floatformat:2 }} USD
```

### 3. Pago (Wompi)
```python
# Convertir a centavos COP
amount_cop_cents = usd_to_cop_cents(plan.price_monthly)

# Enviar a Wompi
wompi_service.create_transaction(
    amount_in_cents=amount_cop_cents,  # 15,996,000 centavos
    currency='COP',
    ...
)
```

## Integración con Wompi

Wompi requiere montos en **centavos de COP**:
- $159.960 COP = 15,996,000 centavos
- La función `usd_to_cop_cents()` convierte automáticamente
- El monto se envía como entero sin decimales

## Pruebas

Ejecutar script de prueba:
```bash
python test_currency_conversion.py
```

Este script verifica:
✅ Conversiones USD → COP
✅ Conversiones a centavos para Wompi
✅ Precios de todos los planes
✅ Verificación de montos

## Ventajas del Sistema

1. **Precios Estables**: Los precios en USD no cambian con fluctuaciones del peso
2. **Flexibilidad**: Fácil actualizar tasa de cambio desde settings
3. **Transparencia**: Usuario ve precio en COP pero sabe equivalencia USD
4. **Compatibilidad Wompi**: Conversión automática a formato requerido
5. **Escalabilidad**: Fácil agregar más monedas en el futuro

## Notas Importantes

- Los precios se almacenan SIEMPRE en USD en la base de datos
- La conversión a COP es solo para visualización y cobro
- Wompi SOLO acepta COP en Colombia
- Los centavos de COP se calculan multiplicando por 100
- El formato colombiano usa punto (.) para miles: $159.960 COP

## Mantenimiento

### Actualizar Tasa de Cambio
Editar `config/settings.py`:
```python
USD_TO_COP_RATE = 4200.00  # Nueva tasa
```

### Agregar Nueva Moneda
1. Agregar configuración en settings.py
2. Crear funciones de conversión en currency_utils.py
3. Actualizar templates para mostrar nueva moneda
4. Actualizar vistas de pago

## Próximos Pasos (Opcional)

- [ ] Integrar API de tasas de cambio en tiempo real
- [ ] Crear modelo CurrencyRate para histórico de tasas
- [ ] Panel admin para actualizar tasas manualmente
- [ ] Soporte multi-moneda (MXN, ARS, etc.)
- [ ] Caché de conversiones para optimizar rendimiento
