# Script para verificar y restaurar sesion de WhatsApp en produccion
# Ejecutar: .\check_whatsapp_server.ps1

$SERVER = "root@84.247.129.180"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "VERIFICANDO SERVIDOR WHATSAPP EN PRODUCCION" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Servidor: 84.247.129.180" -ForegroundColor White
Write-Host ""

# Funcion para ejecutar comandos SSH
function Invoke-SSHCommand {
    param(
        [string]$Command,
        [string]$Description
    )
    
    Write-Host $Description -ForegroundColor Cyan
    Write-Host ""
    
    try {
        $result = ssh $SERVER $Command 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host $result -ForegroundColor Green
        } else {
            Write-Host $result -ForegroundColor Red
        }
    } catch {
        Write-Host "Error ejecutando comando: $_" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host ("----------------------------------------------------------------------") -ForegroundColor DarkGray
    Write-Host ""
}

# Verificar estado de PM2
Write-Host "ESTADO DE SERVICIOS" -ForegroundColor Yellow
Write-Host ""
Invoke-SSHCommand -Command "pm2 status whatsapp-server" -Description "Estado del servidor WhatsApp"

# Ver sesiones guardadas
Write-Host "SESIONES GUARDADAS" -ForegroundColor Yellow
Write-Host ""
Invoke-SSHCommand -Command "ls -la /var/www/whatsapp-server/auth_sessions/" -Description "Archivos de sesion"

# Contar sesiones
Invoke-SSHCommand -Command "ls /var/www/whatsapp-server/auth_sessions/ | wc -l" -Description "Numero de sesiones"

# Ver logs recientes
Write-Host "LOGS RECIENTES (ultimas 30 lineas)" -ForegroundColor Yellow
Write-Host ""
Invoke-SSHCommand -Command "pm2 logs whatsapp-server --lines 30 --nostream" -Description "Logs del servidor"

# Resumen y acciones
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "ACCIONES DISPONIBLES" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Reiniciar servidor WhatsApp:" -ForegroundColor White
Write-Host "   ssh $SERVER `"pm2 restart whatsapp-server`"" -ForegroundColor Cyan
Write-Host ""

Write-Host "2. Ver logs en tiempo real:" -ForegroundColor White
Write-Host "   ssh $SERVER `"pm2 logs whatsapp-server`"" -ForegroundColor Cyan
Write-Host ""

Write-Host "3. Limpiar sesión corrupta (org 23):" -ForegroundColor White
Write-Host "   ssh $SERVER `"rm -rf /var/www/whatsapp-server/auth_sessions/23 && pm2 restart whatsapp-server`"" -ForegroundColor Cyan
Write-Host ""

Write-Host "4. Conectar al servidor (SSH interactivo):" -ForegroundColor White
Write-Host "   ssh $SERVER" -ForegroundColor Cyan
Write-Host ""

Write-Host "5. Acceder al dashboard de WhatsApp:" -ForegroundColor White
Write-Host "   http://84.247.129.180/dashboard/whatsapp-baileys/" -ForegroundColor Cyan
Write-Host ""

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Preguntar si quiere ejecutar alguna accion
Write-Host "Deseas ejecutar alguna accion? (1-5 / N para salir): " -NoNewline -ForegroundColor Yellow
$action = Read-Host

switch ($action) {
    "1" {
        Write-Host ""
        Write-Host "Reiniciando servidor WhatsApp..." -ForegroundColor Yellow
        ssh $SERVER "pm2 restart whatsapp-server"
        Write-Host "Servidor reiniciado" -ForegroundColor Green
    }
    "2" {
        Write-Host ""
        Write-Host "Mostrando logs en tiempo real (Ctrl+C para salir)..." -ForegroundColor Yellow
        ssh $SERVER "pm2 logs whatsapp-server"
    }
    "3" {
        Write-Host ""
        Write-Host "Esto eliminara la sesion de la organizacion 23" -ForegroundColor Yellow
        Write-Host "Estas seguro? (S/N): " -NoNewline
        $confirm = Read-Host
        
        if ($confirm -eq "S" -or $confirm -eq "s") {
            Write-Host ""
            Write-Host "Limpiando sesion y reiniciando..." -ForegroundColor Yellow
            ssh $SERVER "rm -rf /var/www/whatsapp-server/auth_sessions/23 && pm2 restart whatsapp-server"
            Write-Host "Sesion limpiada. Ahora puedes reconectar desde el dashboard" -ForegroundColor Green
        } else {
            Write-Host "Cancelado" -ForegroundColor Red
        }
    }
    "4" {
        Write-Host ""
        Write-Host "Conectando al servidor..." -ForegroundColor Yellow
        ssh $SERVER
    }
    "5" {
        Write-Host ""
        Write-Host "Abriendo navegador..." -ForegroundColor Yellow
        Start-Process "http://84.247.129.180/dashboard/whatsapp-baileys/"
    }
    default {
        Write-Host ""
        Write-Host "
