#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para revisar errores en producción
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.audit.models import ErrorLog
from django.utils import timezone
from datetime import timedelta

print("=" * 80)
print("🔍 MONITOR DE ERRORES - PRODUCCIÓN")
print("=" * 80)
print()

# Errores no resueltos
errors = ErrorLog.objects.filter(is_resolved=False).order_by('-timestamp')[:20]
print(f"Total errores no resueltos: {errors.count()}")
print()

if errors:
    print("📋 LISTA DE ERRORES:")
    print("-" * 80)
    for i, error in enumerate(errors, 1):
        print(f"\n{i}. Error ID: {error.id}")
        print(f"   Severidad: {error.severity}")
        print(f"   Mensaje: {error.message[:150]}")
        print(f"   URL: {error.url}")
        print(f"   Usuario: {error.user if error.user else 'Anónimo'}")
        print(f"   Timestamp: {error.timestamp}")
        if error.traceback:
            print(f"   Traceback (primeras líneas):")
            lines = error.traceback.split('\n')[:5]
            for line in lines:
                print(f"      {line}")
else:
    print("✅ No hay errores sin resolver")
