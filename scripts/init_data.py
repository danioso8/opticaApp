"""
Script para inicializar datos del sistema
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.appointments.models import AppointmentConfiguration, WorkingHours
from datetime import time

User = get_user_model()

def create_admin():
    """Crea o actualiza el usuario administrador"""
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@optica.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    admin.set_password('admin123')
    admin.save()
    print(f"✅ Usuario admin {'creado' if created else 'actualizado'}")
    print(f"   Username: admin")
    print(f"   Password: admin123")

def create_configuration():
    """Crea la configuración inicial del sistema"""
    config, created = AppointmentConfiguration.objects.get_or_create(
        pk=1,
        defaults={
            'is_open': True,
            'slot_duration': 30,
            'max_daily_appointments': 20,
            'advance_booking_days': 30
        }
    )
    print(f"✅ Configuración {'creada' if created else 'actualizada'}")

def create_working_hours():
    """Crea los horarios de trabajo predeterminados"""
    working_hours_data = [
        # Lunes a Viernes: 9:00 AM - 6:00 PM
        (0, time(9, 0), time(18, 0)),   # Lunes
        (1, time(9, 0), time(18, 0)),   # Martes
        (2, time(9, 0), time(18, 0)),   # Miércoles
        (3, time(9, 0), time(18, 0)),   # Jueves
        (4, time(9, 0), time(18, 0)),   # Viernes
        # Sábado: 9:00 AM - 2:00 PM
        (5, time(9, 0), time(14, 0)),   # Sábado
    ]
    
    created_count = 0
    for day, start, end in working_hours_data:
        wh, created = WorkingHours.objects.get_or_create(
            day_of_week=day,
            start_time=start,
            defaults={
                'end_time': end,
                'is_active': True
            }
        )
        if created:
            created_count += 1
    
    print(f"✅ Horarios de trabajo: {created_count} horarios creados")

def main():
    print("\n" + "="*50)
    print("  INICIALIZACIÓN DEL SISTEMA - ÓPTICA")
    print("="*50 + "\n")
    
    create_admin()
    create_configuration()
    create_working_hours()
    
    print("\n" + "="*50)
    print("  ✅ INICIALIZACIÓN COMPLETADA")
    print("="*50)
    print("\n👉 Accede al admin en: http://127.0.0.1:8000/admin/")
    print("   Username: admin")
    print("   Password: admin123\n")

if __name__ == '__main__':
    main()
