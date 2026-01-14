#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Marcar errores NOT-V como resueltos"""
from apps.audit.models import ErrorLog

error_ids = [33, 32, 30, 23]  # Errores de .checked en notification_settings

print("=" * 80)
print("✅ MARCANDO ERRORES NOT-V COMO RESUELTOS")
print("=" * 80)

for error_id in error_ids:
    try:
        error = ErrorLog.objects.get(id=error_id)
        error.is_resolved = True
        error.save()
        print(f"✅ Error #{error_id} marcado como RESUELTO")
        print(f"   {error.error_type}: {error.error_message[:80]}")
        print()
    except ErrorLog.DoesNotExist:
        print(f"❌ Error #{error_id} no encontrado")
    except Exception as e:
        print(f"❌ Error al marcar #{error_id}: {str(e)}")

print("=" * 80)
print("✅ Proceso completado - Errores NOT-V resueltos")
print("=" * 80)
print()
print("📝 Solución aplicada:")
print("   Agregadas validaciones de elementos null antes de acceder a .checked")
print("   Archivo: apps/dashboard/templates/dashboard/notification_settings.html")
