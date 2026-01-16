# FIX SISTEMA DE BOOKING - 16 ENERO 2026

## 📋 RESUMEN EJECUTIVO

**Problema:** Sistema de agendamiento de citas mostraba "Error al cargar las fechas" en producción  
**Causa raíz:** Error 500 en endpoint `/api/available-dates/` por conflicto de middleware  
**Estado:** ✅ RESUELTO  
**Fecha:** 16 de Enero 2026  

---

## 🔍 DIAGNÓSTICO

### Síntomas Reportados
- Usuario reportó: "danioso8329 no está mostrando el horario, dice error al cargar la fecha"
- Página funcional: Oceano Optico (https://optikaapp.com/oceano-optico/agendar/)
- Página con error: CompuEasys/La Casa Logística (https://optikaapp.com/la-casa-logistica/agendar/)

### Error en Consola del Navegador
```javascript
Network error: {
  type: 'NetworkError', 
  message: 'HTTP 500: Internal Server Error - /api/available-dates/?organization_id=5&doctor_id=8',
  url: 'https://www.optikaapp.com/la-casa-logistica/agendar/'
}

Error: SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON
```

### Análisis de Logs del Servidor
```python
Internal Server Error: /api/available-dates/
Traceback (most recent call last):
  File "django/contrib/messages/api.py", line 27, in add_message
    messages = request._messages
    AttributeError: 'WSGIRequest' object has no attribute '_messages'

During handling of the above exception, another exception occurred:
  File "apps/organizations/middleware.py", line 301, in process_request
    messages.warning(
      request,
      f'🔒 "{feature_name}" no está disponible en tu plan actual.'
    )
  django.contrib.messages.api.MessageFailure: 
    You cannot add messages without installing 
    django.contrib.messages.middleware.MessageMiddleware
```

---

## 🎯 CAUSA RAÍZ

### Problema Identificado

El **FeatureAccessMiddleware** en `apps/organizations/middleware.py` estaba procesando **TODAS las peticiones**, incluyendo las APIs públicas (`/api/*`).

Cuando intentaba verificar permisos y mostrar mensajes de advertencia usando `messages.warning()`, fallaba porque:

1. Los endpoints API **no tienen** `MessageMiddleware` configurado
2. Los endpoints API **no necesitan** el sistema de mensajes de Django
3. El middleware asumía que todas las peticiones tenían contexto de mensajes

### Código Problemático (Línea 301)

```python
# apps/organizations/middleware.py - ANTES
def process_request(self, request):
    """Verifica si el usuario tiene acceso a la característica"""
    
    # Saltar verificación para URLs exentas
    if any(request.path.startswith(url) for url in self.EXEMPT_URLS):
        return None
    
    # ... verificaciones ...
    
    if not has_module_access(request.user, required_feature):
        # ❌ ESTO FALLA EN APIs - No tienen MessageMiddleware
        messages.warning(
            request,
            f'🔒 "{feature_name}" no está disponible en tu plan actual.'
        )
        return redirect(reverse('dashboard:home'))
```

### Impacto

- ❌ **Error 500** en todos los endpoints `/api/available-dates/`
- ❌ **Error 500** en `/api/available-slots/`
- ❌ **Booking completamente bloqueado** en producción
- ❌ **Experiencia de usuario rota** - no podían agendar citas

---

## ✅ SOLUCIÓN IMPLEMENTADA

### 1. Fix del Middleware

Agregada verificación para **ignorar todas las rutas API** antes de cualquier procesamiento:

```python
# apps/organizations/middleware.py - DESPUÉS
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

### 2. Configuración de Fechas en Producción

**Problema secundario detectado:** CompuEasys2 solo tenía 1 fecha disponible

```bash
# Organizaciones en Contabo (antes):
2 - compueasys2 - CompuEasys - Activa: True - Fechas: 1
4 - oceano-optico - OCÉANO ÓPTICO - Activa: True - Fechas: 2
3 - optica-demo - Óptica Demo - Activa: True - Fechas: 0
```

**Solución:** Script `setup_compueasys2_dates.py`

```python
# Crear fechas para próximos 60 días (Lunes a Sábado)
schedules = [
    {'day': 0, 'start': '08:00', 'end': '12:00', 'slot': 30},  # Lunes
    {'day': 1, 'start': '08:00', 'end': '12:00', 'slot': 30},  # Martes
    {'day': 2, 'start': '08:00', 'end': '12:00', 'slot': 30},  # Miércoles
    {'day': 3, 'start': '08:00', 'end': '12:00', 'slot': 30},  # Jueves
    {'day': 4, 'start': '08:00', 'end': '12:00', 'slot': 30},  # Viernes
    {'day': 5, 'start': '09:00', 'end': '13:00', 'slot': 30},  # Sábado
]

# Resultado: 52 fechas creadas
```

---

## 🚀 PROCESO DE DEPLOYMENT

### Pasos Ejecutados

1. **Diagnóstico en Local**
   ```bash
   python check_duplicate_compueasys.py
   # Resultado: No duplicados en local
   ```

2. **Verificación en Producción (Contabo)**
   ```bash
   scp check_orgs_contabo.py root@84.247.129.180:/var/www/opticaapp/
   ssh root@84.247.129.180 "cd /var/www/opticaapp && source venv/bin/activate && python check_orgs_contabo.py"
   # Resultado: CompuEasys2 con solo 1 fecha
   ```

3. **Creación de Fechas**
   ```bash
   scp setup_compueasys2_dates.py root@84.247.129.180:/var/www/opticaapp/
   ssh root@84.247.129.180 "cd /var/www/opticaapp && source venv/bin/activate && python setup_compueasys2_dates.py"
   # Resultado: 52 fechas creadas
   ```

4. **Actualización del Middleware**
   ```bash
   scp apps/organizations/middleware.py root@84.247.129.180:/var/www/opticaapp/apps/organizations/middleware.py
   ```

5. **Restart de la Aplicación**
   ```bash
   ssh root@84.247.129.180 'pm2 restart opticaapp'
   # Resultado: ✅ Aplicación reiniciada exitosamente
   ```

---

## 📊 RESULTADOS

### Antes del Fix
```
❌ API /api/available-dates/ → Error 500
❌ Booking CompuEasys2 → "Error al cargar las fechas"
⚠️  CompuEasys2 → Solo 1 fecha disponible
✅ Oceano Optico → Funcionando (2 fechas)
```

### Después del Fix
```
✅ API /api/available-dates/ → HTTP 200
✅ Booking CompuEasys2 → Funcionando correctamente
✅ CompuEasys2 → 52 fechas disponibles (próximos 60 días)
✅ Oceano Optico → Funcionando (2 fechas)
✅ Sistema de agendamiento 100% operativo
```

---

## 📁 ARCHIVOS MODIFICADOS

### Core Fix
- **apps/organizations/middleware.py**
  - Agregada verificación `if request.path.startswith('/api/'):`
  - Previene uso de `messages.warning()` en contextos API
  - Línea agregada: 268

### Scripts de Diagnóstico
- **check_orgs_contabo.py** - Verificación de organizaciones en producción
- **diagnose_danioso_booking.py** - Diagnóstico de configuración de booking
- **setup_compueasys2_dates.py** - Script para crear fechas en producción
- **check_duplicate_compueasys.py** - Verificación de organizaciones duplicadas

### APIs Afectadas
- `/api/available-dates/` - ✅ Funcionando
- `/api/available-slots/` - ✅ Funcionando
- `/api/book/` - ✅ Funcionando

---

## 🧪 TESTING

### Pruebas Realizadas

1. **Test de API en Producción**
   ```bash
   curl https://optikaapp.com/api/available-dates/?organization_id=2
   # Resultado: HTTP 200 - JSON con fechas disponibles
   ```

2. **Test de Booking Web**
   - URL: https://optikaapp.com/la-casa-logistica/agendar/
   - Resultado: ✅ Fechas cargadas correctamente
   - Calendario muestra 52 fechas disponibles

3. **Verificación de Logs**
   ```bash
   ssh root@84.247.129.180 "pm2 logs opticaapp --lines 50"
   # Resultado: Sin errores 500 en /api/available-dates/
   ```

---

## 🔐 LECCIONES APRENDIDAS

### Buenas Prácticas Implementadas

1. **Separación de Concerns**
   - Los middlewares de autenticación/autorización NO deben procesar rutas API públicas
   - Las APIs REST no necesitan el sistema de mensajes de Django

2. **Order of Checks**
   ```python
   # Orden correcto de verificaciones en middleware:
   1. Verificar si es ruta API → return None
   2. Verificar URLs exentas → return None
   3. Verificar autenticación → return None
   4. Verificar permisos específicos
   ```

3. **Error Handling en APIs**
   - Las APIs deben manejar errores en formato JSON
   - No usar `messages.warning()` en contextos API
   - Retornar respuestas apropiadas (Response con status codes)

### Mejoras para el Futuro

1. **Monitoring**
   - Implementar alertas para errores 500 en APIs críticas
   - Dashboard de salud de endpoints de booking

2. **Testing**
   - Tests automatizados para endpoints API públicos
   - Tests de integración del flujo de booking completo

3. **Documentation**
   - Documentar qué middlewares aplican a qué rutas
   - Documentar APIs públicas vs protegidas

---

## 📞 SOPORTE

### URLs de Booking en Producción

- **CompuEasys2:** https://optikaapp.com/booking/compueasys2
- **La Casa Logística:** https://optikaapp.com/la-casa-logistica/agendar/
- **Oceano Optico:** https://optikaapp.com/oceano-optico/agendar/

### Endpoints API

```
GET /api/available-dates/?organization_id={id}&doctor_id={id}
GET /api/available-slots/?organization_id={id}&date={YYYY-MM-DD}&doctor_id={id}
POST /api/book/
```

### Comandos Útiles en Producción

```bash
# Verificar organizaciones y fechas
ssh root@84.247.129.180 "cd /var/www/opticaapp && source venv/bin/activate && python check_orgs_contabo.py"

# Ver logs en tiempo real
ssh root@84.247.129.180 "pm2 logs opticaapp"

# Reiniciar aplicación
ssh root@84.247.129.180 "pm2 restart opticaapp"

# Crear fechas para organización
ssh root@84.247.129.180 "cd /var/www/opticaapp && source venv/bin/activate && python setup_compueasys2_dates.py"
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

- [x] Error 500 en /api/available-dates/ resuelto
- [x] Middleware actualizado con skip de rutas API
- [x] 52 fechas creadas para CompuEasys2
- [x] Aplicación reiniciada en producción
- [x] Booking funcional verificado en navegador
- [x] Logs sin errores críticos
- [x] Código subido a repositorio (commit 0f5d232)
- [x] Documentación creada
- [x] Scripts de diagnóstico documentados

---

**Desarrollado por:** GitHub Copilot + Daniel Osorio  
**Fecha:** 16 de Enero 2026  
**Commit:** 0f5d232 - Fix: Error 500 en API de booking  
**Estado:** ✅ PRODUCCIÓN - FUNCIONANDO
