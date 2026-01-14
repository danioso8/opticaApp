"""
Script para verificar permisos de un usuario específico
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import OrganizationMember, MemberModulePermission

# Buscar usuario
username = "danios8329"
user = User.objects.filter(username__icontains=username).first()

if not user:
    # Intentar buscar por email
    user = User.objects.filter(email__icontains='danios').first()
    if not user:
        print(f"❌ Usuario '{username}' no encontrado")
        print("\n📋 Usuarios disponibles:")
        for u in User.objects.all()[:10]:
            print(f"   • {u.username} - {u.get_full_name() or u.email}")
        exit(1)

print(f"✅ Usuario encontrado: {user.username} - {user.get_full_name() or user.email}")
print("=" * 80)

# Buscar miembros
members = OrganizationMember.objects.filter(user=user).select_related('organization')

if not members:
    print(f"❌ No hay membresías para este usuario")
    exit(1)

for member in members:
    print(f"\n🏢 Organización: {member.organization.name}")
    print(f"   👤 Rol: {member.get_role_display()}")
    print(f"   ✓ Activo: {'Sí' if member.is_active else 'No'}")
    
    # Obtener permisos
    perms = MemberModulePermission.objects.filter(member=member).select_related('module')
    
    if member.role in ['owner', 'admin']:
        print(f"   🔓 ACCESO TOTAL (Owner/Admin)")
    else:
        print(f"\n   📋 Permisos asignados ({perms.count()} módulos):")
        print("   " + "-" * 76)
        
        if perms.count() == 0:
            print("   ⚠️  NO HAY PERMISOS ASIGNADOS")
        else:
            for perm in perms.order_by('module__category', 'module__name'):
                permisos = []
                if perm.can_view: permisos.append('Ver')
                if perm.can_create: permisos.append('Crear')
                if perm.can_edit: permisos.append('Editar')
                if perm.can_delete: permisos.append('Eliminar')
                
                perms_str = ', '.join(permisos) if permisos else 'SIN PERMISOS'
                print(f"   • {perm.module.name:<30} → {perms_str}")

# Buscar a Bibiana Angel
print("\n" + "=" * 80)
print("🔍 Buscando a Bibiana Angel...")

bibiana_user = User.objects.filter(first_name__icontains='bibiana').first()
if bibiana_user:
    print(f"\n✅ Usuario encontrado: {bibiana_user.username} - {bibiana_user.get_full_name()}")
    print("=" * 80)
    
    members_bibiana = OrganizationMember.objects.filter(user=bibiana_user).select_related('organization')
    
    for member in members_bibiana:
        print(f"\n🏢 Organización: {member.organization.name}")
        print(f"   👤 Rol: {member.get_role_display()}")
        print(f"   ✓ Activo: {'Sí' if member.is_active else 'No'}")
        
        # Obtener permisos
        perms = MemberModulePermission.objects.filter(member=member).select_related('module')
        
        if member.role in ['owner', 'admin']:
            print(f"   🔓 ACCESO TOTAL (Owner/Admin)")
        else:
            print(f"\n   📋 Permisos asignados ({perms.count()} módulos):")
            print("   " + "-" * 76)
            
            if perms.count() == 0:
                print("   ⚠️  NO HAY PERMISOS ASIGNADOS")
                print("   💡 Solución: Asignar permisos desde /dashboard/team/")
            else:
                for perm in perms.order_by('module__category', 'module__name'):
                    permisos = []
                    if perm.can_view: permisos.append('✓Ver')
                    if perm.can_create: permisos.append('✓Crear')
                    if perm.can_edit: permisos.append('✓Editar')
                    if perm.can_delete: permisos.append('✓Eliminar')
                    
                    perms_str = ', '.join(permisos) if permisos else '❌ SIN PERMISOS'
                    category = perm.module.get_category_display()
                    print(f"   • [{category}] {perm.module.name:<25} → {perms_str}")
else:
    print("❌ No se encontró a Bibiana Angel")
