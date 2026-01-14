# 🐛 Guía para Capturar y Solucionar Errores JavaScript

## ✅ Sistema Mejorado y Desplegado

Se han aplicado las siguientes mejoras:

### 1. **Endpoint más permisivo**
- ✅ Eliminado `@login_required` (no requiere autenticación)
- ✅ Agregado `@csrf_exempt` (no requiere CSRF token)
- ✅ Logging completo en servidor para debugging
- ✅ Responde con status de éxito/error

### 2. **Script JavaScript mejorado**
- ✅ Console.log para tracking visual
- ✅ Captura errores normales y promesas rechazadas
- ✅ Sin requerimiento de CSRF token
- ✅ Mejor manejo de errores en el fetch

### 3. **Función de test incluida**
- ✅ `window.testErrorCapture()` disponible en consola

---

## 🧪 Cómo Probar el Sistema

### Opción 1: Test desde la Consola del Navegador

1. Abre cualquier página de OpticaApp
2. Abre la consola del navegador (F12)
3. Ejecuta: `window.testErrorCapture()`
4. Deberías ver:
   ```
   🧪 Testing error capture...
   ❌ JS Error captured: {message: "Test error...", ...}
   ✅ Error logged to server: {status: "success", logged: true}
   ```
5. Ve al dashboard de errores: `/saas-admin/errors/`
6. Deberías ver el error registrado

### Opción 2: Reproducir el Error del Modal

1. Ve a la página donde ocurre el error del modal
2. Realiza la acción que causa el error
3. Abre la consola (F12) y verifica los logs:
   - `🔍 Error tracking system initialized` (al cargar)
   - `❌ JS Error captured:` (cuando ocurre el error)
   - `✅ Error logged to server:` (cuando se registra)
4. Ve al dashboard de errores: `/saas-admin/errors/`
5. El error debería aparecer con toda la información

### Opción 3: Test Manual con Código

Abre la consola y ejecuta:

```javascript
// Test 1: Error normal
throw new Error('Test error manual');

// Test 2: Error de variable no definida
console.log(variableQueNoExiste);

// Test 3: Promise rejection
Promise.reject('Test promise rejection');
```

---

## 🔍 Qué Revisar en la Consola

### Mensajes esperados al cargar la página:
```
🔍 Error tracking system initialized
```

### Cuando ocurre un error:
```
❌ JS Error captured: {
  message: "...",
  type: "...",
  stack: "...",
  url: "...",
  lineNumber: "...",
  columnNumber: "..."
}
```

### Cuando se registra correctamente:
```
✅ Error logged to server: {status: "success", logged: true}
```

### Si falla el registro:
```
❌ Failed to log error to server: [error details]
```

---

## 📊 Ver Errores Registrados

### Dashboard de Monitoreo:
**URL**: `https://www.optikaapp.com/saas-admin/errors/`

### Verificar en logs del servidor:
```bash
ssh root@84.247.129.180
pm2 logs opticaapp --lines 100
```

Busca mensajes como:
```
INFO: Recibiendo error JS desde: xxx.xxx.xxx.xxx
INFO: Error capturado: JavaScriptError - Test error...
INFO: Nuevo error registrado (ID: XX): JavaScriptError
```

---

## 🎯 Solucionar el Error del Modal

### Paso 1: Capturar el Error
1. Reproduce el error del modal
2. Verifica en consola que se capture
3. Ve al dashboard de errores

### Paso 2: Analizar Información
El error registrado incluirá:
- ✅ **Mensaje**: Descripción del error
- ✅ **Tipo**: TypeError, ReferenceError, etc.
- ✅ **Stack trace**: Dónde ocurrió exactamente
- ✅ **URL**: Página donde ocurrió
- ✅ **Línea y columna**: Ubicación exacta en el código
- ✅ **Navegador**: User agent completo
- ✅ **Usuario**: Quién experimentó el error

### Paso 3: Identificar la Causa
Con el stack trace y la línea de código, puedes:
1. Ir al archivo específico
2. Ver la línea exacta del error
3. Entender qué variable o función causó el problema

### Paso 4: Solucionar
Ejemplos comunes:

**Error: "Cannot read property 'X' of undefined"**
```javascript
// ❌ Antes
document.getElementById('myElement').value = 'test';

// ✅ Después
const element = document.getElementById('myElement');
if (element) {
    element.value = 'test';
}
```

**Error: "X is not defined"**
```javascript
// ❌ Antes
myFunction();

// ✅ Después
if (typeof myFunction === 'function') {
    myFunction();
}
```

---

## 🛠️ Troubleshooting

### Si NO aparece "🔍 Error tracking system initialized":
- El script no se está cargando
- Verifica que el template base esté incluido
- Limpia caché del navegador (Ctrl+Shift+R)

### Si aparece el error en consola pero NO se registra:
- Revisa Network tab (F12 → Network)
- Busca la petición a `/audit/api/log-js-error/`
- Verifica el status code (debería ser 200)
- Revisa la respuesta del servidor

### Si la petición falla (404, 500, etc.):
- Verifica que la URL esté correcta
- Revisa logs del servidor: `pm2 logs opticaapp`
- Verifica que el endpoint esté en `apps/audit/urls.py`

### Para verificar que el endpoint funciona:
```bash
# Desde el servidor
curl -X POST http://localhost:8000/audit/api/log-js-error/ \
  -H "Content-Type: application/json" \
  -d '{"message":"Test","type":"TestError","stack":"","url":"test"}'
```

Debería responder:
```json
{"status": "success", "logged": true}
```

---

## 📝 Próximos Pasos

1. ✅ Prueba el sistema con `window.testErrorCapture()`
2. ✅ Reproduce el error del modal original
3. ✅ Verifica que se registre en el dashboard
4. ✅ Analiza el stack trace
5. ✅ Identifica y corrige el error
6. ✅ Despliega la corrección
7. ✅ Marca el error como resuelto en el dashboard

---

## 💡 Tips

- **Mantén la consola abierta** mientras navegas para ver errores en tiempo real
- **Revisa el dashboard regularmente** para detectar errores que los usuarios experimentan
- **El sistema agrupa errores iguales** para evitar spam
- **Los errores críticos** aparecen destacados en el dashboard
- **Puedes marcar errores como resueltos** una vez corregidos

---

## 🔗 Enlaces Útiles

- **Dashboard de errores**: https://www.optikaapp.com/saas-admin/errors/
- **Logs PM2**: `ssh root@84.247.129.180 -t "pm2 logs opticaapp"`
- **Archivo de test local**: `test_js_error_capture.html`
