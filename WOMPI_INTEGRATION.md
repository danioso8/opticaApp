# Sistema de Pagos con Wompi - Documentación

## 📋 Resumen

Se ha implementado un sistema completo de pagos con Wompi para gestionar suscripciones, incluyendo:

- ✅ Almacenamiento seguro de tarjetas (tokenización)
- ✅ Pagos únicos y recurrentes
- ✅ Renovación automática de suscripciones
- ✅ Webhooks para procesar eventos de Wompi
- ✅ Notificaciones por email cuando falla un pago
- ✅ Panel administrativo para ver transacciones

## 🗂️ Archivos Creados

### Modelos (apps/users/models.py)
- **PaymentMethod**: Almacena tokens de tarjetas de crédito
- **Transaction**: Registro de todas las transacciones
- **SubscriptionRenewalLog**: Log de intentos de renovación automática

### Servicios (apps/users/wompi_service.py)
- `WompiService`: Clase principal para interactuar con Wompi API
  - `create_transaction()`: Crear transacción de pago
  - `get_transaction()`: Consultar estado de transacción
  - `create_payment_link()`: Crear link de pago
  - `verify_signature()`: Verificar firma de webhooks
  - `tokenize_card_and_save()`: Tokenizar y guardar tarjeta

### Vistas (apps/users/payment_views.py)
- `subscription_checkout`: Página de checkout
- `process_subscription_payment`: Procesar pago de suscripción
- `subscription_success`: Confirmación de pago exitoso
- `payment_methods_list`: Lista de métodos de pago del usuario
- `wompi_webhook`: Endpoint para recibir eventos de Wompi
- `subscription_status`: Estado de la suscripción

### Comando Management (apps/users/management/commands/renew_subscriptions.py)
Comando para renovar automáticamente suscripciones:
```bash
python manage.py renew_subscriptions --days-before=3
```

### Templates
- `subscription_checkout.html`: Página de checkout
- `subscription_success.html`: Confirmación de pago
- `emails/subscription_confirmed.html`: Email de confirmación
- `emails/payment_failed.html`: Email de pago fallido
- `emails/renewal_failed.html`: Email de renovación fallida

## 🔧 Configuración

### 1. Variables de Entorno (.env)

```env
# Wompi Payment Gateway
WOMPI_TEST_MODE=True  # False en producción

# Llaves de producción
WOMPI_PUBLIC_KEY=pub_prod_tu_llave_publica
WOMPI_PRIVATE_KEY=prv_prod_tu_llave_privada
WOMPI_EVENTS_SECRET=prod_events_tu_secret

# Llaves de prueba (sandbox)
# WOMPI_PUBLIC_KEY=pub_test_tu_llave_de_prueba
# WOMPI_PRIVATE_KEY=prv_test_tu_llave_de_prueba
# WOMPI_EVENTS_SECRET=test_events_tu_secret
```

### 2. Obtener Llaves de Wompi

1. Registrarse en https://comercios.wompi.co/
2. Ir a "Configuración" → "API Keys"
3. Copiar:
   - Public Key
   - Private Key  
   - Events Secret (para webhooks)

Para pruebas, usar sandbox: https://sandbox.wompi.co/

### 3. Configurar Webhook en Wompi

1. En el panel de Wompi, ir a "Webhooks"
2. Agregar URL: `https://tu-dominio.onrender.com/users/webhooks/wompi/`
3. Seleccionar evento: `transaction.updated`

## 🚀 Uso

### Flujo de Pago

1. **Usuario selecciona un plan**
   - Desde `/organizations/subscription/plans/`
   - Click en "Seleccionar Plan"

2. **Checkout**
   - Redirige a `/users/subscription/checkout/<plan_id>/?cycle=monthly`
   - Usuario puede:
     - Usar tarjeta guardada
     - Agregar nueva tarjeta

3. **Procesamiento**
   - POST a `/users/subscription/checkout/<plan_id>/process/`
   - Se crea transacción en Wompi
   - Se actualiza suscripción del usuario

4. **Confirmación**
   - Redirige a `/users/subscription/success/<transaction_id>/`
   - Email de confirmación

### Renovación Automática

Configurar un cron job o tarea programada para ejecutar diariamente:

```bash
# Linux/Mac (crontab)
0 2 * * * cd /ruta/proyecto && python manage.py renew_subscriptions --days-before=3

# Windows (Task Scheduler)
python manage.py renew_subscriptions --days-before=3
```

En Render, agregar en `render.yaml`:

```yaml
services:
  - type: cron
    name: subscription-renewal
    schedule: "0 2 * * *"  # Diariamente a las 2 AM
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python manage.py renew_subscriptions --days-before=3"
```

### Webhooks

Wompi enviará notificaciones a `/users/webhooks/wompi/` cuando:
- Una transacción cambie de estado
- Un pago sea aprobado/rechazado

El webhook:
1. Verifica la firma de seguridad
2. Actualiza la transacción en BD
3. Activa/desactiva la suscripción
4. Envía email de notificación

## 🎨 Personalización

### Agregar más información a las transacciones

En `payment_views.py`, puedes agregar metadata:

```python
transaction = Transaction.objects.create(
    user=user,
    amount=amount,
    metadata={'custom_field': 'valor'}
)
```

### Cambiar emails de notificación

Editar templates en `apps/users/templates/users/emails/`:
- `subscription_confirmed.html`
- `payment_failed.html`
- `renewal_failed.html`

### Cambiar días de renovación anticipada

```bash
python manage.py renew_subscriptions --days-before=5
```

## 📊 Panel Administrativo

En `/admin/`:
- **Payment Methods**: Ver tarjetas guardadas
- **Transactions**: Historial de transacciones
- **Subscription Renewal Logs**: Intentos de renovación

En `/saas-admin/`:
- Ver usuarios y sus suscripciones
- Otorgar acceso ilimitado
- Gestionar planes

## 🔒 Seguridad

- ✅ Nunca se almacenan datos completos de tarjetas
- ✅ Solo se guarda el token de Wompi
- ✅ Webhooks verificados con firma SHA256
- ✅ HTTPS obligatorio en producción
- ✅ CSRF protection en todos los formularios

## 🐛 Debugging

### Modo de prueba

Activar logs detallados en `wompi_service.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Simular renovación

```bash
python manage.py renew_subscriptions --dry-run
```

### Ver transacciones en Wompi

Panel de Wompi → Transacciones → Filtrar por fecha/estado

## 📝 Notas Importantes

1. **PostgreSQL requerido**: El modelo Transaction usa JSONField (no funciona en SQLite)
2. **HTTPS obligatorio**: Wompi requiere HTTPS para webhooks en producción
3. **Email configurado**: Configurar EMAIL_HOST_USER y EMAIL_HOST_PASSWORD en .env
4. **Moneda**: Por defecto usa COP (pesos colombianos)

## 🔄 Próximos Pasos

1. Obtener llaves de Wompi (producción o sandbox)
2. Configurar variables en Render
3. Configurar webhook en panel de Wompi
4. Crear cron job para renovación automática
5. Probar flujo completo con tarjetas de prueba

## 🧪 Tarjetas de Prueba (Sandbox)

Wompi proporciona tarjetas de prueba:

```
VISA Aprobada:
4242 4242 4242 4242
CVV: 123
Fecha: Cualquier fecha futura

VISA Rechazada:
4111 1111 1111 1111
CVV: 123
```

Ver más en: https://docs.wompi.co/docs/tarjetas-de-prueba

## 📞 Soporte

- Documentación Wompi: https://docs.wompi.co/
- Panel Wompi: https://comercios.wompi.co/
- Sandbox: https://sandbox.wompi.co/
