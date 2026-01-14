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
    print(f"Línea: {error.line_number}")
    print(f"Columna: {error.column_number}")
    print(f"Resuelto: {error.is_resolved}")
    print(f"Fecha: {error.created_at}")
    print()
    print("STACK TRACE:")
    print("-" * 80)
    print(error.stack_trace if error.stack_trace else "No disponible")
    print("=" * 80)
except ErrorLog.DoesNotExist:
    print("❌ Error #38 no encontrado en la base de datos")
