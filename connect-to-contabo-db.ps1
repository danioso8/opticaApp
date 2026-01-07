# ============================================
# GUIA: Conectar a Base de Datos de Contabo
# ============================================

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " CONECTAR A BASE DE DATOS DE CONTABO DESDE DESARROLLO LOCAL" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "PASO 1: Abrir NUEVA terminal PowerShell" -ForegroundColor Yellow
Write-Host "   - Abre una segunda ventana de PowerShell" -ForegroundColor Gray
Write-Host "   - Navega a: D:\ESCRITORIO\OpticaApp" -ForegroundColor Gray
Write-Host ""

Write-Host "PASO 2: Ejecutar el tunel SSH (en la nueva terminal)" -ForegroundColor Yellow
Write-Host "   Comando:" -ForegroundColor Gray
Write-Host "   .\start-db-tunnel.ps1" -ForegroundColor White
Write-Host ""
Write-Host "   [!] IMPORTANTE: Deja esa terminal ABIERTA todo el tiempo" -ForegroundColor Magenta
Write-Host ""

Write-Host "PASO 3: Regresar a ESTA terminal y ejecutar Django" -ForegroundColor Yellow
Write-Host "   Comando:" -ForegroundColor Gray
Write-Host "   D:/ESCRITORIO/OpticaApp/.venv/Scripts/python.exe manage.py runserver" -ForegroundColor White
Write-Host ""

Write-Host "PASO 4: Trabajar normalmente" -ForegroundColor Yellow
Write-Host "   - Todos los cambios se hacen en la BD de Contabo (PRODUCCION)" -ForegroundColor Red
Write-Host "   - Los usuarios reales veran los cambios inmediatamente" -ForegroundColor Red
Write-Host ""

Write-Host "PARA DETENER:" -ForegroundColor Yellow
Write-Host "   1. Ctrl+C en ESTA terminal (detiene Django)" -ForegroundColor Gray
Write-Host "   2. Ctrl+C en la OTRA terminal (cierra tunel SSH)" -ForegroundColor Gray
Write-Host ""

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Quieres continuar? (S/N): " -NoNewline -ForegroundColor Green
$response = Read-Host

if ($response -eq "S" -or $response -eq "s") {
    Write-Host ""
    Write-Host "[OK] Abre la nueva terminal y ejecuta: .\start-db-tunnel.ps1" -ForegroundColor Green
    Write-Host "     Cuando veas 'Tunel activo', regresa aqui y presiona ENTER" -ForegroundColor Yellow
    Read-Host ""
    
    Write-Host "[INFO] Probando conexion a la base de datos..." -ForegroundColor Cyan
    D:/ESCRITORIO/OpticaApp/.venv/Scripts/python.exe -c "from django.db import connection; connection.ensure_connection(); print('[OK] Conexion exitosa a PostgreSQL de Contabo')"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[OK] Listo! Puedes ejecutar:" -ForegroundColor Green
        Write-Host "   D:/ESCRITORIO/OpticaApp/.venv/Scripts/python.exe manage.py runserver" -ForegroundColor White
    }
} else {
    Write-Host ""
    Write-Host "[CANCELADO] No hay problema. Para volver a SQLite local ejecuta:" -ForegroundColor Yellow
    Write-Host "   Copy-Item .env.local .env -Force" -ForegroundColor White
}
