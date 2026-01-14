#!/usr/bin/env python
# -*- coding: utf-8 -*-
from apps.audit.models import ErrorLog

errors_to_resolve = [41, 42]

print("=" * 80)
print("✅ MARCANDO ERRORES APT-V COMO RESUELTOS")
print("=" * 80)

for error_id in errors_to_resolve:
    try:
        error = ErrorLog.objects.get(id=error_id)
        error.is_resolved = True
        error.save()
        print(f"✅ Error #{error_id} marcado como RESUELTO")
        print(f"   {error.error_type}: {error.error_message[:100]}")
        print()
    except ErrorLog.DoesNotExist:
        print(f"❌ Error #{error_id} no encontrado")
    except Exception as e:
        print(f"❌ Error al marcar #{error_id}: {str(e)}")

print("=" * 80)
print("✅ Proceso completado")
print("=" * 80)
print()
print("📝 Solución aplicada:")
print("   Corregida vista appointment_resend_notification en apps/dashboard/views.py")
print("   Removida importación incorrecta de apps.appointments.tasks")
print("   Usando get_notifier() y send_appointment_confirmation() correctamente")
