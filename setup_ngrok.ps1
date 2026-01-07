# Script de instalacion de ngrok para OpticaApp
# Ejecutar como Administrador

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INSTALACION DE NGROK" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si ngrok ya esta instalado
if (Get-Command ngrok -ErrorAction SilentlyContinue) {
    Write-Host "[OK] ngrok ya esta instalado" -ForegroundColor Green
    ngrok version
} else {
    Write-Host "[!] ngrok no esta instalado. Instalando..." -ForegroundColor Yellow
    Write-Host ""
    
    # Intentar instalar con winget
    Write-Host "Intentando instalar con winget..." -ForegroundColor Yellow
    try {
        winget install --id ngrok.ngrok -e --silent
        Write-Host "[OK] ngrok instalado correctamente" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] No se pudo instalar con winget" -ForegroundColor Red
        Write-Host ""
        Write-Host "INSTALACION MANUAL:" -ForegroundColor Yellow
        Write-Host "1. Ve a: https://ngrok.com/download" -ForegroundColor White
        Write-Host "2. Descarga ngrok para Windows" -ForegroundColor White
        Write-Host "3. Descomprime el archivo" -ForegroundColor White
        Write-Host "4. Mueve ngrok.exe a C:\Windows\System32\" -ForegroundColor White
        Write-Host ""
        Read-Host "Presiona Enter cuando hayas instalado ngrok manualmente"
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que ngrok este disponible ahora
if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] ngrok no esta disponible" -ForegroundColor Red
    Write-Host "Por favor, instala ngrok manualmente e intentalo de nuevo" -ForegroundColor Yellow
    exit 1
}

Write-Host "[!] NECESITAS UN AUTHTOKEN DE NGROK" -ForegroundColor Yellow
Write-Host ""
Write-Host "Pasos:" -ForegroundColor Cyan
Write-Host "1. Ve a: https://dashboard.ngrok.com/signup" -ForegroundColor White
Write-Host "2. Crea una cuenta gratis" -ForegroundColor White
Write-Host "3. Ve a: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor White
Write-Host "4. Copia tu authtoken" -ForegroundColor White
Write-Host ""

$authtoken = Read-Host "Pega tu authtoken aqui (o presiona Enter para configurarlo despues)"

if ($authtoken) {
    Write-Host ""
    Write-Host "Configurando authtoken..." -ForegroundColor Yellow
    ngrok config add-authtoken $authtoken
    Write-Host "[OK] Authtoken configurado" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[!] Authtoken no configurado" -ForegroundColor Yellow
    Write-Host "Configura manualmente con: ngrok config add-authtoken TU_TOKEN" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INICIAR TUNEL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Para iniciar el tunel a tu servidor de WhatsApp:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ngrok http 3000" -ForegroundColor Green
Write-Host ""
Write-Host "Esto mostrara una URL publica como:" -ForegroundColor Yellow
Write-Host "  https://abcd-1234.ngrok-free.app" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANTE:" -ForegroundColor Yellow
Write-Host "  - Copia esa URL completa" -ForegroundColor White
Write-Host "  - En Render, configura la variable de entorno:" -ForegroundColor White
Write-Host "    WHATSAPP_SERVER_URL=https://tu-url.ngrok-free.app" -ForegroundColor Cyan
Write-Host ""

$startNow = Read-Host "Quieres iniciar el tunel ahora? (s/n)"

if ($startNow -eq 's' -or $startNow -eq 'S') {
    Write-Host ""
    Write-Host "[!] INICIANDO TUNEL..." -ForegroundColor Green
    Write-Host "Presiona Ctrl+C para detener" -ForegroundColor Yellow
    Write-Host ""
    Start-Sleep -Seconds 2
    ngrok http 3000
} else {
    Write-Host ""
    Write-Host "Puedes iniciar el tunel cuando quieras con:" -ForegroundColor Cyan
    Write-Host "  ngrok http 3000" -ForegroundColor Green
    Write-Host ""
}

Write-Host ""
Write-Host "PLANES DE NGROK:" -ForegroundColor Cyan
Write-Host ""
Write-Host "GRATIS:" -ForegroundColor Yellow
Write-Host "  - La URL cambia cada vez que reinicias" -ForegroundColor White
Write-Host "  - 40 conexiones por minuto" -ForegroundColor White
Write-Host "  - Perfecto para desarrollo" -ForegroundColor White
Write-Host ""
Write-Host "PAGADO (8 USD/mes):" -ForegroundColor Yellow
Write-Host "  - URL fija (no cambia)" -ForegroundColor White
Write-Host "  - Sin limites de conexion" -ForegroundColor White
Write-Host "  - Tunel siempre activo" -ForegroundColor White
Write-Host ""
Write-Host "Mas info: https://ngrok.com/pricing" -ForegroundColor Cyan
Write-Host ""
