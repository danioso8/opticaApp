#!/usr/bin/env python
"""
Script para revisar errores actuales en producción.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.audit.models import ErrorLog
from django.utils import timezone

print("\n" + "="*80)
print("📊 ERRORES ACTUALES SIN RESOLVER (Top 15)")
print("="*80 + "\n")

# Obtener errores sin resolver ordenados por ocurrencias
errors = ErrorLog.objects.filter(is_resolved=False).order_by('-occurrence_count', '-timestamp')[:15]

if not errors:
    print("✅ ¡No hay errores sin resolver! Sistema limpio.\n")
else:
    for idx, error in enumerate(errors, 1):
        print(f"{'='*80}")
        print(f"🔴 ERROR #{error.id} - Prioridad {idx}")
        print(f"{'='*80}")
        print(f"📌 Tipo: {error.error_type}")
        print(f"💬 Mensaje: {error.error_message[:200]}")
        if len(error.error_message) > 200:
            print(f"   ... (mensaje completo en dashboard)")
        print(f"🔢 Ocurrencias: {error.occurrence_count} veces")
        print(f"⚠️  Severidad: {error.severity}")
        print(f"🌐 URL: {error.url or 'N/A'}")
        print(f"👤 Usuario: {error.user.username if error.user else 'Anónimo'}")
        print(f"📅 Primera vez: {error.timestamp}")
        print(f"🕐 Última vez: {error.last_seen}")
        
        # Mostrar stack trace si existe (primeras líneas)
        if error.stack_trace:
            lines = error.stack_trace.split('\n')[:5]
            print(f"📚 Stack (primeras líneas):")
            for line in lines:
                print(f"   {line}")
        print()

    print(f"\n{'='*80}")
    print(f"📊 RESUMEN: {len(errors)} errores sin resolver")
    print(f"{'='*80}\n")
    
    # Estadísticas
    critical = errors.filter(severity='CRITICAL').count()
    high = errors.filter(severity='ERROR').count()
    medium = errors.filter(severity='WARNING').count()
    
    print("🎯 Por Severidad:")
    print(f"   💀 CRÍTICO: {critical}")
    print(f"   ❌ ERROR: {high}")
    print(f"   ⚠️  WARNING: {medium}")
    print()
    
    # Los 3 más frecuentes
    print("🔥 Top 3 Más Frecuentes:")
    for idx, error in enumerate(errors[:3], 1):
        print(f"   {idx}. {error.error_type} - {error.occurrence_count} veces")
    print()

print(f"📍 Dashboard completo: https://www.optikaapp.com/saas-admin/errors/")
print()
