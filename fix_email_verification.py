"""
Fix email verification for danioso8 user
The column is is_email_verified, not email_verified!
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optica_project.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserProfile
from django.utils import timezone

# Get the user
user = User.objects.get(username='danioso8')
print(f"Usuario: {user.username}")
print(f"Email: {user.email}")
print(f"is_active: {user.is_active}")
print(f"is_superuser: {user.is_superuser}")

# Get or create UserProfile
profile, created = UserProfile.objects.get_or_create(user=user)

if created:
    print("✅ UserProfile creado")
else:
    print("ℹ️ UserProfile ya existía")

# Set the CORRECT field name: is_email_verified
profile.is_email_verified = True
profile.email_verified_at = timezone.now()
profile.save()

print(f"\n✅ Email verificado correctamente!")
print(f"is_email_verified: {profile.is_email_verified}")
print(f"email_verified_at: {profile.email_verified_at}")
