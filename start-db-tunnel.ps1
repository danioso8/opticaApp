# Script para crear tunel SSH a PostgreSQL de Contabo
# Esto permite conectarse a la base de datos de forma segura

Write-Host "[INFO] Creando tunel SSH a PostgreSQL de Contabo..." -ForegroundColor Cyan
Write-Host "   Puerto local: 5433" -ForegroundColor Yellow
Write-Host "   Puerto remoto: 5432" -ForegroundColor Yellow
Write-Host "   Servidor: 84.247.129.180" -ForegroundColor Yellow
Write-Host ""
Write-Host "[!] Deja esta ventana ABIERTA mientras trabajas" -ForegroundColor Magenta
Write-Host "   Presiona Ctrl+C para cerrar el tunel" -ForegroundColor Magenta
Write-Host ""

# Crear túnel SSH (puerto local 5433 -> puerto remoto 5432)
ssh -L 5433:localhost:5432 root@84.247.129.180 -N
