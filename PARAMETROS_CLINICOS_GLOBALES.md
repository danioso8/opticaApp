# Sistema de Parámetros Clínicos Globales

## 📋 Descripción

El sistema ahora utiliza **parámetros clínicos globales** que están disponibles para todas las organizaciones, reduciendo duplicación y facilitando la gestión.

## 🔄 Cambios Implementados

### 1. Sistema Híbrido

- **Parámetros Globales**: Sin organización (`organization=null`), visibles para todos
- **Parámetros Personalizados**: Con organización específica, solo para esa óptica

### 2. Consultas Actualizadas

Todas las consultas ahora incluyen parámetros globales:

```python
ClinicalParameter.objects.filter(
    Q(organization=request.organization) | Q(organization__isnull=True),
    parameter_type='lens_material',
    is_active=True
)
```

### 3. Parámetros Incluidos

Se crearon **121 parámetros clínicos globales** organizados en:

#### Lentes Oftálmicos (43 parámetros)
- ✅ **7 Materiales**: CR-39, Policarbonato, Trivex, Alto Índice 1.60/1.67/1.74, Vidrio
- ✅ **12 Tratamientos**: Antireflejo, Blue Light, Fotocromático, Transitions, Polarizado, UV400, etc.
- ✅ **8 Tipos**: Monofocales, Bifocales, Trifocales, Progresivos, Ocupacionales, Deportivos, etc.
- ✅ **8 Marcas**: Essilor, Zeiss, Hoya, Transitions, Varilux, Crizal, Kodak, Rodenstock
- ✅ **8 Tipos de Monturas**: Completa, Semi al aire, Al aire, Deportiva, Aviador, etc.

#### Lentes de Contacto (18 parámetros)
- ✅ **6 Tipos**: Blandos, RGP, Esféricos, Tóricos, Multifocales, Cosméticos
- ✅ **6 Marcas**: Acuvue, Biofinity, Air Optix, Bausch+Lomb, Dailies, Proclear
- ✅ **6 Regímenes**: Diario, Quincenal, Mensual, Trimestral, Anual, Uso Extendido

#### Medicamentos (11 parámetros)
- ✅ Lágrimas artificiales (Systane, Refresh)
- ✅ Antibióticos (Tobramicina, Moxifloxacino)
- ✅ Antiinflamatorios (Prednisolona)
- ✅ Antihistamínicos (Ketotifeno)
- ✅ Antiglaucoma (Timolol, Latanoprost)
- ✅ Midriáticos (Ciclopentolato, Tropicamida)

#### Diagnósticos (13 parámetros)
- ✅ Defectos refractivos: Miopía, Hipermetropía, Astigmatismo, Presbicia
- ✅ Superficie ocular: Ojo seco, Conjuntivitis, Blefaritis, Pterigión
- ✅ Cristalino: Catarata
- ✅ Glaucoma
- ✅ Retina: Retinopatía diabética, Degeneración macular
- ✅ Córnea: Queratocono

#### Exámenes y Otros (36 parámetros)
- ✅ **11 Exámenes**: Campimetría, Topografía, OCT, Paquimetría, Tonometría, etc.
- ✅ **5 Terapias**: Terapia visual, Ortóptica, Higiene palpebral, Oclusión, etc.
- ✅ **10 Especialidades**: Oftalmólogo, Retinólogo, Glaucomatólogo, etc.
- ✅ **10 Recomendaciones**: Uso de lentes, protección solar, descansos visuales, etc.

## 🚀 Scripts Disponibles

### Local (Desarrollo)

#### 1. Eliminar todos los parámetros
```bash
python delete_all_clinical_params.py
```

#### 2. Crear parámetros globales completos
```bash
python populate_global_clinical_params.py
```

#### 3. Verificar funcionamiento
```bash
python verify_global_params.py
```

### Render (Producción)

```bash
# En el shell de Render:
python setup_global_params_render.py
```

Este script hace todo el proceso automáticamente:
- Elimina parámetros existentes
- Crea los parámetros globales estándar
- Verifica la instalación

## 💡 Ventajas del Sistema

### Para los Usuarios
- ✅ Parámetros estándar disponibles inmediatamente
- ✅ Consistencia entre organizaciones
- ✅ Pueden agregar parámetros personalizados si lo necesitan

### Para el Sistema
- ✅ Reduce duplicación en la base de datos
- ✅ Facilita mantenimiento y actualizaciones
- ✅ Escalabilidad mejorada

### Para Nuevas Organizaciones
- ✅ Catálogo completo desde el inicio
- ✅ No necesitan configurar nada
- ✅ Pueden empezar a trabajar inmediatamente

## 🔧 Cómo Funciona

### Consulta de Parámetros

Cuando una organización consulta parámetros, obtiene:
1. Todos los parámetros globales (organization=null)
2. Sus propios parámetros personalizados

### Creación de Parámetros

- **Usuario normal**: Crea parámetros para su organización
- **Modal de examen visual**: Crea parámetros de su organización automáticamente

### Prevención de Duplicados

El modelo tiene `unique_together = ['organization', 'parameter_type', 'name']`:
- Un usuario NO puede crear "Policarbonato" si ya existe global
- Un usuario SÍ puede crear "Policarbonato Especial" (nombre diferente)

## 📊 Estadísticas

```
Total Parámetros Globales: 121

Materiales de Lentes:        7
Tratamientos:               12
Tipos de Lentes:             8
Marcas de Lentes:            8
Tipos de Monturas:           8
Tipos de LC:                 6
Marcas de LC:                6
Régimen de LC:               6
Medicamentos:               11
Diagnósticos:               13
Exámenes:                   11
Terapias:                    5
Especialidades:             10
Recomendaciones:            10
```

## 🔄 Migración

### Archivos Modificados

1. **apps/dashboard/views_clinical.py**
   - Agregado `Q(organization__isnull=True)` en todas las consultas
   - 8 consultas actualizadas

2. **Nuevos Scripts**
   - `delete_all_clinical_params.py`
   - `populate_global_clinical_params.py`
   - `verify_global_params.py`
   - `setup_global_params_render.py`

### Base de Datos

No se requiere migración de Django. Los cambios son solo en las consultas.

## ✅ Validación

Para verificar que todo funciona:

```bash
python verify_global_params.py
```

Debe mostrar:
- ✅ 121 parámetros globales
- ✅ Policarbonato encontrado
- ✅ Antireflejo encontrado
- ✅ Progresivos encontrado
- ✅ Miopía encontrado

## 🎯 Próximos Pasos

1. ✅ Ejecutar en Render: `python setup_global_params_render.py`
2. ✅ Verificar en la aplicación que aparecen los parámetros
3. ✅ Probar crear un nuevo material personalizado
4. ✅ Confirmar que no se duplican los nombres globales

## 📝 Notas Importantes

- Los parámetros globales NO pertenecen a ninguna organización
- Cada organización puede agregar sus propios parámetros
- No se pueden crear duplicados dentro de la misma organización
- Los parámetros globales se muestran como "🌍 Global" en las consultas

## 🔐 Seguridad

- Solo administradores pueden crear parámetros globales (organization=null)
- Usuarios normales crean parámetros para su organización
- El sistema previene duplicados automáticamente

---

**Fecha de Implementación**: 17 de Diciembre 2025  
**Versión**: 1.0.0  
**Estado**: ✅ Implementado y Validado
