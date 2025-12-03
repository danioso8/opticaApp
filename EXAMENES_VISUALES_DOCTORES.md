# Sistema de Exámenes Visuales y Gestión de Doctores

## Descripción General

El sistema ahora permite gestionar múltiples exámenes visuales (historias clínicas) para cada paciente y asociar cada examen con un doctor/optómetra específico de la organización.

## Características Implementadas

### 1. **Gestión de Doctores/Optómetras**

#### Módulo Completo de Doctores
- **Crear Doctores**: Formulario completo con 5 tabs (Información Básica, Profesional, Contacto, Horarios, Adicional)
- **Listar Doctores**: Vista con cards modernas mostrando foto, especialidad, contacto y horarios
- **Ver Perfil**: Detalle completo del doctor con toda su información
- **Editar**: Actualizar información del doctor
- **Eliminar**: Desactivación suave (soft delete) para mantener historial

#### Información del Doctor
- **Personal**: Nombre completo, identificación, especialidad, foto
- **Profesional**: Tarjeta profesional, RETHUS, fecha de graduación, universidad, firma digital
- **Contacto**: Email, teléfono fijo, celular, dirección
- **Horarios**: Configuración semanal (Lunes a Domingo)
- **Adicional**: Biografía profesional, notas internas

### 2. **Asociación Doctor-Examen Visual**

#### Cambios en el Modelo
- El campo `doctor` en `ClinicalHistory` ahora es un **ForeignKey** al modelo `Doctor`
- Permite asociar cada examen visual con un doctor registrado en la organización
- Relación: Un doctor puede tener múltiples historias clínicas
- Si se elimina un doctor, las historias clínicas mantienen la referencia (SET_NULL)

#### Formulario de Historia Clínica
- **Dropdown de Doctores**: Selector con todos los doctores activos de la organización
- **Información Visible**: Muestra nombre completo, especialidad y tarjeta profesional
- **Validación**: Campo obligatorio para garantizar trazabilidad
- **Alertas**: Mensaje si no hay doctores registrados con enlace directo para crear uno

### 3. **Múltiples Exámenes por Paciente**

#### ¿Cómo Crear Múltiples Exámenes?

1. **Acceso al Paciente**
   - Ve a "Pacientes" en el sidebar
   - Selecciona el paciente
   - Dirígete a la pestaña "Exámenes Visuales"

2. **Crear Nuevo Examen**
   - Click en "Nuevo Examen" en la sección de exámenes visuales
   - Completa el formulario:
     - Selecciona la fecha del examen
     - **Selecciona el doctor** que realizó el examen (obligatorio)
     - Completa los datos del examen (anamnesis, refracción, diagnóstico, etc.)
   - Guarda el examen

3. **Historial de Exámenes**
   - Todos los exámenes se muestran en orden cronológico (más reciente primero)
   - Cada examen muestra:
     - Fecha del examen
     - Doctor que lo realizó
     - Resumen de refracción (OD/OS)
     - Motivo de consulta
   - Puedes ver, editar o eliminar cada examen individualmente

#### Renovación de Fórmula Anual

**Flujo Típico:**
1. Paciente vuelve después de un año
2. Creas un nuevo examen visual desde la pestaña "Exámenes Visuales"
3. Seleccionas el doctor actual (puede ser el mismo u otro)
4. Completas los nuevos datos del examen
5. El sistema mantiene todo el historial:
   - Examen del año anterior
   - Examen actual
   - Y todos los exámenes futuros

**Ventajas:**
- ✅ Historial completo de cambios en la visión del paciente
- ✅ Comparación entre exámenes anteriores y actuales
- ✅ Trazabilidad de qué doctor realizó cada examen
- ✅ Seguimiento de evolución de fórmulas
- ✅ Datos para análisis estadísticos

### 4. **Visualización en el Perfil del Paciente**

#### Pestaña "Exámenes Visuales"
Muestra todos los exámenes del paciente con:
- **Badge de tipo**: "Examen Visual"
- **Doctor**: Nombre del doctor que realizó el examen
- **Fecha**: Fecha del examen
- **Resumen de Refracción**: Fórmula OD y OS en formato compacto
- **Motivo**: Resumen del motivo de consulta
- **Acciones**: Ver detalle, editar, eliminar

#### Detalle del Examen
Cuando ves el detalle de un examen, se muestra:
- Nombre completo del doctor
- Especialidad del doctor
- Tarjeta profesional del doctor
- Toda la información del examen visual completo

## Uso del Sistema

### Para Crear un Doctor

1. Ve a "Doctores / Optómetras" en el sidebar
2. Click en "Nuevo Doctor"
3. Completa los tabs:
   - **Básica**: Nombre, identificación, especialidad
   - **Profesional**: Credenciales (T.P, RETHUS), universidad, firma, foto
   - **Contacto**: Email, teléfonos, dirección
   - **Horarios**: Días y horarios de atención
   - **Adicional**: Biografía y notas internas
4. Click en "Crear Doctor"

### Para Crear un Examen Visual

1. Ve a "Pacientes" → Selecciona el paciente
2. Pestaña "Exámenes Visuales"
3. Click en "Nuevo Examen"
4. **Selecciona el doctor** del dropdown (obligatorio)
5. Completa el formulario del examen:
   - Motivo de consulta
   - Síntomas
   - Antecedentes
   - Agudeza visual
   - Refracción (fórmula)
   - Queratometría
   - Tonometría
   - Biomicroscopía
   - Fondo de ojo
   - Diagnóstico
   - Tratamiento
   - Seguimiento
6. Click en "Guardar Historia Clínica"

### Para Ver Historial de Exámenes

1. Accede al perfil del paciente
2. Pestaña "Exámenes Visuales"
3. Verás todos los exámenes en orden cronológico
4. Click en "Ver Detalle" para ver el examen completo
5. Puedes comparar diferentes exámenes para ver evolución

## Estructura de la Base de Datos

### Tabla: Doctor
```
- id (Primary Key)
- organization (ForeignKey a Organization)
- full_name (CharField)
- identification (CharField)
- specialty (CharField con choices: optometrist, ophthalmologist, general, other)
- professional_card (CharField)
- rethus (CharField)
- graduation_date (DateField)
- university (CharField)
- email (EmailField)
- phone (CharField)
- mobile (CharField)
- address (TextField)
- monday_schedule - sunday_schedule (CharField)
- signature (ImageField)
- photo (ImageField)
- bio (TextField)
- notes (TextField)
- is_active (BooleanField)
- created_at (DateTimeField)
- updated_at (DateTimeField)
```

### Tabla: ClinicalHistory
```
- id (Primary Key)
- organization (ForeignKey a Organization)
- patient (ForeignKey a Patient)
- doctor (ForeignKey a Doctor, null=True, SET_NULL)
- date (DateField)
- ... (todos los campos del examen visual)
- created_at (DateTimeField)
- updated_at (DateTimeField)
```

### Relaciones
- Un paciente puede tener **múltiples** historias clínicas (exámenes)
- Cada historia clínica está asociada a **un solo doctor**
- Un doctor puede tener **múltiples** historias clínicas
- Si se elimina un doctor, las historias clínicas **mantienen** la referencia (no se eliminan)

## Migraciones Aplicadas

1. **0006_auto_20251202_1909.py**: Creación del modelo Doctor con índices
2. **0007_alter_clinicalhistory_doctor.py**: Cambio del campo doctor de CharField a ForeignKey

## URLs Implementadas

### Doctores
- `/dashboard/doctors/` - Lista de doctores
- `/dashboard/doctors/create/` - Crear doctor
- `/dashboard/doctors/<id>/` - Detalle del doctor
- `/dashboard/doctors/<id>/edit/` - Editar doctor
- `/dashboard/doctors/<id>/delete/` - Eliminar (desactivar) doctor

### Historias Clínicas
- `/dashboard/patients/<patient_id>/clinical-history/` - Lista de exámenes del paciente
- `/dashboard/patients/<patient_id>/clinical-history/create/` - Crear examen
- `/dashboard/patients/<patient_id>/clinical-history/<history_id>/` - Detalle del examen
- `/dashboard/patients/<patient_id>/clinical-history/<history_id>/edit/` - Editar examen
- `/dashboard/patients/<patient_id>/clinical-history/<history_id>/delete/` - Eliminar examen

## Casos de Uso Comunes

### Caso 1: Paciente Nueva
1. Crea el paciente
2. Crea el primer examen visual
3. Selecciona el doctor que lo atendió
4. Completa los datos del examen
5. Guarda

### Caso 2: Renovación Anual de Fórmula
1. Busca el paciente existente
2. Ve a "Exámenes Visuales"
3. Click en "Nuevo Examen" (mantiene los anteriores)
4. Selecciona el doctor (puede ser el mismo u otro)
5. Completa el nuevo examen
6. El historial anterior se preserva automáticamente

### Caso 3: Cambio de Doctor
1. Si un paciente cambia de doctor
2. Al crear el nuevo examen, simplemente selecciona el nuevo doctor
3. El historial muestra qué doctor atendió cada examen
4. Trazabilidad completa

### Caso 4: Comparar Exámenes Anteriores
1. Accede al paciente
2. Pestaña "Exámenes Visuales"
3. Abre diferentes exámenes en pestañas del navegador
4. Compara refracción, diagnósticos, tratamientos
5. Identifica cambios y evolución

## Validaciones Implementadas

- ✅ Campo doctor es obligatorio en el formulario
- ✅ Solo se muestran doctores activos de la organización
- ✅ Si no hay doctores, aparece mensaje con enlace para crear
- ✅ Multi-tenancy: Solo doctores de la misma organización
- ✅ Soft delete: Doctores desactivados no se eliminan físicamente

## Próximas Mejoras Sugeridas

1. **Filtros en Lista de Exámenes**: Por fecha, doctor, diagnóstico
2. **Comparador de Exámenes**: Vista lado a lado de dos exámenes
3. **Estadísticas por Doctor**: Cantidad de exámenes, tipos de diagnósticos más comunes
4. **Notificaciones de Seguimiento**: Alertas cuando se acerca la fecha de seguimiento
5. **Exportación de Historial**: PDF con todos los exámenes del paciente
6. **Plantillas de Examen**: Copiar datos de examen anterior para agilizar
7. **Firma Digital en Examen**: Integrar la firma del doctor en el PDF del examen

## Notas Técnicas

- El sistema usa multi-tenancy: Cada organización tiene sus propios doctores y pacientes
- Los doctores se pueden desactivar pero no eliminar para mantener historial
- La fecha del examen puede ser diferente a la fecha de creación del registro
- El formulario usa tabs para organizar la gran cantidad de campos del examen visual
- Las imágenes (foto y firma del doctor) se guardan en media/doctors/

## Soporte

Para más información sobre el uso del sistema, consulta:
- `GUIA_USO_SAAS.md` - Guía general del sistema SaaS
- `PROJECT_SUMMARY.md` - Resumen técnico del proyecto
- `TESTING.md` - Guías de prueba
