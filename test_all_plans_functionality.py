#!/usr/bin/env python
"""Script para crear usuarios de prueba con cada tipo de plan y verificar funcionalidad"""
import os
import sys
import django
from datetime import timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.organizations.models import SubscriptionPlan, Organization
from apps.users.models import UserSubscription

User = get_user_model()

print("\n" + "="*70)
print("🧪 TEST COMPLETO DE FUNCIONALIDAD POR PLAN")
print("="*70 + "\n")

# Obtener todos los planes
plans = SubscriptionPlan.objects.all().order_by('price_monthly')

test_users = []

# Crear o obtener usuarios de prueba para cada plan
for plan in plans:
    username = f"test_{plan.plan_type}"
    email = f"test_{plan.plan_type}@test.com"
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email}
    )
    
    if created:
        user.set_password('test123')
        user.save()
        print(f"✅ Usuario creado: {username}")
    else:
        print(f"✓  Usuario existente: {username}")
    
    # Crear o actualizar suscripción
    try:
        sub = UserSubscription.objects.get(user=user)
        sub.plan = plan
        sub.is_active = True
        sub.end_date = timezone.now() + timedelta(days=30)
        sub.save()
        print(f"   📝 Suscripción actualizada a {plan.name}")
    except UserSubscription.DoesNotExist:
        sub = UserSubscription.objects.create(
            user=user,
            plan=plan,
            is_active=True,
            end_date=timezone.now() + timedelta(days=30),
            payment_status='paid'
        )
        print(f"   ✨ Suscripción creada: {plan.name}")
    
    test_users.append((user, sub, plan))
    print()

# Test de creación de organizaciones para cada usuario
print("\n" + "-"*70)
print("🧪 TEST DE CREACIÓN DE ORGANIZACIONES")
print("-"*70 + "\n")

for user, sub, plan in test_users:
    print(f"\n👤 Usuario: {user.username} - Plan: {plan.name}")
    print(f"   Límite: {plan.max_users if plan.max_users < 999999 else '∞'} organizaciones")
    
    # Contar organizaciones existentes
    existing_orgs = user.owned_organizations.filter(is_active=True).count()
    print(f"   Organizaciones actuales: {existing_orgs}")
    
    # Verificar si puede crear más
    can_create = sub.can_create_organizations()
    print(f"   ¿Puede crear más? {'✅ Sí' if can_create else '❌ No'}")
    
    # Intentar crear organizaciones hasta el límite
    if plan.max_users < 999999:
        # Plan con límite
        orgs_to_create = plan.max_users - existing_orgs
        print(f"   Intentando crear {orgs_to_create} organizaciones adicionales...")
        
        for i in range(orgs_to_create):
            try:
                if sub.can_create_organizations():
                    org = Organization.objects.create(
                        name=f"Test Org {user.username} #{existing_orgs + i + 1}",
                        slug=f"test-org-{user.username}-{existing_orgs + i + 1}",
                        email=f"org{existing_orgs + i + 1}@{user.username}.com",
                        owner=user
                    )
                    print(f"      ✅ Creada: {org.name}")
                else:
                    print(f"      ⚠️  Límite alcanzado en organización #{existing_orgs + i + 1}")
                    break
            except Exception as e:
                print(f"      ❌ Error: {str(e)}")
                break
        
        # Intentar crear una más (debería fallar)
        print(f"   Intentando crear una más (debería fallar)...")
        if sub.can_create_organizations():
            print(f"      ⚠️  ERROR: Permitió crear más del límite!")
        else:
            print(f"      ✅ Correctamente bloqueado - Límite respetado")
    else:
        # Plan ilimitado
        print(f"   ✅ Plan ILIMITADO - Siempre puede crear más")
        # Crear 3 de prueba
        for i in range(3):
            if i >= existing_orgs:
                try:
                    org = Organization.objects.create(
                        name=f"Test Org {user.username} #{existing_orgs + i + 1}",
                        slug=f"test-org-{user.username}-{existing_orgs + i + 1}",
                        email=f"org{existing_orgs + i + 1}@{user.username}.com",
                        owner=user
                    )
                    print(f"      ✅ Creada: {org.name}")
                except Exception as e:
                    print(f"      ❌ Error: {str(e)}")
    
    # Resumen final
    final_count = user.owned_organizations.filter(is_active=True).count()
    print(f"   📊 Total final: {final_count} organizaciones")

print("\n" + "="*70)
print("✅ TEST COMPLETADO")
print("="*70 + "\n")
