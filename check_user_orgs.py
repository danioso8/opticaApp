#!/usr/bin/env python
"""Script para verificar el estado de suscripción y organizaciones del usuario"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import UserSubscription
from django.contrib.auth import get_user_model

User = get_user_model()

# Buscar usuario
username = 'compufayes'
u = User.objects.filter(username=username).first()

if not u:
    print(f"❌ Usuario '{username}' no encontrado")
    sys.exit(1)

print(f"\n{'='*60}")
print(f"📊 INFORMACIÓN DEL USUARIO: {u.username}")
print(f"{'='*60}\n")

if hasattr(u, 'subscription'):
    sub = u.subscription
    print(f"✅ Tiene suscripción activa")
    print(f"   Plan: {sub.plan.name}")
    print(f"   Tipo de Plan: {sub.plan.plan_type}")
    print(f"   Max Users (usado como max_orgs): {sub.plan.max_users}")
    print(f"   Plan activo: {sub.is_active}")
    print(f"   Plan expirado: {sub.is_expired}")
    print(f"   Días restantes: {sub.days_remaining}")
    
    # Contar organizaciones
    orgs_count = u.owned_organizations.filter(is_active=True).count()
    print(f"\n📈 ORGANIZACIONES:")
    print(f"   Organizaciones actuales: {orgs_count}")
    print(f"   Puede crear más: {sub.can_create_organizations()}")
    
    # Listar organizaciones
    orgs = u.owned_organizations.filter(is_active=True)
    if orgs.exists():
        print(f"\n📋 LISTA DE ORGANIZACIONES:")
        for i, org in enumerate(orgs, 1):
            print(f"   {i}. {org.name} (ID: {org.id})")
    
    # Verificar límite
    if sub.plan.max_users >= 999999:
        print(f"\n🎉 Plan con acceso ILIMITADO")
    else:
        print(f"\n📊 Límite: {orgs_count}/{sub.plan.max_users}")
        if orgs_count >= sub.plan.max_users:
            print(f"⚠️  LÍMITE ALCANZADO - No puede crear más organizaciones")
        else:
            print(f"✅ Puede crear {sub.plan.max_users - orgs_count} organizaciones más")
else:
    print(f"❌ Usuario sin suscripción")

print(f"\n{'='*60}\n")
