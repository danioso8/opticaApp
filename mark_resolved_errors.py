#!/usr/bin/env python
"""
Script para marcar errores específicos como resueltos.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.audit.models import ErrorLog

# Errores ya resueltos
resolved_errors = [
    22,  # IntegrityError NULL - resuelto con migración 0005
    20,  # IntegrityError NULL - mismo error
    21,  # IntegrityError NULL - mismo error
]

print("\n🔧 Marcando errores como resueltos...\n")

for error_id in resolved_errors:
    try:
        error = ErrorLog.objects.get(id=error_id)
        if not error.is_resolved:
            error.is_resolved = True
            error.save()
            print(f"✅ Error #{error_id} marcado como RESUELTO: {error.error_type}")
        else:
            print(f"ℹ️  Error #{error_id} ya estaba resuelto")
    except ErrorLog.DoesNotExist:
        print(f"❌ Error #{error_id} no existe")

print("\n✨ Proceso completado\n")
