"""
Deshabilitar verificación de email y activar todos los usuarios
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserProfile
from django.utils import timezone

print('=' * 60)
print('ACTIVANDO TODOS LOS USUARIOS')
print('=' * 60)

# Obtener todos los usuarios
users = User.objects.all()
print(f'\nTotal usuarios: {users.count()}\n')

for user in users:
    # Activar usuario
    if not user.is_active:
        user.is_active = True
        user.save()
        print(f'✅ Activado: {user.username}')
    
    # Obtener o crear UserProfile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Verificar email
    if not profile.is_email_verified:
        profile.is_email_verified = True
        profile.email_verified_at = timezone.now()
        profile.save()
        print(f'✅ Email verificado: {user.username} ({user.email})')
    else:
        print(f'ℹ️  Ya verificado: {user.username} ({user.email})')

print('\n' + '=' * 60)
print('VERIFICACIÓN FINAL')
print('=' * 60)

total = User.objects.count()
activos = User.objects.filter(is_active=True).count()
verificados = UserProfile.objects.filter(is_email_verified=True).count()

print(f'Total usuarios: {total}')
print(f'Usuarios activos: {activos}')
print(f'Emails verificados: {verificados}')
print('\n✅ Todos los usuarios pueden acceder sin verificar email')
print('=' * 60)
