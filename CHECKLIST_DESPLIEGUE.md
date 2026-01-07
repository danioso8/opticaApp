# 🚀 CHECKLIST COMPLETO - DESPLIEGUE OPTICAAPP

## ✅ ESTADO ACTUAL

### Lo que ya tienes funcionando:
- ✅ OpticaApp completa desarrollada
- ✅ Módulo de promociones funcional
- ✅ WhatsApp Baileys integrado
- ✅ Pruebas exitosas (2 mensajes enviados)
- ✅ Sistema de no-repetición validado
- ✅ Scripts de despliegue preparados
- ✅ Archivos listos en: `contabo_deploy/`

---

## 📋 PASOS PARA PRODUCCIÓN

### FASE 1: CONTABO VPS (30 minutos)

#### Paso 1.1: Contratar servidor
1. Ve a: **https://contabo.com/**
2. Selecciona: **Cloud VPS S**
   - Precio: **$3.99/mes**
   - RAM: 4GB
   - Disco: 50GB SSD
   - Región: **Frankfurt, Germany** (más cerca de Render)
3. Sistema operativo: **Ubuntu 22.04 LTS**
4. Completa el registro y pago
5. **ESPERA EMAIL** con credenciales (puede tardar hasta 24 horas)

#### Paso 1.2: Anotar datos del email
Recibirás algo como:
```
Your VPS is ready!
IP Address: 123.45.67.89
Username: root
Password: Abc123XyzTemp!
SSH Port: 22
```

**📝 ANOTA AQUÍ:**
- IP: ___________________________
- Usuario: root
- Contraseña: ___________________________

---

### FASE 2: CONFIGURAR SERVIDOR (20 minutos)

#### Paso 2.1: Subir archivos desde tu PC

Abre PowerShell y ejecuta:

```powershell
# Ir a la carpeta con archivos preparados
cd D:\ESCRITORIO\OpticaApp\contabo_deploy

# Subir TODO al servidor (reemplaza 123.45.67.89 con TU IP)
scp * root@123.45.67.89:/root/

# Te pedirá la contraseña del email
```

#### Paso 2.2: Conectarte al servidor

```powershell
# Conectar por SSH (reemplaza con TU IP)
ssh root@123.45.67.89

# Primera vez te preguntará: "Are you sure (yes/no)?"
# Escribe: yes
# Luego ingresa la contraseña
```

#### Paso 2.3: Ejecutar instalación automática

Ya dentro del servidor, ejecuta:

```bash
# Dar permisos de ejecución
chmod +x /root/install_contabo.sh
chmod +x /root/start_whatsapp.sh

# Ejecutar instalación (tarda ~5 minutos)
bash /root/install_contabo.sh

# Verás algo como:
# [1/7] Actualizando sistema...
# [2/7] Instalando utilidades...
# ...
# [7/7] Instalación completada
```

#### Paso 2.4: Mover archivos a carpeta correcta

```bash
# Mover server.js y package.json
mv /root/server.js /root/whatsapp-server/
mv /root/package.json /root/whatsapp-server/

# Verificar que estén ahí
ls -la /root/whatsapp-server/
```

---

### FASE 3: ACTIVAR WHATSAPP (10 minutos)

#### Paso 3.1: Iniciar servidor

```bash
# Ejecutar script de inicio
bash /root/start_whatsapp.sh

# Verás los logs y aparecerá un CÓDIGO QR
```

#### Paso 3.2: Escanear QR con tu celular

1. **Abre WhatsApp** en tu celular
2. Ve a **Menú (⋮) → Dispositivos vinculados**
3. Toca **"Vincular un dispositivo"**
4. **Escanea el QR** que apareció en la terminal
5. ✅ **¡Conectado!** Verás: "WhatsApp conectado para 23"

#### Paso 3.3: Verificar que quedó corriendo

```bash
# Presiona Ctrl+C para salir de los logs

# Ver estado del servidor
pm2 status

# Debe mostrar:
# │ whatsapp-opticaapp │ online │
```

---

### FASE 4: PROBAR CONEXIÓN (5 minutos)

#### Paso 4.1: Desde tu PC (PowerShell)

```powershell
# Reemplaza 123.45.67.89 con TU IP de Contabo
$ip = "123.45.67.89"

$body = @{
    organization_id = 23
    phone = "3009787566"
    message = "¡Prueba desde servidor Contabo! 🚀"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://$ip:3000/send-message" `
    -Method POST `
    -Headers @{"x-api-key"="opticaapp_2026_whatsapp_baileys_secret_key_12345"} `
    -Body $body `
    -ContentType "application/json"
```

#### Paso 4.2: Verificar respuesta

Debe responder:
```json
{
  "success": true,
  "message": "Mensaje enviado correctamente"
}
```

✅ **¡Revisa tu WhatsApp!** Debe llegar el mensaje.

---

### FASE 5: DESPLEGAR DJANGO EN RENDER (30 minutos)

#### Paso 5.1: Preparar repositorio

```powershell
# En tu PC, en D:\ESCRITORIO\OpticaApp

# Inicializar Git (si no lo has hecho)
git init
git add .
git commit -m "OpticaApp lista para producción"

# Crear repositorio en GitHub
# Ve a: https://github.com/new
# Nombre: opticaapp
# Visibilidad: Private
# Crear repositorio

# Subir código
git remote add origin https://github.com/TU_USUARIO/opticaapp.git
git branch -M main
git push -u origin main
```

#### Paso 5.2: Crear servicio en Render

1. Ve a: **https://render.com/**
2. Registrate o inicia sesión
3. Click **"New +"** → **"Web Service"**
4. Conecta tu repositorio de GitHub
5. Configuración:
   - **Name**: opticaapp
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn opticaapp.wsgi:application`
   - **Plan**: Free (o Starter $7/mes)

#### Paso 5.3: Variables de entorno en Render

Click en **"Environment"** y agrega:

```
SECRET_KEY=tu_secret_key_aqui_cambiar
DEBUG=False
ALLOWED_HOSTS=opticaapp.onrender.com
DATABASE_URL=postgres://... (Render te da esto)

# IMPORTANTE: Esta es la IP de tu servidor Contabo
WHATSAPP_SERVER_URL=http://123.45.67.89:3000

WHATSAPP_API_KEY=opticaapp_2026_whatsapp_baileys_secret_key_12345
```

#### Paso 5.4: Crear base de datos PostgreSQL

1. En Render: **"New +"** → **"PostgreSQL"**
2. Nombre: opticaapp-db
3. Plan: Free
4. Copiar la **DATABASE_URL** que te da
5. Pegarla en las variables de entorno del Web Service

#### Paso 5.5: Deploy

1. Click **"Create Web Service"**
2. Espera ~5 minutos mientras despliega
3. Te dará una URL: `https://opticaapp.onrender.com`

---

### FASE 6: MIGRAR BASE DE DATOS (10 minutos)

#### Paso 6.1: Desde Render Shell

En Render, ve a tu servicio y click **"Shell"**:

```bash
# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
# Usuario: admin
# Email: tu@email.com
# Contraseña: (la que quieras)

# Crear parámetros clínicos
python create_clinical_parameters.py
```

---

### FASE 7: VERIFICACIÓN FINAL (5 minutos)

#### ✅ Checklist de verificación:

1. [ ] **WhatsApp Contabo funcionando**
   ```bash
   # En SSH de Contabo
   pm2 status
   # Debe mostrar: online
   ```

2. [ ] **Django Render funcionando**
   - Abre: `https://opticaapp.onrender.com`
   - Debe cargar la página de login

3. [ ] **Conexión WhatsApp ↔ Render funcionando**
   - En Render, crea una campaña promocional
   - Envía a un número de prueba
   - Verifica que llegue el mensaje

4. [ ] **Sesión WhatsApp persistente**
   ```bash
   # En SSH de Contabo
   ls -la /root/whatsapp-server/auth_sessions/
   # Debe mostrar carpeta con la sesión
   ```

---

## 🎯 DESPUÉS DEL DESPLIEGUE

### Comandos útiles en Contabo (SSH)

```bash
# Ver estado del servidor WhatsApp
pm2 status

# Ver logs en tiempo real
pm2 logs whatsapp-opticaapp

# Reiniciar servidor
pm2 restart whatsapp-opticaapp

# Detener servidor
pm2 stop whatsapp-opticaapp

# Ver recursos del servidor
htop

# Salir de SSH
exit
```

### Comandos útiles en Render

- **Ver logs**: Click en "Logs" en tu servicio
- **Reiniciar**: Click en "Manual Deploy" → "Deploy latest commit"
- **Shell**: Click en "Shell" para ejecutar comandos Django

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### WhatsApp se desconecta en Contabo

```bash
# Ver logs
pm2 logs whatsapp-opticaapp

# Si muestra error, reiniciar
pm2 restart whatsapp-opticaapp

# Si persiste, borrar sesión y escanear QR nuevamente
rm -rf /root/whatsapp-server/auth_sessions/*
pm2 restart whatsapp-opticaapp
pm2 logs whatsapp-opticaapp
# Escanea el nuevo QR
```

### Render no puede conectar con Contabo

```bash
# Verificar que el puerto 3000 esté abierto
ufw status

# Debe mostrar:
# 3000/tcp    ALLOW    Anywhere

# Probar desde tu PC
curl http://TU_IP_CONTABO:3000/health

# Si no responde, revisar firewall
ufw allow 3000/tcp
```

### Campaña no envía mensajes

1. Verificar en Render logs si hay errores
2. Verificar variable `WHATSAPP_SERVER_URL` correcta
3. Probar manualmente la conexión (Paso 4.1)
4. Verificar que WhatsApp esté conectado en Contabo

---

## 💰 COSTOS MENSUALES

| Servicio | Plan | Costo |
|----------|------|-------|
| Contabo VPS | Cloud VPS S | $3.99 |
| Render Django | Free | $0 |
| Render PostgreSQL | Free | $0 |
| **TOTAL** | | **$3.99/mes** |

**Opcional para mejor performance:**
- Render Starter: +$7/mes (recomendado para producción)
- **Total con Render pago**: $10.99/mes

---

## 📱 CONTACTOS DE SOPORTE

- **Contabo**: support@contabo.com
- **Render**: https://render.com/docs
- **Baileys (WhatsApp)**: https://github.com/WhiskeySockets/Baileys

---

## 🎉 ¡LISTO!

Tu sistema estará corriendo 24/7:
- ✅ Django en la nube (Render)
- ✅ WhatsApp en servidor dedicado (Contabo)
- ✅ Base de datos PostgreSQL
- ✅ Campañas promocionales automáticas
- ✅ Sin repetir pacientes
- ✅ Límites seguros de WhatsApp

**Tiempo total estimado**: 2-3 horas (incluyendo espera de Contabo)

**¡Éxito con OpticaApp!** 🚀👓
