"""
Script para asignar usuarios al grupo Doctores
Ejecutar en Render con: python assign_doctors_group.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Group

def assign_doctors_to_group():
    # Crear grupo Doctores si no existe
    doctors_group, created = Group.objects.get_or_create(name='Doctores')
    if created:
        print("✓ Grupo 'Doctores' creado")
    else:
        print("✓ Grupo 'Doctores' ya existe")
    
    # Lista de usuarios que son doctores (por username, email o nombre)
    doctor_identifiers = [
        'Luis Andres Duque Taborda',
        'Sara Ines Espinel Torres',
        'luisandres',
        'saraines',
    ]
    
    doctors_found = 0
    
    # Buscar y asignar por username
    for identifier in doctor_identifiers:
        # Buscar por username
        users = User.objects.filter(username__icontains=identifier)
        for user in users:
            if doctors_group not in user.groups.all():
                user.groups.add(doctors_group)
                print(f"✓ Usuario '{user.username}' ({user.get_full_name()}) agregado al grupo Doctores")
                doctors_found += 1
            else:
                print(f"  Usuario '{user.username}' ya está en el grupo Doctores")
    
    # Buscar por nombre completo
    users = User.objects.filter(
        first_name__icontains='Luis',
        last_name__icontains='Duque'
    ) | User.objects.filter(
        first_name__icontains='Sara',
        last_name__icontains='Espinel'
    )
    
    for user in users:
        if doctors_group not in user.groups.all():
            user.groups.add(doctors_group)
            print(f"✓ Usuario '{user.username}' ({user.get_full_name()}) agregado al grupo Doctores")
            doctors_found += 1
        else:
            print(f"  Usuario '{user.username}' ya está en el grupo Doctores")
    
    # Mostrar resumen
    print(f"\n--- RESUMEN ---")
    print(f"Total de usuarios en grupo 'Doctores': {doctors_group.user_set.count()}")
    print("\nUsuarios en el grupo Doctores:")
    for user in doctors_group.user_set.all():
        print(f"  - {user.get_full_name() or user.username} ({user.email})")

if __name__ == '__main__':
    print("=== Asignando doctores al grupo Doctores ===\n")
    assign_doctors_to_group()
    print("\n✓ Proceso completado")
