#!/usr/bin/env python
"""
Script de verificación del sistema de almacenamiento multi-tenant
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.core.storage_utils import (
    OrganizationUploadPath,
    get_organization_media_path,
    get_organization_storage_usage
)
from apps.organizations.models import Organization

print("=" * 80)
print("🔍 VERIFICACIÓN DEL SISTEMA DE ALMACENAMIENTO MULTI-TENANT")
print("=" * 80)
print()

# Test 1: Verificar que las carpetas existen
print("📁 Test 1: Verificación de carpetas creadas")
print("-" * 80)
for org in Organization.objects.all():
    path = get_organization_media_path(org.id, '')
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} Organización {org.id} ({org.name}): {path}")
    
    if exists:
        # Contar subcarpetas
        subdirs = [d for d in path.iterdir() if d.is_dir()]
        print(f"   📂 {len(subdirs)} subcarpetas creadas")
print()

# Test 2: Verificar que OrganizationUploadPath funciona
print("🧪 Test 2: Funcionalidad de OrganizationUploadPath")
print("-" * 80)

class MockInstance:
    def __init__(self, org_id):
        self.organization_id = org_id
        self.organization = type('obj', (object,), {'id': org_id})()

uploader = OrganizationUploadPath('logos')
for org in Organization.objects.all():
    instance = MockInstance(org.id)
    path = uploader(instance, 'test_logo.png')
    expected = f'org_{org.id}/logos/test_logo.png'
    status = "✅" if path == expected else "❌"
    print(f"{status} Org {org.id}: {path} (esperado: {expected})")
print()

# Test 3: Calcular uso de almacenamiento
print("💾 Test 3: Uso de almacenamiento por organización")
print("-" * 80)
for org in Organization.objects.all():
    usage = get_organization_storage_usage(org.id)
    print(f"📊 {org.name} (ID: {org.id})")
    print(f"   Archivos: {usage['file_count']}")
    print(f"   Tamaño: {usage['total_bytes']} bytes ({usage['total_mb']:.2f} MB)")
print()

# Test 4: Verificar permisos
print("🔐 Test 4: Permisos de carpetas")
print("-" * 80)
for org in Organization.objects.all():
    path = get_organization_media_path(org.id, '')
    if path.exists():
        stat = path.stat()
        mode = oct(stat.st_mode)[-3:]
        # www-data UID suele ser 33 en Debian/Ubuntu
        owner = f"UID: {stat.st_uid}, GID: {stat.st_gid}"
        status = "✅" if mode >= '755' else "⚠️"
        print(f"{status} {path}: {mode} ({owner})")
print()

print("=" * 80)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 80)
