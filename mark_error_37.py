#!/usr/bin/env python
# -*- coding: utf-8 -*-
from apps.audit.models import ErrorLog

try:
    error = ErrorLog.objects.get(id=37)
    error.is_resolved = True
    error.save()
    print(f"✅ Error #37 marcado como RESUELTO")
    print(f"   {error.error_type}: {error.error_message[:80]}")
    print(f"   Solución: Agregado SweetAlert2 CDN al template")
except ErrorLog.DoesNotExist:
    print("❌ Error #37 no encontrado")
