"""
Script para eliminar doctor específico con ID 71360801
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models import Doctor

doctor = Doctor.objects.get(identification='71360801')
print(f"Eliminando doctor: {doctor.full_name}")
doctor.delete()
print("✅ Doctor eliminado exitosamente")
