# Guía Rápida - Configuración de Wompi

## 🚀 Paso 1: Obtener Llaves de Wompi

### Opción A: Modo Producción (Pagos Reales)
1. Ve a https://comercios.wompi.co/
2. Inicia sesión o crea una cuenta
3. Ve a **"Configuración"** → **"Llaves API"**
4. Copia las siguientes llaves:
   - **Public Key** (empieza con `pub_prod_`)
   - **Private Key** (empieza con `prv_prod_`)
   - **Events Secret** (para webhooks)

### Opción B: Modo Prueba/Sandbox (Recomendado para empezar)
1. Ve a https://sandbox.wompi.co/
2. Crea una cuenta de prueba
3. Ve a **"Configuración"** → **"Llaves API"**
4. Copia las siguientes llaves:
   - **Public Key** (empieza con `pub_test_`)
   - **Private Key** (empieza con `prv_test_`)
   - **Events Secret** (para webhooks)

## 📝 Paso 2: Configurar Variables en Render

1. Ve a tu dashboard de Render: https://dashboard.render.com/
2. Selecciona tu servicio web (OpticaApp)
3. Ve a **"Environment"**
4. Agrega las siguientes variables:

```
WOMPI_TEST_MODE=False          # True si usas sandbox, False para producción
WOMPI_PUBLIC_KEY=pub_prod_XXXXX  # Tu llave pública
WOMPI_PRIVATE_KEY=prv_prod_XXXXX # Tu llave privada
WOMPI_EVENTS_SECRET=prod_events_XXXXX # Tu secret para webhooks
```

5. Click en **"Save Changes"**
6. El servicio se redesplegará automáticamente

## 🔗 Paso 3: Configurar Webhook en Wompi

1. En el panel de Wompi, ve a **"Webhooks"** o **"Integraciones"**
2. Click en **"Agregar Webhook"**
3. Configura:
   - **URL**: `https://tu-app.onrender.com/users/webhooks/wompi/`
   - **Eventos**: Selecciona `transaction.updated`
   - **Estado**: Activo
4. Guarda el webhook

## ✅ Paso 4: Verificar Configuración

### En Local (Desarrollo):
```bash
# Agregar en tu .env local
WOMPI_TEST_MODE=True
WOMPI_PUBLIC_KEY=pub_test_tu_llave
WOMPI_PRIVATE_KEY=prv_test_tu_llave
WOMPI_EVENTS_SECRET=test_events_tu_secret

# Probar
python manage.py shell
>>> from apps.users.wompi_service import wompi_service
>>> print(wompi_service.public_key)
>>> print("Test mode:", wompi_service.test_mode)
```

### En Render (Producción):
1. Ve a **"Logs"** en tu servicio de Render
2. Busca mensajes de inicio que mencionen Wompi
3. Verifica que no haya errores de configuración

## 🧪 Paso 5: Probar con Tarjetas de Prueba

Si estás en modo sandbox, usa estas tarjetas de prueba:

### VISA Aprobada:
```
Número: 4242 4242 4242 4242
CVV: 123
Fecha: Cualquier fecha futura (ej: 12/25)
```

### Mastercard Aprobada:
```
Número: 5555 5555 5555 4444
CVV: 123
Fecha: Cualquier fecha futura
```

### Tarjeta Rechazada:
```
Número: 4111 1111 1111 1111
CVV: 123
```

## 🎯 Paso 6: Probar el Flujo Completo

1. Accede a tu app: `https://tu-app.onrender.com`
2. Inicia sesión con un usuario normal (no superuser)
3. Ve a **"Planes"** o **"Suscripciones"**
4. Selecciona un plan
5. Completa el checkout con una tarjeta de prueba
6. Verifica que:
   - El pago se procese
   - Recibas un email de confirmación
   - La suscripción se active

## ⚙️ Paso 7: Configurar Renovación Automática (Opcional)

### En Render:

1. Ve a tu servicio web
2. Agrega un **Cron Job**:
   - **Comando**: `python manage.py renew_subscriptions --days-before=3`
   - **Programación**: `0 2 * * *` (diariamente a las 2 AM)

O usa el archivo `render.yaml`:

```yaml
- type: cron
  name: subscription-renewal
  env: python
  schedule: "0 2 * * *"
  buildCommand: "pip install -r requirements.txt"
  startCommand: "python manage.py renew_subscriptions --days-before=3"
```

## 📊 Monitoreo

### Ver Transacciones:
- Panel Admin: `https://tu-app.onrender.com/admin/users/transaction/`
- Panel Wompi: https://comercios.wompi.co/transacciones

### Ver Logs de Renovación:
- Panel Admin: `https://tu-app.onrender.com/admin/users/subscriptionrenewallog/`

## 🔧 Troubleshooting

### Error: "Invalid API Key"
- Verifica que las llaves estén correctas en Render
- Asegúrate de que las llaves coincidan con el modo (test/prod)

### Error: "Webhook signature invalid"
- Verifica que `WOMPI_EVENTS_SECRET` esté configurado
- Asegúrate de usar HTTPS en producción

### Pagos no se procesan:
- Revisa los logs en Render
- Verifica en panel de Wompi el estado de las transacciones
- Asegúrate de que el email del usuario esté configurado

## 📞 Soporte Wompi

- Email: soporte@wompi.co
- Documentación: https://docs.wompi.co/
- Teléfono: +57 (601) 508 9000

## ✨ ¡Listo!

Tu integración de Wompi está configurada. Los usuarios ahora pueden:
- ✅ Seleccionar planes de suscripción
- ✅ Pagar con tarjeta de crédito/débito
- ✅ Guardar tarjetas para pagos futuros
- ✅ Renovación automática de suscripciones
- ✅ Recibir notificaciones por email
