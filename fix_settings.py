#!/usr/bin/env python3
"""
Script para corregir errores en settings.py - Version 2
Elimina toda la configuración de Celery y la reescribe correctamente
"""
import re

print('Leyendo settings.py...')
with open('/var/www/opticaapp/config/settings.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Hacer backup
with open('/var/www/opticaapp/config/settings.py.backup2', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('✓ Backup creado: config/settings.py.backup2')

# Encontrar y eliminar toda la sección de Celery Beat Schedule
new_lines = []
skip_celery = False
brace_count = 0

for i, line in enumerate(lines):
    if '# Celery Beat Schedule' in line:
        skip_celery = True
        # Agregar la nueva configuración correcta
        new_lines.append('# Celery Beat Schedule\n')
        new_lines.append('try:\n')
        new_lines.append('    from celery.schedules import crontab\n')
        new_lines.append('    CELERY_BEAT_SCHEDULE = {\n')
        new_lines.append("        'check-trials-daily': {\n")
        new_lines.append("            'task': 'apps.organizations.tasks.check_trial_status_daily',\n")
        new_lines.append("            'schedule': crontab(hour=9, minute=0),\n")
        new_lines.append("        },\n")
        new_lines.append("        'update-usage-stats-daily': {\n")
        new_lines.append("            'task': 'apps.organizations.tasks.update_module_usage_stats',\n")
        new_lines.append("            'schedule': crontab(hour=2, minute=0),\n")
        new_lines.append("        },\n")
        new_lines.append("        'archive-expired-weekly': {\n")
        new_lines.append("            'task': 'apps.organizations.tasks.archive_expired_organizations',\n")
        new_lines.append("            'schedule': crontab(hour=3, minute=0, day_of_week=0),\n")
        new_lines.append("        },\n")
        new_lines.append("        'delete-archived-monthly': {\n")
        new_lines.append("            'task': 'apps.organizations.tasks.delete_archived_organizations',\n")
        new_lines.append("            'schedule': crontab(hour=4, minute=0, day_of_month=1),\n")
        new_lines.append("        },\n")
        new_lines.append('    }\n')
        new_lines.append('except ImportError:\n')
        new_lines.append('    CELERY_BEAT_SCHEDULE = {}\n')
        new_lines.append('\n')
        continue
    
    if skip_celery:
        # Contar llaves para saber cuándo terminaobraz el CELERY_BEAT_SCHEDULE
        brace_count += line.count('{') - line.count('}')
        if brace_count <= 0 and ('}' in line or 'except' in line):
            skip_celery = False
        continue
    
    new_lines.append(line)

# Escribir cambios
with open('/var/www/opticaapp/config/settings.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('\n✅ Settings.py corregido exitosamente')
print('Para restaurar: mv config/settings.py.backup2 config/settings.py')
