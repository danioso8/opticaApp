#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Ver detalles completos de errores específicos"""

from apps.audit.models import ErrorLog

error_ids = [33, 32, 30, 27, 23, 16, 13]

print("=" * 80)
print("🔍 DETALLES COMPLETOS DE ERRORES NOT-V")
print("=" * 80)
print()

for error_id in error_ids:
    try:
        error = ErrorLog.objects.get(id=error_id)
        print(f"{'=' * 80}")
        print(f"Error #{error.id}")
        print(f"{'=' * 80}")
        print(f"Timestamp: {error.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Severidad: {error.severity}")
        print(f"Tipo: {error.error_type}")
        print(f"URL: {error.url}")
        print()
        print(f"MENSAJE:")
        print(error.error_message)
        print()
        if error.stack_trace:
            print(f"STACK TRACE:")
            print(error.stack_trace[:1000])
            print()
        print()
    except ErrorLog.DoesNotExist:
        print(f"❌ Error #{error_id} no encontrado")
        print()
