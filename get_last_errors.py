#!/usr/bin/env python
"""
Script para mostrar los últimos 2 errores en detalle
"""
import os
import sys
import django

sys.path.insert(0, '/var/www/opticaapp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.audit.models import ErrorLog

print("\n" + "=" * 80)
print("ÚLTIMOS 2 ERRORES REGISTRADOS")
print("=" * 80)

errors = ErrorLog.objects.all().order_by('-timestamp')[:2]

for i, e in enumerate(errors, 1):
    print(f"\n{'='*80}")
    print(f"ERROR #{i} (ID: {e.id})")
    print(f"{'='*80}")
    print(f"Tipo: {e.error_type}")
    print(f"Severidad: {e.severity}")
    print(f"Estado: {'✓ Resuelto' if e.is_resolved else '⏱ Pendiente'}")
    print(f"Ocurrencias: {e.occurrence_count}")
    print(f"Fecha: {e.timestamp}")
    print(f"\nMensaje:")
    print(f"  {e.error_message}")
    print(f"\nURL:")
    print(f"  {e.url}")
    
    if e.stack_trace:
        print(f"\nStack Trace:")
        print("-" * 80)
        print(e.stack_trace)
    
    if e.user:
        print(f"\nUsuario: {e.user.username}")
    
    print(f"\n{'='*80}\n")
