#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

# Crear tabla SidebarCustomization
sql = """
CREATE TABLE IF NOT EXISTS dashboard_sidebarcustomization (
    id BIGSERIAL PRIMARY KEY,
    config JSONB NOT NULL DEFAULT '{}'::jsonb,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    organization_id BIGINT NOT NULL REFERENCES organizations_organization(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    UNIQUE(user_id, organization_id)
);

CREATE INDEX IF NOT EXISTS dashboard_sidebarcustomization_organization_id 
ON dashboard_sidebarcustomization(organization_id);

CREATE INDEX IF NOT EXISTS dashboard_sidebarcustomization_user_id 
ON dashboard_sidebarcustomization(user_id);
"""

with connection.cursor() as cursor:
    cursor.execute(sql)
    
print("✅ Tabla dashboard_sidebarcustomization creada exitosamente")

# Ahora marcar la migración como aplicada
from django.db import connection
from datetime import datetime

with connection.cursor() as cursor:
    cursor.execute(
        "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
        ['dashboard', '0013_sidebarcustomization', datetime.now()]
    )
    connection.commit()

print("✅ Migración 0013_sidebarcustomization marcada como aplicada")
