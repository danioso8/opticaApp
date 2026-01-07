"""
Script para depurar horarios de CompuEasys
"""
import os
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models import WorkingHours, SpecificDateSchedule, AppointmentConfiguration
from apps.appointments.utils import get_available_slots_for_date

def debug_compueasys_schedule():
    """Depurar horarios de CompuEasys"""
    print("🔍 Depurando horarios de CompuEasys...\n")
    
    # Buscar CompuEasys
    try:
        org = Organization.objects.get(slug='compueasys')
        print(f"✅ Organización encontrada: {org.name}")
        print(f"   ID: {org.id}")
        print(f"   Activa: {org.is_active}\n")
    except Organization.DoesNotExist:
        print("❌ CompuEasys no encontrada")
        return
    
    # Verificar configuración
    config = AppointmentConfiguration.get_config(org)
    if config:
        print(f"📋 Configuración de citas:")
        print(f"   Sistema abierto: {config.is_open}")
        print(f"   Duración de slot: {config.slot_duration} minutos\n")
    else:
        print("❌ No hay configuración de citas\n")
        return
    
    # Verificar horarios de trabajo (recurrentes)
    working_hours = WorkingHours.objects.filter(organization=org, is_active=True)
    print(f"⏰ Horarios de trabajo recurrentes: {working_hours.count()}")
    if working_hours.exists():
        days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        for wh in working_hours:
            print(f"   {days[wh.day_of_week]}: {wh.start_time} - {wh.end_time}")
    else:
        print("   ⚠️ No hay horarios recurrentes configurados")
    
    print()
    
    # Verificar horarios específicos
    today = date.today()
    specific_schedules = SpecificDateSchedule.objects.filter(
        organization=org,
        is_active=True,
        date__gte=today
    ).order_by('date')[:5]
    
    print(f"📅 Horarios específicos próximos: {specific_schedules.count()}")
    for schedule in specific_schedules:
        print(f"   {schedule.date}: {schedule.start_time} - {schedule.end_time}")
        if schedule.doctor_profile:
            print(f"      Doctor: {schedule.doctor_profile}")
    
    print()
    
    # Probar obtener slots para hoy
    print(f"🧪 Probando obtener slots para hoy ({today}):")
    slots = get_available_slots_for_date(today, org)
    print(f"   Total de slots: {len(slots)}")
    
    if slots:
        available = [s for s in slots if s['available']]
        print(f"   Slots disponibles: {len(available)}")
        print(f"   Primeros 5 slots:")
        for slot in slots[:5]:
            status = "✅ Disponible" if slot['available'] else "❌ Ocupado"
            print(f"      {slot['time']} - {status}")
    else:
        print("   ⚠️ No hay slots para hoy")
        print("\n💡 Posibles causas:")
        print("   1. No hay horarios configurados para hoy")
        print("   2. El sistema está cerrado")
        print("   3. Hoy es un día bloqueado")
    
    # Probar mañana
    tomorrow = today + timedelta(days=1)
    print(f"\n🧪 Probando obtener slots para mañana ({tomorrow}):")
    slots_tomorrow = get_available_slots_for_date(tomorrow, org)
    print(f"   Total de slots: {len(slots_tomorrow)}")
    
    if slots_tomorrow:
        available = [s for s in slots_tomorrow if s['available']]
        print(f"   Slots disponibles: {len(available)}")

if __name__ == '__main__':
    debug_compueasys_schedule()
