from apps.audit.models import ErrorLog
from django.utils import timezone
from datetime import timedelta

print("=" * 80)
print("ERRORES NO RESUELTOS")
print("=" * 80)

errors = ErrorLog.objects.filter(is_resolved=False).order_by('-timestamp')[:30]
total = errors.count()

print(f"Total: {total} errores\n")

if total == 0:
    print("✅ No hay errores sin resolver")
else:
    for i, error in enumerate(errors, 1):
        print(f"\n{'='*80}")
        print(f"ERROR #{i} (ID: {error.id})")
        print(f"{'='*80}")
        print(f"Tipo: {error.error_type}")
        print(f"URL: {error.url or 'N/A'}")
        print(f"Método: {error.method or 'N/A'}")
        print(f"Usuario: {error.user.username if error.user else 'Anónimo'}")
        print(f"Organización: {error.organization.name if error.organization else 'N/A'}")
        print(f"Timestamp: {error.timestamp}")
        print(f"\nMensaje de error:")
        print(error.error_message[:500] if error.error_message else 'N/A')
        if error.stack_trace:
            print(f"\nStack Trace (primeras 20 líneas):")
            lines = error.stack_trace.split('\n')[:20]
            for line in lines:
                print(line)
        print()
