"""
Script para verificar la configuración en Render y hacer pruebas
Ejecutar en Render Shell: python debug_render.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import LandingPageConfig, Organization
from datetime import date, timedelta

print("=" * 80)
print("DEBUG RENDER - Verificación de Configuración")
print("=" * 80)

# 1. Verificar organizaciones
print("\n1️⃣  ORGANIZACIONES:")
orgs = Organization.objects.all()
for org in orgs:
    print(f"   ID: {org.id} - {org.name} - Activa: {org.is_active}")

# 2. Verificar configuración de landing page
print("\n2️⃣  CONFIGURACIÓN LANDING PAGE:")
configs = LandingPageConfig.objects.all()
for config in configs:
    print(f"   Org: {config.organization.name}")
    print(f"   - Logo: {config.logo}")
    print(f"   - Logo Size: {config.logo_size if hasattr(config, 'logo_size') else 'Campo no existe'}")
    print(f"   - Hero Image: {config.hero_image}")
    print(f"   - Hero Image Fit: {config.hero_image_fit if hasattr(config, 'hero_image_fit') else 'Campo no existe'}")
    print(f"   - Hero Position X: {config.hero_image_position_x if hasattr(config, 'hero_image_position_x') else 'Campo no existe'}")
    print(f"   - Hero Position Y: {config.hero_image_position_y if hasattr(config, 'hero_image_position_y') else 'Campo no existe'}")
    print(f"   - Hero Scale: {config.hero_image_scale if hasattr(config, 'hero_image_scale') else 'Campo no existe'}")
    print(f"   - Overlay Opacity: {config.hero_overlay_opacity if hasattr(config, 'hero_overlay_opacity') else 'Campo no existe'}")

# 3. Probar endpoint de slots
print("\n3️⃣  PRUEBA DE ENDPOINT AVAILABLE SLOTS:")
try:
    from apps.appointments.utils import get_available_slots_for_date
    
    test_date = date.today() + timedelta(days=1)
    org = Organization.objects.filter(is_active=True).first()
    
    if org:
        print(f"   Probando con organización: {org.name} (ID: {org.id})")
        print(f"   Fecha: {test_date}")
        
        slots = get_available_slots_for_date(test_date, org, None)
        print(f"   ✅ Slots encontrados: {len(slots)}")
        
        if slots:
            print(f"   Primer slot: {slots[0]}")
    else:
        print("   ❌ No hay organizaciones activas")
        
except Exception as e:
    print(f"   ❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

# 4. Verificar campos en la BD
print("\n4️⃣  VERIFICAR CAMPOS EN BASE DE DATOS:")
try:
    from django.db import connection
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'organizations_landingpageconfig'
            ORDER BY column_name;
        """)
        columns = [row[0] for row in cursor.fetchall()]
        
        print("   Columnas en organizations_landingpageconfig:")
        for col in columns:
            print(f"      - {col}")
            
        # Verificar campos específicos
        required_fields = [
            'logo_size',
            'hero_image_fit',
            'hero_image_position_x',
            'hero_image_position_y',
            'hero_image_scale',
            'hero_overlay_opacity'
        ]
        
        print("\n   Campos requeridos:")
        for field in required_fields:
            exists = field in columns
            status = "✅" if exists else "❌"
            print(f"      {status} {field}")
            
except Exception as e:
    print(f"   ❌ Error al verificar columnas: {str(e)}")

print("\n" + "=" * 80)
print("FIN DE VERIFICACIÓN")
print("=" * 80)
