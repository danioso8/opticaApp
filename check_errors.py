#!/usr/bin/env python
"""Script temporal para revisar errores en producción"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.audit.models import ErrorLog
from django.utils import timezone
from datetime import timedelta

# Errores de los últimos 7 días
seven_days_ago = timezone.now() - timedelta(days=7)
total_errors = ErrorLog.objects.filter(timestamp__gte=seven_days_ago).count()

print(f"\n{'='*60}")
print(f"REPORTE DE ERRORES - Últimos 7 días")
print(f"{'='*60}")
print(f"Total de errores: {total_errors}\n")

# Errores críticos no resueltos
critical_errors = ErrorLog.objects.filter(
    severity='CRITICAL',
    is_resolved=False,
    timestamp__gte=seven_days_ago
).order_by('-timestamp')[:5]

print(f"\n🔴 ERRORES CRÍTICOS NO RESUELTOS: {critical_errors.count()}")
print("-" * 60)
for i, error in enumerate(critical_errors, 1):
    print(f"\n{i}. ID: {error.id}")
    print(f"   Tipo: {error.error_type}")
    print(f"   Mensaje: {error.error_message[:150]}")
    print(f"   Fecha: {error.timestamp}")
    print(f"   Ocurrencias: {error.occurrence_count}")
    print(f"   URL: {error.url or 'N/A'}")

# Errores más frecuentes
from django.db.models import Count
frequent_errors = ErrorLog.objects.filter(
    timestamp__gte=seven_days_ago
).values('error_type').annotate(
    count=Count('id')
).order_by('-count')[:10]

print(f"\n\n📊 TOP 10 ERRORES MÁS FRECUENTES:")
print("-" * 60)
for i, error in enumerate(frequent_errors, 1):
    print(f"{i}. {error['error_type'][:50]} - {error['count']} veces")

# Errores por severidad
from django.db.models import Q
severity_stats = {}
for severity in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
    count = ErrorLog.objects.filter(
        severity=severity,
        timestamp__gte=seven_days_ago
    ).count()
    severity_stats[severity] = count

print(f"\n\n📈 DISTRIBUCIÓN POR SEVERIDAD:")
print("-" * 60)
for severity, count in severity_stats.items():
    bar = '█' * min(count, 50)
    print(f"{severity:10} {count:5} {bar}")

# Errores recientes (últimas 24h)
recent_errors = ErrorLog.objects.filter(
    timestamp__gte=timezone.now() - timedelta(hours=24)
).order_by('-timestamp')[:10]

print(f"\n\n⏰ ÚLTIMOS 10 ERRORES (24 horas):")
print("-" * 60)
for i, error in enumerate(recent_errors, 1):
    status = "✅" if error.is_resolved else "❌"
    print(f"\n{i}. {status} [{error.severity}] {error.error_type[:40]}")
    print(f"   {error.error_message[:100]}")
    print(f"   {error.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")

print(f"\n{'='*60}\n")
