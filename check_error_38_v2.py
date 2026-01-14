#!/usr/bin/env python
# -*- coding: utf-8 -*-
from apps.audit.models import ErrorLog

try:
    error = ErrorLog.objects.get(id=38)
    print("=" * 80)
    print(f"ERROR #{error.id}")
    print("=" * 80)
    print(f"Tipo: {error.error_type}")
    print(f"Mensaje: {error.error_message}")
    print(f"URL: {error.url}")
    print(f"Resuelto: {error.is_resolved}")
    print(f"Fecha: {error.created_at}")
    print()
    print("DETALLES ADICIONALES:")
    print("-" * 80)
    if hasattr(error, 'details') and error.details:
        print(error.details)
    print()
    print("STACK TRACE:")
    print("-" * 80)
    if hasattr(error, 'stack_trace') and error.stack_trace:
        print(error.stack_trace)
    else:
        print("No disponible")
    print("=" * 80)
except ErrorLog.DoesNotExist:
    print("❌ Error #38 no encontrado en la base de datos")
