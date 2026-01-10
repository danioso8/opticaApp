# Subiendo archivos de configuración
scp config/settings.py root@84.247.129.180:/var/www/opticaapp/config/
scp config/urls.py root@84.247.129.180:/var/www/opticaapp/config/

# Subiendo apps principales
scp -r apps/public root@84.247.129.180:/var/www/opticaapp/apps/
scp -r apps/dashboard root@84.247.129.180:/var/www/opticaapp/apps/
scp -r apps/organizations root@84.247.129.180:/var/www/opticaapp/apps/
scp -r apps/users root@84.247.129.180:/var/www/opticaapp/apps/

# Reiniciando
ssh root@84.247.129.180 'pm2 restart opticaapp && pm2 save'
