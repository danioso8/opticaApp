#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, '/var/www/opticaapp')
os.chdir('/var/www/opticaapp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from apps.organizations.models import Organization

print("Buscando organizaciones con 'compu' o 'easy'...")
orgs = Organization.objects.filter(name__icontains='compu').values('id', 'name', 'slug', 'is_active')
for org in orgs:
    print(f"  ID: {org['id']}, Name: {org['name']}, Slug: {org['slug']}, Active: {org['is_active']}")

orgs2 = Organization.objects.filter(name__icontains='easy').values('id', 'name', 'slug', 'is_active')
for org in orgs2:
    print(f"  ID: {org['id']}, Name: {org['name']}, Slug: {org['slug']}, Active: {org['is_active']}")

print("\nBuscando usuario 'danioso8329'...")
from apps.users.models import CustomUser
users = CustomUser.objects.filter(username__icontains='danioso').values('id', 'username', 'email')
for user in users:
    print(f"  ID: {user['id']}, Username: {user['username']}, Email: {user['email']}")
