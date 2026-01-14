#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Lista errores pendientes agrupados"""

from apps.audit.models import ErrorLog
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

print("=" * 80)
print("🔍 ERRORES PENDIENTES - AGRUPADOS POR TIPO")
print("=" * 80)
print()

week_ago = timezone.now() - timedelta(days=7)
errors = ErrorLog.objects.filter(
    is_resolved=False,
    timestamp__gte=week_ago
).order_by('-timestamp')

# Agrupar por tipo de error
error_groups = {}
for error in errors:
    key = f"{error.error_type}:{error.error_message[:50]}"
    if key not in error_groups:
        error_groups[key] = {
            'tipo': error.error_type,
            'mensaje': error.error_message,
            'url': error.url,
            'ids': [],
            'count': 0
        }
    error_groups[key]['ids'].append(error.id)
    error_groups[key]['count'] += 1

# Mostrar agrupados
for i, (key, data) in enumerate(sorted(error_groups.items(), key=lambda x: x[1]['count'], reverse=True), 1):
    print(f"{i}. [{data['count']}x] {data['tipo']}")
    print(f"   IDs: {', '.join(map(str, data['ids']))}")
    print(f"   Mensaje: {data['mensaje'][:100]}")
    print(f"   URL: {data['url']}")
    
    # Sugerir módulo
    url = data['url'] or ''
    if '/appointments/' in url:
        codigo = 'APT-V'
    elif '/patients/' in url and 'visual-exam' in url:
        codigo = 'EXM'
    elif '/patients/' in url:
        codigo = 'PAT-V'
    elif '/notifications/' in url:
        codigo = 'NOT-V'
    elif '/configuration/' in url:
        codigo = 'CFG'
    elif '/api/' in url:
        codigo = 'API'
    else:
        codigo = '???'
    
    print(f"   📁 Módulo sugerido: {codigo}")
    print()

print("=" * 80)
print(f"Total de errores pendientes: {errors.count()}")
print("=" * 80)
print()
print("💡 INSTRUCCIONES PARA SOLUCIONAR:")
print("   Usa el formato: 'Soluciona [MODULO] #[IDS]'")
print("   Ejemplo: 'Soluciona NOT-V #33,32,30,23'")
print("   Ejemplo: 'Soluciona EXM #26,25'")
