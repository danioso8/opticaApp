from apps.audit.models import ErrorLog
from django.db.models import Count
from datetime import datetime, timedelta

print("="*80)
print("ERRORES RECIENTES (ÚLTIMAS 24 HORAS)")
print("="*80)

recent = ErrorLog.objects.filter(
    created_at__gte=datetime.now() - timedelta(hours=24)
).values('id', 'error_type', 'message', 'count', 'is_resolved').order_by('-count')[:15]

for i, e in enumerate(recent, 1):
    status = "✓ RESUELTO" if e['is_resolved'] else "⏱ PENDIENTE"
    print(f"\n{i}. ID {e['id']} - {status}")
    print(f"   Tipo: {e['error_type']}")
    print(f"   Count: {e['count']}")
    print(f"   Mensaje: {e['message'][:120]}")

print("\n" + "="*80)
print("ERRORES DE NOTIFICACIONES")
print("="*80)

notif_errors = ErrorLog.objects.filter(
    message__icontains='notification'
).order_by('-created_at')[:5]

for i, e in enumerate(notif_errors, 1):
    status = "✓ RESUELTO" if e.is_resolved else "⏱ PENDIENTE"
    print(f"\n{i}. ID {e.id} - {status} - Count: {e.count}")
    print(f"   {e.message[:150]}")
    print(f"   Última vez: {e.updated_at}")
