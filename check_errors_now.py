#!/usr/bin/env python
"""Script para revisar errores actuales en el monitor"""
import os
import django
import sys
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opticaapp.settings')
django.setup()

from apps.audit.models import ErrorLog
from django.db.models import Count
from datetime import datetime, timedelta

print('='*80)
print('ERRORES EN LAS ÚLTIMAS 24 HORAS')
print('='*80)

recent_errors = ErrorLog.objects.filter(
    created_at__gte=datetime.now() - timedelta(hours=24)
).values('error_type', 'message', 'url').annotate(
    count=Count('id')
).order_by('-count')[:20]

for i, err in enumerate(recent_errors, 1):
    print(f'\n{i}. [{err["error_type"]}] (Count: {err["count"]})')
    print(f'   Mensaje: {err["message"][:150]}')
    print(f'   URL: {err["url"] or "N/A"}')

print('\n' + '='*80)
print('ERRORES CRÍTICOS NO RESUELTOS')
print('='*80)

critical = ErrorLog.objects.filter(
    is_resolved=False,
    severity='CRITICAL'
).order_by('-count', '-created_at')[:10]

for i, err in enumerate(critical, 1):
    print(f'\n{i}. ID: {err.id} | Count: {err.count}')
    print(f'   Tipo: {err.error_type}')
    print(f'   Mensaje: {err.message[:150]}')
    print(f'   URL: {err.url or "N/A"}')
    print(f'   Creado: {err.created_at}')

print('\n' + '='*80)
print('ERRORES DE IMPORTACIÓN DE NOTIFICACIONES')
print('='*80)

import_errors = ErrorLog.objects.filter(
    message__icontains='send_notification',
    is_resolved=False
).order_by('-created_at')[:5]

for i, err in enumerate(import_errors, 1):
    print(f'\n{i}. ID: {err.id} | Count: {err.count}')
    print(f'   Tipo: {err.error_type}')
    print(f'   Mensaje: {err.message[:200]}')
    print(f'   Creado: {err.created_at}')
    print(f'   Última vez: {err.updated_at}')
