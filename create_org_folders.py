#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.core.storage_utils import create_organization_media_folders
from apps.organizations.models import Organization

print("🔧 Creando estructura de carpetas para organizaciones existentes...")
print()

for org in Organization.objects.all():
    print(f"📁 Organización {org.id}: {org.name}")
    try:
        create_organization_media_folders(org.id)
        print(f"   ✅ Carpetas creadas exitosamente")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

print("🎉 Proceso completado!")
