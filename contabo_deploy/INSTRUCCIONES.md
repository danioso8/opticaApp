# INSTRUCCIONES DE DESPLIEGUE EN CONTABO

## PASO 1: Subir archivos al servidor

Desde PowerShell en tu PC:

```powershell
# Reemplaza 123.45.67.89 con la IP de tu servidor Contabo

# Subir scripts de instalaciÃ³n
scp install_contabo.sh root@123.45.67.89:/root/
scp start_whatsapp.sh root@123.45.67.89:/root/

# Subir archivos de WhatsApp
scp server.js root@123.45.67.89:/root/
scp package.json root@123.45.67.89:/root/
```

## PASO 2: Conectarte al servidor

```powershell
ssh root@123.45.67.89
```

## PASO 3: Ejecutar instalaciÃ³n

```bash
# Dar permisos de ejecuciÃ³n
chmod +x /root/install_contabo.sh
chmod +x /root/start_whatsapp.sh

# Ejecutar instalaciÃ³n
bash /root/install_contabo.sh
```

## PASO 4: Mover archivos a la carpeta correcta

```bash
# Mover server.js y package.json
mv /root/server.js /root/whatsapp-server/
mv /root/package.json /root/whatsapp-server/

# El script de instalaciÃ³n ya instalÃ³ las dependencias
```

## PASO 5: Iniciar servidor

```bash
bash /root/start_whatsapp.sh
```

## PASO 6: Escanear cÃ³digo QR

1. El servidor mostrarÃ¡ un cÃ³digo QR en la terminal
2. Abre WhatsApp en tu celular
3. Ve a "Dispositivos vinculados"
4. Escanea el cÃ³digo QR
5. Â¡Listo! El servidor quedarÃ¡ conectado 24/7

## PASO 7: Configurar en Render

En tu aplicaciÃ³n de Render, configura:

```
Variable: WHATSAPP_SERVER_URL
Valor: http://TU_IP_CONTABO:3000
```

## COMANDOS ÃšTILES

```bash
# Ver estado del servidor
pm2 status

# Ver logs
pm2 logs whatsapp-opticaapp

# Reiniciar servidor
pm2 restart whatsapp-opticaapp

# Detener servidor
pm2 stop whatsapp-opticaapp
```

## PROBAR CONEXIÃ“N

Desde PowerShell en tu PC:

```powershell
$body = @{
    organization_id = 23
    phone = "3009787566"
    message = "Prueba desde Contabo"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://TU_IP_CONTABO:3000/send-message" `
    -Method POST `
    -Headers @{"x-api-key"="opticaapp_2026_whatsapp_baileys_secret_key_12345"} `
    -Body $body `
    -ContentType "application/json"
```

Â¡Ã‰xito! ðŸš€
