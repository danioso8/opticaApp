"""
Verificar configuración de booking para danioso8329
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.core.models import User
from apps.organizations.models import Organization
from apps.appointments.models import SpecificDateSchedule, AppointmentConfiguration, WorkingHours

print("=" * 60)
print("VERIFICANDO BOOKING - danioso8329")
print("=" * 60)

# Buscar usuario
try:
    user = User.objects.get(username='danioso8329')
    print(f"\n✓ Usuario encontrado: {user.username}")
except User.DoesNotExist:
    print("\n✗ Usuario danioso8329 NO existe")
    exit(1)

# Verificar organización
if hasattr(user, 'userprofile') and user.userprofile:
    org = user.userprofile.organization
    if org:
        print(f"✓ Organización: {org.name} (ID: {org.id})")
        print(f"  - Slug: {org.slug}")
        print(f"  - Activa: {org.is_active}")
    else:
        print("✗ Usuario SIN organización asignada")
        exit(1)
else:
    print("✗ Usuario SIN perfil (userprofile)")
    exit(1)

# Verificar configuración de citas
print(f"\n{'=' * 60}")
print("CONFIGURACIÓN DE CITAS")
print("=" * 60)

try:
    config = AppointmentConfiguration.objects.get(organization=org)
    print(f"✓ Configuración existe")
    print(f"  - Abierto: {config.is_open}")
    print(f"  - Máx días adelante: {config.max_days_in_advance}")
    print(f"  - Duración cita: {config.appointment_duration} min")
except AppointmentConfiguration.DoesNotExist:
    print(f"✗ NO hay configuración de citas")
    config = None

# Verificar horarios de trabajo (WorkingHours)
print(f"\n{'=' * 60}")
print("HORARIOS DE TRABAJO (WorkingHours)")
print("=" * 60)

working_hours = WorkingHours.objects.filter(organization=org, is_active=True)
if working_hours.exists():
    print(f"✓ {working_hours.count()} horarios configurados:")
    for wh in working_hours:
        print(f"  - {wh.get_weekday_display()}: {wh.start_time} - {wh.end_time}")
        print(f"    Doctor: {wh.doctor_profile or 'Todos'}")
else:
    print("✗ NO hay horarios de trabajo configurados")

# Verificar fechas específicas (SpecificDateSchedule)
print(f"\n{'=' * 60}")
print("FECHAS ESPECÍFICAS (SpecificDateSchedule)")
print("=" * 60)

from datetime import date, timedelta
today = date.today()
future_date = today + timedelta(days=60)

specific_dates = SpecificDateSchedule.objects.filter(
    organization=org,
    date__gte=today,
    date__lte=future_date,
    is_active=True
).order_by('date')

if specific_dates.exists():
    print(f"✓ {specific_dates.count()} fechas específicas disponibles:")
    for sd in specific_dates[:10]:  # Mostrar solo las primeras 10
        print(f"  - {sd.date} ({sd.date.strftime('%A')})")
        print(f"    Doctor: {sd.doctor_profile or 'No asignado'}")
        print(f"    Slots: {sd.start_time} - {sd.end_time}, Duración: {sd.slot_duration}min")
else:
    print(f"✗ NO hay fechas específicas configuradas")
    print(f"   Rango buscado: {today} a {future_date}")

# Comparar con Oceano Optico
print(f"\n{'=' * 60}")
print("COMPARACIÓN CON OCEANO OPTICO")
print("=" * 60)

try:
    oceano = Organization.objects.get(slug='oceano-optico')
    print(f"\n✓ Oceano Optico encontrada (ID: {oceano.id})")
    
    oceano_config = AppointmentConfiguration.objects.filter(organization=oceano).first()
    print(f"  - Config: {'Existe' if oceano_config else 'NO existe'}")
    if oceano_config:
        print(f"    Abierto: {oceano_config.is_open}")
    
    oceano_wh = WorkingHours.objects.filter(organization=oceano, is_active=True).count()
    print(f"  - WorkingHours: {oceano_wh}")
    
    oceano_sd = SpecificDateSchedule.objects.filter(
        organization=oceano,
        date__gte=today,
        is_active=True
    ).count()
    print(f"  - SpecificDateSchedule: {oceano_sd}")
    
except Organization.DoesNotExist:
    print("✗ Oceano Optico NO encontrada")

# Resumen
print(f"\n{'=' * 60}")
print("DIAGNÓSTICO")
print("=" * 60)

problems = []

if not config:
    problems.append("❌ Falta AppointmentConfiguration")
elif not config.is_open:
    problems.append("❌ Sistema de citas CERRADO")

if not working_hours.exists():
    problems.append("⚠️  No hay WorkingHours (opcional si usa SpecificDateSchedule)")

if not specific_dates.exists():
    problems.append("❌ NO hay SpecificDateSchedule (REQUERIDO para mostrar fechas)")

if problems:
    print("\nPROBLEMAS ENCONTRADOS:")
    for p in problems:
        print(f"  {p}")
    
    print("\n💡 SOLUCIÓN:")
    print("  El sistema necesita SpecificDateSchedule para mostrar fechas disponibles.")
    print("  Debes crear fechas específicas para que aparezcan en el calendario.")
else:
    print("\n✓ Configuración correcta")

print("\n" + "=" * 60)
