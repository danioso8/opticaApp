"""
Script para eliminar configuraciones de facturación duplicadas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.billing.models import InvoiceConfiguration
from django.db.models import Count

print("=" * 50)
print("LIMPIEZA DE CONFIGURACIONES DUPLICADAS")
print("=" * 50)

# Encontrar duplicados
duplicates = (InvoiceConfiguration.objects
              .values('organization')
              .annotate(count=Count('id'))
              .filter(count__gt=1))

print(f"\nOrganizaciones con configuraciones duplicadas: {duplicates.count()}")

for dup in duplicates:
    org_id = dup['organization']
    count = dup['count']
    
    # Obtener todas las configs para esta org, ordenadas por fecha de actualización
    configs = InvoiceConfiguration.objects.filter(
        organization_id=org_id
    ).order_by('-updated_at')
    
    print(f"\nOrganización ID {org_id}: {count} configuraciones")
    
    # Mantener la más reciente (primera), eliminar el resto
    keep = configs.first()
    to_delete = configs.exclude(id=keep.id)
    
    print(f"  Manteniendo: ID {keep.id} (IVA: {keep.iva_porcentaje}%, Descuento: {keep.descuento_maximo_porcentaje}%)")
    
    for config in to_delete:
        print(f"  Eliminando: ID {config.id} (IVA: {config.iva_porcentaje}%, Descuento: {config.descuento_maximo_porcentaje}%)")
        config.delete()

# Verificar resultado
remaining = InvoiceConfiguration.objects.all()
print(f"\n{'='*50}")
print(f"RESULTADO FINAL: {remaining.count()} configuraciones")
print(f"{'='*50}")

for config in remaining:
    print(f"ID {config.id} - {config.organization.name}")
    print(f"  IVA: {config.iva_porcentaje}%")
    print(f"  Descuento máximo: {config.descuento_maximo_porcentaje}%")
    print(f"  Retefuente: {config.aplicar_retefuente} ({config.retefuente_porcentaje}%)")
    print(f"  ReteIVA: {config.aplicar_reteiva} ({config.reteiva_porcentaje}%)")
    print(f"  Métodos de pago: {config.metodos_pago_disponibles}")
    print(f"  Actualizado: {config.updated_at}")
    print()
