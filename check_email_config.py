"""
Verificar configuración de email y usuarios recientes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from apps.users.models import UserProfile

print('=' * 60)
print('CONFIGURACIÓN DE EMAIL')
print('=' * 60)
print(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
print(f'EMAIL_HOST: {getattr(settings, "EMAIL_HOST", "No configurado")}')
print(f'EMAIL_PORT: {getattr(settings, "EMAIL_PORT", "No configurado")}')
print(f'EMAIL_HOST_USER: {getattr(settings, "EMAIL_HOST_USER", "No configurado")}')
print(f'EMAIL_USE_TLS: {getattr(settings, "EMAIL_USE_TLS", "No configurado")}')
print(f'DEFAULT_FROM_EMAIL: {getattr(settings, "DEFAULT_FROM_EMAIL", "No configurado")}')

print('\n' + '=' * 60)
print('USUARIOS RECIENTES')
print('=' * 60)
recent_users = User.objects.all().order_by('-date_joined')[:10]
for u in recent_users:
    print(f'  - {u.username} ({u.email})')
    print(f'    Creado: {u.date_joined}')
    print(f'    Activo: {u.is_active}')
    
    try:
        profile = UserProfile.objects.get(user=u)
        print(f'    Email verificado: {profile.is_email_verified}')
        print(f'    Verificado el: {profile.email_verified_at}')
    except UserProfile.DoesNotExist:
        print(f'    ⚠️  No tiene UserProfile')
    print()

print('=' * 60)
print(f'Total usuarios: {User.objects.count()}')
print(f'Usuarios verificados: {UserProfile.objects.filter(is_email_verified=True).count()}')
print('=' * 60)
