# Script de Deployment - Bot Auto-Corrector
# Ejecutar comando por comando en PowerShell

Write-Host "`n================================================" -ForegroundColor Green
Write-Host "🤖 DEPLOYMENT BOT AUTO-CORRECTOR" -ForegroundColor Green  
Write-Host "================================================`n" -ForegroundColor Green

Write-Host "Ejecuta estos comandos UNO POR UNO:`n" -ForegroundColor Yellow

Write-Host "# 1. Subir bot auto-corrector" -ForegroundColor Cyan
Write-Host 'scp apps\audit\error_auto_fix.py root@84.247.129.180:/var/www/opticaapp/apps/audit/' -ForegroundColor White
Write-Host ""

Write-Host "# 2. Subir comando Django" -ForegroundColor Cyan  
Write-Host 'scp apps\audit\management\commands\auto_fix_errors.py root@84.247.129.180:/var/www/opticaapp/apps/audit/management/commands/' -ForegroundColor White
Write-Host ""

Write-Host "# 3. Conectar al servidor" -ForegroundColor Cyan
Write-Host 'ssh root@84.247.129.180' -ForegroundColor White
Write-Host ""

Write-Host "# 4. Ya en el servidor, ejecutar:" -ForegroundColor Cyan
Write-Host 'cd /var/www/opticaapp' -ForegroundColor White
Write-Host 'mkdir -p apps/audit/management/commands' -ForegroundColor White
Write-Host 'touch apps/audit/management/__init__.py' -ForegroundColor White
Write-Host 'touch apps/audit/management/commands/__init__.py' -ForegroundColor White
Write-Host 'source venv/bin/activate' -ForegroundColor White
Write-Host 'pm2 restart opticaapp' -ForegroundColor White
Write-Host 'python manage.py auto_fix_errors --dry-run' -ForegroundColor White
Write-Host ""

Write-Host "================================================" -ForegroundColor Green
Write-Host "✅ LISTO - El bot estará funcionando" -ForegroundColor Green
Write-Host "================================================`n" -ForegroundColor Green
