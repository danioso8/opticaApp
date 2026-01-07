# 📱 WhatsApp Server para OpticaApp

Servidor Node.js con Baileys para enviar notificaciones de WhatsApp de forma gratuita y multi-tenant.

## 🚀 Características

- ✅ **Multi-tenant**: Múltiples organizaciones con sus propias sesiones
- ✅ **Sesiones persistentes**: Las conexiones se guardan y restauran automáticamente
- ✅ **API REST**: Fácil integración con cualquier backend
- ✅ **Escaneo QR**: Conexión simple escaneando código QR
- ✅ **Reconexión automática**: Maneja desconexiones y reconecta automáticamente
- ✅ **Gratuito**: Sin costos de Twilio ni servicios de pago

## 📋 Requisitos

- Node.js 18+ 
- npm o yarn
- 1GB RAM mínimo (recomendado 2GB)
- Servidor con IP pública (VPS)

## 🔧 Instalación Local (Pruebas)

### 1. Instalar dependencias

```bash
cd whatsapp-server
npm install
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` y cambia:
```
PORT=3000
API_KEY=tu_clave_secreta_super_segura_cambiar_aqui
NODE_ENV=development
```

### 3. Iniciar servidor

```bash
npm start
```

O para desarrollo con auto-reload:
```bash
npm run dev
```

El servidor estará en: `http://localhost:3000`

## 🌐 Despliegue en VPS (Producción)

### Opción 1: DigitalOcean ($6/mes)

1. **Crear Droplet:**
   - Ubuntu 22.04 LTS
   - Plan: Basic ($6/mes - 1GB RAM)
   - Datacenter: Nueva York o Ámsterdam

2. **Conectar por SSH:**
```bash
ssh root@tu_ip_del_droplet
```

3. **Instalar Node.js:**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
node -v  # Verificar instalación
```

4. **Instalar PM2 (Gestor de procesos):**
```bash
sudo npm install -g pm2
```

5. **Subir código:**
```bash
# En tu máquina local
scp -r whatsapp-server root@tu_ip:/var/www/
```

O clonar desde Git:
```bash
cd /var/www
git clone https://tu-repositorio.git whatsapp-server
```

6. **Configurar:**
```bash
cd /var/www/whatsapp-server
npm install
cp .env.example .env
nano .env  # Editar y guardar
```

Configuración `.env` para producción:
```
PORT=3000
API_KEY=clave_muy_segura_generada_aleatoriamente_123456
NODE_ENV=production
```

7. **Iniciar con PM2:**
```bash
pm2 start server.js --name whatsapp-server
pm2 save
pm2 startup  # Copiar y ejecutar el comando que aparece
```

8. **Configurar Firewall:**
```bash
sudo ufw allow 22  # SSH
sudo ufw allow 3000  # WhatsApp Server
sudo ufw enable
```

9. **Obtener IP pública:**
```bash
curl ifconfig.me
```

### Opción 2: Contabo VPS (€3.99/mes)

1. **Crear VPS en:** https://contabo.com
   - Plan: Cloud VPS S (4GB RAM)
   - OS: Ubuntu 22.04

2. Seguir pasos 2-9 de la opción DigitalOcean

### Opción 3: Vultr ($5/mes)

1. **Crear servidor en:** https://vultr.com
   - Plan: Cloud Compute ($5/mes)
   - Location: New York o Miami
   - OS: Ubuntu 22.04

2. Seguir pasos 2-9 de la opción DigitalOcean

## 🔗 Configurar OpticaApp (Django)

### 1. Actualizar `.env` de Django:

```env
WHATSAPP_SERVER_URL=http://TU_IP_DEL_VPS:3000
WHATSAPP_SERVER_API_KEY=la_misma_clave_que_pusiste_en_el_servidor
```

Para producción con HTTPS (recomendado):
```env
WHATSAPP_SERVER_URL=https://whatsapp.tu-dominio.com
WHATSAPP_SERVER_API_KEY=tu_clave_secreta
```

### 2. Instalar librería requests:

```bash
pip install requests
```

### 3. Aplicar migraciones (si las hay):

```bash
python manage.py migrate
```

### 4. Reiniciar Django:

```bash
# En Render se reinicia automáticamente
# Local:
python manage.py runserver
```

## 📖 Uso

### Desde OpticaApp Dashboard:

1. Ve a: **Dashboard** → **Configuración** → **WhatsApp Local**
2. Haz clic en **"Conectar WhatsApp"**
3. Escanea el código QR con tu WhatsApp
4. ¡Listo! Las notificaciones se enviarán automáticamente

### API Endpoints:

#### 1. Iniciar Sesión (Generar QR)
```bash
POST /api/start-session
Headers: X-API-Key: tu_clave
Body: {
  "organization_id": "23"
}
```

#### 2. Obtener QR
```bash
GET /api/qr/23
Headers: X-API-Key: tu_clave
```

#### 3. Ver Estado
```bash
GET /api/status/23
Headers: X-API-Key: tu_clave
```

#### 4. Enviar Mensaje
```bash
POST /api/send-message
Headers: X-API-Key: tu_clave
Body: {
  "organization_id": "23",
  "phone": "3001234567",
  "message": "¡Hola! Tu cita es mañana a las 10am"
}
```

#### 5. Cerrar Sesión
```bash
POST /api/logout
Headers: X-API-Key: tu_clave
Body: {
  "organization_id": "23"
}
```

## 🔐 Seguridad

1. **API Key fuerte:** Genera una clave aleatoria de al menos 32 caracteres
2. **Firewall:** Solo permite tráfico desde la IP de Render
3. **HTTPS:** Usa nginx como proxy inverso (ver sección abajo)
4. **Backups:** PM2 guarda logs en `/root/.pm2/logs/`

## 🌐 HTTPS con Nginx (Recomendado)

### 1. Instalar Nginx y Certbot:
```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

### 2. Configurar dominio:
Crea `/etc/nginx/sites-available/whatsapp`:
```nginx
server {
    listen 80;
    server_name whatsapp.tu-dominio.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 3. Activar configuración:
```bash
sudo ln -s /etc/nginx/sites-available/whatsapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Obtener certificado SSL:
```bash
sudo certbot --nginx -d whatsapp.tu-dominio.com
```

### 5. Actualizar `.env` de Django:
```env
WHATSAPP_SERVER_URL=https://whatsapp.tu-dominio.com
```

## 🐛 Solución de Problemas

### El servidor no inicia:
```bash
pm2 logs whatsapp-server
```

### Reiniciar servidor:
```bash
pm2 restart whatsapp-server
```

### Ver procesos activos:
```bash
pm2 list
```

### Eliminar sesión corrupta:
```bash
cd /var/www/whatsapp-server
rm -rf auth_sessions/ORGANIZATION_ID
pm2 restart whatsapp-server
```

### Ver uso de memoria:
```bash
pm2 monit
```

## 📊 Monitoreo

Ver logs en tiempo real:
```bash
pm2 logs whatsapp-server --lines 100
```

Estadísticas:
```bash
pm2 describe whatsapp-server
```

## 💰 Costos Estimados

| Proveedor | Plan | RAM | Precio/mes |
|-----------|------|-----|------------|
| Contabo | VPS S | 4GB | €3.99 (~$4.30) |
| Vultr | Cloud Compute | 1GB | $5 |
| DigitalOcean | Basic | 1GB | $6 |
| Hetzner | CX11 | 2GB | €4.15 (~$4.50) |

**Recomendado:** Contabo (mejor relación precio/recursos)

## 🎯 Próximos Pasos

- [ ] Implementar webhooks para mensajes recibidos
- [ ] Panel de administración web
- [ ] Métricas y estadísticas
- [ ] Rate limiting
- [ ] Soporte para archivos multimedia

## 📝 Notas

- Cada organización necesita un número de WhatsApp diferente
- Las sesiones se guardan en `auth_sessions/`
- El servidor restaura sesiones automáticamente al reiniciar
- Tiempo de escaneo QR: ~30 segundos
- Conexión estable: puede durar semanas sin necesidad de re-escanear

## 🆘 Soporte

Si tienes problemas:
1. Revisa los logs: `pm2 logs whatsapp-server`
2. Verifica que el servidor esté corriendo: `pm2 list`
3. Prueba el endpoint de salud: `curl http://localhost:3000/health`

---

**Desarrollado para OpticaApp** 🚀
