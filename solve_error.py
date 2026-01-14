#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔧 SOLUCIONADOR RÁPIDO DE ERRORES

Uso:
    python solve_error.py [CODIGO] [ERROR_IDS]
    
Ejemplos:
    python solve_error.py NOT-V 33,32,30,23
    python solve_error.py EXM 26,25
    python solve_error.py API 19,18
    python solve_error.py --mark-resolved 35,36
    python solve_error.py --list-pending
"""

import sys
from apps.audit.models import ErrorLog
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

MODULO_MAP = {
    'APT': {
        'nombre': 'Citas/Appointments',
        'archivos': ['apps/appointments/views.py', 'apps/appointments/urls.py'],
        'templates': ['apps/dashboard/templates/dashboard/appointments/']
    },
    'APT-V': {
        'nombre': 'Citas Vista',
        'archivos': ['apps/dashboard/templates/dashboard/appointments/detail.html',
                     'apps/dashboard/templates/dashboard/appointments/list.html']
    },
    'PAT': {
        'nombre': 'Pacientes',
        'archivos': ['apps/patients/models.py', 'apps/patients/views.py']
    },
    'PAT-V': {
        'nombre': 'Pacientes Vista',
        'archivos': ['apps/dashboard/templates/dashboard/patients/detail.html',
                     'apps/dashboard/templates/dashboard/patients/list.html']
    },
    'EXM': {
        'nombre': 'Exámenes Visuales',
        'archivos': ['apps/dashboard/templates/dashboard/patients/visual_exam_form.html',
                     'apps/dashboard/templates/dashboard/patients/visual_exam_edit.html']
    },
    'NOT': {
        'nombre': 'Notificaciones Backend',
        'archivos': ['apps/notifications/views.py', 'apps/notifications/notifications.py']
    },
    'NOT-V': {
        'nombre': 'Notificaciones Vista',
        'archivos': ['apps/dashboard/templates/dashboard/notifications/settings.html']
    },
    'CFG': {
        'nombre': 'Configuración',
        'archivos': ['apps/dashboard/views_configuration.py', 'apps/dashboard/urls.py']
    },
    'WF': {
        'nombre': 'Workflows',
        'archivos': ['apps/dashboard/views_workflows.py']
    },
    'API': {
        'nombre': 'API General',
        'archivos': ['apps/appointments/views.py', 'apps/dashboard/views.py']
    },
    'WA': {
        'nombre': 'WhatsApp',
        'archivos': ['apps/notifications/views_whatsapp_baileys.py',
                     'apps/notifications/models_whatsapp_connection.py',
                     'whatsapp-server/server.js']
    },
    'ADM': {
        'nombre': 'Admin SAAS',
        'archivos': ['apps/admin_dashboard/views.py']
    }
}

def listar_errores_pendientes():
    """Lista errores pendientes agrupados por patrón"""
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
            print(f"   📁 Módulo sugerido: APT-V")
        elif '/patients/' in url and 'visual-exam' in url:
            print(f"   📁 Módulo sugerido: EXM")
        elif '/patients/' in url:
            print(f"   📁 Módulo sugerido: PAT-V")
        elif '/notifications/' in url:
            print(f"   📁 Módulo sugerido: NOT-V")
        elif '/configuration/' in url:
            print(f"   📁 Módulo sugerido: CFG")
        elif '/api/' in url:
            print(f"   📁 Módulo sugerido: API")
        
        print()

def mostrar_info_modulo(codigo):
    """Muestra información del módulo y archivos a revisar"""
    if codigo not in MODULO_MAP:
        print(f"❌ Código '{codigo}' no reconocido")
        print(f"📋 Códigos válidos: {', '.join(MODULO_MAP.keys())}")
        return False
    
    modulo = MODULO_MAP[codigo]
    print("=" * 80)
    print(f"📂 MÓDULO: {modulo['nombre']} ({codigo})")
    print("=" * 80)
    print()
    print("📄 Archivos a revisar:")
    for archivo in modulo['archivos']:
        print(f"   - {archivo}")
    print()
    return True

def marcar_resueltos(error_ids):
    """Marca errores como resueltos"""
    print("=" * 80)
    print("✅ MARCANDO ERRORES COMO RESUELTOS")
    print("=" * 80)
    print()
    
    for error_id in error_ids:
        try:
            error = ErrorLog.objects.get(id=error_id)
            error.is_resolved = True
            error.save()
            print(f"✅ Error #{error_id} marcado como RESUELTO")
            print(f"   {error.error_type}: {error.error_message[:80]}")
            print()
        except ErrorLog.DoesNotExist:
            print(f"❌ Error #{error_id} no encontrado")
        except Exception as e:
            print(f"❌ Error al marcar #{error_id}: {str(e)}")

def mostrar_detalles_errores(error_ids):
    """Muestra detalles completos de errores específicos"""
    print("=" * 80)
    print("🔍 DETALLES DE ERRORES")
    print("=" * 80)
    print()
    
    for error_id in error_ids:
        try:
            error = ErrorLog.objects.get(id=error_id)
            print(f"Error #{error.id}")
            print(f"  Timestamp: {error.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"  Severidad: {error.severity}")
            print(f"  Tipo: {error.error_type}")
            print(f"  Mensaje: {error.error_message}")
            print(f"  URL: {error.url}")
            if error.user:
                print(f"  Usuario: {error.user.username}")
            if error.organization:
                print(f"  Organización: {error.organization.name}")
            if error.stack_trace:
                print(f"  Stack Trace disponible: Sí ({len(error.stack_trace)} caracteres)")
            print(f"  Resuelto: {'✅ Sí' if error.is_resolved else '❌ No'}")
            print()
        except ErrorLog.DoesNotExist:
            print(f"❌ Error #{error_id} no encontrado")
            print()

# Ejecutar según argumentos
if len(sys.argv) < 2:
    print(__doc__)
    sys.exit(0)

comando = sys.argv[1]

if comando == '--list-pending':
    listar_errores_pendientes()
elif comando == '--mark-resolved':
    if len(sys.argv) < 3:
        print("❌ Debes proporcionar los IDs de error")
        print("Ejemplo: --mark-resolved 35,36,37")
        sys.exit(1)
    error_ids = [int(x.strip()) for x in sys.argv[2].split(',')]
    marcar_resueltos(error_ids)
elif comando == '--details':
    if len(sys.argv) < 3:
        print("❌ Debes proporcionar los IDs de error")
        print("Ejemplo: --details 35,36")
        sys.exit(1)
    error_ids = [int(x.strip()) for x in sys.argv[2].split(',')]
    mostrar_detalles_errores(error_ids)
elif comando in MODULO_MAP:
    mostrar_info_modulo(comando)
    if len(sys.argv) >= 3:
        error_ids = [int(x.strip()) for x in sys.argv[2].split(',')]
        print()
        mostrar_detalles_errores(error_ids)
else:
    print(f"❌ Comando '{comando}' no reconocido")
    print(__doc__)
