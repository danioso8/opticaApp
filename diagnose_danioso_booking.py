import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.appointments.models import SpecificDateSchedule, AppointmentConfiguration
from datetime import date, timedelta

print("="*70)
print("DIAGNÓSTICO DE BOOKING - danioso8329")
print("="*70)

# Buscar usuario
try:
    user = User.objects.get(username='danioso8329')
    print(f"\n✅ Usuario: {user.username}")
    
    if hasattr(user, 'userprofile') and user.userprofile:
        org = user.userprofile.organization
        print(f"✅ Organización: {org.name} (ID: {org.id})")
        print(f"   Slug: {org.slug}")
        print(f"   Activa: {org.is_active}")
    else:
        print("❌ Usuario SIN userprofile")
        exit(1)
        
except User.DoesNotExist:
    print("\n❌ Usuario danioso8329 NO existe")
    exit(1)

# Verificar configuración de citas
print(f"\n{'='*70}")
print("CONFIGURACIÓN DE CITAS")
print("="*70)

try:
    config = AppointmentConfiguration.objects.get(organization=org)
    print(f"✅ AppointmentConfiguration existe")
    print(f"   Abierto: {config.is_open}")
    print(f"   Máx días: {config.max_days_in_advance}")
    print(f"   Duración: {config.appointment_duration} min")
except AppointmentConfiguration.DoesNotExist:
    print(f"❌ NO hay AppointmentConfiguration")
    config = None

# Verificar fechas específicas (lo que realmente necesita)
print(f"\n{'='*70}")
print("FECHAS ESPECÍFICAS (SpecificDateSchedule)")
print("="*70)

today = date.today()
future_date = today + timedelta(days=60)

specific_dates = SpecificDateSchedule.objects.filter(
    organization=org,
    date__gte=today,
    date__lte=future_date,
    is_active=True
).order_by('date')

print(f"Fechas disponibles ({today} a {future_date}): {specific_dates.count()}")

if specific_dates.exists():
    print(f"\n✅ Primeras fechas disponibles:")
    for sd in specific_dates[:5]:
        print(f"   - {sd.date} ({sd.date.strftime('%A')})")
        print(f"     Doctor: {sd.doctor_profile or 'No asignado'}")
        print(f"     Horario: {sd.start_time} - {sd.end_time}")
else:
    print(f"\n❌ NO hay fechas específicas configuradas")
    print("   ⚠️ ESTE ES EL PROBLEMA: Sin fechas específicas, el sistema")
    print("      no puede mostrar ningún horario disponible.")

# Comparar con Oceano Optico (que sí funciona)
print(f"\n{'='*70}")
print("COMPARACIÓN CON OCEANO OPTICO (que sí funciona)")
print("="*70)

try:
    oceano = Organization.objects.get(slug='oceano-optico')
    print(f"✅ Oceano Optico: {oceano.name} (ID: {oceano.id})")
    
    oceano_dates = SpecificDateSchedule.objects.filter(
        organization=oceano,
        date__gte=today,
        is_active=True
    ).count()
    
    print(f"   Fechas disponibles: {oceano_dates}")
    
    if oceano_dates > 0:
        print(f"\n   Primeras 3 fechas de Oceano Optico:")
        for sd in SpecificDateSchedule.objects.filter(
            organization=oceano,
            date__gte=today,
            is_active=True
        ).order_by('date')[:3]:
            print(f"   - {sd.date}: {sd.start_time}-{sd.end_time}")
    
except Organization.DoesNotExist:
    print("❌ Oceano Optico NO encontrada")

# DIAGNÓSTICO FINAL
print(f"\n{'='*70}")
print("DIAGNÓSTICO FINAL")
print("="*70)

if specific_dates.count() == 0:
    print("\n❌ PROBLEMA ENCONTRADO:")
    print("   El usuario danioso8329 NO tiene fechas específicas")
    print("   configuradas (SpecificDateSchedule).")
    print("\n💡 SOLUCIÓN:")
    print("   Necesitas crear fechas específicas para que aparezcan")
    print("   en el calendario de booking.")
    print(f"\n   Opciones:")
    print(f"   1. Copiar fechas de Oceano Optico a {org.name}")
    print(f"   2. Crear nuevas fechas manualmente")
    print(f"   3. Configurar WorkingHours y generar fechas automáticamente")
else:
    print(f"\n✅ Configuración correcta")
    print(f"   {specific_dates.count()} fechas disponibles")

print("\n" + "="*70)
