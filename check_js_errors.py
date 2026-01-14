#!/usr/bin/env python
"""
Script para verificar errores JavaScript capturados
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, '/var/www/opticaapp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.audit.models import ErrorLog
from django.utils import timezone
from datetime import timedelta

# Buscar errores JavaScript
js_error_types = [
    'JavaScriptError', 
    'Error', 
    'TypeError', 
    'ReferenceError', 
    'UnhandledPromiseRejection',
    'SyntaxError',
    'RangeError'
]

print("=" * 80)
print("ERRORES JAVASCRIPT CAPTURADOS")
print("=" * 80)

# Total de errores JS
js_errors = ErrorLog.objects.filter(error_type__in=js_error_types)
print(f"\nTotal de errores JavaScript registrados: {js_errors.count()}")

# Últimos 10 errores JS
recent_js = js_errors.order_by('-timestamp')[:10]
if recent_js.exists():
    print("\n📋 Últimos 10 errores JavaScript:")
    print("-" * 80)
    for e in recent_js:
        status = "✓ Resuelto" if e.is_resolved else "⏱ Pendiente"
        print(f"\nID: {e.id} | {e.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | {status}")
        print(f"Tipo: {e.error_type}")
        print(f"Mensaje: {e.error_message[:100]}...")
        print(f"URL: {e.url}")
        print(f"Ocurrencias: {e.occurrence_count}")
else:
    print("\n⚠️  No se han capturado errores JavaScript aún")

# Últimas 24 horas
last_24h = timezone.now() - timedelta(hours=24)
recent_count = js_errors.filter(timestamp__gte=last_24h).count()
print(f"\n📊 Errores JavaScript en las últimas 24 horas: {recent_count}")

# Todos los errores (incluyendo backend)
all_errors = ErrorLog.objects.all()
print(f"\n📊 Total de errores (backend + frontend): {all_errors.count()}")

print("\n" + "=" * 80)
