"""
Script de verificación del sistema multi-tenant
Ejecutar después de aplicar migraciones y migrar datos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import Organization, OrganizationMember, SubscriptionPlan, Subscription
from apps.patients.models import Patient
from apps.appointments.models import Appointment, AppointmentConfiguration
from apps.sales.models import Product, Category, Sale

def verify_system():
    """Verifica que el sistema SaaS esté funcionando correctamente"""
    
    print("\n" + "="*60)
    print("VERIFICACIÓN DEL SISTEMA MULTI-TENANT SAAS")
    print("="*60)
    
    # 1. Verificar organizaciones
    print("\n1. ORGANIZACIONES")
    print("-" * 60)
    orgs = Organization.objects.all()
    print(f"   Total de organizaciones: {orgs.count()}")
    for org in orgs:
        print(f"   - {org.name} (ID: {org.id})")
        print(f"     Owner: {org.owner.username}")
        print(f"     Slug: {org.slug}")
        sub = org.current_subscription
        if sub:
            print(f"     Plan: {sub.plan.name} ({sub.get_billing_cycle_display()})")
            print(f"     Estado: {'Activa' if sub.is_active else 'Inactiva'}")
            print(f"     Días restantes: {sub.days_remaining}")
        else:
            print(f"     ⚠️  Sin suscripción activa")
    
    # 2. Verificar planes
    print("\n2. PLANES DE SUSCRIPCIÓN")
    print("-" * 60)
    plans = SubscriptionPlan.objects.all()
    print(f"   Total de planes: {plans.count()}")
    for plan in plans:
        print(f"   - {plan.name}: ${plan.price_monthly}/mes")
        print(f"     Usuarios: {plan.max_users}, Citas: {plan.max_appointments_month}, Pacientes: {plan.max_patients}")
    
    # 3. Verificar usuarios y membresías
    print("\n3. USUARIOS Y MEMBRESÍAS")
    print("-" * 60)
    users = User.objects.all()
    print(f"   Total de usuarios: {users.count()}")
    for user in users[:5]:  # Primeros 5
        memberships = OrganizationMember.objects.filter(user=user, is_active=True)
        print(f"   - {user.username} ({user.email})")
        for mem in memberships:
            print(f"     → {mem.organization.name} ({mem.get_role_display()})")
    
    # 4. Verificar datos por organización
    print("\n4. DATOS POR ORGANIZACIÓN")
    print("-" * 60)
    for org in orgs:
        print(f"\n   Organización: {org.name}")
        
        patients = Patient.objects.filter(organization=org).count()
        appointments = Appointment.objects.filter(organization=org).count()
        products = Product.objects.filter(organization=org).count()
        sales = Sale.objects.filter(organization=org).count()
        
        print(f"     - Pacientes: {patients}")
        print(f"     - Citas: {appointments}")
        print(f"     - Productos: {products}")
        print(f"     - Ventas: {sales}")
        
        # Verificar configuración
        try:
            config = AppointmentConfiguration.objects.get(organization=org)
            print(f"     - Sistema de citas: {'Abierto' if config.is_open else 'Cerrado'}")
        except AppointmentConfiguration.DoesNotExist:
            print(f"     - ⚠️  Sin configuración de citas")
    
    # 5. Verificar aislamiento de datos
    print("\n5. VERIFICACIÓN DE AISLAMIENTO")
    print("-" * 60)
    if orgs.count() >= 2:
        org1 = orgs[0]
        org2 = orgs[1]
        
        patients_org1 = Patient.objects.filter(organization=org1).count()
        patients_org2 = Patient.objects.filter(organization=org2).count()
        
        print(f"   {org1.name}: {patients_org1} pacientes")
        print(f"   {org2.name}: {patients_org2} pacientes")
        print(f"   ✓ Datos correctamente aislados por organización")
    else:
        print(f"   ⚠️  Se necesitan al menos 2 organizaciones para verificar aislamiento")
    
    # 6. Verificar datos sin organización (no deberían existir)
    print("\n6. VERIFICACIÓN DE INTEGRIDAD")
    print("-" * 60)
    patients_no_org = Patient.objects.filter(organization__isnull=True).count()
    appointments_no_org = Appointment.objects.filter(organization__isnull=True).count()
    products_no_org = Product.objects.filter(organization__isnull=True).count()
    sales_no_org = Sale.objects.filter(organization__isnull=True).count()
    
    if patients_no_org == 0 and appointments_no_org == 0 and products_no_org == 0 and sales_no_org == 0:
        print(f"   ✓ Todos los datos tienen organización asignada")
    else:
        print(f"   ⚠️  Datos sin organización encontrados:")
        if patients_no_org > 0:
            print(f"      - {patients_no_org} pacientes sin organización")
        if appointments_no_org > 0:
            print(f"      - {appointments_no_org} citas sin organización")
        if products_no_org > 0:
            print(f"      - {products_no_org} productos sin organización")
        if sales_no_org > 0:
            print(f"      - {sales_no_org} ventas sin organización")
    
    # 7. Resumen
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    print(f"✓ Organizaciones activas: {orgs.filter(is_active=True).count()}")
    print(f"✓ Planes disponibles: {plans.filter(is_active=True).count()}")
    print(f"✓ Usuarios totales: {users.count()}")
    print(f"✓ Pacientes totales: {Patient.objects.count()}")
    print(f"✓ Citas totales: {Appointment.objects.count()}")
    print(f"✓ Productos totales: {Product.objects.count()}")
    print(f"✓ Ventas totales: {Sale.objects.count()}")
    
    print("\n" + "="*60)
    print("VERIFICACIÓN COMPLETADA")
    print("="*60)
    print("\nAccede a:")
    print("  - Dashboard: http://localhost:8000/dashboard/")
    print("  - Organizaciones: http://localhost:8000/organizations/")
    print("  - Admin: http://localhost:8000/admin/")

if __name__ == '__main__':
    try:
        verify_system()
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {str(e)}")
        import traceback
        traceback.print_exc()
