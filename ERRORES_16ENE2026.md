# REGISTRO DE ERRORES - 16 ENERO 2026

## 📊 RESUMEN DE ERRORES DEL DÍA

**Total de errores detectados:** 2 críticos  
**Total de errores resueltos:** 2  
**Tasa de resolución:** 100%  
**Tiempo de resolución promedio:** ~45 minutos  

---

## 🔴 ERROR #1: Error 500 en API de Booking

### Identificación
- **Código:** HTTP 500 Internal Server Error
- **Endpoint:** `/api/available-dates/`
- **Severidad:** 🔴 CRÍTICA
- **Impacto:** Sistema de booking completamente bloqueado
- **Reportado por:** Usuario (danioso8329/La Casa Logística)
- **Fecha detección:** 16 Enero 2026
- **Fecha resolución:** 16 Enero 2026
- **Tiempo de resolución:** ~30 minutos

### Síntomas
```javascript
// Error en consola del navegador
Network error: {
  type: 'NetworkError', 
  message: 'HTTP 500: Internal Server Error - /api/available-dates/?organization_id=5&doctor_id=8'
}

Error: SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON
```

### Stack Trace Completo
```python
Internal Server Error: /api/available-dates/
Traceback (most recent call last):
  File "/var/www/opticaapp/venv/lib/python3.12/site-packages/django/contrib/messages/api.py", line 27, in add_message
    messages = request._messages
    ^^^^^^^^^^^^^^^^^
AttributeError: 'WSGIRequest' object has no attribute '_messages'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/var/www/opticaapp/venv/lib/python3.12/site-packages/django/core/handlers/exception.py", line 55, in inner
    response = get_response(request)
    ^^^^^^^^^^^^^^^^^^^^^
  File "/var/www/opticaapp/venv/lib/python3.12/site-packages/django/utils/deprecation.py", line 133, in __call__
    response = self.process_request(request)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/var/www/opticaapp/apps/organizations/middleware.py", line 301, in process_request
    messages.warning(
  File "/var/www/opticaapp/venv/lib/python3.12/site-packages/django/contrib/messages/api.py", line 110, in warning
    add_message(
  File "/var/www/opticaapp/venv/lib/python3.12/site-packages/django/contrib/messages/api.py", line 35, in add_message
    raise MessageFailure(
django.contrib.messages.api.MessageFailure: 
  You cannot add messages without installing 
  django.contrib.messages.middleware.MessageMiddleware
```

### Causa Raíz
El **FeatureAccessMiddleware** en `apps/organizations/middleware.py` estaba procesando las peticiones API y ejecutando `messages.warning()`, pero:

1. Los endpoints API públicos **NO tienen** `MessageMiddleware` configurado
2. El objeto `request` en APIs **no tiene** el atributo `_messages`
3. El middleware asumía que todas las peticiones tienen contexto de mensajes

**Archivo:** `apps/organizations/middleware.py`  
**Línea:** 301  
**Función:** `process_request()`

### Código Problemático
```python
# ANTES - CÓDIGO CON ERROR
def process_request(self, request):
    """Verifica si el usuario tiene acceso a la característica"""
    
    # Saltar verificación para URLs exentas
    if any(request.path.startswith(url) for url in self.EXEMPT_URLS):
        return None
    
    # ... otras verificaciones ...
    
    if not has_module_access(request.user, required_feature):
        # ❌ ESTO FALLA EN APIs - No tienen MessageMiddleware
        messages.warning(
            request,
            f'🔒 "{feature_name}" no está disponible en tu plan actual.'
        )
        return redirect(reverse('dashboard:home'))
```

### Solución Implementada
```python
# DESPUÉS - CÓDIGO CORREGIDO
def process_request(self, request):
    """Verifica si el usuario tiene acceso a la característica"""
    
    # ✅ NUEVO: Saltar verificación para URLs de API (no tienen MessageMiddleware)
    if request.path.startswith('/api/'):
        return None
    
    # Saltar verificación para URLs exentas
    if any(request.path.startswith(url) for url in self.EXEMPT_URLS):
        return None
    
    # ... resto del código sin cambios ...
```

### Archivos Modificados
- `apps/organizations/middleware.py` (línea 268 agregada)

### Testing de Validación
```bash
# Antes del fix
curl https://optikaapp.com/api/available-dates/?organization_id=2
# Resultado: HTTP 500

# Después del fix
curl https://optikaapp.com/api/available-dates/?organization_id=2
# Resultado: HTTP 200 - {"dates": [...]}
```

### Estado
✅ **RESUELTO** - 16 Enero 2026, 18:30

---

## 🟡 ERROR #2: Fechas Insuficientes en CompuEasys2

### Identificación
- **Código:** N/A (Problema de configuración)
- **Componente:** Sistema de agendamiento
- **Severidad:** 🟡 MEDIA
- **Impacto:** Experiencia de usuario pobre - pocas opciones de citas
- **Reportado por:** Diagnóstico automático
- **Fecha detección:** 16 Enero 2026
- **Fecha resolución:** 16 Enero 2026
- **Tiempo de resolución:** ~15 minutos

### Síntomas
```bash
# Organizaciones en Contabo
2 - compueasys2 - CompuEasys - Activa: True - Fechas: 1 ❌
4 - oceano-optico - OCÉANO ÓPTICO - Activa: True - Fechas: 2 ⚠️
3 - optica-demo - Óptica Demo - Activa: True - Fechas: 0 ❌
```

Usuario veía calendario casi vacío, solo 1 fecha disponible.

### Causa Raíz
La organización CompuEasys2 (ID: 2, slug: `compueasys2`) tenía:
- Solo **1 fecha** configurada en `SpecificDateSchedule`
- No había horarios recurrentes en `WorkingHours`
- Sistema requiere fechas específicas para mostrar disponibilidad

**Tabla afectada:** `appointments_specificdateschedule`  
**Registros:** 1 (insuficiente)

### Solución Implementada

Script Python para crear fechas automáticamente:

```python
# setup_compueasys2_dates.py
schedules = [
    {'day': 0, 'start': '08:00', 'end': '12:00', 'slot': 30},  # Lunes
    {'day': 1, 'start': '08:00', 'end': '12:00', 'slot': 30},  # Martes
    {'day': 2, 'start': '08:00', 'end': '12:00', 'slot': 30},  # Miércoles
    {'day': 3, 'start': '08:00', 'end': '12:00', 'slot': 30},  # Jueves
    {'day': 4, 'start': '08:00', 'end': '12:00', 'slot': 30},  # Viernes
    {'day': 5, 'start': '09:00', 'end': '13:00', 'slot': 30},  # Sábado
]

# Crear fechas para próximos 60 días
# Resultado: 52 fechas creadas (solo días laborables)
```

### Ejecución en Producción
```bash
scp setup_compueasys2_dates.py root@84.247.129.180:/var/www/opticaapp/
ssh root@84.247.129.180 "cd /var/www/opticaapp && source venv/bin/activate && python setup_compueasys2_dates.py"

# Output:
# Organización: CompuEasys (ID: 2)
# Config: Existe - Abierto: True
# Doctor: Daniel Andres Osorio Velasquez
# Creadas: 51
# Total disponibles: 52
```

### Resultado
```bash
# Después del fix
2 - compueasys2 - CompuEasys - Activa: True - Fechas: 52 ✅
```

### Estado
✅ **RESUELTO** - 16 Enero 2026, 18:45

---

## 🔍 PATRONES DE ERRORES IDENTIFICADOS

### Patrón 1: Middleware Incompatible con APIs
**Problema:** Middlewares que asumen contexto web (cookies, sesiones, mensajes) procesando APIs REST

**Indicadores:**
- AttributeError en `request._messages`
- MessageFailure exceptions
- Error 500 en endpoints `/api/*`

**Solución estándar:**
```python
# Siempre verificar tipo de request en middlewares
def process_request(self, request):
    # Skip API routes
    if request.path.startswith('/api/'):
        return None
    
    # Skip AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return None
    
    # ... resto del procesamiento ...
```

### Patrón 2: Configuración Insuficiente de Datos
**Problema:** Organizaciones sin datos necesarios para funcionar (fechas, horarios, doctores)

**Indicadores:**
- Calendarios vacíos
- "No hay fechas disponibles"
- Contadores en 0 o muy bajos

**Solución estándar:**
1. Scripts de verificación de configuración
2. Scripts de población de datos por defecto
3. Alertas cuando configuración es insuficiente

---

## 📈 MÉTRICAS DE ERRORES

### Por Severidad
```
🔴 Críticos (Bloquean funcionalidad): 1
🟡 Medios (Degradan experiencia):     1
🟢 Bajos (Menores):                   0
```

### Por Componente
```
Middleware:          1 error
Configuración BD:    1 error
Frontend:            0 errores
Backend API:         0 errores (después del fix)
```

### Por Tipo
```
Code bugs:           1 (middleware)
Configuration:       1 (fechas insuficientes)
Performance:         0
Security:            0
```

### Tiempo de Resolución
```
Error #1 (500 API):   ~30 min
Error #2 (Fechas):    ~15 min
Total:                ~45 min
```

---

## 🛡️ PREVENCIÓN DE ERRORES SIMILARES

### Checklist para Nuevos Middlewares

- [ ] ¿Procesa rutas API? → Agregar skip explícito
- [ ] ¿Usa `messages.*`? → Verificar que request tiene `_messages`
- [ ] ¿Usa `redirect()`? → No aplicar en APIs (retornar Response)
- [ ] ¿Asume autenticación? → Verificar `request.user.is_authenticated`
- [ ] ¿Modifica session? → Verificar que session existe

### Checklist para Nuevas Organizaciones

- [ ] AppointmentConfiguration creada y `is_open=True`
- [ ] Al menos 30 días de fechas disponibles en SpecificDateSchedule
- [ ] Al menos 1 doctor asignado y activo
- [ ] WorkingHours configurados (opcional si usa SpecificDateSchedule)
- [ ] Logo y branding configurados
- [ ] Plan y límites asignados correctamente

### Testing Recomendado

```python
# Test de API endpoints
def test_api_available_dates_returns_200():
    response = client.get('/api/available-dates/?organization_id=2')
    assert response.status_code == 200
    assert 'dates' in response.json()

# Test de middleware skip
def test_middleware_skips_api_routes():
    request = RequestFactory().get('/api/test/')
    middleware = FeatureAccessMiddleware()
    result = middleware.process_request(request)
    assert result is None  # Debe retornar None (skip)

# Test de configuración mínima
def test_organization_has_minimum_dates():
    org = Organization.objects.get(id=2)
    dates_count = SpecificDateSchedule.objects.filter(
        organization=org,
        date__gte=date.today(),
        is_active=True
    ).count()
    assert dates_count >= 30  # Mínimo 30 días disponibles
```

---

## 🔗 ERRORES RELACIONADOS

### Errores Similares en el Pasado
- **15 Ene 2026:** Error en notificaciones WhatsApp (import error)
- **14 Ene 2026:** Problema de desconexión persistente WhatsApp
- **08 Ene 2026:** Middleware de mensajes en contextos incorrectos

### Documentación Relacionada
- [ERRORES_SOLUCIONADOS_15ENE2026.md](./ERRORES_SOLUCIONADOS_15ENE2026.md)
- [FIX_BOOKING_16ENE2026.md](./FIX_BOOKING_16ENE2026.md)
- [PROTECCIONES_WHATSAPP_ANTI_BLOQUEO.md](./PROTECCIONES_WHATSAPP_ANTI_BLOQUEO.md)

---

## 📞 CONTACTO Y ESCALAMIENTO

### Nivel 1 - Errores de Configuración
- Verificar con scripts de diagnóstico
- Ejecutar scripts de población de datos
- Reiniciar servicios si es necesario

### Nivel 2 - Errores de Código
- Revisar logs: `pm2 logs opticaapp --lines 200`
- Buscar stack traces completos
- Aplicar fixes y hacer deployment

### Nivel 3 - Errores Críticos de Sistema
- Contactar a DevOps
- Revisar estado de base de datos
- Considerar rollback si es necesario

---

## ✅ ESTADO ACTUAL DEL SISTEMA

**Fecha:** 16 Enero 2026, 19:00  
**Estado General:** 🟢 OPERATIVO  

### Componentes
```
✅ Booking API:        FUNCIONANDO
✅ Frontend Booking:   FUNCIONANDO
✅ Base de Datos:      SALUDABLE
✅ Middleware:         CORREGIDO
✅ CompuEasys2:        52 fechas disponibles
✅ Oceano Optico:      2 fechas disponibles
⚠️  Optica Demo:       0 fechas (pendiente configurar)
```

### Próximas Acciones
1. Configurar fechas para Optica Demo
2. Implementar monitoring de APIs con alertas
3. Agregar tests automatizados para middleware
4. Crear dashboard de salud de organizaciones

---

**Documento actualizado:** 16 Enero 2026, 19:00  
**Próxima revisión:** 17 Enero 2026  
**Responsable:** Daniel Osorio / GitHub Copilot
