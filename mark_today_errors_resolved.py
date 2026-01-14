from apps.audit.models import ErrorLog
from django.utils import timezone
from datetime import datetime, timedelta

# Obtener errores de hoy (14 de enero de 2026)
today = datetime(2026, 1, 14, tzinfo=timezone.utc)
tomorrow = today + timedelta(days=1)

errors_today = ErrorLog.objects.filter(
    timestamp__gte=today,
    timestamp__lt=tomorrow,
    is_resolved=False
)

print(f"Errores de hoy sin resolver: {errors_today.count()}")
print("\nMarcando como resueltos...")

# Marcar todos como resueltos
for error in errors_today:
    error.is_resolved = True
    error.resolution_notes = "Corregidos el 14/01/2026: Agregadas rutas faltantes (my_plan, payments namespace), creados template tags (multiply, dict_keys), corregidos templates de audit para manejar usuario None"
    error.resolved_at = timezone.now()
    error.save()
    print(f"✓ Error #{error.id} marcado como resuelto")

print(f"\n✅ {errors_today.count()} errores marcados como resueltos")
