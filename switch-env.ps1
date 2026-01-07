# Script para cambiar entre ambiente de desarrollo y produccion
# Uso: .\switch-env.ps1 dev   (para desarrollo)
#      .\switch-env.ps1 prod  (para produccion)

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "prod")]
    [string]$Environment
)

$envFile = ".env"
$devFile = ".env.local"
$prodFile = ".env.production"

if ($Environment -eq "dev") {
    Write-Host "Cambiando a ambiente de DESARROLLO..." -ForegroundColor Cyan
    
    if (Test-Path $devFile) {
        Copy-Item $devFile $envFile -Force
        Write-Host "[OK] Archivo .env configurado para DESARROLLO LOCAL" -ForegroundColor Green
        Write-Host "   Base de datos: SQLite (db.sqlite3)" -ForegroundColor Yellow
        Write-Host "   Emails: Se mostraran en consola" -ForegroundColor Yellow
        Write-Host "   URL: http://localhost:8000" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "[!] RECUERDA: Estas trabajando en LOCAL - no afecta a produccion" -ForegroundColor Magenta
    } else {
        Write-Host "[ERROR] Archivo $devFile no encontrado" -ForegroundColor Red
    }
}
elseif ($Environment -eq "prod") {
    Write-Host "Cambiando a ambiente de PRODUCCION..." -ForegroundColor Yellow
    
    $confirmation = Read-Host "[!] Estas seguro de que quieres conectar a PRODUCCION? (escribe 'SI' para confirmar)"
    
    if ($confirmation -eq "SI") {
        if (Test-Path $prodFile) {
            Copy-Item $prodFile $envFile -Force
            Write-Host "[OK] Archivo .env configurado para PRODUCCION" -ForegroundColor Green
            Write-Host "   Base de datos: PostgreSQL (Render/Contabo)" -ForegroundColor Yellow
            Write-Host "   Emails: Se enviaran realmente" -ForegroundColor Yellow
            Write-Host "   URL: https://opticaapp-4e16.onrender.com" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "[CUIDADO] Estas conectado a PRODUCCION - afecta a usuarios reales" -ForegroundColor Red
        } else {
            Write-Host "[ERROR] Archivo $prodFile no encontrado" -ForegroundColor Red
        }
    } else {
        Write-Host "[CANCELADO] Operacion cancelada" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Ambiente actual en .env:" -ForegroundColor Cyan
if (Test-Path $envFile) {
    $dbUrl = Get-Content $envFile | Select-String "DATABASE_URL" | Select-Object -First 1
    $debug = Get-Content $envFile | Select-String "^DEBUG" | Select-Object -First 1
    
    Write-Host "   $debug" -ForegroundColor Gray
    if ($dbUrl) {
        Write-Host "   DATABASE_URL configurado (PostgreSQL)" -ForegroundColor Gray
    } else {
        Write-Host "   Sin DATABASE_URL (usara SQLite local)" -ForegroundColor Gray
    }
}
