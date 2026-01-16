#!/usr/bin/env python3
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models import SpecificDateSchedule
from datetime import date

print("="*70)
print("ORGANIZACIONES EN CONTABO")
print("="*70)

orgs = Organization.objects.all()
today = date.today()

for o in orgs:
    fechas = SpecificDateSchedule.objects.filter(
        organization=o, 
        date__gte=today, 
        is_active=True
    ).count()
    print(f"{o.id} - {o.slug} - {o.name} - Activa: {o.is_active} - Fechas: {fechas}")

print("\n" + "="*70)
