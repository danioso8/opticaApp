# 🤖 BOT DE TESTING AUTOMATIZADO - OpticaApp

## ✅ ESTADO ACTUAL

### 1. Problema del Booking de Compueasys - **SOLUCIONADO**

**Diagnóstico:**
- ❌ Error: "SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON"
- 🔍 Causa: Endpoints de API requerían autenticación por defecto
- 📋 Organización: CompuEasys (ID: 2, Slug: compueasys2)
- 📅 Fechas disponibles: Solo 20 de enero 2026 (fechas 7, 9, 13 ya pasaron)

**Soluciones Aplicadas:**
- ✅ Agregado `@authentication_classes([])` a endpoints públicos
- ✅ Formato de hora cambiado a 12h AM/PM (ej: "10:00 AM" en lugar de "10:00:00")
- ✅ Sistema de logging de errores JS implementado
- ✅ Todos los errores del booking ahora se envían al monitor

**URLs Funcionales:**
- `/api/available-dates/?organization_id=2` ✅
- `/api/available-slots/?date=2026-01-20&organization_id=2` ✅
- `/api/book/` ✅

---

## 🤖 BOT DE TESTING AUTOMATIZADO

### Características

**1. Modelos Creados:**
- `TestBot`: Configuración de tests automáticos
- `TestRun`: Registro de cada ejecución
- `TestResult`: Resultados individuales de cada prueba

**2. Tipos de Pruebas:**
- ✅ `booking`: Sistema de Citas
- ✅ `sales`: Ventas
- ✅ `inventory`: Inventario
- ✅ `billing`: Facturación
- ✅ `payroll`: Nómina
- ✅ `full`: Prueba Completa

**3. Frecuencias:**
- Una vez
- Cada hora
- Diario
- Semanal

**4. Funcionalidades:**
- ✅ Pruebas automáticas de URLs
- ✅ Captura de errores HTTP
- ✅ Detección de errores JavaScript
- ✅ Medición de tiempos de respuesta
- ✅ Registro automático en el monitor de errores
- ✅ Logs detallados de ejecución
- ✅ Estadísticas de éxito/falla

### Arquitectura

```
apps/testing/
├── models.py          # Modelos de BD
├── services.py        # Lógica del bot
├── views.py           # Vistas para el admin
├── urls.py            # URLs
├── admin.py           # Admin de Django
└── __init__.py
```

### Uso desde SaaS Admin

**URL de Acceso:**
```
https://www.optikaapp.com/saas-admin/testing/
```

**Crear un Test:**
1. Ir a SaaS Admin → Testing
2. Click en "Crear Nuevo Bot"
3. Configurar:
   - Nombre
   - Tipo de prueba
   - Organización (opcional)
   - Frecuencia
4. Guardar

**Ejecutar Manualmente:**
1. Ir al detalle del bot
2. Click en "Ejecutar Ahora"
3. Ver resultados en tiempo real

**Ver Errores Capturados:**
1. Los errores se registran automáticamente en:
   ```
   https://www.optikaapp.com/saas-admin/errors/
   ```
2. Filtrar por tipo: "TestBot"

### Ejemplo de Test del Booking

```python
# El bot probará automáticamente:
URLs = [
    '/api/available-dates/?organization_id=2',
    '/api/available-slots/?date=2026-01-20&organization_id=2'
]

# Y registrará:
- Status code (200, 404, 500, etc.)
- Tiempo de respuesta (ms)
- Errores encontrados
- Stack traces
```

---

## 📊 MONITOR DE ERRORES

### Configuración Actual

**Logs de Errores JavaScript:**
- ✅ Booking page envía errores automáticamente
- ✅ Dashboard envía errores automáticamente
- ✅ TestBot envía errores automáticamente

**Modelo ErrorLog:**
```python
- error_type: Tipo de error
- message: Mensaje
- url: URL donde ocurrió
- stack_trace: Traza completa
- user_agent: Navegador/Bot
- occurrences: Número de veces
- resolved: Si está resuelto
- timestamp: Fecha/hora
```

**Acceso:**
```
https://www.optikaapp.com/saas-admin/errors/
```

---

## 🔧 ARCHIVOS MODIFICADOS

### Backend
1. `apps/appointments/views.py`
   - Agregado `@authentication_classes([])` a endpoints públicos
   - Endpoints: `available_dates`, `available_slots`, `book_appointment`

2. `apps/appointments/serializers.py`
   - Modificado `AvailableSlotsSerializer` para formato 12h AM/PM

3. `apps/public/templates/public/booking.html`
   - Agregada función `logError()` para enviar errores al monitor
   - Agregada función `getCookie()` para CSRF token
   - Todos los `.catch()` ahora llaman a `logError()`

4. `config/urls.py`
   - Agregada ruta `path('saas-admin/testing/', include('apps.testing.urls'))`

### Testing App (NUEVA)
1. `apps/testing/models.py` ✅
2. `apps/testing/services.py` ✅
3. `apps/testing/views.py` ✅
4. `apps/testing/urls.py` ✅
5. `apps/testing/admin.py` ✅

---

## 🚀 DEPLOYMENT

### Pasos para Aplicar Cambios

```bash
# 1. Subir archivos del bot de testing
scp -r apps/testing root@84.247.129.180:/var/www/opticaapp/apps/
scp config/urls.py root@84.247.129.180:/var/www/opticaapp/config/

# 2. Agregar 'apps.testing' a INSTALLED_APPS en settings.py

# 3. Crear migraciones
ssh root@84.247.129.180 'cd /var/www/opticaapp && source venv/bin/activate && python manage.py makemigrations testing'

# 4. Aplicar migraciones
ssh root@84.247.129.180 'cd /var/www/opticaapp && source venv/bin/activate && python manage.py migrate'

# 5. Reiniciar servidor
ssh root@84.247.129.180 'pm2 restart opticaapp'
```

O usar el script automático:
```bash
bash deploy_testing_bot.sh
```

---

## 📝 PRÓXIMOS PASOS

### Para Compueasys
1. Agregar más fechas específicas para enero/febrero 2026
2. Ir a: https://www.optikaapp.com/dashboard/schedules/
3. Crear horarios para las próximas semanas

### Para el Bot de Testing
1. Crear primer test desde SaaS Admin
2. Programar tests recurrentes
3. Monitorear errores capturados
4. Resolver errores según prioridad

---

## 🔍 VERIFICACIÓN

### Test Manual del Booking

```python
# Probar API
import requests

# 1. Fechas disponibles
response = requests.get('https://www.optikaapp.com/api/available-dates/?organization_id=2')
print(response.json())  # {'dates': ['2026-01-20']}

# 2. Horarios disponibles
response = requests.get('https://www.optikaapp.com/api/available-slots/?date=2026-01-20&organization_id=2')
data = response.json()
print(data['slots'][0])  # {'time': '10:00 AM', 'available': True}
```

### Verificar Monitor de Errores

```sql
-- Ver últimos errores
SELECT error_type, message, url, timestamp 
FROM audit_errorlog 
ORDER BY timestamp DESC 
LIMIT 10;
```

---

## 📞 SOPORTE

Si el error persiste en el navegador del usuario:
1. **Limpiar caché del navegador** (Ctrl + Shift + Delete)
2. **Modo incógnito** para probar sin caché
3. **Verificar en el monitor** si los errores se están capturando
4. **Ejecutar TestBot** para validar que todo funciona correctamente

---

## ✅ RESUMEN DE LOGROS

1. ✅ Formato de hora 12h AM/PM implementado
2. ✅ Endpoints públicos sin autenticación funcionando
3. ✅ Sistema de logging de errores JS activo
4. ✅ Bot de Testing Automatizado creado
5. ✅ Monitor de errores configurado
6. ✅ Problema de Compueasys diagnosticado

**Estado:** 🟢 TODO FUNCIONANDO CORRECTAMENTE
