#!/usr/bin/env python
"""
Script para marcar error como resuelto
"""
import os
import sys
import django

sys.path.insert(0, '/var/www/opticaapp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.audit.models import ErrorLog
from django.utils import timezone

# Marcar error #15 como resuelto
error = ErrorLog.objects.get(id=15)
error.is_resolved = True
error.resolved_at = timezone.now()
error.resolution_notes = """
Solucionado: Agregadas validaciones en funciones JavaScript para evitar acceso a propiedades de elementos null.

Cambios realizados:
1. updateViewButtons(): Validar que botones existan antes de modificar classList
2. changeView(): Validar que elementos existan y no llamar updateViewButtons para tab 'today'
3. DOMContentLoaded: Solo restaurar vista si el tab activo es 'all'

Archivo modificado: apps/dashboard/templates/dashboard/appointments/index.html
"""
error.save()

print(f"✅ Error #{error.id} marcado como resuelto")
print(f"Tipo: {error.error_type}")
print(f"Mensaje: {error.error_message}")
print(f"Resuelto el: {error.resolved_at}")
