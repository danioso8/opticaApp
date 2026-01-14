#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para marcar errores como resueltos
"""
import sys
from apps.audit.models import ErrorLog

error_ids = [35]  # IDs de errores a marcar como resueltos

print("=" * 80)
print("✅ MARCANDO ERRORES COMO RESUELTOS")
print("=" * 80)

for error_id in error_ids:
    try:
        error = ErrorLog.objects.get(id=error_id)
        error.is_resolved = True
        error.save()
        print(f"✅ Error #{error_id} marcado como RESUELTO")
        print(f"   Tipo: {error.error_type}")
        print(f"   Mensaje: {error.error_message[:100]}")
        print()
    except ErrorLog.DoesNotExist:
        print(f"❌ Error #{error_id} no encontrado")
    except Exception as e:
        print(f"❌ Error al marcar #{error_id}: {str(e)}")

print("=" * 80)
print("✅ Proceso completado")
print("=" * 80)
