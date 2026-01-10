"""
Script de prueba para generar un error y verificar el sistema de monitoreo.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.audit.models import ErrorLog
from django.contrib.auth import get_user_model

User = get_user_model()

# Crear un error de prueba
ErrorLog.objects.create(
    error_type='TestError',
    error_message='Este es un error de prueba del sistema de monitoreo',
    stack_trace='Traceback (most recent call last):\n  File "test.py", line 1, in <module>\n    raise TestError("Error de prueba")\nTestError: Error de prueba',
    url='/test/error/',
    method='GET',
    severity='ERROR',
    request_data={'test': 'data'},
    context={'environment': 'development', 'test': True}
)

print("✓ Error de prueba creado exitosamente")

# Mostrar estadísticas
total = ErrorLog.objects.count()
unresolved = ErrorLog.objects.filter(is_resolved=False).count()
critical = ErrorLog.objects.filter(severity='CRITICAL').count()

print(f"\nEstadísticas:")
print(f"  Total de errores: {total}")
print(f"  Sin resolver: {unresolved}")
print(f"  Críticos: {critical}")

print(f"\nAccede a http://127.0.0.1:8000/saas-admin/errors/ para ver el dashboard")
print(f"O accede a http://127.0.0.1:8000/admin/audit/errorlog/ para el admin completo")
