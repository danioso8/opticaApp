#!/bin/bash
cd /var/www/opticaapp
source venv/bin/activate

echo "=========================================="
echo "🔍 ÚLTIMOS ERRORES EN BASE DE DATOS"
echo "=========================================="
echo ""

python manage.py dbshell <<EOF
SELECT 
    id,
    error_type,
    message,
    url,
    timestamp,
    occurrences,
    resolved
FROM audit_errorlog
ORDER BY timestamp DESC
LIMIT 5;
EOF
