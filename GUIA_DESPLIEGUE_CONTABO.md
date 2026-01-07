# 🚀 GUÍA DE DESPLIEGUE EN CONTABO VPS

## 📊 ARQUITECTURA FINAL

```
[Usuarios] 
   ↓
[Render - Django App] → Puerto 8000
   ↓ (peticiones HTTP)
[Contabo VPS - Node.js WhatsApp] → Puerto 3000
   ↓
[WhatsApp]
```

## ✅ VENTAJAS DE CONTABO VS NGROK

| Característica | Contabo VPS | ngrok Gratis | ngrok Pagado |
|---------------|-------------|--------------|--------------|
| **Precio** | $3.99/mes | Gratis | $8/mes |
| **URL/IP** | Fija (IP pública) | Cambia | Fija |
| **Uptime** | 24/7 | Depende de tu PC | Depende de tu PC |
| **Conexiones** | Ilimitadas | 40/min | Ilimitadas |
| **Sesión WhatsApp** | Persistente | Se pierde al apagar PC | Se pierde al apagar PC |
| **Profesional** | ✅ Sí | ❌ No | ⚠️ Depende |

## 📋 PASO 1: CONTRATAR CONTABO

### 1.1 Crear cuenta
1. Ve a: https://contabo.com/
2. Selecciona: **Cloud VPS S** ($3.99/mes)
   - 4 vCPU Cores
   - 4GB RAM
   - 50GB SSD
   - Europa (Frankfurt/Nuremberg recomendado)
3. Sistema operativo: **Ubuntu 22.04 LTS**
4. Completa el pago

### 1.2 Obtener credenciales
Recibirás email con:
- **IP pública**: `123.45.67.89`
- **Usuario**: `root`
- **Contraseña**: `tu_password_temporal`

## 📋 PASO 2: CONECTARTE AL SERVIDOR

### 2.1 Desde Windows (PowerShell)

```powershell
# Opción 1: SSH nativo de Windows 10/11
ssh root@123.45.67.89

# Opción 2: PuTTY (descargar de putty.org)
# Host: 123.45.67.89
# Port: 22
# User: root
```

### 2.2 Primera conexión
1. Ingresa contraseña del email
2. Cambia contraseña cuando te lo pida
3. Ya estás dentro del servidor

## 📋 PASO 3: CONFIGURAR SERVIDOR

### 3.1 Actualizar sistema
```bash
# Actualizar paquetes
apt update && apt upgrade -y

# Instalar utilidades básicas
apt install -y curl wget git ufw
```

### 3.2 Instalar Node.js 20
```bash
# Descargar script de instalación de Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -

# Instalar Node.js
apt install -y nodejs

# Verificar instalación
node --version  # Debe mostrar v20.x.x
npm --version   # Debe mostrar 10.x.x
```

### 3.3 Instalar PM2 (Process Manager)
```bash
# PM2 mantiene tu servidor corriendo 24/7
npm install -g pm2

# Verificar
pm2 --version
```

## 📋 PASO 4: SUBIR SERVIDOR DE WHATSAPP

### 4.1 Opción A: Transferir archivos desde tu PC

**En tu PC (PowerShell):**
```powershell
# Comprimir el servidor
cd D:\ESCRITORIO\OpticaApp
Compress-Archive -Path whatsapp-server -DestinationPath whatsapp-server.zip

# Transferir a Contabo (reemplaza la IP)
scp whatsapp-server.zip root@123.45.67.89:/root/
```

**En Contabo (SSH):**
```bash
# Descomprimir
cd /root
apt install -y unzip
unzip whatsapp-server.zip
cd whatsapp-server

# Instalar dependencias
npm install
```

### 4.2 Opción B: Copiar código manualmente

**En Contabo (SSH):**
```bash
# Crear directorio
mkdir -p /root/whatsapp-server
cd /root/whatsapp-server

# Crear package.json
cat > package.json << 'EOF'
{
  "name": "opticaapp-whatsapp-server",
  "version": "1.0.0",
  "description": "Servidor WhatsApp Baileys para OpticaApp",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "@whiskeysockets/baileys": "^6.6.0",
    "express": "^4.18.2",
    "qrcode-terminal": "^0.12.0",
    "pino": "^8.16.0"
  }
}
EOF

# Instalar dependencias
npm install
```

**Luego copia el contenido de server.js desde tu PC al servidor**

## 📋 PASO 5: CONFIGURAR FIREWALL

```bash
# Permitir SSH (IMPORTANTE - no te bloquees)
ufw allow 22/tcp

# Permitir puerto 3000 (WhatsApp server)
ufw allow 3000/tcp

# Activar firewall
ufw enable

# Verificar estado
ufw status
```

## 📋 PASO 6: INICIAR SERVIDOR CON PM2

```bash
cd /root/whatsapp-server

# Iniciar con PM2
pm2 start server.js --name whatsapp-opticaapp

# Ver logs en tiempo real
pm2 logs whatsapp-opticaapp

# Guardar configuración para auto-inicio
pm2 save
pm2 startup

# Verificar que esté corriendo
pm2 status
```

## 📋 PASO 7: ESCANEAR CÓDIGO QR

### 7.1 Primera conexión de WhatsApp

**En Contabo (SSH):**
```bash
# Ver logs donde aparece el QR
pm2 logs whatsapp-opticaapp

# Aparecerá un código QR en la terminal
```

**En tu celular:**
1. Abre WhatsApp
2. Ve a **Dispositivos vinculados**
3. Escanea el código QR de la terminal
4. ✅ Conectado

### 7.2 Verificar sesión guardada
```bash
# La sesión se guarda en:
ls -la /root/whatsapp-server/auth_sessions/

# Debe aparecer carpeta con ID de organización
```

## 📋 PASO 8: PROBAR CONEXIÓN

### 8.1 Desde tu PC local
```powershell
# Probar endpoint (reemplaza IP)
$body = @{
    organization_id = 23
    phone = "3009787566"
    message = "Prueba desde Contabo VPS"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://123.45.67.89:3000/send-message" `
    -Method POST `
    -Headers @{"x-api-key"="opticaapp_2026_whatsapp_baileys_secret_key_12345"} `
    -Body $body `
    -ContentType "application/json"
```

### 8.2 Debe responder:
```json
{
  "success": true,
  "message": "Mensaje enviado correctamente"
}
```

## 📋 PASO 9: CONFIGURAR EN RENDER

### 9.1 Variable de entorno
En tu app de Render:

```
Nombre: WHATSAPP_SERVER_URL
Valor: http://123.45.67.89:3000
```

### 9.2 Probar desde Render
Una vez desplegado, crea una campaña promocional y verifica que los mensajes se envíen correctamente.

## 🔐 PASO 10: SEGURIDAD ADICIONAL (OPCIONAL)

### 10.1 Cambiar puerto SSH
```bash
# Editar configuración SSH
nano /etc/ssh/sshd_config

# Cambiar línea:
Port 2222  # En lugar de 22

# Reiniciar SSH
systemctl restart sshd

# Actualizar firewall
ufw allow 2222/tcp
ufw delete allow 22/tcp
```

### 10.2 Restringir acceso al puerto 3000
```bash
# Solo permitir IP de Render
# (Consulta IPs de Render en su documentación)
ufw allow from RENDER_IP to any port 3000
```

### 10.3 Configurar SSL/HTTPS (Recomendado)
```bash
# Instalar Nginx
apt install -y nginx certbot python3-certbot-nginx

# Configurar dominio (si tienes uno)
# Por ejemplo: whatsapp.opticaapp.com → 123.45.67.89
```

## 📊 COMANDOS ÚTILES DE PM2

```bash
# Ver estado de procesos
pm2 status

# Ver logs en tiempo real
pm2 logs whatsapp-opticaapp

# Reiniciar servidor
pm2 restart whatsapp-opticaapp

# Detener servidor
pm2 stop whatsapp-opticaapp

# Eliminar proceso
pm2 delete whatsapp-opticaapp

# Monitorear recursos
pm2 monit

# Ver información detallada
pm2 show whatsapp-opticaapp
```

## 🔄 MANTENIMIENTO

### Actualizar código
```bash
cd /root/whatsapp-server

# Respaldar sesiones (IMPORTANTE)
cp -r auth_sessions auth_sessions_backup

# Actualizar código (subir nuevo server.js)
# ...

# Reiniciar
pm2 restart whatsapp-opticaapp
```

### Ver uso de recursos
```bash
# CPU y RAM
htop

# Espacio en disco
df -h

# Logs del sistema
journalctl -xe
```

## ❓ TROUBLESHOOTING

### Problema: No puedo conectarme por SSH
```bash
# Desde panel de Contabo, usa la consola web (VNC)
# Verifica firewall: ufw status
```

### Problema: WhatsApp se desconecta
```bash
# Ver logs
pm2 logs whatsapp-opticaapp

# Reiniciar
pm2 restart whatsapp-opticaapp

# Si persiste, eliminar sesión y volver a escanear QR
rm -rf auth_sessions/*
pm2 restart whatsapp-opticaapp
```

### Problema: Puerto 3000 no responde
```bash
# Verificar que esté corriendo
pm2 status

# Verificar firewall
ufw status

# Ver si el puerto está escuchando
netstat -tlnp | grep 3000
```

## 💰 COSTOS MENSUALES ESTIMADOS

- **Contabo VPS**: $3.99/mes
- **Django en Render**: Gratis (plan free) o $7/mes (plan básico)
- **Base de datos PostgreSQL**: Gratis en Render o incluida en plan
- **TOTAL**: ~$4-11/mes

## 🎯 PRÓXIMOS PASOS

1. ✅ Contratar Contabo
2. ✅ Configurar servidor Ubuntu
3. ✅ Instalar Node.js + PM2
4. ✅ Transferir servidor WhatsApp
5. ✅ Escanear QR de WhatsApp
6. ✅ Configurar IP en Render
7. ✅ Probar envío de campañas
8. 🚀 ¡Sistema en producción 24/7!

---

**¿Necesitas ayuda?** Puedo crear scripts automáticos para cada paso.
