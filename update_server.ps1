# Script para actualizar OpticaApp en Contabo
# Ejecutar desde: D:\ESCRITORIO\OpticaApp

$SERVER = "root@84.247.129.180"
$REMOTE_DIR = "/var/www/opticaapp"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " ACTUALIZANDO OPTICAAPP EN CONTABO" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Crear archivo temporal comprimido con los cambios
Write-Host "📦 1. Comprimiendo archivos..." -ForegroundColor Yellow
$tempZip = "opticaapp_update.zip"

# Excluir archivos innecesarios
$excludeFiles = @(
    "*.pyc",
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "*.sqlite3",
    "node_modules",
    "auth_sessions",
    "*.log",
    "media",
    "staticfiles"
)

# Comprimir archivos importantes
Compress-Archive -Path `
    "apps",
    "opticaapp",
    "static",
    "templates",
    "manage.py",
    "requirements.txt",
    "package.json",
    "tailwind.config.js" `
    -DestinationPath $tempZip -Force

Write-Host "   ✅ Archivos comprimidos: $tempZip" -ForegroundColor Green

# 2. Subir archivo al servidor
Write-Host ""
Write-Host "📤 2. Subiendo archivos al servidor..." -ForegroundColor Yellow
scp $tempZip ${SERVER}:/var/www/

Write-Host "   ✅ Archivos subidos" -ForegroundColor Green

# 3. Descomprimir y actualizar en el servidor
Write-Host ""
Write-Host "🔄 3. Actualizando código en el servidor..." -ForegroundColor Yellow

ssh $SERVER @"
cd /var/www/opticaapp
unzip -o /var/www/$tempZip
rm /var/www/$tempZip
echo '✅ Código actualizado'
"@

# 4. Instalar dependencias Python
Write-Host ""
Write-Host "📦 4. Instalando dependencias Python..." -ForegroundColor Yellow
ssh $SERVER 'cd /var/www/opticaapp && source venv/bin/activate && pip install -r requirements.txt'

# 5. Ejecutar migraciones
Write-Host ""
Write-Host "🗃️  5. Ejecutando migraciones..." -ForegroundColor Yellow
ssh $SERVER 'cd /var/www/opticaapp && source venv/bin/activate && python manage.py migrate'

# 6. Compilar Tailwind CSS
Write-Host ""
Write-Host "🎨 6. Compilando Tailwind CSS..." -ForegroundColor Yellow
ssh $SERVER 'cd /var/www/opticaapp && npm run build:css'

# 7. Recolectar archivos estáticos
Write-Host ""
Write-Host "📊 7. Recolectando archivos estáticos..." -ForegroundColor Yellow
ssh $SERVER 'cd /var/www/opticaapp && source venv/bin/activate && python manage.py collectstatic --noinput'

# 8. Reiniciar servicios
Write-Host ""
Write-Host "🔄 8. Reiniciando servicios..." -ForegroundColor Yellow
ssh $SERVER 'sudo systemctl restart opticaapp && sudo systemctl reload nginx'

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " ACTUALIZACION COMPLETADA" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URL: https://www.opticapp.com.co" -ForegroundColor Green
Write-Host ""

# Limpiar archivo temporal local
Remove-Item $tempZip -ErrorAction SilentlyContinue
Write-Host "Archivo temporal eliminado" -ForegroundColor Gray
