#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para revisar errores en el monitor del SAAS-Admin
"""

from apps.audit.models import ErrorLog
from django.utils import timezone
from datetime import timedelta

print("=" * 80)
print("🔍 MONITOR DE ERRORES - SAAS ADMIN")
print("=" * 80)
print()

# Estadísticas generales
total_errors = ErrorLog.objects.count()
unresolved_errors = ErrorLog.objects.filter(is_resolved=False).count()
critical_errors = ErrorLog.objects.filter(severity='CRITICAL', is_resolved=False).count()
recent_errors = ErrorLog.objects.filter(timestamp__gte=timezone.now()-timedelta(days=1)).count()

print("📊 ESTADÍSTICAS GENERALES")
print("-" * 80)
print(f"Total de errores: {total_errors}")
print(f"Errores no resueltos: {unresolved_errors}")
print(f"Errores críticos: {critical_errors}")
print(f"Errores en las últimas 24 horas: {recent_errors}")
print()

# Errores por severidad
print("📈 DISTRIBUCIÓN POR SEVERIDAD")
print("-" * 80)
from django.db.models import Count
errors_by_severity = ErrorLog.objects.values('severity').annotate(count=Count('id')).order_by('severity')
for item in errors_by_severity:
    severity_icon = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔴'
    }.get(item['severity'], '❓')
    print(f"{severity_icon} {item['severity']}: {item['count']} errores")
print()

# Errores no resueltos recientes
print("🚨 ERRORES NO RESUELTOS (Últimos 7 días)")
print("-" * 80)
week_ago = timezone.now() - timedelta(days=7)
errors = ErrorLog.objects.filter(
    is_resolved=False,
    timestamp__gte=week_ago
).select_related('user', 'organization').order_by('-timestamp')[:20]

if errors:
    for e in errors:
        print(f"\n#{e.id} | {e.timestamp.strftime('%d/%m/%Y %H:%M:%S')} | {e.severity}")
        print(f"  Tipo: {e.error_type}")
        print(f"  Mensaje: {e.error_message[:200]}")
        if e.url:
            print(f"  URL: {e.url}")
        if e.user:
            print(f"  Usuario: {e.user.username}")
        if e.organization:
            print(f"  Organización: {e.organization.name}")
        print(f"  Stack trace: {'Sí' if e.stack_trace else 'No'}")
else:
    print("✅ No hay errores no resueltos en los últimos 7 días")

print()
print("=" * 80)

# Top 10 errores más frecuentes
print("\n🔝 TOP 10 ERRORES MÁS FRECUENTES (Últimos 7 días)")
print("-" * 80)
top_errors = ErrorLog.objects.filter(
    timestamp__gte=week_ago
).values('error_type', 'error_message').annotate(
    count=Count('id')
).order_by('-count')[:10]

for i, error in enumerate(top_errors, 1):
    print(f"\n{i}. [{error['count']} veces] {error['error_type']}")
    print(f"   {error['error_message'][:150]}")

print()
print("=" * 80)
print("✅ Análisis completado")
print("=" * 80)
