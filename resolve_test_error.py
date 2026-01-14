#!/usr/bin/env python
import os, sys, django
sys.path.insert(0, '/var/www/opticaapp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.audit.models import ErrorLog
from django.utils import timezone

e = ErrorLog.objects.get(id=14)
e.is_resolved = True
e.resolved_at = timezone.now()
e.resolution_notes = 'Error de prueba del sistema de captura. No requiere acción.'
e.save()
print(f'✅ Error #{e.id} marcado como resuelto')
