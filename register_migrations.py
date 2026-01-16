#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from datetime import datetime

migrations_to_add = [
    ('organizations', '0028_organization_upload_paths'),
    ('patients', '0033_doctor_upload_paths'),
    ('dashboard', '0030_arframe_upload_paths'),
    ('billing', '0016_upload_paths'),
]

with connection.cursor() as cursor:
    for app, name in migrations_to_add:
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
            [app, name, datetime.now()]
        )
    connection.commit()

print("✅ Migraciones registradas exitosamente")
