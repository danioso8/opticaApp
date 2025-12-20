# 📋 GUÍA RÁPIDA: Cómo Usar el Sistema de Exámenes Especiales

## 🎯 ACCESO RÁPIDO

### URLs Principales:
```
Dashboard de Exámenes: http://localhost:8000/dashboard/exam-orders/pending/
Lista de Órdenes:      http://localhost:8000/dashboard/exam-orders/
Crear Orden Nueva:     http://localhost:8000/dashboard/exam-order/create/
```

---

## 👨‍⚕️ PARA DOCTORES

### 1️⃣ Ordenar un Examen Desde Historia Clínica

**Opción A - Desde el menú:**
1. Ve a: **Dashboard → Historias Clínicas**
2. Busca el paciente y entra a su historia
3. Busca el botón **"Ordenar Examen Especial"**
4. Llena el formulario:
   - **Tipo de examen:** Selecciona (Tonometría, Retinografía, OCT, etc.)
   - **Prioridad:** 
     - Rutina (normal)
     - Urgente (atención prioritaria)
     - STAT (inmediato)
   - **Indicación clínica:** "Control de PIO", "Sospecha glaucoma", etc.
   - **Instrucciones especiales:** (opcional)
5. Click en **"Crear Orden"**
6. Se genera el PDF automáticamente → **Imprimir y dar al paciente**

**Opción B - Directa:**
```
http://localhost:8000/dashboard/exam-order/create/
```
- Selecciona paciente de la lista
- Sigue pasos 4-6

### 2️⃣ Ver Todas las Órdenes

```
http://localhost:8000/dashboard/exam-orders/
```

**Filtros disponibles:**
- Por estado (Pendiente, En Proceso, Completado)
- Por tipo de examen
- Búsqueda por nombre de paciente
- Ordenar por fecha/prioridad

### 3️⃣ Revisar Resultados

1. Ve a la lista de órdenes
2. Busca las que están **"Completado"** (verde)
3. Click en el nombre del paciente o "Ver Detalle"
4. Verás:
   - Datos del examen
   - Resultados ingresados
   - Imágenes (si aplica)
   - Interpretación
5. Click en **"Imprimir PDF"** para guardar en historia física

---

## 🔬 PARA TÉCNICOS DE LABORATORIO

### 1️⃣ Ver Exámenes Pendientes (Dashboard)

```
http://localhost:8000/dashboard/exam-orders/pending/
```

**Lo que verás:**
```
┌─────────────────────────────────────────────────┐
│  📊 EXÁMENES PENDIENTES                         │
├─────────────────────────────────────────────────┤
│  🔴 Urgentes: 3                                 │
│  🟡 Pendientes: 15                              │
│  🟢 Hoy: 8                                       │
└─────────────────────────────────────────────────┘

LISTA ORDENADA POR PRIORIDAD:
┌──────────────┬──────────────┬──────────┬────────┐
│ Paciente     │ Examen       │ Prioridad│ Acción │
├──────────────┼──────────────┼──────────┼────────┤
│ Juan Pérez   │ Tonometría   │ URGENTE  │ [Ver]  │
│ Ana López    │ Retinografía │ Rutina   │ [Ver]  │
└──────────────┴──────────────┴──────────┴────────┘
```

### 2️⃣ Proceso Completo de un Examen

**PASO 1 - Paciente llega con la orden impresa:**
- Si no trae la orden, búscala en el dashboard
- Verifica que sea el paciente correcto

**PASO 2 - Marcar como "En Proceso":**
1. Click en "Ver Detalle" de la orden
2. Busca el botón **"Actualizar Estado"**
3. Cambia a: **"En Proceso"**
4. Esto saca la orden del dashboard de pendientes

**PASO 3 - Realizar el examen:**
- Ejecuta el procedimiento médico
- Toma las mediciones
- Si aplica, toma fotografías

**PASO 4 - Ingresar Resultados:**

#### 📌 Para TONOMETRÍA:
```
URL: http://localhost:8000/dashboard/tonometry/create/
```
1. Selecciona la orden del listado
2. Llena el formulario:
   - **OD (Ojo Derecho):** presión en mmHg (ej: 15)
   - **OI (Ojo Izquierdo):** presión en mmHg (ej: 14)
   - **Método:** Goldmann,Neumático, etc.
   - **Hora:** automático
   - **Observaciones:** cualquier nota relevante
3. Click **"Guardar"**

#### 📌 Para RETINOGRAFÍA:
```
URL: http://localhost:8000/dashboard/retinography/create/
```
1. Selecciona la orden
2. Llena campos:
   - **Hallazgos OD/OI:** describe lo observado
   - **Sube imágenes:**
     - Foto del ojo derecho (PNG/JPG)
     - Foto del ojo izquierdo (PNG/JPG)
   - **Calidad de imagen:** Excelente/Buena/Regular
3. Click **"Guardar"**

#### 📌 Para OCT:
```
URL: http://localhost:8000/dashboard/oct/create/
```
1. Selecciona la orden
2. Llena:
   - **Tipo de scan:** Mácula, Nervio óptico, etc.
   - **Grosor foveal:** en micras
   - **Sube imagen del OCT**
   - **Hallazgos:** descripción
3. Click **"Guardar"**

**PASO 5 - Imprimir Resultado:**
1. Después de guardar, aparece botón **"Imprimir PDF"**
2. Se genera PDF profesional con:
   - Logo de la clínica
   - Datos del paciente
   - Resultados
   - Tu firma digital
3. Imprime y entrega al paciente

**PASO 6 - Orden Completada:**
- El estado cambia automáticamente a **"Completado"**
- Desaparece del dashboard de pendientes
- El doctor ya puede ver los resultados

---

## 🔍 CASOS DE USO COMUNES

### Caso 1: Paciente Perdió la Orden
```
1. Ve al Dashboard: /exam-orders/pending/
2. Busca por nombre del paciente
3. Entra al detalle de la orden
4. Click en "Imprimir PDF"
5. Dale la nueva impresión
```

### Caso 2: Examen Urgente
```
1. En el dashboard, aparecen arriba en ROJO
2. Atiende primero estos
3. Marca como "En Proceso" inmediatamente
4. Realiza el examen
5. Ingresa resultados lo más rápido posible
```

### Caso 3: No Puedes Completar el Examen
```
1. Ve a la orden
2. Click "Actualizar Estado"
3. Cambia a "Pendiente" nuevamente
4. En "Observaciones" escribe el motivo
   (ej: "Paciente no pudo quedarse quieto")
5. Informa al doctor
```

### Caso 4: Error en los Datos Ingresados
```
1. Ve a la lista de órdenes
2. Busca la orden completada
3. Click en "Ver Detalle"
4. Busca el enlace "Editar Resultados"
5. Corrige los datos
6. Guarda nuevamente
```

---

## 📊 TIPOS DE EXÁMENES DISPONIBLES

### 1. **Tonometría** (Medición de Presión Intraocular)
- **Cuándo:** Control glaucoma, pacientes >40 años
- **Datos:** Presión OD/OI en mmHg
- **Normal:** 10-21 mmHg
- **Alerta:** >21 mmHg (posible glaucoma)

### 2. **Retinografía** (Fotografía del Fondo de Ojo)
- **Cuándo:** Diabetes, hipertensión, glaucoma
- **Datos:** Imágenes + descripción hallazgos
- **Upload:** 2 fotos (OD + OI)

### 3. **OCT** (Tomografía de Coherencia Óptica)
- **Cuándo:** DMAE, edema macular, glaucoma
- **Datos:** Grosor retinal, imágenes
- **Precisión:** Hasta micras

### 4. **Motilidad Ocular**
- **Cuándo:** Estrabismo, parálisis, niños
- **Datos:** Movimientos en 8 direcciones
- **Resultado:** Normal/Anormal por dirección

### 5. **Otros (en código, no en BD aún):**
- Campo Visual
- Topografía Corneal
- Paquimetría
- Queratometría
- Visión de Colores

---

## 🎨 ESTADOS Y COLORES

```
🟡 PENDIENTE    → Amarillo → Esperando ser realizado
🔵 AGENDADO     → Azul    → Cita programada
🟠 EN PROCESO   → Naranja → Técnico realizándolo
🟢 COMPLETADO   → Verde   → Resultados listos
❌ CANCELADO    → Rojo    → No se realizó
```

---

## 🚀 TIPS PARA TRABAJAR EFICIENTEMENTE

### Para Doctores:
✅ Ordena el examen apenas lo identifiques en consulta  
✅ Sé específico en "Indicación clínica" para guiar al técnico  
✅ Marca URGENTE solo lo que realmente lo es  
✅ Revisa resultados el mismo día que se completan  

### Para Técnicos:
✅ Abre el Dashboard al inicio del día  
✅ Prioriza: STAT → Urgentes → Rutina  
✅ Marca "En Proceso" para que otros sepan que lo estás atendiendo  
✅ Sube imágenes en buena calidad (>800x600px)  
✅ Imprime el resultado inmediatamente después de guardar  
✅ Guarda las imágenes originales por si se necesitan después  

### General:
✅ Usa Chrome o Edge (mejor rendimiento para PDFs)  
✅ Ten impresora configurada antes de empezar  
✅ Si hay dudas en resultados, marca en Observaciones  
✅ Los PDFs se pueden reimprimir cuando sea necesario  

---

## ❓ PREGUNTAS FRECUENTES

**P: ¿Puedo editar una orden después de crearla?**  
R: Sí, entra al detalle y busca "Editar Orden"

**P: ¿Cómo cancelo un examen que no se va a realizar?**  
R: Cambia el estado a "Cancelado" y escribe el motivo

**P: ¿Se puede ver el historial de exámenes de un paciente?**  
R: Sí, en la Historia Clínica aparecen todos en orden cronológico

**P: ¿Los PDFs quedan guardados?**  
R: Se generan en tiempo real, pero puedes regenerarlos cuando quieras

**P: ¿Puedo subir más de 2 imágenes en retinografía?**  
R: Actualmente solo 2 (una por ojo), pero se puede ampliar

**P: ¿Qué pasa si subo una imagen muy grande?**  
R: Django la optimiza automáticamente

**P: ¿Puedo crear órdenes para exámenes que no están en la base de datos?**  
R: Sí, puedes seleccionar el tipo en la orden, pero no podrás ingresar resultados estructurados (solo en observaciones)

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### "No veo el botón Ordenar Examen"
- Verifica que tienes permiso de doctor
- Asegúrate de estar en una Historia Clínica válida

### "Error al subir imagen"
- Verifica que sea JPG o PNG
- Tamaño máximo: 5MB
- Renombra el archivo si tiene caracteres especiales

### "El PDF no se genera"
- Verifica que WeasyPrint esté instalado
- Revisa que el navegador permita popups
- Intenta con otro navegador

### "No aparecen los exámenes pendientes"
- Verifica que haya órdenes en estado "Pendiente"
- Refresca la página (F5)
- Revisa que estés en la organización correcta

---

## 📞 CONTACTO

Si tienes problemas técnicos o necesitas agregar funcionalidades:
- Revisar logs en: `D:\ESCRITORIO\OpticaApp\logs\`
- Documentación completa: `EXAMENES_ESPECIALES_COMPLETO.md`

---

**¡Sistema listo para usar! 🎉**

Comienza por el Dashboard de Pendientes:
```
http://localhost:8000/dashboard/exam-orders/pending/
```
