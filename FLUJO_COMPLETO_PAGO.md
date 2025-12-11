# 🔄 Flujo Completo de Registro y Pago con Wompi

## 📋 Proceso Paso a Paso

### 1️⃣ **REGISTRO** (`/organizations/register/`)

**Usuario completa el formulario:**
- Nombre y apellido
- Email
- Usuario y contraseña
- **Selecciona un plan** (Gratuito, Básico, Profesional, Empresarial)

**Sistema ejecuta:**
```python
✓ Crea usuario (is_active=False)
✓ Crea perfil (is_email_verified=False)
✓ Crea suscripción con payment_status='pending' (si no es gratuito)
✓ Envía email de verificación
✓ Redirige a: /users/verification/pending/
```

---

### 2️⃣ **VERIFICACIÓN DE EMAIL**

**Usuario recibe email y hace clic en enlace:**
- Enlace: `/users/verify/<token>/`

**Sistema ejecuta:**
```python
✓ Valida el token (no usado, no expirado)
✓ Activa el usuario (is_active=True)
✓ Marca email como verificado
✓ Verifica si hay suscripción pendiente

SI hay suscripción pendiente:
  ✓ Hace login automático
  ✓ Redirige a: /users/subscription/checkout/<plan_id>/
  
SI NO hay suscripción pendiente (plan gratuito):
  ✓ Redirige a: /dashboard/login/
```

---

### 3️⃣ **CHECKOUT DE PAGO** (`/users/subscription/checkout/<plan_id>/`)

**Usuario ve página de checkout con:**
- Resumen del plan seleccionado
- Monto a pagar (mensual o anual)
- Formulario de tarjeta de crédito (integrado con Wompi)

**Campos del formulario:**
```
- Número de tarjeta
- Fecha de expiración
- CVV
- Nombre del titular
- Guardar método de pago (opcional)
```

**Tarjetas de prueba Wompi:**
```
✓ Número: 4242 4242 4242 4242
  CVV: 123
  Fecha: 12/25
  Resultado: Aprobada

✓ Número: 4111 1111 1111 1111
  CVV: 123
  Fecha: 12/25
  Resultado: Aprobada
```

---

### 4️⃣ **PROCESAMIENTO DE PAGO** (`POST /users/subscription/checkout/<plan_id>/process/`)

**Cuando el usuario hace clic en "Pagar":**

```python
1. Tokeniza la tarjeta con Wompi
   wompi_service.tokenize_card_and_save()
   
2. Crea la transacción
   wompi_service.create_transaction()
   - amount_in_cents = monto * 100
   - currency = 'COP'
   - reference = "SUB-{user_id}-{plan_id}-{uuid}"
   
3. Actualiza la suscripción
   - payment_status = 'paid'
   - is_active = True
   - start_date = ahora
   - end_date = ahora + 30 días (o 365 si es anual)
   - amount_paid = monto
   
4. Envía email de confirmación
   send_subscription_confirmation_email()
   
5. Redirige a: /users/subscription/success/<transaction_id>/
```

---

### 5️⃣ **CONFIRMACIÓN DE PAGO** (`/users/subscription/success/<transaction_id>/`)

**Usuario ve:**
- ✅ Mensaje de éxito
- 📄 Detalles de la transacción:
  - ID de transacción
  - Monto pagado
  - Plan activado
  - Fecha de vencimiento
- 🎁 Beneficios del plan
- 🔘 Botones:
  - "Ir a Mis Empresas" → `/organizations/`
  - "Ver Mi Suscripción" → `/users/subscription/status/`

---

### 6️⃣ **WEBHOOK DE WOMPI** (`POST /users/webhooks/wompi/`)

**Wompi notifica el estado del pago:**

```python
✓ Verifica la firma del webhook (seguridad)
✓ Busca la transacción por wompi_transaction_id
✓ Actualiza el estado:
  - APPROVED → payment_status='paid', is_active=True
  - DECLINED → payment_status='failed', is_active=False
  - VOIDED → payment_status='refunded'
✓ Envía email según el resultado
```

---

## 🎯 Flujos Especiales

### **Plan Gratuito:**
```
Registro → Verificar Email → Login → Dashboard
(No pasa por checkout)
```

### **Plan de Pago:**
```
Registro → Verificar Email → Checkout → Pago → Dashboard
```

### **Renovación Automática:**
```
Cron Job (cada día):
  → python manage.py renew_subscriptions --days-before=3
  → Cobra con método de pago guardado
  → Extiende end_date
  → Envía email de confirmación
```

---

## 📊 Estados de la Suscripción

| Estado | payment_status | is_active | Significado |
|--------|---------------|-----------|-------------|
| ⏳ Pendiente | `pending` | `False` | Esperando pago |
| ✅ Activa | `paid` | `True` | Suscripción activa |
| ❌ Fallida | `failed` | `False` | Pago rechazado |
| 🔄 Procesando | `processing` | `False` | En proceso |
| 💰 Reembolsada | `refunded` | `False` | Dinero devuelto |
| ⛔ Cancelada | `cancelled` | `False` | Usuario canceló |

---

## 🔐 Seguridad Implementada

✅ **Verificación de Email:** Usuario debe verificar antes de pagar  
✅ **Tokens UUID:** Imposibles de predecir  
✅ **Expiración:** Tokens expiran en 24 horas  
✅ **HTTPS:** Requerido en producción  
✅ **Firma de Webhook:** Validación con events_secret  
✅ **PCI Compliance:** Wompi maneja datos de tarjetas  

---

## 🧪 Probar el Flujo Completo

### **Paso 1: Registrarse**
```
URL: http://localhost:8000/organizations/register/
- Completa el formulario
- Elige "Plan Básico" ($29.99/mes)
- Usa tu email real
```

### **Paso 2: Verificar Email**
```
- Revisa tu bandeja de entrada
- Clic en "Verificar mi correo electrónico"
- Serás redirigido automáticamente al checkout
```

### **Paso 3: Pagar**
```
Tarjeta de prueba:
- Número: 4242 4242 4242 4242
- CVV: 123
- Fecha: 12/25
- Nombre: Test User
- Clic en "Procesar Pago"
```

### **Paso 4: Confirmación**
```
- Verás página de éxito
- Recibirás email de confirmación
- Clic en "Ir a Mis Empresas"
- ¡Listo! Dashboard accesible
```

---

## 📧 Emails Enviados

1. **Email de Verificación** (al registrarse)
   - Template: `users/emails/verify_email.html`
   - Asunto: "Verifica tu correo electrónico - OpticaApp"

2. **Confirmación de Suscripción** (pago exitoso)
   - Template: `users/emails/subscription_confirmed.html`
   - Asunto: "¡Suscripción Activada!"

3. **Pago Fallido** (pago rechazado)
   - Template: `users/emails/payment_failed.html`
   - Asunto: "Error en el Pago"

4. **Renovación Fallida** (auto-renovación rechazada)
   - Template: `users/emails/renewal_failed.html`
   - Asunto: "Problema con tu Renovación"

---

## 🔄 Middleware Order (Importante)

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.organizations.middleware.TenantMiddleware',
    'apps.users.email_verification_middleware.EmailVerificationMiddleware',  # ← ANTES
    'apps.organizations.middleware.SubscriptionMiddleware',  # ← DESPUÉS
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

**Orden importante:**
1. EmailVerificationMiddleware verifica email
2. SubscriptionMiddleware verifica suscripción activa

---

## ✅ Estado del Sistema

**Implementado:**
- ✅ Registro con selección de plan
- ✅ Verificación de email
- ✅ Redirección automática a checkout
- ✅ Procesamiento de pagos con Wompi
- ✅ Actualización de suscripciones
- ✅ Webhooks de Wompi
- ✅ Emails de confirmación
- ✅ Renovación automática (comando)
- ✅ Gestión de métodos de pago

**URLs Activas:**
- `/organizations/register/` - Registro
- `/users/verify/<token>/` - Verificación
- `/users/subscription/checkout/<plan_id>/` - Checkout
- `/users/subscription/success/<tx_id>/` - Éxito
- `/users/subscription/status/` - Estado
- `/users/payment-methods/` - Métodos de pago
- `/users/webhooks/wompi/` - Webhook

---

**🎉 El sistema está 100% funcional y listo para usar!**
