# 🚀 Guía de Deployment - OpticaApp en Contabo VPS

## 📋 Información del Servidor

- **Proveedor:** Contabo VPS
- **IP:** 84.247.129.180
- **Sistema Operativo:** Ubuntu/Debian
- **Usuario:** root
- **Ubicación del Proyecto:** `/var/www/opticaapp/`

## 🔧 Configuración Inicial del Servidor

### 1. Conectarse al servidor
```bash
ssh root@84.247.129.180
```

### 2. Instalar dependencias del sistema
```bash
# Actualizar paquetes
apt update && apt upgrade -y

# Instalar Python, PostgreSQL y dependencias
apt install -y python3.12 python3.12-venv python3-pip postgresql postgresql-contrib nginx git

# Instalar Node.js (para WhatsApp server)
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Instalar PM2
npm install -g pm2
```

### 3. Configurar PostgreSQL
```bash
# Cambiar a usuario postgres
sudo -u postgres psql

# Crear base de datos y usuario
CREATE DATABASE opticaapp_db;
CREATE USER opticaapp_user WITH PASSWORD 'tu_password_seguro';
ALTER ROLE opticaapp_user SET client_encoding TO 'utf8';
ALTER ROLE opticaapp_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE opticaapp_user SET timezone TO 'America/Bogota';
GRANT ALL PRIVILEGES ON DATABASE opticaapp_db TO opticaapp_user;
\q
```

## 📦 Deployment de la Aplicación

### 1. Clonar o subir el proyecto
```bash
cd /var/www/
git clone https://github.com/danioso8/opticaApp.git opticaapp
# O subir archivos con SCP/SFTP
```

### 2. Configurar entorno virtual
```bash
cd /var/www/opticaapp
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
# Crear archivo .env
nano /var/www/opticaapp/.env
```

Contenido del `.env`:
```bash
SECRET_KEY=tu-secret-key-super-segura-cambiala
DEBUG=False
ALLOWED_HOSTS=84.247.129.180,opticaapp.com,www.opticaapp.com

# Base de datos
DATABASE_URL=postgresql://opticaapp_user:tu_password_seguro@localhost:5432/opticaapp_db

# Twilio (opcional)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=tu_auth_token_de_twilio
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Configuración
WEBSITE_URL=http://84.247.129.180
BUSINESS_PHONE=300 123 4567
```

### 4. Ejecutar migraciones
```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py createsuperuser
```

## 🔄 Gestión con PM2

### 1. Iniciar Django con PM2
```bash
pm2 start /var/www/opticaapp/venv/bin/gunicorn \
  --name opticaapp \
  --cwd /var/www/opticaapp \
  -- --bind 0.0.0.0:8000 --workers 3 config.wsgi:application
```

### 2. Iniciar WhatsApp Server (opcional)
```bash
cd /var/www/opticaapp/whatsapp-server
npm install
pm2 start index.js --name whatsapp-server
```

### 3. Guardar configuración PM2
```bash
pm2 save
pm2 startup
```

### 4. Comandos útiles de PM2
```bash
pm2 list                    # Ver procesos
pm2 logs opticaapp          # Ver logs
pm2 restart opticaapp       # Reiniciar
pm2 stop opticaapp          # Detener
pm2 delete opticaapp        # Eliminar proceso
pm2 monit                   # Monitor en tiempo real
```

## 🔄 Actualización de la Aplicación

### Opción 1: Desde Git
```bash
cd /var/www/opticaapp
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
pm2 restart opticaapp
```

### Opción 2: Con archivo comprimido
```bash
# En tu máquina local
tar -czf opticaapp_update.tar.gz apps/ config/ templates/ static/
scp opticaapp_update.tar.gz root@84.247.129.180:/tmp/

# En el servidor
cd /var/www/opticaapp
tar -xzf /tmp/opticaapp_update.tar.gz
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --no-input
pm2 restart opticaapp
```

## 🗄️ Backup de Base de Datos

### Crear backup
```bash
# Backup completo
sudo -u postgres pg_dump opticaapp_db > /backup/opticaapp_$(date +%Y%m%d_%H%M%S).sql

# Backup comprimido
sudo -u postgres pg_dump opticaapp_db | gzip > /backup/opticaapp_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Restaurar backup
```bash
# Desde archivo SQL
sudo -u postgres psql opticaapp_db < /backup/opticaapp_20260107.sql

# Desde archivo comprimido
gunzip -c /backup/opticaapp_20260107.sql.gz | sudo -u postgres psql opticaapp_db
```

### Automatizar backups con cron
```bash
# Editar crontab
crontab -e

# Agregar línea (backup diario a las 2 AM)
0 2 * * * sudo -u postgres pg_dump opticaapp_db | gzip > /backup/opticaapp_$(date +\%Y\%m\%d).sql.gz
```

## 🔒 Configuración de SSL (Opcional)

### Con Certbot (Let's Encrypt)
```bash
# Instalar Certbot
apt install -y certbot python3-certbot-nginx

# Obtener certificado
certbot --nginx -d opticaapp.com -d www.opticaapp.com

# Renovación automática
certbot renew --dry-run
```

Actualizar `.env`:
```bash
DEBUG=False
ALLOWED_HOSTS=opticaapp.com,www.opticaapp.com
WEBSITE_URL=https://opticaapp.com
```

Actualizar `config/settings.py`:
```python
# Descomentar línea:
SECURE_SSL_REDIRECT = True

# Actualizar CSRF_TRUSTED_ORIGINS:
CSRF_TRUSTED_ORIGINS = [
    'https://opticaapp.com',
    'https://www.opticaapp.com',
]
```

## 🐛 Troubleshooting

### Ver logs de Django
```bash
pm2 logs opticaapp --lines 100
```

### Verificar estado de servicios
```bash
pm2 status
systemctl status postgresql
systemctl status nginx
```

### Probar conexión a base de datos
```bash
sudo -u postgres psql -d opticaapp_db -c "SELECT COUNT(*) FROM auth_user;"
```

### Limpiar sesiones de WhatsApp
```bash
cd /var/www/opticaapp/whatsapp-server
rm -rf .wwebjs_auth .wwebjs_cache
pm2 restart whatsapp-server
```

### Error 400 Bad Request
- Verificar `ALLOWED_HOSTS` en `.env`
- Verificar `DEBUG` está en `True` para HTTP o `False` con SSL
- Reiniciar: `pm2 restart opticaapp`

### Error 500 Internal Server Error
- Ver logs: `pm2 logs opticaapp --err`
- Verificar migraciones: `python manage.py showmigrations`
- Verificar conexión BD: `python manage.py dbshell`

## 📞 Soporte

Para más información, consulta:
- [Documentación de Django](https://docs.djangoproject.com/)
- [PM2 Documentation](https://pm2.keymetrics.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Última actualización:** Enero 2026  
**Versión:** 2.0 (Contabo VPS)
