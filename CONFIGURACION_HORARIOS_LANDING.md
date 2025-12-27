# Configuración de Horarios en Landing Page

## Resumen de Cambios

Se ha implementado la funcionalidad para configurar los horarios de atención directamente desde el panel de administración de la landing page. Ahora puedes personalizar completamente los horarios que se muestran a tus clientes, incluyendo un horario especial para el almuerzo.

## Nuevas Características

### 1. Horarios Personalizables por Día

- **Lunes a Viernes**: Configura el horario de apertura y cierre para días laborables
- **Sábado**: Define horario específico para sábados
- **Domingo**: Opción de marcar como "Cerrado" o establecer horario específico

### 2. Horario de Almuerzo

- **Activar/Desactivar**: Puedes marcar si el negocio cierra para almorzar
- **Horario Flexible**: Define las horas de inicio y fin del almuerzo
- **Visualización Destacada**: El horario de almuerzo se muestra con un diseño especial en color amarillo

## Campos Agregados al Modelo

Los siguientes campos fueron agregados a `LandingPageConfig`:

```python
# Horarios de Atención
schedule_weekday_start = 'Hora de Inicio (Lunes-Viernes)'
schedule_weekday_end = 'Hora de Fin (Lunes-Viernes)'
schedule_saturday_start = 'Hora de Inicio (Sábado)'
schedule_saturday_end = 'Hora de Fin (Sábado)'
schedule_sunday_closed = 'Domingo Cerrado' (True/False)
schedule_sunday_start = 'Hora de Inicio (Domingo)'
schedule_sunday_end = 'Hora de Fin (Domingo)'

# Horario de Almuerzo
has_lunch_break = 'Cierra para Almorzar' (True/False)
lunch_break_start = 'Inicio del Almuerzo'
lunch_break_end = 'Fin del Almuerzo'
```

## Valores por Defecto

Los valores por defecto que se aplican a nuevas configuraciones son:

- **Lunes - Viernes**: 10:00 AM - 7:00 PM
- **Sábado**: 10:00 AM - 2:00 PM
- **Domingo**: Cerrado
- **Horario de Almuerzo**: Desactivado por defecto

## Cómo Configurar los Horarios

### Paso 1: Acceder al Panel de Administración

1. Inicia sesión en el panel de administración de Django
2. Navega a **Organizaciones** → **Configuraciones de Landing Page**

### Paso 2: Seleccionar la Configuración

1. Haz clic en la configuración de landing page que deseas editar
2. Busca la sección **"Horarios de Atención"**

### Paso 3: Configurar los Horarios

#### Horarios de Días Laborables

```
Hora de Inicio (Lunes-Viernes): 10:00 AM
Hora de Fin (Lunes-Viernes): 7:00 PM
```

#### Horarios de Sábado

```
Hora de Inicio (Sábado): 10:00 AM
Hora de Fin (Sábado): 2:00 PM
```

#### Horarios de Domingo

```
☑ Domingo Cerrado    ← Marca esta casilla si cierras los domingos
```

Si **NO** cierras los domingos, desmarca la casilla y configura:
```
Hora de Inicio (Domingo): 10:00 AM
Hora de Fin (Domingo): 2:00 PM
```

#### Horario de Almuerzo

Si tu negocio cierra para almorzar:

```
☑ Cierra para Almorzar    ← Marca esta casilla
Inicio del Almuerzo: 12:00 PM
Fin del Almuerzo: 1:00 PM
```

### Paso 4: Guardar los Cambios

Haz clic en el botón **"Guardar"** al final del formulario.

## Visualización en la Landing Page

Los horarios se muestran en la sección de contacto de la landing page con el siguiente formato:

```
┌─────────────────────────────────────────┐
│     Horarios de Atención                │
│─────────────────────────────────────────│
│ Lunes - Viernes    10:00 AM - 7:00 PM  │
│─────────────────────────────────────────│
│ 🍽️ Hora de Almuerzo  12:00 PM - 1:00 PM │  ← Aparece si está activado
│─────────────────────────────────────────│
│ Sábado             10:00 AM - 2:00 PM   │
│─────────────────────────────────────────│
│ Domingo            Cerrado              │
└─────────────────────────────────────────┘
```

## Ejemplos de Configuración

### Ejemplo 1: Horario sin Cierre de Almuerzo

```
Lunes - Viernes: 8:00 AM - 6:00 PM
Sábado: 9:00 AM - 1:00 PM
Domingo: Cerrado
Almuerzo: No cierra
```

### Ejemplo 2: Horario con Cierre de Almuerzo

```
Lunes - Viernes: 8:00 AM - 6:00 PM
Sábado: 9:00 AM - 1:00 PM
Domingo: Cerrado
Almuerzo: 12:00 PM - 2:00 PM
```

### Ejemplo 3: Abierto Todos los Días

```
Lunes - Viernes: 9:00 AM - 8:00 PM
Sábado: 10:00 AM - 6:00 PM
Domingo: 11:00 AM - 4:00 PM
Almuerzo: 1:00 PM - 2:00 PM
```

## Archivos Modificados

### 1. Modelo de Datos
- **Archivo**: `apps/organizations/models.py`
- **Cambios**: Agregados 10 nuevos campos al modelo `LandingPageConfig`

### 2. Migración de Base de Datos
- **Archivo**: `apps/organizations/migrations/0020_add_schedule_fields_to_landing_config.py`
- **Estado**: ✅ Aplicada exitosamente

### 3. Templates
- **Archivo**: `apps/public/templates/public/home.html`
- **Cambios**: Actualizado para mostrar horarios configurables con soporte para horario de almuerzo

- **Archivo**: `apps/public/templates/public/organization_landing.html`
- **Cambios**: Actualizado para mostrar horarios configurables con soporte para horario de almuerzo

### 4. Panel de Administración
- **Archivo**: `apps/organizations/admin.py`
- **Cambios**: Agregada sección "Horarios de Atención" en el formulario de configuración

## Script de Verificación

Se ha creado un script para verificar las configuraciones de horarios:

```bash
python verificar_horarios_landing.py
```

Este script muestra:
- Todas las configuraciones de landing page existentes
- Los horarios configurados para cada organización
- Si tienen horario de almuerzo activo
- Instrucciones sobre cómo cambiar los horarios

## Notas Técnicas

### Formato de Hora

Los horarios se almacenan como cadenas de texto (CharField) con el formato:
- Ejemplo: "10:00 AM", "7:00 PM", "12:30 PM"
- Máximo 10 caracteres

### Valores Nulos

- Los campos de domingo pueden estar vacíos si `schedule_sunday_closed=True`
- Los campos de almuerzo pueden estar vacíos si `has_lunch_break=False`

### Retrocompatibilidad

Las configuraciones existentes automáticamente reciben los valores por defecto al aplicar la migración. No es necesario actualizar manualmente las configuraciones antiguas.

## Preguntas Frecuentes

**Q: ¿Puedo tener diferentes horarios para cada día de la semana?**
A: Actualmente el sistema agrupa Lunes-Viernes. El Sábado y Domingo tienen configuración independiente.

**Q: ¿El horario de almuerzo aplica a todos los días?**
A: Sí, si activas el horario de almuerzo, se muestra como aplicable a todos los días de atención.

**Q: ¿Los cambios se reflejan inmediatamente?**
A: Sí, al guardar la configuración en el admin, los cambios se muestran de inmediato en la landing page.

**Q: ¿Puedo usar formato de 24 horas?**
A: Se recomienda usar formato de 12 horas con AM/PM para mejor legibilidad, pero puedes usar el formato que prefieras.

## Soporte

Si necesitas ayuda adicional o tienes preguntas sobre la configuración de horarios, contacta al equipo de desarrollo.

---

**Fecha de Implementación**: 27 de Diciembre de 2025  
**Versión**: 1.0  
**Estado**: ✅ Producción
