"""
Script para migrar usuarios existentes al sistema de verificación de email
Crea perfiles para usuarios que no tienen y los marca como verificados
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.email_verification_models import UserProfile
from django.utils import timezone


def migrate_existing_users():
    """Migra usuarios existentes creando sus perfiles"""
    
    print("=" * 60)
    print("MIGRACIÓN DE USUARIOS EXISTENTES")
    print("=" * 60)
    
    # Obtener usuarios sin perfil
    users_without_profile = User.objects.exclude(
        id__in=UserProfile.objects.values_list('user_id', flat=True)
    )
    
    total = users_without_profile.count()
    print(f"\nUsuarios sin perfil encontrados: {total}")
    
    if total == 0:
        print("✓ Todos los usuarios ya tienen perfil")
        return
    
    print("\n¿Deseas crear perfiles para estos usuarios?")
    print("Los usuarios existentes serán marcados como VERIFICADOS automáticamente")
    print("para no interrumpir su acceso.\n")
    
    for user in users_without_profile:
        print(f"  - {user.username} ({user.email}) - is_active: {user.is_active}")
    
    confirm = input("\n¿Continuar? (s/n): ").lower().strip()
    
    if confirm != 's':
        print("Operación cancelada")
        return
    
    print("\nCreando perfiles...")
    created_count = 0
    
    for user in users_without_profile:
        try:
            profile = UserProfile.objects.create(
                user=user,
                is_email_verified=True,  # Usuarios existentes son verificados automáticamente
                email_verified_at=timezone.now()
            )
            
            # Asegurar que el usuario esté activo
            if not user.is_active:
                user.is_active = True
                user.save()
            
            print(f"  ✓ {user.username} - Perfil creado y marcado como verificado")
            created_count += 1
            
        except Exception as e:
            print(f"  ✗ {user.username} - Error: {e}")
    
    print(f"\n{'='*60}")
    print(f"MIGRACIÓN COMPLETADA")
    print(f"Perfiles creados: {created_count}/{total}")
    print(f"{'='*60}")


if __name__ == '__main__':
    migrate_existing_users()
