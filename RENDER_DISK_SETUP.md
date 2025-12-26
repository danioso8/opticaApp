# ==========================================
# CONFIGURACIÓN DE DISCO PERSISTENTE EN RENDER
# ==========================================

## 📦 ¿Qué es un Render Disk?

Un Render Disk es almacenamiento persistente que sobrevive entre deployments.
Sin esto, cada vez que despliegas, los archivos subidos (logos, imágenes) se pierden.

## 🔧 Cómo Configurar el Disco Persistente

### Paso 1: Crear el Disco en Render

1. Ve a tu servicio en Render Dashboard: https://dashboard.render.com
2. Haz clic en tu servicio "OpticaApp" (o como lo hayas llamado)
3. Ve a la pestaña **"Disks"** en el menú lateral
4. Haz clic en **"Add Disk"**

### Paso 2: Configuración del Disco

Usa estos valores:

```
Name: media-storage
Mount Path: /opt/render/project/src/media_storage
Size: 1 GB (gratis) o más si necesitas
```

**IMPORTANTE:** El `Mount Path` debe ser exactamente: `/opt/render/project/src/media_storage`

### Paso 3: Variables de Entorno (Opcional)

Si quieres personalizar la ruta, agrega esta variable de entorno en Render:

```
RENDER_MEDIA_PATH=/opt/render/project/src/media_storage
```

### Paso 4: Desplegar

1. Haz commit y push de los cambios a tu repositorio
2. Render detectará los cambios y redesplegará automáticamente
3. El disco se montará automáticamente en la ruta especificada

## 📝 Configuración Actual

- **Desarrollo (DEBUG=True)**: Usa carpeta local `media/`
- **Producción (DEBUG=False)**: Usa disco persistente en `/opt/render/project/src/media_storage`
- **URLs de Media**: `/media/` (accesible públicamente)

## ✅ Verificar que Funciona

1. Sube un logo desde la configuración de landing page
2. Guarda y verifica que se muestre
3. Redespliega tu aplicación en Render
4. Verifica que el logo sigue ahí (¡debería estar!)

## 🔍 Troubleshooting

### Problema: Los archivos desaparecen después de desplegar

**Solución:** Asegúrate de que el disco está montado correctamente:

```bash
# En Render Shell (desde el dashboard):
ls -la /opt/render/project/src/media_storage
```

Deberías ver los archivos subidos.

### Problema: Error de permisos

**Solución:** Render maneja los permisos automáticamente. Si hay problemas, verifica que el Mount Path sea correcto.

### Problema: El disco no aparece en Render

**Solución:** 
- Solo los planes pagados permiten discos persistentes
- El plan gratuito de Render NO incluye discos persistentes
- Alternativa gratuita: Usar Cloudflare R2 (S3-compatible, gratis hasta 10GB)

## 💰 Costos de Render Disk

- **Gratis:** NO (el plan gratuito no incluye discos)
- **Starter:** $7/mes incluye 1GB de disco
- **Disk adicional:** $0.25/GB/mes

## 🎯 Alternativa GRATUITA: Cloudflare R2

Si quieres almacenamiento gratuito, puedo configurar Cloudflare R2:
- Gratis hasta 10GB de almacenamiento
- Sin cargos de egreso (descarga)
- Compatible con S3
- Requiere cuenta de Cloudflare

**¿Quieres que configure Cloudflare R2 en lugar de Render Disk?**

## 📂 Estructura de Archivos en el Disco

```
/opt/render/project/src/media_storage/
├── landing/
│   ├── logos/
│   │   ├── logo.jpg
│   │   ├── logo_empresa2.png
│   │   └── ...
│   └── hero/
│       ├── hero_image.jpg
│       └── ...
├── organizations/
│   └── logos/
│       └── ...
└── ...
```

## 🚀 Comandos Útiles en Render Shell

```bash
# Ver archivos en el disco
ls -la /opt/render/project/src/media_storage

# Ver tamaño del disco usado
du -sh /opt/render/project/src/media_storage

# Ver permisos
ls -la /opt/render/project/src/media_storage/landing/logos
```

## 📌 Notas Importantes

1. **Backups:** Render NO hace backups automáticos de los discos. Considera hacer backups periódicos.
2. **Migración:** Si cambias de servidor, debes migrar los archivos del disco manualmente.
3. **Escalabilidad:** Para alto volumen de archivos, considera usar S3/Cloudflare R2.

---

**Estado Actual:** ✅ Configuración lista. Solo falta crear el disco en Render Dashboard.
