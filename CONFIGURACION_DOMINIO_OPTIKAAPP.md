# Configuración del Dominio optikaapp.com en Contabo

## Paso 1: Configurar DNS

En tu proveedor de dominio (donde compraste optikaapp.com), configura estos registros DNS:

```
Tipo    Nombre              Valor                   TTL
A       @                   84.247.129.180          3600
A       www                 84.247.129.180          3600
CNAME   demo                optikaapp.com           3600
```

## Paso 2: Configurar Nginx en Contabo

1. **Conectar al servidor:**
```bash
ssh root@84.247.129.180
```

2. **Crear configuración de Nginx para optikaapp.com:**
```bash
nano /etc/nginx/sites-available/optikaapp
```

3. **Agregar esta configuración:**
```nginx
server {
    listen 80;
    server_name optikaapp.com www.optikaapp.com demo.optikaapp.com;
    
    # Redirigir HTTP a HTTPS (después de configurar SSL)
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name optikaapp.com www.optikaapp.com demo.optikaapp.com;
    
    # SSL Certificates (configurar con Certbot)
    ssl_certificate /etc/letsencrypt/live/optikaapp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/optikaapp.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Logs
    access_log /var/log/nginx/optikaapp_access.log;
    error_log /var/log/nginx/optikaapp_error.log;
    
    # Client upload size
    client_max_body_size 100M;
    
    # Static files
    location /static/ {
        alias /var/www/opticaapp/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/opticaapp/media/;
        expires 7d;
    }
    
    # Proxy to Daphne (Django)
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_redirect off;
        proxy_buffering off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
```

4. **Habilitar el sitio:**
```bash
ln -s /etc/nginx/sites-available/optikaapp /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## Paso 3: Configurar SSL con Let's Encrypt

1. **Instalar Certbot:**
```bash
apt update
apt install certbot python3-certbot-nginx -y
```

2. **Obtener certificado SSL:**
```bash
certbot --nginx -d optikaapp.com -d www.optikaapp.com -d demo.optikaapp.com
```

3. **Configurar renovación automática:**
```bash
certbot renew --dry-run
```

## Paso 4: Actualizar Django Settings

En `/var/www/opticaapp/config/settings.py`:

```python
# Allowed hosts
ALLOWED_HOSTS = [
    'optikaapp.com',
    'www.optikaapp.com',
    'demo.optikaapp.com',
    '84.247.129.180',
    'localhost',
    '127.0.0.1',
]

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://optikaapp.com',
    'https://www.optikaapp.com',
    'https://demo.optikaapp.com',
]

# Secure settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

## Paso 5: Crear Cuenta Demo

```bash
cd /var/www/opticaapp
source venv/bin/activate
python manage.py setup_demo
```

## Paso 6: Recargar Aplicación

```bash
systemctl restart opticaapp
systemctl status opticaapp
```

## Paso 7: Verificar

1. Visita https://optikaapp.com - Debe cargar la landing page
2. Visita https://optikaapp.com/dashboard/login/ - Debe cargar el login
3. Login con: demo@optikaapp.com / demo123

## Paso 8: Optimizaciones Adicionales

### Configurar compresión Gzip en Nginx:
```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
```

### Configurar cache de static files:
```bash
# En Django settings
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
```

### Monitoreo:
```bash
# Ver logs en tiempo real
tail -f /var/log/nginx/optikaapp_access.log
tail -f /var/log/nginx/optikaapp_error.log
journalctl -u opticaapp -f
```

## Troubleshooting

### Si el dominio no resuelve:
```bash
# Verificar DNS
dig optikaapp.com
nslookup optikaapp.com
```

### Si hay error 502 Bad Gateway:
```bash
# Verificar que Daphne esté corriendo
systemctl status opticaapp
netstat -tlnp | grep 8000
```

### Si hay error de permisos:
```bash
chown -R www-data:www-data /var/www/opticaapp/media
chown -R www-data:www-data /var/www/opticaapp/staticfiles
```

## Checklist Final

- [ ] DNS configurado y propagado (puede tomar 24-48 horas)
- [ ] Nginx configurado y corriendo
- [ ] SSL certificado instalado
- [ ] Django settings actualizado
- [ ] Cuenta demo creada
- [ ] Aplicación reiniciada
- [ ] Landing page cargando correctamente
- [ ] Login funcional
- [ ] Demo accesible

## Contacto de Soporte

Si necesitas ayuda:
- Email: soporte@optikaapp.com
- WhatsApp: +57 300 123 4567
