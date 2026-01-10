"""
Script para crear varios errores de prueba con diferentes severidades.
"""
import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.audit.models import ErrorLog
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

# Obtener un usuario para asignar a algunos errores
try:
    user = User.objects.filter(is_superuser=True).first()
except:
    user = None

# Crear diferentes tipos de errores
errors_to_create = [
    {
        'error_type': 'ValueError',
        'error_message': 'Invalid value provided for field',
        'severity': 'WARNING',
        'url': '/api/patients/create/',
        'method': 'POST',
        'user': user
    },
    {
        'error_type': 'DatabaseError',
        'error_message': 'Connection to database lost',
        'severity': 'CRITICAL',
        'url': '/appointments/list/',
        'method': 'GET',
        'user': user
    },
    {
        'error_type': 'PermissionDenied',
        'error_message': 'User does not have permission to access this resource',
        'severity': 'WARNING',
        'url': '/admin/users/delete/',
        'method': 'DELETE',
        'user': user
    },
    {
        'error_type': 'KeyError',
        'error_message': 'Required key "organization_id" not found in request data',
        'severity': 'ERROR',
        'url': '/api/organizations/update/',
        'method': 'PUT',
        'user': None
    },
    {
        'error_type': 'ValidationError',
        'error_message': 'Email format is invalid',
        'severity': 'INFO',
        'url': '/users/register/',
        'method': 'POST',
        'user': None
    },
    {
        'error_type': 'TimeoutError',
        'error_message': 'Request to DIAN service timed out',
        'severity': 'ERROR',
        'url': '/billing/invoice/send/',
        'method': 'POST',
        'user': user
    },
]

# Crear errores con diferentes timestamps
for i, error_data in enumerate(errors_to_create):
    timestamp = timezone.now() - timedelta(hours=i*2)
    
    ErrorLog.objects.create(
        error_type=error_data['error_type'],
        error_message=error_data['error_message'],
        stack_trace=f'Traceback (most recent call last):\n  File "app.py", line {i+10}, in process\n    raise {error_data["error_type"]}("{error_data["error_message"]}")\n{error_data["error_type"]}: {error_data["error_message"]}',
        url=error_data['url'],
        method=error_data['method'],
        severity=error_data['severity'],
        user=error_data.get('user'),
        timestamp=timestamp,
        request_data={'test': True, 'index': i},
        context={'environment': 'development', 'version': '1.0.0'}
    )
    print(f"✓ Error {i+1}: {error_data['error_type']} - {error_data['severity']}")

# Crear algunos errores duplicados
duplicate_error = ErrorLog.objects.first()
if duplicate_error:
    for i in range(3):
        similar = ErrorLog.objects.create(
            error_type=duplicate_error.error_type,
            error_message=duplicate_error.error_message,
            stack_trace=duplicate_error.stack_trace,
            url=duplicate_error.url,
            method=duplicate_error.method,
            severity=duplicate_error.severity,
            timestamp=timezone.now() - timedelta(hours=i),
        )
        similar.occurrence_count = i + 2
        similar.save()
    print(f"\n✓ Creados 3 errores duplicados del tipo {duplicate_error.error_type}")

# Marcar algunos como resueltos
resolved_count = ErrorLog.objects.filter(severity__in=['INFO', 'WARNING'])[:2].count()
for error in ErrorLog.objects.filter(severity__in=['INFO', 'WARNING'])[:2]:
    if user:
        error.mark_resolved(user)
print(f"\n✓ Marcados {resolved_count} errores como resueltos")

# Mostrar estadísticas finales
total = ErrorLog.objects.count()
unresolved = ErrorLog.objects.filter(is_resolved=False).count()
critical = ErrorLog.objects.filter(severity='CRITICAL', is_resolved=False).count()
by_severity = {}
for severity_choice in ErrorLog.SEVERITY_CHOICES:
    count = ErrorLog.objects.filter(severity=severity_choice[0]).count()
    if count > 0:
        by_severity[severity_choice[1]] = count

print(f"\n" + "="*50)
print(f"ESTADÍSTICAS FINALES")
print(f"="*50)
print(f"Total de errores: {total}")
print(f"Sin resolver: {unresolved}")
print(f"Críticos pendientes: {critical}")
print(f"\nPor severidad:")
for sev_name, count in by_severity.items():
    print(f"  {sev_name}: {count}")

print(f"\n" + "="*50)
print(f"Dashboard disponible en:")
print(f"  http://127.0.0.1:8000/saas-admin/errors/")
print(f"\nAdmin completo en:")
print(f"  http://127.0.0.1:8000/admin/audit/errorlog/")
print(f"="*50)
