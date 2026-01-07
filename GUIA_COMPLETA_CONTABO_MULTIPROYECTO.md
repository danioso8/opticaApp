# 🚀 GUÍA COMPLETA - DESPLIEGUE DE 7 PROYECTOS EN CONTABO VPS

## 📊 ARQUITECTURA FINAL

```
[Contabo VPS - 150 GB SSD - 8 GB RAM - 4 vCPU]
│
├── NGINX (Puerto 80/443) - Proxy reverso con SSL
│   ├── proyecto1.tudominio.com → localhost:8001
│   ├── proyecto2.tudominio.com → localhost:8002
│   ├── proyecto3.tudominio.com → localhost:8003
│   ├── proyecto4.tudominio.com → localhost:8004
│   ├── proyecto5.tudominio.com → localhost:8005
│   ├── proyecto6.tudominio.com → localhost:8006
│   └── opticaapp.tudominio.com → localhost:8007
│
├── POSTGRESQL (Puerto 5432)
│   ├── proyecto1_db (usuario: proyecto1_user)
│   ├── proyecto2_db (usuario: proyecto2_user)
│   ├── proyecto3_db (usuario: proyecto3_user)
│   ├── proyecto4_db (usuario: proyecto4_user)
│   ├── proyecto5_db (usuario: proyecto5_user)
│   ├── proyecto6_db (usuario: proyecto6_user)
│   └── opticaapp_db (usuario: opticaapp_user)
│
├── DJANGO PROJECTS (Gunicorn)
│   ├── /var/www/proyecto1 → Puerto 8001
│   ├── /var/www/proyecto2 → Puerto 8002
│   ├── /var/www/proyecto3 → Puerto 8003
│   ├── /var/www/proyecto4 → Puerto 8004
│   ├── /var/www/proyecto5 → Puerto 8005
│   ├── /var/www/proyecto6 → Puerto 8006
│   └── /var/www/opticaapp → Puerto 8007
│
├── NODE.JS WHATSAPP (Puerto 3000)
│   └── /var/www/whatsapp-server
│
├── PM2 - Process Manager
│   ├── Gestiona todos los proyectos Django
│   ├── Gestiona servidor WhatsApp
│   ├── Auto-restart en caso de error
│   └── Auto-inicio al reiniciar servidor
│
└── BACKUPS AUTOMÁTICOS (Cron)
    ├── Bases de datos → Diario 2:00 AM
    ├── Archivos estáticos → Semanal
    └── Retención: 7 días
```

---

## 💰 ANÁLISIS DE RECURSOS

### Distribución de recursos para 7 proyectos:

| Proyecto | RAM | CPU | Disco | Puerto |
|----------|-----|-----|-------|--------|
| Proyecto 1 | 800 MB | 0.5 | 15 GB | 8001 |
| Proyecto 2 | 800 MB | 0.5 | 15 GB | 8002 |
| Proyecto 3 | 800 MB | 0.5 | 15 GB | 8003 |
| Proyecto 4 | 800 MB | 0.5 | 15 GB | 8004 |
| Proyecto 5 | 800 MB | 0.5 | 15 GB | 8005 |
| Proyecto 6 | 800 MB | 0.5 | 15 GB | 8006 |
| **OpticaApp** | **1 GB** | **0.5** | **20 GB** | **8007** |
| WhatsApp | 300 MB | 0.2 | 5 GB | 3000 |
| PostgreSQL | 1 GB | 0.3 | 20 GB | 5432 |
| Nginx | 100 MB | 0.1 | 1 GB | 80/443 |
| Sistema | 500 MB | 0.4 | 5 GB | - |
| **TOTAL** | **7.1 GB** | **3.5** | **116 GB** | - |
| **DISPONIBLE** | **0.9 GB** | **0.5** | **34 GB** | ✅ |

**Conclusión**: Recursos suficientes con margen del 11-22% ✅

---

## 📋 FASE 1: CONTRATACIÓN (5 minutos)

### 1.1 Contratar Contabo VPS

1. Ve a: https://contabo.com/es/vps/cloud-vps-10/
2. Configura:
   - **Contrato**: 12 meses (ahorra 20%)
   - **Región**: Unión Europea (Frankfurt)
   - **Almacenamiento**: 150 GB SSD (Gratis)
   - **Imagen**: Ubuntu 22.04 LTS
   - **Auto Backup**: Opcional (€0.75/mes)

3. **Total**: €43.20 (pago único 12 meses) = €3.60/mes

### 1.2 Esperar email con credenciales

Recibirás (en 1-24 horas):
```
IP: 123.45.67.89
Usuario: root
Contraseña: TuPasswordTemporal123!
Puerto SSH: 22
```

---

## 📋 FASE 2: INSTALACIÓN DEL STACK (30 minutos)

### 2.1 Conectarse al servidor

```powershell
# Desde tu PC (PowerShell)
ssh root@123.45.67.89

# Primera vez: escribir "yes"
# Luego ingresar contraseña del email
```

### 2.2 Ejecutar script de instalación automática

```bash
# Descargar script desde tu repositorio
# O copiar el contenido de install_full_stack.sh

chmod +x install_full_stack.sh
bash install_full_stack.sh
```

El script instalará:
- ✅ Node.js 20.x
- ✅ Python 3.11
- ✅ PostgreSQL 15
- ✅ Nginx
- ✅ PM2
- ✅ Certbot (SSL)
- ✅ Git, ufw, htop

**Tiempo**: ~20 minutos

---

## 📋 FASE 3: CONFIGURAR POSTGRESQL (20 minutos)

### 3.1 Crear bases de datos y usuarios

```bash
# Ejecutar script automático
bash create_databases.sh
```

Esto creará:

```sql
-- 7 bases de datos independientes
CREATE DATABASE proyecto1_db;
CREATE DATABASE proyecto2_db;
CREATE DATABASE proyecto3_db;
CREATE DATABASE proyecto4_db;
CREATE DATABASE proyecto5_db;
CREATE DATABASE proyecto6_db;
CREATE DATABASE opticaapp_db;

-- 7 usuarios con contraseñas seguras
CREATE USER proyecto1_user WITH PASSWORD 'password_aleatorio_1';
CREATE USER proyecto2_user WITH PASSWORD 'password_aleatorio_2';
-- ... etc

-- Permisos aislados
GRANT ALL PRIVILEGES ON DATABASE proyecto1_db TO proyecto1_user;
-- ... etc
```

### 3.2 Configurar acceso remoto (opcional)

Si quieres conectarte desde tu PC:

```bash
# Editar postgresql.conf
nano /etc/postgresql/15/main/postgresql.conf
# Cambiar: listen_addresses = '*'

# Editar pg_hba.conf
nano /etc/postgresql/15/main/pg_hba.conf
# Agregar: host all all 0.0.0.0/0 md5

# Reiniciar
systemctl restart postgresql

# Abrir puerto en firewall
ufw allow 5432/tcp
```

---

## 📋 FASE 4: ESTRUCTURA DE PROYECTOS (10 minutos)

### 4.1 Crear directorios

```bash
mkdir -p /var/www/proyecto1
mkdir -p /var/www/proyecto2
mkdir -p /var/www/proyecto3
mkdir -p /var/www/proyecto4
mkdir -p /var/www/proyecto5
mkdir -p /var/www/proyecto6
mkdir -p /var/www/opticaapp
mkdir -p /var/www/whatsapp-server

# Crear usuario www-data si no existe
id -u www-data &>/dev/null || useradd -r -s /bin/false www-data
```

### 4.2 Estructura de cada proyecto

```
/var/www/proyecto1/
├── venv/                    # Entorno virtual Python
├── proyecto1/               # Código Django
│   ├── manage.py
│   ├── proyecto1/           # Settings
│   └── apps/
├── static/                  # Archivos estáticos
├── media/                   # Archivos subidos
├── logs/                    # Logs de la aplicación
└── .env                     # Variables de entorno
```

---

## 📋 FASE 5: DESPLEGAR PROYECTOS (1-2 horas)

### 5.1 Subir código desde tu PC

**Opción A: Git (Recomendado)**

```bash
# En el servidor
cd /var/www/proyecto1
git clone https://github.com/tu_usuario/proyecto1.git .
```

**Opción B: SCP desde tu PC**

```powershell
# Desde tu PC
scp -r D:\MIS_PROYECTOS\proyecto1 root@123.45.67.89:/var/www/
```

### 5.2 Configurar cada proyecto

```bash
# Script automático para cada proyecto
bash deploy_project.sh proyecto1 8001 proyecto1_db proyecto1_user
bash deploy_project.sh proyecto2 8002 proyecto2_db proyecto2_user
# ... etc
bash deploy_project.sh opticaapp 8007 opticaapp_db opticaapp_user
```

El script hace:
1. Crear entorno virtual
2. Instalar dependencias
3. Configurar .env
4. Ejecutar migraciones
5. Recolectar estáticos
6. Configurar Gunicorn
7. Iniciar con PM2

---

## 📋 FASE 6: CONFIGURAR NGINX (30 minutos)

### 6.1 Configurar dominios

Primero, en tu proveedor de DNS (ej: Namecheap, GoDaddy):

```
Tipo A:
proyecto1.tudominio.com → 123.45.67.89
proyecto2.tudominio.com → 123.45.67.89
proyecto3.tudominio.com → 123.45.67.89
proyecto4.tudominio.com → 123.45.67.89
proyecto5.tudominio.com → 123.45.67.89
proyecto6.tudominio.com → 123.45.67.89
opticaapp.tudominio.com → 123.45.67.89
```

### 6.2 Crear configuraciones Nginx

```bash
# Script automático
bash configure_nginx.sh
```

Esto crea archivos en `/etc/nginx/sites-available/`:

```nginx
# /etc/nginx/sites-available/proyecto1
server {
    listen 80;
    server_name proyecto1.tudominio.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /var/www/proyecto1/static/;
    }

    location /media/ {
        alias /var/www/proyecto1/media/;
    }
}
```

### 6.3 Activar configuraciones

```bash
# Crear enlaces simbólicos
ln -s /etc/nginx/sites-available/proyecto1 /etc/nginx/sites-enabled/
ln -s /etc/nginx/sites-available/proyecto2 /etc/nginx/sites-enabled/
# ... etc

# Verificar configuración
nginx -t

# Reiniciar Nginx
systemctl restart nginx
```

---

## 📋 FASE 7: CONFIGURAR SSL (20 minutos)

### 7.1 Obtener certificados SSL (Let's Encrypt)

```bash
# Instalar Certbot (ya incluido en script)
apt install certbot python3-certbot-nginx -y

# Obtener certificados para todos los dominios
certbot --nginx -d proyecto1.tudominio.com
certbot --nginx -d proyecto2.tudominio.com
certbot --nginx -d proyecto3.tudominio.com
certbot --nginx -d proyecto4.tudominio.com
certbot --nginx -d proyecto5.tudominio.com
certbot --nginx -d proyecto6.tudominio.com
certbot --nginx -d opticaapp.tudominio.com

# Email para renovaciones
# Aceptar términos: Y
```

### 7.2 Renovación automática

```bash
# Verificar timer de renovación
systemctl status certbot.timer

# Probar renovación
certbot renew --dry-run
```

Los certificados se renuevan automáticamente cada 60 días.

---

## 📋 FASE 8: CONFIGURAR PM2 (15 minutos)

### 8.1 Iniciar todos los proyectos

```bash
# Proyecto 1
pm2 start /var/www/proyecto1/start.sh --name proyecto1

# Proyecto 2
pm2 start /var/www/proyecto2/start.sh --name proyecto2

# ... etc

# OpticaApp
pm2 start /var/www/opticaapp/start.sh --name opticaapp

# WhatsApp
pm2 start /var/www/whatsapp-server/server.js --name whatsapp
```

### 8.2 Configurar auto-inicio

```bash
# Guardar configuración actual
pm2 save

# Configurar inicio automático
pm2 startup

# Copiar y ejecutar el comando que aparece
# Ejemplo: sudo env PATH=$PATH:/usr/bin...
```

### 8.3 Ver estado

```bash
# Ver todos los procesos
pm2 status

# Debe mostrar:
# proyecto1    │ online │
# proyecto2    │ online │
# proyecto3    │ online │
# proyecto4    │ online │
# proyecto5    │ online │
# proyecto6    │ online │
# opticaapp    │ online │
# whatsapp     │ online │
```

---

## 📋 FASE 9: MIGRAR BASES DE DATOS (30 minutos)

### 9.1 Exportar desde Render

```bash
# Para cada proyecto en Render
pg_dump RENDER_DATABASE_URL > proyecto1_backup.sql
pg_dump RENDER_DATABASE_URL > proyecto2_backup.sql
# ... etc
```

### 9.2 Transferir a Contabo

```powershell
# Desde tu PC
scp proyecto1_backup.sql root@123.45.67.89:/root/
scp proyecto2_backup.sql root@123.45.67.89:/root/
# ... etc
```

### 9.3 Importar en Contabo

```bash
# En el servidor Contabo
psql -U proyecto1_user -d proyecto1_db < /root/proyecto1_backup.sql
psql -U proyecto2_user -d proyecto2_db < /root/proyecto2_backup.sql
# ... etc

# Verificar importación
psql -U proyecto1_user -d proyecto1_db -c "SELECT COUNT(*) FROM auth_user;"
```

---

## 📋 FASE 10: CONFIGURAR RESPALDOS (20 minutos)

### 10.1 Crear script de respaldo

```bash
# Script ya creado: backup_all.sh
chmod +x /root/backup_all.sh
```

El script respaldará:
- ✅ 7 bases de datos PostgreSQL
- ✅ Archivos de media de cada proyecto
- ✅ Sesiones de WhatsApp
- ✅ Configuraciones de Nginx

### 10.2 Configurar cron

```bash
# Editar crontab
crontab -e

# Agregar:
# Respaldo diario a las 2:00 AM
0 2 * * * /root/backup_all.sh

# Limpieza de respaldos antiguos (7 días)
0 3 * * * find /root/backups -type f -mtime +7 -delete
```

### 10.3 Probar respaldo manual

```bash
bash /root/backup_all.sh

# Verificar
ls -lh /root/backups/
```

---

## 📋 FASE 11: MONITOREO (15 minutos)

### 11.1 Instalar script de monitoreo

```bash
# Script ya creado: monitor_resources.sh
chmod +x /root/monitor_resources.sh
```

Monitorea:
- CPU, RAM, Disco
- Estado de servicios (Nginx, PostgreSQL, PM2)
- Envía alertas si >80% de uso

### 11.2 Configurar alertas por email

```bash
# Instalar mailutils
apt install mailutils -y

# Configurar email en monitor_resources.sh
nano /root/monitor_resources.sh
# ALERT_EMAIL="tu@email.com"
```

### 11.3 Ejecutar cada hora

```bash
crontab -e

# Agregar:
0 * * * * /root/monitor_resources.sh
```

---

## 📋 FASE 12: FIREWALL Y SEGURIDAD (10 minutos)

### 12.1 Configurar UFW

```bash
# Reiniciar firewall
ufw --force reset

# Reglas básicas
ufw default deny incoming
ufw default allow outgoing

# Permitir servicios necesarios
ufw allow 22/tcp     # SSH
ufw allow 80/tcp     # HTTP
ufw allow 443/tcp    # HTTPS
ufw allow 3000/tcp   # WhatsApp (solo si necesitas acceso externo)

# Activar
ufw enable

# Verificar
ufw status numbered
```

### 12.2 Cambiar puerto SSH (Recomendado)

```bash
# Editar configuración
nano /etc/ssh/sshd_config

# Cambiar:
Port 2222

# Reiniciar SSH
systemctl restart sshd

# Actualizar firewall
ufw allow 2222/tcp
ufw delete allow 22/tcp

# Ahora conectar con:
# ssh root@123.45.67.89 -p 2222
```

### 12.3 Configurar fail2ban

```bash
# Instalar
apt install fail2ban -y

# Configurar
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
nano /etc/fail2ban/jail.local

# Configurar:
[sshd]
enabled = true
maxretry = 3
bantime = 3600

# Iniciar
systemctl enable fail2ban
systemctl start fail2ban
```

---

## 📊 VERIFICACIÓN FINAL

### Checklist de validación:

```bash
# 1. Verificar servicios
systemctl status nginx
systemctl status postgresql
pm2 status

# 2. Verificar conectividad
curl http://localhost:8001  # proyecto1
curl http://localhost:8002  # proyecto2
# ... etc
curl http://localhost:8007  # opticaapp

# 3. Verificar bases de datos
psql -U proyecto1_user -d proyecto1_db -c "\dt"

# 4. Verificar SSL
curl https://proyecto1.tudominio.com
curl https://opticaapp.tudominio.com

# 5. Verificar WhatsApp
curl http://localhost:3000/health

# 6. Verificar recursos
htop
df -h
free -h
```

### Tabla de verificación:

| Componente | Puerto | Estado | URL |
|------------|--------|--------|-----|
| Nginx | 80/443 | ✅ | https://proyecto1.tudominio.com |
| Proyecto 1 | 8001 | ✅ | https://proyecto1.tudominio.com |
| Proyecto 2 | 8002 | ✅ | https://proyecto2.tudominio.com |
| Proyecto 3 | 8003 | ✅ | https://proyecto3.tudominio.com |
| Proyecto 4 | 8004 | ✅ | https://proyecto4.tudominio.com |
| Proyecto 5 | 8005 | ✅ | https://proyecto5.tudominio.com |
| Proyecto 6 | 8006 | ✅ | https://proyecto6.tudominio.com |
| OpticaApp | 8007 | ✅ | https://opticaapp.tudominio.com |
| WhatsApp | 3000 | ✅ | http://localhost:3000 |
| PostgreSQL | 5432 | ✅ | localhost |

---

## 🔧 COMANDOS ÚTILES

### PM2

```bash
# Ver estado
pm2 status

# Ver logs de un proyecto
pm2 logs proyecto1

# Ver logs de todos
pm2 logs

# Reiniciar un proyecto
pm2 restart proyecto1

# Reiniciar todos
pm2 restart all

# Detener un proyecto
pm2 stop proyecto1

# Eliminar un proyecto
pm2 delete proyecto1

# Monitorear en tiempo real
pm2 monit
```

### Nginx

```bash
# Verificar configuración
nginx -t

# Recargar configuración
nginx -s reload

# Reiniciar servicio
systemctl restart nginx

# Ver logs de error
tail -f /var/log/nginx/error.log

# Ver logs de acceso
tail -f /var/log/nginx/access.log
```

### PostgreSQL

```bash
# Conectar a base de datos
psql -U proyecto1_user -d proyecto1_db

# Ver bases de datos
psql -U postgres -c "\l"

# Respaldo manual
pg_dump -U proyecto1_user proyecto1_db > backup.sql

# Restaurar
psql -U proyecto1_user proyecto1_db < backup.sql

# Ver conexiones activas
psql -U postgres -c "SELECT * FROM pg_stat_activity;"
```

### Sistema

```bash
# Ver uso de recursos
htop

# Ver espacio en disco
df -h

# Ver uso de RAM
free -h

# Ver procesos de Python
ps aux | grep python

# Ver procesos de Node
ps aux | grep node

# Reiniciar servidor (cuidado)
reboot
```

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### Problema: Un proyecto no inicia

```bash
# Ver logs
pm2 logs proyecto1

# Verificar que el puerto no esté en uso
lsof -i :8001

# Reiniciar proyecto
pm2 restart proyecto1

# Si persiste, iniciar manualmente
cd /var/www/proyecto1
source venv/bin/activate
gunicorn proyecto1.wsgi:application --bind 0.0.0.0:8001
```

### Problema: Base de datos no conecta

```bash
# Verificar que PostgreSQL esté corriendo
systemctl status postgresql

# Verificar usuario y contraseña
psql -U proyecto1_user -d proyecto1_db

# Ver logs de PostgreSQL
tail -f /var/log/postgresql/postgresql-15-main.log

# Reiniciar PostgreSQL
systemctl restart postgresql
```

### Problema: SSL no funciona

```bash
# Verificar certificados
certbot certificates

# Renovar manualmente
certbot renew

# Ver logs de Certbot
tail -f /var/log/letsencrypt/letsencrypt.log

# Reconfigurar Nginx
certbot --nginx -d proyecto1.tudominio.com
```

### Problema: Servidor lento

```bash
# Ver uso de recursos
htop

# Ver procesos que más consumen
top

# Si un proyecto consume mucho, reiniciarlo
pm2 restart proyecto_pesado

# Liberar caché
sync; echo 3 > /proc/sys/vm/drop_caches

# Ver espacio en disco
df -h

# Limpiar logs antiguos
journalctl --vacuum-time=7d
```

---

## 💰 COSTOS MENSUALES

| Servicio | Costo |
|----------|-------|
| Contabo VPS 10 (12 meses) | €3.60 |
| Auto Backup (opcional) | €0.75 |
| **TOTAL** | **€4.35/mes** |

**vs Render con discos persistentes:**
- 7 proyectos × $2-5/mes = **$14-35/mes**
- **Ahorro**: $10-30/mes = **$120-360/año** 🎉

---

## 📈 PLAN DE CRECIMIENTO

### Si necesitas más recursos:

**Opción 1: Añadir Object Storage**
- +250 GB: €2.49/mes
- Para imágenes, videos, archivos

**Opción 2: Upgrade a VPS 20**
- 8 vCPU, 16 GB RAM, 300 GB SSD
- Costo: €7.20/mes
- Soporta 15-20 proyectos

**Opción 3: Múltiples VPS**
- VPS 1: Proyectos 1-4
- VPS 2: Proyectos 5-7 + WhatsApp
- Load balancer con Nginx

**Opción 4: Dedicated Server**
- Cuando tengas 30+ proyectos
- €50-100/mes
- Recursos dedicados

---

## 📞 SOPORTE Y RECURSOS

- **Contabo Support**: support@contabo.com
- **Documentación PostgreSQL**: https://www.postgresql.org/docs/
- **Documentación Nginx**: https://nginx.org/en/docs/
- **PM2 Docs**: https://pm2.keymetrics.io/
- **Django Docs**: https://docs.djangoproject.com/

---

## ✅ PRÓXIMOS PASOS

1. ✅ Contratar Contabo VPS
2. ✅ Esperar email con credenciales
3. ✅ Ejecutar scripts de instalación
4. ✅ Subir proyectos
5. ✅ Configurar dominios
6. ✅ Migrar bases de datos
7. ✅ Configurar respaldos
8. ✅ Monitorear y optimizar

**Tiempo total estimado**: 4-6 horas (primera vez)

**¡Todo listo para producción 24/7!** 🚀
