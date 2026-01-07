# 🚀 GUÍA RÁPIDA - DESPLIEGUE EN CONTABO

## 📋 CHECKLIST DE EJECUCIÓN

### PASO 1: Contratar Contabo (5 min)
- [ ] Ir a https://contabo.com/es/vps/cloud-vps-10/
- [ ] Seleccionar 12 meses (€3.60/mes)
- [ ] Región: Unión Europea
- [ ] Almacenamiento: 150 GB SSD
- [ ] Sistema: Ubuntu 22.04 LTS
- [ ] Completar pago
- [ ] Esperar email con credenciales (1-24h)

### PASO 2: Subir scripts al servidor (5 min)

```powershell
# Desde tu PC
cd D:\ESCRITORIO\OpticaApp\contabo_deploy

# Subir todos los scripts (reemplaza IP)
scp *.sh root@TU_IP_CONTABO:/root/
```

### PASO 3: Conectar y ejecutar instalación (30 min)

```bash
# Conectar
ssh root@TU_IP_CONTABO

# Dar permisos
chmod +x /root/*.sh

# Ejecutar instalación del stack
bash /root/install_full_stack.sh
# Espera ~20 minutos

# Crear bases de datos
bash /root/create_databases.sh

# Ver credenciales creadas
cat /root/database_credentials.txt
```

### PASO 4: Subir tus proyectos (variable)

```bash
# Opción A: Git (recomendado)
cd /var/www
git clone https://github.com/tu_usuario/proyecto1.git proyecto1
git clone https://github.com/tu_usuario/proyecto2.git proyecto2
# ... etc

# Opción B: Desde tu PC con SCP
# scp -r D:\MIS_PROYECTOS\proyecto1 root@TU_IP:/var/www/
```

### PASO 5: Desplegar cada proyecto (10-15 min c/u)

```bash
# Proyecto 1
bash /root/deploy_project.sh proyecto1 8001 proyecto1_db proyecto1_user

# Proyecto 2
bash /root/deploy_project.sh proyecto2 8002 proyecto2_db proyecto2_user

# Proyecto 3
bash /root/deploy_project.sh proyecto3 8003 proyecto3_db proyecto3_user

# Proyecto 4
bash /root/deploy_project.sh proyecto4 8004 proyecto4_db proyecto4_user

# Proyecto 5
bash /root/deploy_project.sh proyecto5 8005 proyecto5_db proyecto5_user

# Proyecto 6
bash /root/deploy_project.sh proyecto6 8006 proyecto6_db proyecto6_user

# OpticaApp
bash /root/deploy_project.sh opticaapp 8007 opticaapp_db opticaapp_user

# Verificar que todos estén corriendo
pm2 status
```

### PASO 6: Configurar dominios DNS (10 min)

En tu proveedor de DNS (ej: Namecheap, GoDaddy):

```
Tipo A:
proyecto1.tudominio.com  →  TU_IP_CONTABO
proyecto2.tudominio.com  →  TU_IP_CONTABO
proyecto3.tudominio.com  →  TU_IP_CONTABO
proyecto4.tudominio.com  →  TU_IP_CONTABO
proyecto5.tudominio.com  →  TU_IP_CONTABO
proyecto6.tudominio.com  →  TU_IP_CONTABO
opticaapp.tudominio.com  →  TU_IP_CONTABO
```

Espera 5-60 min para propagación DNS.

### PASO 7: Configurar Nginx (10 min)

```bash
# Ejecutar script de configuración
bash /root/configure_nginx.sh

# Te pedirá tu dominio base
# Ejemplo: tudominio.com

# Verificar
nginx -t

# Ver sitios activos
ls -la /etc/nginx/sites-enabled/
```

### PASO 8: Instalar SSL (20 min)

```bash
# Para cada dominio
certbot --nginx -d proyecto1.tudominio.com
certbot --nginx -d proyecto2.tudominio.com
certbot --nginx -d proyecto3.tudominio.com
certbot --nginx -d proyecto4.tudominio.com
certbot --nginx -d proyecto5.tudominio.com
certbot --nginx -d proyecto6.tudominio.com
certbot --nginx -d opticaapp.tudominio.com

# Email: tu@email.com
# Aceptar términos: Y
# Redirect HTTP a HTTPS: 2 (Yes)
```

### PASO 9: Configurar WhatsApp (15 min)

```bash
# Subir servidor WhatsApp
cd /var/www
mkdir whatsapp-server
# Copiar server.js y package.json

cd whatsapp-server
npm install

# Iniciar con PM2
pm2 start server.js --name whatsapp

# Ver logs para QR
pm2 logs whatsapp

# Escanear QR con tu celular
# WhatsApp > Dispositivos vinculados > Vincular dispositivo
```

### PASO 10: Configurar respaldos (10 min)

```bash
# Configurar cron para respaldos automáticos
crontab -e

# Agregar estas líneas:
0 2 * * * /root/backup_all.sh
0 3 * * * find /root/backups -type d -mtime +7 -delete
0 * * * * /root/monitor_resources.sh

# Guardar y salir
```

### PASO 11: Migrar datos de Render (opcional, 30 min)

```bash
# Exportar desde Render
pg_dump RENDER_DATABASE_URL > proyecto1.sql

# Transferir a Contabo
scp proyecto1.sql root@TU_IP:/root/

# Importar en Contabo
psql -U proyecto1_user -d proyecto1_db < /root/proyecto1.sql

# Repetir para cada proyecto
```

---

## ✅ VERIFICACIÓN FINAL

```bash
# Ver todos los servicios
pm2 status
# Deben estar todos "online"

# Verificar Nginx
systemctl status nginx

# Verificar PostgreSQL
systemctl status postgresql

# Probar dominios
curl https://proyecto1.tudominio.com
curl https://opticaapp.tudominio.com

# Ver recursos del servidor
htop
df -h
free -h
```

---

## 🎯 RESUMEN DE COMANDOS

```bash
# Instalar stack
bash install_full_stack.sh

# Crear BDs
bash create_databases.sh

# Desplegar proyecto
bash deploy_project.sh NOMBRE PUERTO DB_NAME DB_USER

# Configurar Nginx
bash configure_nginx.sh

# Instalar SSL
certbot --nginx -d dominio.com

# Respaldo manual
bash backup_all.sh

# Ver estado
pm2 status
pm2 logs PROYECTO
```

---

## 💾 ARCHIVOS IMPORTANTES

```
/root/database_credentials.txt  - Credenciales de BDs
/root/backups/                  - Respaldos automáticos
/var/log/monitor_resources.log  - Log de monitoreo
/var/www/PROYECTO/logs/         - Logs de cada proyecto
/etc/nginx/sites-available/     - Configs de Nginx
```

---

## 📞 SOPORTE

- Contabo: support@contabo.com
- Documentación completa: GUIA_COMPLETA_CONTABO_MULTIPROYECTO.md
- Checklist detallado: CHECKLIST_DESPLIEGUE.md

---

## 🚀 ¡LISTO!

Tiempo total estimado: **4-6 horas** (primera vez)

**Todos tus proyectos corriendo 24/7 en un solo servidor por €3.60/mes** 🎉
