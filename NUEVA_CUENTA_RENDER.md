# 🆕 Configuración desde Cero con Nueva Cuenta Render

## 📋 Paso 1: Crear Nueva Cuenta

1. Ve a: https://render.com
2. Click en **"Get Started"**
3. Regístrate con **diferente email** (puede ser Gmail, GitHub, etc.)
4. Verifica tu email

---

## 🔗 Paso 2: Conectar GitHub

1. En el dashboard, click en **"New +"**
2. Selecciona **"Blueprint"**
3. Si es la primera vez, te pedirá conectar GitHub:
   - Click en **"Connect GitHub"**
   - Autoriza a Render
   - Selecciona el repositorio: `danioso8/opticaApp`

---

## 🚀 Paso 3: Aplicar Blueprint

1. Con el repo conectado, Render detectará automáticamente `render.yaml`
2. Verás un resumen:

   **Database:**
   - `oceano-optico-db` (PostgreSQL Free)
   
   **Web Service:**
   - `oceano-optico` (Python Free)
   - 10 variables de entorno

3. Click en **"Apply"** o **"Create Resources"**

---

## ⏱️ Paso 4: Esperar Deploy

El proceso toma ~10-15 minutos:

### En la Base de Datos:
```
Creating PostgreSQL instance...
✓ Database ready
```

### En el Servicio Web:
```
Cloning repository...
Running build command: ./build.sh
==> Instalando dependencias...
==> Recolectando archivos estáticos...
==> Aplicando migraciones...
✓ Superusuario creado: admin / admin123
==> Build completado exitosamente ✓

Starting service...
✓ Your service is live 🎉
```

---

## 🌐 Paso 5: Acceder a la Aplicación

Una vez completado:

**URL de tu app:**
```
https://oceano-optico.onrender.com
```

**Panel de administración:**
```
https://oceano-optico.onrender.com/admin/
```

**Credenciales (creadas automáticamente):**
- Usuario: `admin`
- Contraseña: `admin123`

⚠️ **IMPORTANTE**: Cambia la contraseña inmediatamente después del primer login

---

## 📊 URLs Útiles

| Recurso | URL |
|---------|-----|
| Landing Page | https://oceano-optico.onrender.com/ |
| Agendar Cita | https://oceano-optico.onrender.com/agendar/ |
| Dashboard | https://oceano-optico.onrender.com/dashboard/ |
| Ventas | https://oceano-optico.onrender.com/dashboard/sales/ |
| Admin Django | https://oceano-optico.onrender.com/admin/ |
| API Config | https://oceano-optico.onrender.com/api/configuration/ |

---

## ⚠️ Notas del Plan Free

### Limitaciones:
- ⏱️ App se "duerme" después de 15 min de inactividad
- 🐌 Primera carga después de dormir toma ~1 minuto
- 📊 750 horas gratis por mes por servicio
- 💾 PostgreSQL: 1GB de almacenamiento
- 🔄 Deploy automático en cada push a GitHub

### Características:
- ✅ SSL/HTTPS automático
- ✅ Dominio `.onrender.com` incluido
- ✅ Deploy automático desde GitHub
- ✅ Logs en tiempo real
- ✅ Variables de entorno seguras
- ✅ Backups automáticos de BD

---

## 🔧 Troubleshooting

### Error: "Build failed"
1. Ve a **Logs** en el servicio web
2. Busca el error específico
3. Común: permisos en `build.sh`
   - Solución: Ya está configurado en `.gitattributes`

### Error: "Database connection failed"
1. Verifica que la base de datos esté "Available"
2. La variable `DATABASE_URL` se configura automáticamente desde el Blueprint

### Error: "Module not found"
1. Verifica que `requirements.txt` esté actualizado
2. Todos los paquetes necesarios ya están incluidos

### La app no carga
1. Primer acceso después de dormir toma ~1 minuto
2. Refresca la página
3. Verifica los logs del servicio

---

## 🎯 Próximos Pasos Post-Deploy

### 1. Cambiar Contraseña Admin
```
1. Login en /admin/ con admin/admin123
2. Click en tu usuario (arriba derecha)
3. Cambiar contraseña
```

### 2. Crear Usuarios del Personal
```
Dashboard → Usuarios → Agregar Usuario
- Asignar roles: Vendedor, Optometrista, Administrador
```

### 3. Configurar Horarios
```
Dashboard → Configuración → Horarios Específicos
- Agregar fechas y horarios de atención
```

### 4. Agregar Productos (Opcional)
```
Dashboard → Ventas → Productos
- Agregar monturas, lentes, accesorios
```

### 5. WhatsApp Notifications (Opcional)
Para habilitar notificaciones por WhatsApp:
- Opción A: Usar Twilio (de pago, $1/mes)
- Opción B: Bot local con Baileys (gratis, solo local)

Documentación en: `whatsapp-bot/README.md`

---

## 📱 Monitorear tu Aplicación

### Logs en Tiempo Real:
```
Dashboard → oceano-optico → Logs
```

### Métricas:
```
Dashboard → oceano-optico → Metrics
- CPU usage
- Memory usage
- Request rate
```

### Eventos:
```
Dashboard → oceano-optico → Events
- Deploys
- Crashes
- Restarts
```

---

## 🆙 Actualizar la Aplicación

Cada vez que hagas `git push` a GitHub, Render hará deploy automático:

```bash
# En tu computadora
git add .
git commit -m "Nueva funcionalidad"
git push origin main

# Render automáticamente:
# 1. Detecta el push
# 2. Clona el código
# 3. Ejecuta build.sh
# 4. Hace deploy
```

---

## 💰 Upgrade a Plan Pagado (Opcional)

Si necesitas:
- Sin "sleep" (app siempre activa)
- Más recursos (CPU/RAM)
- Más almacenamiento en BD
- Custom domain con SSL

Render ofrece planes desde $7/mes para web service.

---

## ✅ Checklist Final

Antes de considerar el deploy completo:

- [ ] App accesible en https://oceano-optico.onrender.com
- [ ] Admin login funciona (admin/admin123)
- [ ] Contraseña de admin cambiada
- [ ] Al menos 1 usuario staff creado
- [ ] Horarios específicos configurados
- [ ] Primera cita de prueba agendada
- [ ] Dashboard muestra datos correctamente
- [ ] (Opcional) WhatsApp configurado

---

## 🆘 Soporte

Si encuentras problemas:

1. **Logs del Servicio**: Primer lugar para buscar errores
2. **Render Docs**: https://render.com/docs
3. **Render Community**: https://community.render.com
4. **GitHub Issues**: Crear issue en tu repo

---

¡Tu sistema está listo para producción! 🎉
