# Pasos para Aplicar Migraciones en Render

## 🚀 Método 1: Desde la Shell de Render (Más Rápido)

1. Ve a https://dashboard.render.com
2. Selecciona tu servicio `opticaapp`
3. Click en **"Shell"** en el menú lateral izquierdo
4. Espera a que cargue la terminal
5. Ejecuta estos comandos uno por uno:

```bash
python manage.py migrate
```

Si hay errores, ejecuta:
```bash
python manage.py migrate --run-syncdb
```

## 🔄 Método 2: Forzar Re-Deploy

Si el Método 1 no funciona:

1. Ve a https://dashboard.render.com
2. Selecciona tu servicio `opticaapp`
3. Click en **"Manual Deploy"**
4. Selecciona **"Clear build cache & deploy"**
5. Espera a que termine el deploy (puede tomar 5-10 minutos)

## ✅ Verificar que Funciona

Después de aplicar las migraciones:

1. Ve a tu landing page: https://opticaapp-4e16.onrender.com/
2. Intenta agendar una cita
3. Deberías ver los horarios disponibles

## 📋 Migraciones Pendientes

Estas son las migraciones que necesitas aplicar:

- `0016_add_logo_size_field` - Tamaño del logo
- `0017_landingpageconfig_hero_image_fit` - Ajuste de imagen hero
- `0018_landingpageconfig_hero_image_position_x_and_more` - Posición y zoom de imagen

## 🆘 Si Sigue Sin Funcionar

Ejecuta en la Shell de Render:

```bash
python manage.py showmigrations organizations
```

Esto mostrará qué migraciones están aplicadas (✓) y cuáles faltan (⬜).
