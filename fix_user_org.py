"""
Verificar y configurar organización para el usuario danioso8329
"""

from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.payroll.models import Employee

print("=" * 80)
print("DIAGNÓSTICO USUARIO danioso8329")
print("=" * 80)

# Obtener usuario
usuario = User.objects.get(username='danioso8329')
print(f"\n👤 Usuario: {usuario.username}")
print(f"   Email: {usuario.email}")
print(f"   Staff: {usuario.is_staff}")
print(f"   Superuser: {usuario.is_superuser}")

# Ver perfil
print(f"\n🔍 Verificando perfil...")
if hasattr(usuario, 'userprofile'):
    profile = usuario.userprofile
    print(f"   ✓ Tiene UserProfile")
    print(f"   Organization: {profile.organization if hasattr(profile, 'organization') else 'N/A'}")
    
    # Ver todos los atributos del perfil
    print(f"\n   Atributos del perfil:")
    for attr in dir(profile):
        if not attr.startswith('_') and not callable(getattr(profile, attr)):
            try:
                value = getattr(profile, attr)
                if 'org' in attr.lower():
                    print(f"      {attr}: {value}")
            except:
                pass
else:
    print(f"   ✗ NO tiene UserProfile")

# Ver organizaciones disponibles
print(f"\n🏢 Organizaciones en el sistema:")
for org in Organization.objects.all():
    emps = Employee.objects.filter(organization=org).count()
    print(f"   ID {org.id}: {org.name} - {emps} empleados")

# Verificar si el usuario puede ver la org 2
org2 = Organization.objects.get(id=2)
print(f"\n🎯 Organización CompuEasys (ID: 2):")
empleados = Employee.objects.filter(organization=org2)
print(f"   Total empleados: {empleados.count()}")
for emp in empleados:
    print(f"      ✓ {emp.numero_documento} - {emp.primer_nombre} {emp.primer_apellido}")

# Intentar asignar la organización al perfil si existe
print(f"\n🔧 Intentando configurar organización...")
try:
    if hasattr(usuario, 'userprofile'):
        # Ver qué campo usar para la organización
        if hasattr(usuario.userprofile, 'current_organization'):
            usuario.userprofile.current_organization = org2
            usuario.userprofile.save()
            print(f"   ✓ current_organization configurado a: {org2.name}")
        elif hasattr(usuario.userprofile, 'organization'):
            usuario.userprofile.organization = org2
            usuario.userprofile.save()
            print(f"   ✓ organization configurado a: {org2.name}")
        else:
            print(f"   ⚠️  No se encontró campo de organización en UserProfile")
            
            # Intentar crear/actualizar relación
            from django.contrib.contenttypes.models import ContentType
            print(f"\n   Buscando otras formas de relacionar usuario con organización...")
            
    else:
        print(f"   ⚠️  Usuario sin UserProfile")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print(f"\n✅ Diagnóstico completado")
