# Generación de PDF de Historia Clínica

## Descripción

Sistema implementado para generar reportes en PDF profesionales de las historias clínicas oftalmológicas, incluyendo gráficos de fondo de ojo y tablas detalladas con todos los datos del examen.

## Características Implementadas

### 1. Generación de PDF Profesional
- **Formato**: PDF con diseño profesional en tamaño carta
- **Estructura completa**: Incluye todas las secciones de la historia clínica
- **Encabezado y pie de página**: Con datos de la organización y paginación automática
- **Diseño organizado**: Secciones claramente diferenciadas con colores y estilos

### 2. Gráficos de Fondo de Ojo
- **Diagramas anatómicos**: Representación gráfica del ojo derecho (OD) y ojo izquierdo (OS)
- **Elementos visualizados**:
  - Disco óptico con excavación (copa)
  - Mácula
  - Vasos sanguíneos (arterias y venas)
  - Contorno del ojo
- **Colores anatómicos**: Representación realista con colores apropiados

### 3. Tablas de Datos Clínicos

#### Módulo de Refracción
- Esfera, Cilindro, Eje y Adición para ambos ojos
- Agudeza visual sin corrección (SC) y con corrección (CC)
- Distancia pupilar

#### Queratometría
- K1 y K2 con sus respectivos ejes para OD y OS

#### Presión Intraocular (PIO)
- Valores de PIO para ambos ojos
- Método de medición utilizado

#### Biomicroscopía
- Examen detallado del segmento anterior
- Párpados, conjuntiva, córnea, cámara anterior, iris, cristalino, pupila

#### Fondo de Ojo
- Vítreo, disco óptico, relación copa/disco, mácula, vasos, retina
- Gráficos anatómicos de ambos ojos

### 4. Secciones Completas

- **Anamnesis**: Motivo de consulta, enfermedad actual, antecedentes médicos, síntomas
- **Exámenes**: Refracción, queratometría, tonometría, biomicroscopía, fondo de ojo, motilidad
- **Diagnóstico**: Diagnóstico principal, diferencial y específicos
- **Pronóstico**: Expectativa de evolución del paciente
- **Manejo**: Plan de tratamiento, prescripciones, recomendaciones
- **Seguimiento**: Fecha de control y remisiones

### 5. Información del Paciente y Doctor
- Datos completos del paciente (nombre, identificación, edad, contacto)
- Información del doctor/optómetra que atendió
- Fecha del examen y número de historia clínica
- Firmas del profesional y paciente/acudiente

## Archivos Creados/Modificados

### Nuevos Archivos
1. **`apps/patients/pdf_utils.py`**
   - Utilidades para dibujo de gráficos de fondo de ojo
   - Funciones para crear tablas de refracción, queratometría y PIO
   - Canvas personalizado con encabezado y pie de página
   - Clases: `NumberedCanvas`, funciones: `draw_eye_fundus_diagram`, `draw_refraction_table`, etc.

### Archivos Modificados
1. **`apps/dashboard/views_clinical.py`**
   - Agregada función `clinical_history_pdf()`: Vista que genera el PDF completo
   - Importaciones necesarias de reportlab
   - Lógica completa para construir el documento PDF con todas las secciones

2. **`apps/dashboard/views.py`**
   - Importada la función `clinical_history_pdf` desde views_clinical

3. **`apps/dashboard/urls.py`**
   - Nueva URL: `/patients/<patient_id>/clinical-history/<history_id>/pdf/`
   - Nombre: `clinical_history_pdf`

4. **`apps/dashboard/templates/dashboard/patients/clinical_history_detail.html`**
   - Botón "Generar PDF" agregado en el header
   - Color rojo distintivo para el botón de PDF

5. **`apps/dashboard/templates/dashboard/patients/clinical_history_list.html`**
   - Botón "PDF" agregado en cada historia clínica de la lista
   - Acceso rápido para generar PDF desde el listado

6. **`requirements.txt`**
   - Agregada librería: `reportlab==4.0.7`

## Uso

### Desde el Detalle de Historia Clínica
1. Ir a la historia clínica de un paciente
2. Click en el botón "Generar PDF" (rojo con ícono de PDF)
3. El PDF se abrirá en una nueva pestaña o se descargará automáticamente

### Desde la Lista de Historias Clínicas
1. En la lista de historias de un paciente
2. Click en el botón "PDF" junto a cada historia
3. Se genera y descarga el PDF inmediatamente

## URL del Endpoint
```
/dashboard/patients/<patient_id>/clinical-history/<history_id>/pdf/
```

## Ejemplo de Uso Programático
```python
# En un template
<a href="{% url 'dashboard:clinical_history_pdf' patient.id history.id %}" 
   target="_blank">
    Generar PDF
</a>
```

## Estructura del PDF Generado

1. **Portada**
   - Título: "HISTORIA CLÍNICA DE OPTOMETRÍA"
   - Datos del paciente en tabla

2. **Anamnesis**
   - Motivo de consulta
   - Enfermedad actual
   - Antecedentes médicos
   - Síntomas presentes

3. **Módulo de Refracción**
   - Tabla completa con valores para OD y OS
   - Distancia pupilar

4. **Queratometría** (si aplica)
   - Tabla con K1 y K2 para ambos ojos

5. **Presión Intraocular** (si aplica)
   - Tabla con PIO y método

6. **Examen Externo** (si aplica)
   - Hallazgos para ambos ojos

7. **Biomicroscopía** (si aplica)
   - Tabla detallada del segmento anterior

8. **Fondo de Ojo** (nueva página)
   - Gráficos anatómicos de OD y OS
   - Tabla con hallazgos detallados

9. **Módulo Oculomotor** (si aplica)
   - Motilidad, cover test, convergencia

10. **Exámenes Complementarios** (si aplica)
    - OCT, campo visual, topografía, etc.

11. **Conclusiones**
    - Diagnóstico principal y diferencial
    - Diagnósticos específicos
    - Pronóstico

12. **Manejo y Observaciones**
    - Disposición y plan de tratamiento
    - Prescripciones (lentes, medicamentos)
    - Recomendaciones
    - Seguimiento y remisiones

13. **Firmas**
    - Espacio para firma del profesional
    - Espacio para firma del paciente/acudiente

## Dependencias

- **Django 3.2.25**: Framework web
- **ReportLab 4.0.7**: Generación de PDF
- **Pillow 9.5.0**: Procesamiento de imágenes (ya instalado)

## Características Técnicas

- **Tamaño de página**: Letter (8.5" x 11")
- **Márgenes**: 1 pulgada en todos los lados
- **Fuentes**: Helvetica y Helvetica-Bold
- **Colores**: Paleta profesional con azules, morados y grises
- **Paginación**: Automática con número de página
- **Encabezado**: Nombre de la organización en cada página
- **Pie de página**: Número de página y doctor que atendió

## Beneficios

1. **Profesionalismo**: Documento con formato profesional para entregar al paciente
2. **Gráficos visuales**: Diagramas de fondo de ojo facilitan la comprensión
3. **Completo**: Incluye todos los datos de la historia clínica
4. **Imprimible**: Listo para imprimir y archivar físicamente
5. **Legal**: Documento formal con firmas para archivo
6. **Portable**: Formato PDF universal, se abre en cualquier dispositivo
7. **Compartible**: Fácil de enviar por email o WhatsApp al paciente

## Futuras Mejoras Posibles

- [ ] Agregar logo de la organización en el encabezado
- [ ] Incluir imágenes de retinografías adjuntas
- [ ] Código QR para verificación del documento
- [ ] Firma digital electrónica
- [ ] Marca de agua con estado del documento
- [ ] Opción de idioma (inglés/español)
- [ ] Personalización de colores por organización
- [ ] Plantillas personalizables
- [ ] Exportación a otros formatos (Word, HTML)

## Notas de Implementación

- El PDF se genera dinámicamente cada vez que se solicita
- No se almacenan PDFs generados (se crean on-the-fly)
- Los gráficos de fondo de ojo se dibujan usando formas geométricas de reportlab
- El sistema maneja correctamente historias clínicas con datos incompletos
- Los campos opcionales solo aparecen si tienen datos
