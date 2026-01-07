# Script para preparar archivos para subir a Contabo
# Ejecutar en PowerShell desde D:\ESCRITORIO\OpticaApp

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  PREPARAR ARCHIVOS PARA CONTABO" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Crear carpeta temporal
$tempDir = ".\contabo_deploy"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

Write-Host "[1/4] Copiando archivos necesarios..." -ForegroundColor Yellow

# Copiar servidor de WhatsApp (sin node_modules ni sesiones)
Copy-Item ".\whatsapp-server\server.js" -Destination "$tempDir\server.js"
Copy-Item ".\whatsapp-server\package.json" -Destination "$tempDir\package.json"

Write-Host "[OK] Archivos copiados" -ForegroundColor Green
Write-Host ""

Write-Host "[2/4] Copiando scripts de instalacion..." -ForegroundColor Yellow

# Copiar scripts de instalación
Copy-Item ".\install_contabo.sh" -Destination "$tempDir\install_contabo.sh"
Copy-Item ".\start_whatsapp.sh" -Destination "$tempDir\start_whatsapp.sh"

Write-Host "[OK] Scripts copiados" -ForegroundColor Green
Write-Host ""

Write-Host "[3/4] Creando archivo de instrucciones..." -ForegroundColor Yellow

# Crear README con instrucciones
$instructions = @"
# INSTRUCCIONES DE DESPLIEGUE EN CONTABO

## PASO 1: Subir archivos al servidor

Desde PowerShell en tu PC:

``````powershell
# Reemplaza 123.45.67.89 con la IP de tu servidor Contabo

# Subir scripts de instalación
scp install_contabo.sh root@123.45.67.89:/root/
scp start_whatsapp.sh root@123.45.67.89:/root/

# Subir archivos de WhatsApp
scp server.js root@123.45.67.89:/root/
scp package.json root@123.45.67.89:/root/
``````

## PASO 2: Conectarte al servidor

``````powershell
ssh root@123.45.67.89
``````

## PASO 3: Ejecutar instalación

``````bash
# Dar permisos de ejecución
chmod +x /root/install_contabo.sh
chmod +x /root/start_whatsapp.sh

# Ejecutar instalación
bash /root/install_contabo.sh
``````

## PASO 4: Mover archivos a la carpeta correcta

``````bash
# Mover server.js y package.json
mv /root/server.js /root/whatsapp-server/
mv /root/package.json /root/whatsapp-server/

# El script de instalación ya instaló las dependencias
``````

## PASO 5: Iniciar servidor

``````bash
bash /root/start_whatsapp.sh
``````

## PASO 6: Escanear código QR

1. El servidor mostrará un código QR en la terminal
2. Abre WhatsApp en tu celular
3. Ve a "Dispositivos vinculados"
4. Escanea el código QR
5. ¡Listo! El servidor quedará conectado 24/7

## PASO 7: Configurar en Render

En tu aplicación de Render, configura:

``````
Variable: WHATSAPP_SERVER_URL
Valor: http://TU_IP_CONTABO:3000
``````

## COMANDOS ÚTILES

``````bash
# Ver estado del servidor
pm2 status

# Ver logs
pm2 logs whatsapp-opticaapp

# Reiniciar servidor
pm2 restart whatsapp-opticaapp

# Detener servidor
pm2 stop whatsapp-opticaapp
``````

## PROBAR CONEXIÓN

Desde PowerShell en tu PC:

``````powershell
`$body = @{
    organization_id = 23
    phone = "3009787566"
    message = "Prueba desde Contabo"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://TU_IP_CONTABO:3000/send-message" ``
    -Method POST ``
    -Headers @{"x-api-key"="opticaapp_2026_whatsapp_baileys_secret_key_12345"} ``
    -Body `$body ``
    -ContentType "application/json"
``````

¡Éxito! 🚀
"@

$instructions | Out-File -FilePath "$tempDir\INSTRUCCIONES.md" -Encoding UTF8

Write-Host "[OK] Instrucciones creadas" -ForegroundColor Green
Write-Host ""

Write-Host "[4/4] Listando archivos preparados..." -ForegroundColor Yellow
Write-Host ""
Get-ChildItem $tempDir | Format-Table Name, Length -AutoSize

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  ARCHIVOS LISTOS" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Archivos en: $tempDir" -ForegroundColor Green
Write-Host ""
Write-Host "SIGUIENTE PASO:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Contrata tu VPS en Contabo:" -ForegroundColor White
Write-Host "   https://contabo.com/" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Recibirás email con:" -ForegroundColor White
Write-Host "   - IP del servidor: 123.45.67.89" -ForegroundColor Cyan
Write-Host "   - Usuario: root" -ForegroundColor Cyan
Write-Host "   - Contraseña temporal" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Abre INSTRUCCIONES.md y sigue los pasos" -ForegroundColor White
Write-Host ""
Write-Host "4. Comando rápido para subir todo:" -ForegroundColor White
Write-Host ""
Write-Host "   cd $tempDir" -ForegroundColor Green
Write-Host "   scp * root@TU_IP_CONTABO:/root/" -ForegroundColor Green
Write-Host ""
