#!/bin/bash
# Script para ejecutar en Render Shell para solucionar migración bloqueada

echo "=== Solucionando migración bloqueada en Render ==="

# Opción 1: Marcar migración como aplicada (si los cambios ya existen)
echo "Intentando marcar migración como aplicada..."
python manage.py migrate patients 0015 --fake

# Verificar estado
echo ""
echo "Verificando estado de migraciones..."
python manage.py showmigrations patients

echo ""
echo "=== Solución completada ==="
echo "Si aún hay problemas, ejecuta: python manage.py migrate --run-syncdb"
