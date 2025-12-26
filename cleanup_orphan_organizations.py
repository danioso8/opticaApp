"""
Script para eliminar organizaciones huérfanas sin usuarios
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization, OrganizationMember

def cleanup_orphan_organizations():
    print("🔍 Buscando organizaciones sin usuarios...")
    
    all_orgs = Organization.objects.all()
    
    for org in all_orgs:
        member_count = OrganizationMember.objects.filter(organization=org).count()
        
        if member_count == 0:
            print(f"\n⚠️  Organización sin usuarios:")
            print(f"  ID: {org.id}")
            print(f"  Nombre: {org.name}")
            print(f"  Activa: {org.is_active}")
            
            confirm = input(f"¿Eliminar esta organización? (s/n): ")
            if confirm.lower() == 's':
                org_name = org.name
                org.delete()
                print(f"✅ Organización '{org_name}' eliminada")
            else:
                print("❌ Organización conservada")

if __name__ == '__main__':
    cleanup_orphan_organizations()
