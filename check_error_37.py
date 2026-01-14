#!/usr/bin/env python
# -*- coding: utf-8 -*-
from apps.audit.models import ErrorLog

try:
    e = ErrorLog.objects.get(id=37)
    print(f"Error #37: {e.error_message}")
    print(f"URL: {e.url}")
    print(f"Resuelto: {e.is_resolved}")
except ErrorLog.DoesNotExist:
    print("Error #37 no encontrado")
