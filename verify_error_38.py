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
    print(f"Método: {error.method if hasattr(error, 'method') else 'N/A'}")
    print(f"Resuelto: {error.is_resolved}")
    print(f"Fecha: {error.timestamp}")
    print()
    print("STACK TRACE:")
    print("-" * 80)
    print(error.stack_trace)
    print("=" * 80)
    print()
    print("ANÁLISIS:")
    print("-" * 80)
    if "404" in error.error_message and "/api/appointments/" in error.error_message:
        print("✅ Error identificado: Ruta /api/appointments/.../resend-notification/ no existe")
        print("✅ Solución aplicada: Creada ruta en /dashboard/appointments/.../resend-notification/")
        print("📝 Archivo corregido: apps/dashboard/templates/dashboard/appointments/detail.html")
        print("📝 Vista creada: appointment_resend_notification en apps/dashboard/views.py")
        print("📝 URL agregada: apps/dashboard/urls.py")
except ErrorLog.DoesNotExist:
    print("❌ Error #38 no encontrado en la base de datos")
