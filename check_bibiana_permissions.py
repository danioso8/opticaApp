"""
Script para verificar permisos de Bibiana Angel
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import OrganizationMember, MemberModulePermission, Organization

print("=" * 80)
print("🔍 Buscando usuarios y organizaciones...")
print("=" * 80)

# Listar todas las organizaciones
orgs = Organization.objects.all()
print(f"\n📊 Organizaciones ({orgs.count()}):")
for org in orgs:
    print(f"   • ID: {org.id} - {org.name}")

# Buscar a Bibiana
print("\n" + "=" * 80)
print("👤 Buscando usuarios con 'bibiana' o 'angel'...")
print("=" * 80)

users = User.objects.filter(first_name__icontains='bibiana') | User.objects.filter(last_name__icontains='angel')

if not users.exists():
    print("❌ No se encontró ningún usuario")
    print("\n📋 Primeros 10 usuarios del sistema:")
    for u in User.objects.all()[:10]:
        print(f"   • {u.username} - {u.first_name} {u.last_name} ({u.email})")
else:
    for user in users:
        print(f"\n✅ Usuario: {user.username}")
        print(f"   Nombre: {user.first_name} {user.last_name}")
        print(f"   Email: {user.email}")
        print(f"   Activo: {'Sí' if user.is_active else 'No'}")
        
        # Buscar membresías
        members = OrganizationMember.objects.filter(user=user).select_related('organization')
        
        if not members.exists():
            print(f"   ⚠️  Sin membresías")
        else:
            for member in members:
                print(f"\n   🏢 Organización: {member.organization.name} (ID: {member.organization.id})")
                print(f"      👤 Rol: {member.get_role_display()}")
                print(f"      ✓ Activo: {'Sí' if member.is_active else 'No'}")
                print(f"      🆔 Member ID: {member.id}")
                
                # Obtener permisos
                perms = MemberModulePermission.objects.filter(member=member).select_related('module')
                
                if member.role in ['owner', 'admin']:
                    print(f"      🔓 ACCESO TOTAL (Owner/Admin)")
                else:
                    print(f"\n      📋 Permisos asignados: {perms.count()} módulos")
                    
                    if perms.count() == 0:
                        print("      ⚠️  NO HAY PERMISOS ASIGNADOS")
                        print(f"      💡 URL para asignar: https://www.optikaapp.com/dashboard/team/{member.id}/permissions/")
                    else:
                        print("      " + "-" * 72)
                        for perm in perms.order_by('module__category', 'module__name'):
                            permisos = []
                            if perm.can_view: permisos.append('👁️ Ver')
                            if perm.can_create: permisos.append('➕ Crear')
                            if perm.can_edit: permisos.append('✏️ Editar')
                            if perm.can_delete: permisos.append('🗑️ Eliminar')
                            
                            perms_str = ' | '.join(permisos) if permisos else '❌ SIN PERMISOS'
                            category = perm.module.get_category_display()
                            print(f"      • [{category}] {perm.module.name:<25} → {perms_str}")

# Listar todos los miembros de OCÉANO ÓPTICO
print("\n" + "=" * 80)
print("👥 TODOS LOS MIEMBROS DE OCÉANO ÓPTICO")
print("=" * 80)

oceano = Organization.objects.filter(name__icontains='oceano').first()
if oceano:
    members = OrganizationMember.objects.filter(organization=oceano).select_related('user')
    print(f"\n🏢 Organización: {oceano.name} (ID: {oceano.id})")
    print(f"   Miembros totales: {members.count()}")
    print("\n")
    
    for member in members:
        perms_count = MemberModulePermission.objects.filter(member=member).count()
        print(f"   • {member.user.get_full_name() or member.user.username:<25} ({member.user.username})")
        print(f"     Rol: {member.get_role_display():<15} | Activo: {'✓' if member.is_active else '✗'} | Permisos: {perms_count} | ID: {member.id}")
