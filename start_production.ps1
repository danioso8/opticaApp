# Script para mantener WhatsApp Server + ngrok corriendo
# Ejecutar en PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OPTICAAPP - SERVIDOR PRODUCCIÓN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que el servidor de WhatsApp esté corriendo
Write-Host "🔍 Verificando servidor de WhatsApp..." -ForegroundColor Yellow

$nodeProcess = Get-Process node -ErrorAction SilentlyContinue
if (-not $nodeProcess) {
    Write-Host "⚠️  Servidor de WhatsApp no está corriendo. Iniciando..." -ForegroundColor Yellow
    
    # Iniciar servidor de WhatsApp en segundo plano
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'd:\ESCRITORIO\OpticaApp\whatsapp-server'; node server.js" -WindowStyle Minimized
    
    Write-Host "✅ Servidor de WhatsApp iniciado" -ForegroundColor Green
    Start-Sleep -Seconds 5
} else {
    Write-Host "✅ Servidor de WhatsApp ya está corriendo (PID: $($nodeProcess.Id))" -ForegroundColor Green
}

Write-Host ""

# Verificar ngrok
Write-Host "🔍 Verificando ngrok..." -ForegroundColor Yellow

if (Get-Command ngrok -ErrorAction SilentlyContinue) {
    Write-Host "✅ ngrok está instalado" -ForegroundColor Green
    
    # Verificar si ngrok ya está corriendo
    $ngrokProcess = Get-Process ngrok -ErrorAction SilentlyContinue
    
    if ($ngrokProcess) {
        Write-Host "✅ Túnel ngrok ya está activo" -ForegroundColor Green
        
        # Obtener la URL pública
        try {
            $tunnels = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -ErrorAction SilentlyContinue
            if ($tunnels.tunnels.Count -gt 0) {
                $publicUrl = $tunnels.tunnels[0].public_url
                Write-Host ""
                Write-Host "🌐 URL PÚBLICA DEL SERVIDOR:" -ForegroundColor Green
                Write-Host "   $publicUrl" -ForegroundColor Cyan
                Write-Host ""
                Write-Host "📋 Configura esta URL en Render:" -ForegroundColor Yellow
                Write-Host "   Variable: WHATSAPP_SERVER_URL" -ForegroundColor White
                Write-Host "   Valor: $publicUrl" -ForegroundColor Cyan
            }
        } catch {
            Write-Host "⚠️  No se pudo obtener la URL pública automáticamente" -ForegroundColor Yellow
            Write-Host "   Ve a http://localhost:4040 para ver los túneles activos" -ForegroundColor White
        }
    } else {
        Write-Host "⚠️  ngrok no está corriendo. Iniciando túnel..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "🚀 INICIANDO TÚNEL NGROK..." -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Yellow
        Write-Host "   • Esta ventana mostrará la URL pública" -ForegroundColor White
        Write-Host "   • Copia la URL que empieza con 'https://'" -ForegroundColor White
        Write-Host "   • Configúrala en Render como WHATSAPP_SERVER_URL" -ForegroundColor White
        Write-Host "   • NO CIERRES esta ventana" -ForegroundColor White
        Write-Host ""
        Start-Sleep -Seconds 3
        
        # Iniciar ngrok
        ngrok http 3000
    }
} else {
    Write-Host "❌ ngrok no está instalado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Para instalar ngrok:" -ForegroundColor Yellow
    Write-Host "   1. Ejecuta: .\setup_ngrok.ps1" -ForegroundColor White
    Write-Host "   O manualmente:" -ForegroundColor White
    Write-Host "   2. Ve a https://ngrok.com/download" -ForegroundColor White
    Write-Host "   3. Descarga e instala ngrok" -ForegroundColor White
    Write-Host "   4. Ejecuta: ngrok config add-authtoken TU_TOKEN" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ESTADO DEL SISTEMA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Mostrar procesos activos
Write-Host "📊 Procesos activos:" -ForegroundColor Yellow
Write-Host ""

if (Get-Process node -ErrorAction SilentlyContinue) {
    Write-Host "   ✅ WhatsApp Server (Node.js)" -ForegroundColor Green
} else {
    Write-Host "   ❌ WhatsApp Server NO está corriendo" -ForegroundColor Red
}

if (Get-Process ngrok -ErrorAction SilentlyContinue) {
    Write-Host "   ✅ Túnel ngrok" -ForegroundColor Green
} else {
    Write-Host "   ❌ Túnel ngrok NO está corriendo" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔗 URLs útiles:" -ForegroundColor Yellow
Write-Host "   • Dashboard ngrok: http://localhost:4040" -ForegroundColor White
Write-Host "   • Logs WhatsApp: D:\ESCRITORIO\OpticaApp\whatsapp-server" -ForegroundColor White
Write-Host ""
Write-Host "💡 Comandos útiles:" -ForegroundColor Yellow
Write-Host "   • Ver procesos: Get-Process node, ngrok" -ForegroundColor White
Write-Host "   • Detener todo: Stop-Process -Name node,ngrok -Force" -ForegroundColor White
Write-Host "   • Reiniciar: Ejecuta este script nuevamente" -ForegroundColor White
Write-Host ""
