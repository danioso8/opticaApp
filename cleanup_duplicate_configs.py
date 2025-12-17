"""
Script para limpiar configuraciones duplicadas.
Asegura que solo exista UNA configuración por organización.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.billing.models import InvoiceConfiguration, DianConfiguration
from apps.organizations.models import Organization
from django.db.models import Count

def cleanup_invoice_configurations():
    """Elimina configuraciones de facturación duplicadas."""
    print("=" * 80)
    print("🔍 BUSCANDO CONFIGURACIONES DE FACTURACIÓN DUPLICADAS")
    print("=" * 80)
    print()
    
    # Encontrar organizaciones con múltiples configuraciones
    orgs_with_duplicates = (
        InvoiceConfiguration.objects
        .values('organization')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
    )
    
    if not orgs_with_duplicates:
        print("✅ No se encontraron configuraciones de facturación duplicadas")
        print()
        return
    
    total_deleted = 0
    
    for item in orgs_with_duplicates:
        org_id = item['organization']
        count = item['count']
        
        try:
            org = Organization.objects.get(id=org_id)
            print(f"📋 Organización: {org.name}")
            print(f"   Configuraciones encontradas: {count}")
            
            # Obtener todas las configuraciones ordenadas por última actualización
            configs = InvoiceConfiguration.objects.filter(
                organization=org
            ).order_by('-updated_at', '-created_at')
            
            # Mantener la primera (más reciente o más completa)
            config_to_keep = configs.first()
            configs_to_delete = list(configs[1:])
            
            print(f"   ✅ Manteniendo configuración ID: {config_to_keep.id}")
            print(f"      Creada: {config_to_keep.created_at}")
            print(f"      Actualizada: {config_to_keep.updated_at}")
            
            for config in configs_to_delete:
                print(f"   ❌ Eliminando configuración ID: {config.id}")
                config.delete()
                total_deleted += 1
            
            print()
            
        except Organization.DoesNotExist:
            print(f"⚠️  Organización ID {org_id} no existe, eliminando configuraciones huérfanas...")
            InvoiceConfiguration.objects.filter(organization_id=org_id).delete()
            print()
    
    print(f"📊 Total configuraciones de facturación eliminadas: {total_deleted}")
    print()


def cleanup_dian_configurations():
    """Elimina configuraciones DIAN duplicadas."""
    print("=" * 80)
    print("🔍 BUSCANDO CONFIGURACIONES DIAN DUPLICADAS")
    print("=" * 80)
    print()
    
    # Encontrar organizaciones con múltiples configuraciones
    orgs_with_duplicates = (
        DianConfiguration.objects
        .values('organization')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
    )
    
    if not orgs_with_duplicates:
        print("✅ No se encontraron configuraciones DIAN duplicadas")
        print()
        return
    
    total_deleted = 0
    
    for item in orgs_with_duplicates:
        org_id = item['organization']
        count = item['count']
        
        try:
            org = Organization.objects.get(id=org_id)
            print(f"📋 Organización: {org.name}")
            print(f"   Configuraciones encontradas: {count}")
            
            # Obtener todas las configuraciones ordenadas
            # Priorizar las que están activas y tienen más datos completos
            configs = DianConfiguration.objects.filter(
                organization=org
            ).order_by('-is_active', '-updated_at', '-created_at')
            
            # Mantener la primera (activa, más reciente o más completa)
            config_to_keep = configs.first()
            configs_to_delete = list(configs[1:])
            
            print(f"   ✅ Manteniendo configuración ID: {config_to_keep.id}")
            print(f"      Activa: {config_to_keep.is_active}")
            print(f"      NIT: {config_to_keep.nit or 'No configurado'}")
            print(f"      Creada: {config_to_keep.created_at}")
            print(f"      Actualizada: {config_to_keep.updated_at}")
            
            for config in configs_to_delete:
                print(f"   ❌ Eliminando configuración ID: {config.id}")
                print(f"      Activa: {config.is_active}")
                print(f"      NIT: {config.nit or 'No configurado'}")
                config.delete()
                total_deleted += 1
            
            print()
            
        except Organization.DoesNotExist:
            print(f"⚠️  Organización ID {org_id} no existe, eliminando configuraciones huérfanas...")
            DianConfiguration.objects.filter(organization_id=org_id).delete()
            print()
    
    print(f"📊 Total configuraciones DIAN eliminadas: {total_deleted}")
    print()


def verify_cleanup():
    """Verifica que la limpieza fue exitosa."""
    print("=" * 80)
    print("✅ VERIFICACIÓN FINAL")
    print("=" * 80)
    print()
    
    # Verificar InvoiceConfiguration
    invoice_duplicates = (
        InvoiceConfiguration.objects
        .values('organization')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
    )
    
    if invoice_duplicates.exists():
        print("⚠️  Aún hay configuraciones de facturación duplicadas:")
        for item in invoice_duplicates:
            org = Organization.objects.get(id=item['organization'])
            print(f"   - {org.name}: {item['count']} configuraciones")
    else:
        print("✅ Todas las organizaciones tienen máximo 1 configuración de facturación")
    
    # Verificar DianConfiguration
    dian_duplicates = (
        DianConfiguration.objects
        .values('organization')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
    )
    
    if dian_duplicates.exists():
        print("⚠️  Aún hay configuraciones DIAN duplicadas:")
        for item in dian_duplicates:
            org = Organization.objects.get(id=item['organization'])
            print(f"   - {org.name}: {item['count']} configuraciones")
    else:
        print("✅ Todas las organizaciones tienen máximo 1 configuración DIAN")
    
    print()
    
    # Estadísticas finales
    total_orgs = Organization.objects.count()
    orgs_with_invoice_config = InvoiceConfiguration.objects.values('organization').distinct().count()
    orgs_with_dian_config = DianConfiguration.objects.values('organization').distinct().count()
    
    print("📊 ESTADÍSTICAS FINALES:")
    print(f"   Total organizaciones: {total_orgs}")
    print(f"   Organizaciones con configuración de facturación: {orgs_with_invoice_config}")
    print(f"   Organizaciones con configuración DIAN: {orgs_with_dian_config}")
    print()


def main():
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "LIMPIEZA DE CONFIGURACIONES DUPLICADAS" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    input("⚠️  Este script eliminará configuraciones duplicadas. Presiona ENTER para continuar...")
    print()
    
    # Limpiar configuraciones de facturación
    cleanup_invoice_configurations()
    
    # Limpiar configuraciones DIAN
    cleanup_dian_configurations()
    
    # Verificar limpieza
    verify_cleanup()
    
    print("=" * 80)
    print("✅ LIMPIEZA COMPLETADA")
    print("=" * 80)
    print()
    print("💡 A partir de ahora:")
    print("   - Cada organización tendrá máximo 1 configuración de facturación")
    print("   - Cada organización tendrá máximo 1 configuración DIAN")
    print("   - El sistema usa get_or_create para asegurar configuración única")
    print()


if __name__ == '__main__':
    main()
