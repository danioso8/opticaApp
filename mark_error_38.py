#!/usr/bin/env python
# -*- coding: utf-8 -*-
from apps.audit.models import ErrorLog

try:
    error = ErrorLog.objects.get(id=38)
    error.is_resolved = True
    error.save()
    print(f"✅ Error #38 marcado como RESUELTO")
    print(f"   {error.error_type}: {error.error_message[:80]}")
    print(f"   Solución: Creada vista appointment_resend_notification y ruta en urls.py")
except ErrorLog.DoesNotExist:
    print("❌ Error #38 no encontrado")
