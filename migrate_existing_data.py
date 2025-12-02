"""
Script para migrar datos existentes a la organización por defecto
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import Organization, SubscriptionPlan, Subscription
from apps.patients.models import Patient
from apps.appointments.models import (
    Appointment, AppointmentConfiguration, 
    WorkingHours, SpecificDateSchedule, BlockedDate, TimeSlot
)
from apps.sales.models import Product, Category, Sale

def migrate_existing_data():
    """Migra todos los datos existentes a una organización por defecto"""
    
    print("\n1. Verificando/Creando organización por defecto...")
    
    # Obtener o crear el primer usuario
    user = User.objects.first()
    if not user:
        print("   Creando usuario admin...")
        user = User.objects.create_superuser(
            username='admin',
            email='admin@opticaapp.com',
            password='admin123'
        )
        print(f"   ✓ Usuario admin creado")
    
    # Crear organización por defecto
    org, created = Organization.objects.get_or_create(
        slug='organizacion-principal',
        defaults={
            'name': 'Organización Principal',
            'email': user.email,
            'owner': user
        }
    )
    
    if created:
        print(f"   ✓ Organización creada: {org.name}")
        
        # Crear plan gratuito
        free_plan, _ = SubscriptionPlan.objects.get_or_create(
            slug='free',
            defaults={
                'name': 'Plan Gratuito',
                'plan_type': 'free',
                'price_monthly': 0,
                'price_yearly': 0,
                'max_users': 1,
                'max_appointments_month': 50,
                'max_patients': 100,
                'max_storage_mb': 100,
            }
        )
        
        # Crear suscripción
        Subscription.objects.create(
            organization=org,
            plan=free_plan,
            billing_cycle='monthly',
            payment_status='paid'
        )
        print(f"   ✓ Suscripción creada")
    else:
        print(f"   ↻ Usando organización existente: {org.name}")
    
    # Migrar pacientes
    print("\n2. Migrando Pacientes...")
    patients_updated = Patient.objects.filter(organization__isnull=True).update(organization=org)
    print(f"   ✓ {patients_updated} pacientes migrados")
    
    # Migrar citas
    print("\n3. Migrando Citas...")
    appointments_updated = Appointment.objects.filter(organization__isnull=True).update(organization=org)
    print(f"   ✓ {appointments_updated} citas migradas")
    
    # Migrar configuración de citas
    print("\n4. Migrando Configuración de Citas...")
    config_updated = AppointmentConfiguration.objects.filter(organization__isnull=True).update(organization=org)
    print(f"   ✓ {config_updated} configuraciones migradas")
    
    # Migrar horarios
    print("\n5. Migrando Horarios...")
    hours_updated = WorkingHours.objects.filter(organization__isnull=True).update(organization=org)
    print(f"   ✓ {hours_updated} horarios migrados")
    
    # Migrar horarios específicos
    print("\n6. Migrando Horarios Específicos...")
    specific_updated = SpecificDateSchedule.objects.filter(organization__isnull=True).update(organization=org)
    print(f"   ✓ {specific_updated} horarios específicos migrados")
    
    # Migrar fechas bloqueadas
    print("\n7. Migrando Fechas Bloqueadas...")
    blocked_updated = BlockedDate.objects.filter(organization__isnull=True).update(organization=org)
    print(f"   ✓ {blocked_updated} fechas bloqueadas migradas")
    
    # Migrar time slots
    print("\n8. Migrando Time Slots...")
    slots_updated = TimeSlot.objects.filter(organization__isnull=True).update(organization=org)
    print(f"   ✓ {slots_updated} time slots migrados")
    
    # Migrar categorías
    print("\n9. Migrando Categorías...")
    categories_updated = Category.objects.filter(organization__isnull=True).update(organization=org)
    print(f"   ✓ {categories_updated} categorías migradas")
    
    # Migrar productos
    print("\n10. Migrando Productos...")
    products_updated = Product.objects.filter(organization__isnull=True).update(organization=org)
    print(f"   ✓ {products_updated} productos migrados")
    
    # Migrar ventas
    print("\n11. Migrando Ventas...")
    sales_updated = Sale.objects.filter(organization__isnull=True).update(organization=org)
    print(f"   ✓ {sales_updated} ventas migradas")
    
    print("\n" + "=" * 60)
    print("✓ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print(f"\nOrganización: {org.name}")
    print(f"Owner: {org.owner.username}")
    print(f"Plan: {org.current_subscription.plan.name if org.current_subscription else 'Sin plan'}")
    print("\nTodos los datos existentes han sido asignados a esta organización.")

if __name__ == '__main__':
    print("=" * 60)
    print("MIGRACIÓN DE DATOS EXISTENTES A SISTEMA MULTI-TENANT")
    print("=" * 60)
    
    try:
        migrate_existing_data()
    except Exception as e:
        print(f"\n❌ Error durante la migración: {str(e)}")
        import traceback
        traceback.print_exc()
