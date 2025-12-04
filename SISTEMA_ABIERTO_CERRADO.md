# 🔄 Sistema Abierto/Cerrado - Guía de Uso

## ¿Qué es el Sistema Abierto/Cerrado?

El **botón de Sistema Abierto/Cerrado** es un control ubicado en el header del dashboard que permite **activar o desactivar el sistema de agendamiento de citas** de forma inmediata.

### Ubicación
- **Desktop**: Se encuentra en la parte superior derecha del dashboard, al lado de la fecha actual
- **Mobile**: Visible en el header móvil
- **Indicador visual**: Toggle switch con texto de estado

---

## 🟢 Sistema ABIERTO (Verde)

Cuando el sistema está **ABIERTO**:

### ✅ Lo que funciona:
1. **Agendamiento de Citas**
   - Los pacientes PUEDEN agendar citas desde la página de reservas
   - Se muestran todos los horarios disponibles
   - Las confirmaciones de cita se envían normalmente

2. **Visualización**
   - Toggle en color **verde** (bg-green-500)
   - Texto muestra: **"Abierto"** en verde
   - Punto del switch desplazado a la derecha

3. **Notificaciones**
   - WhatsApp y email funcionan normalmente
   - Recordatorios de citas activos

### Casos de uso:
- ✅ Horario de atención normal
- ✅ Días laborales habituales
- ✅ Cuando hay disponibilidad de agenda

---

## 🔴 Sistema CERRADO (Rojo)

Cuando el sistema está **CERRADO**:

### ❌ Lo que NO funciona:
1. **Agendamiento Bloqueado**
   - Los pacientes NO pueden agendar citas nuevas
   - La página de reservas muestra mensaje: "Sistema temporalmente cerrado"
   - No se muestran horarios disponibles

2. **Visualización**
   - Toggle en color **gris** (bg-gray-300)
   - Texto muestra: **"Cerrado"** en rojo
   - Punto del switch en posición izquierda

### ✅ Lo que SÍ funciona (cuando está cerrado):
- Ver citas existentes en el calendario
- Modificar citas desde el panel de administración
- Las notificaciones de citas ya programadas se siguen enviando
- Acceso completo al dashboard administrativo

### Casos de uso para CERRAR el sistema:
- 🏥 **Días festivos o feriados**
- 🔧 **Mantenimiento de la agenda**
- 👨‍⚕️ **Ausencia del médico/optómetra**
- 📅 **Agenda completa sin disponibilidad**
- 🚨 **Emergencias que requieren cerrar temporalmente**
- 🏖️ **Vacaciones programadas**

---

## 🎯 ¿Cómo Funciona?

### Cambiar el Estado
1. Hacer clic en el toggle switch
2. El sistema cambia instantáneamente (no requiere guardar)
3. Se muestra una notificación de confirmación
4. Los cambios aplican inmediatamente para todos los usuarios

### Proceso Técnico
```javascript
// Al hacer clic en el toggle
toggleSystem() → 
  POST /toggle-system/ → 
    Actualiza AppointmentConfiguration.is_open → 
      Notifica en tiempo real → 
        UI se actualiza automáticamente
```

### Persistencia
- El estado se guarda en la base de datos
- Permanece así hasta que se vuelva a cambiar manualmente
- No se cierra automáticamente (excepto por fechas bloqueadas)

---

## 📊 Diferencia entre Sistema Cerrado y Fechas Bloqueadas

| Característica | Sistema Cerrado | Fecha Bloqueada |
|---------------|-----------------|-----------------|
| **Alcance** | TODO el sistema | Solo una fecha específica |
| **Duración** | Indefinida hasta cambio manual | Solo el día especificado |
| **Control** | Toggle único | Múltiples fechas pueden bloquearse |
| **Uso** | Cierre general/emergencias | Días específicos (festivos, ausencias) |
| **Prioridad** | Más alta | Se suma al sistema cerrado |

### Ejemplo:
- Si el sistema está **ABIERTO** pero hay una **fecha bloqueada** el 25/12/2025:
  - ❌ No se pueden agendar citas para el 25/12/2025
  - ✅ Sí se pueden agendar para otros días

- Si el sistema está **CERRADO**:
  - ❌ No se pueden agendar citas en NINGUNA fecha
  - (Las fechas bloqueadas ya no son necesarias porque todo está bloqueado)

---

## 🛠️ Recomendaciones de Uso

### ✅ Mejores Prácticas

1. **Planificación**
   - Usar **fechas bloqueadas** para cierres programados conocidos
   - Usar **sistema cerrado** solo para cierres generales o emergencias

2. **Comunicación**
   - Avisar a los pacientes antes de cerrar el sistema
   - Colocar mensaje en página de reservas indicando cuándo reabrirá

3. **Horarios de Trabajo**
   - Configurar bien los horarios de trabajo en lugar de abrir/cerrar constantemente
   - El sistema automáticamente no muestra horarios fuera del horario laboral

4. **Mantenimiento Temporal**
   - Cerrar el sistema brevemente si necesita hacer ajustes en la configuración
   - Reabrir inmediatamente después

### ❌ Evitar

1. ❌ Cerrar y abrir el sistema múltiples veces al día
   - Mejor usar configuración de horarios de trabajo
   
2. ❌ Cerrar por períodos cortos predecibles
   - Usar fechas bloqueadas específicas en su lugar

3. ❌ Olvidar reabrir después de mantenimiento
   - Configurar recordatorios si cierra temporalmente

---

## 🔔 Notificaciones en Tiempo Real

Cuando cambias el estado del sistema:

1. **WebSocket Notification**: 
   - Todos los administradores conectados reciben notificación
   - Se actualiza la UI automáticamente

2. **Mensaje en Dashboard**:
   - Toast notification: "Sistema abierto" (verde) o "Sistema cerrado" (rojo)

3. **Página Pública**:
   - La página de reservas se actualiza inmediatamente
   - Muestra u oculta el formulario de agendamiento

---

## 🧪 Verificar que Funciona

### Prueba Manual

1. **Estado Inicial**
   - Verifica el color del toggle (verde = abierto, gris = cerrado)
   - Lee el texto de estado

2. **Cambiar Estado**
   - Haz clic en el toggle
   - Deberías ver:
     - El switch cambiar de posición
     - El color cambiar
     - Una notificación de confirmación

3. **Verificar en Frontend Público**
   - Abre la página de reservas en otra pestaña
   - Con sistema abierto: formulario de agendamiento visible
   - Con sistema cerrado: mensaje "Sistema temporalmente cerrado"

4. **Verificar Persistencia**
   - Cierra la sesión y vuelve a entrar
   - El estado debería mantenerse como lo dejaste

### Endpoint API

```javascript
// Obtener estado actual
GET /api/configuration/
Response: { "is_open": true/false, ... }

// Cambiar estado
POST /toggle-system/
Response: { 
  "success": true, 
  "is_open": true/false, 
  "message": "Sistema abierto/cerrado" 
}
```

---

## 🎨 Indicadores Visuales

### Desktop
```
[Sistema: ] [🔘──] [Abierto]  ← Verde cuando está abierto
[Sistema: ] [──🔘] [Cerrado]  ← Rojo cuando está cerrado
```

### Estados del Toggle

| Estado | Color Fondo | Posición Punto | Texto | Color Texto |
|--------|-------------|----------------|-------|-------------|
| Abierto | Verde (#10b981) | Derecha | "Abierto" | Verde |
| Cerrado | Gris (#d1d5db) | Izquierda | "Cerrado" | Rojo |

---

## 💡 Casos de Uso Reales

### Ejemplo 1: Vacaciones de Fin de Año
```
Escenario: La óptica cierra del 24/12 al 2/01

Opción A (Recomendada):
- Bloquear fechas específicas: 24/12, 25/12, 26/12, 31/12, 1/01, 2/01
- Mantener sistema ABIERTO
- Ventaja: Pueden agendar para otras fechas de enero

Opción B (No recomendada):
- Cerrar sistema completamente
- Desventaja: No pueden agendar ni para fechas posteriores
```

### Ejemplo 2: Emergencia del Doctor
```
Escenario: El optómetra se enferma inesperadamente hoy

Acción:
1. CERRAR sistema inmediatamente
2. Colocar mensaje en página: "Sistema cerrado temporalmente. Disculpe las molestias"
3. Contactar a pacientes con citas de hoy
4. REABRIR cuando el doctor regrese
```

### Ejemplo 3: Configuración de Agenda Nueva
```
Escenario: Vas a modificar todos los horarios de trabajo

Acción:
1. CERRAR sistema
2. Realizar cambios en configuración
3. Probar que todo funciona
4. REABRIR sistema
```

---

## 📞 Preguntas Frecuentes

**P: ¿Las citas ya agendadas se cancelan al cerrar el sistema?**
R: No, las citas existentes permanecen. Solo se bloquea el agendamiento de nuevas citas.

**P: ¿Los recordatorios se envían si el sistema está cerrado?**
R: Sí, los recordatorios de citas ya programadas se siguen enviando normalmente.

**P: ¿Puedo ver el calendario si el sistema está cerrado?**
R: Sí, como administrador puedes ver y gestionar todas las citas desde el panel.

**P: ¿Cómo saben los pacientes que el sistema está cerrado?**
R: La página de reservas muestra un mensaje claro indicando que el sistema está temporalmente cerrado.

**P: ¿Puedo programar que se cierre automáticamente?**
R: Actualmente no, pero puedes usar fechas bloqueadas para días específicos conocidos.

---

## 🔧 Solución de Problemas

### El toggle no cambia
1. Verifica que estés autenticado
2. Comprueba que hay una organización activa
3. Revisa la consola del navegador por errores
4. Verifica que el endpoint `/toggle-system/` responde

### El estado no persiste
1. Verifica la conexión a base de datos
2. Comprueba que AppointmentConfiguration existe para tu organización
3. Revisa logs del servidor

### Los pacientes aún pueden agendar
1. Limpia caché del navegador
2. Verifica que el frontend esté consultando el endpoint correcto
3. Comprueba que no haya múltiples configuraciones

---

**Última actualización**: Diciembre 4, 2025
**Versión**: 1.0
