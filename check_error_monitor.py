#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, '/var/www/opticaapp')
os.chdir('/var/www/opticaapp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from apps.audit.models import ErrorLog
from django.utils import timezone
from datetime import timedelta

print("="*80)
print("🔍 ÚLTIMOS ERRORES EN EL MONITOR")
print("="*80)

# Obtener últimos 5 errores
errors = ErrorLog.objects.all().order_by('-timestamp')[:5]

if not errors:
    print("\n✅ No hay errores registrados")
else:
    for i, error in enumerate(errors, 1):
        print(f"\n{'='*80}")
        print(f"ERROR #{i} - ID: {error.id}")
        print(f"{'='*80}")
        print(f"📅 Fecha: {error.timestamp}")
        print(f"🔴 Tipo: {error.error_type}")
        print(f"📝 Mensaje: {error.message[:200]}...")
        print(f"🌐 URL: {error.url}")
        print(f"👤 User Agent: {error.user_agent[:100]}...")
        print(f"📊 Ocurrencias: {error.occurrences}")
        print(f"✅ Resuelto: {error.resolved}")
        if error.stack_trace:
            print(f"\n📚 Stack Trace:")
            print(error.stack_trace[:500] + "..." if len(error.stack_trace) > 500 else error.stack_trace)
        print()

print("\n" + "="*80)
print("📊 ESTADÍSTICAS")
print("="*80)

# Errores de las últimas 24 horas
last_24h = timezone.now() - timedelta(hours=24)
errors_24h = ErrorLog.objects.filter(timestamp__gte=last_24h).count()
print(f"Errores últimas 24h: {errors_24h}")

# Errores no resueltos
unresolved = ErrorLog.objects.filter(resolved=False).count()
print(f"Errores sin resolver: {unresolved}")

# Tipos de error más comunes
from django.db.models import Count
top_errors = ErrorLog.objects.values('error_type').annotate(
    count=Count('id')
).order_by('-count')[:5]

print("\n🔝 Top 5 tipos de error:")
for err in top_errors:
    print(f"  - {err['error_type']}: {err['count']} ocurrencias")
