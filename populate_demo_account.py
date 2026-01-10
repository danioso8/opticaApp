import os
import django
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opticaapp.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.patients.models_doctors import Doctor
from apps.patients.models import Patient
from apps.sales.models import Product, Category
from apps.appointments.models import Appointment

def create_demo_data():
    print("=" * 60)
    print("CREANDO DATOS DEMO PARA OPTICAAPP")
    print("=" * 60)
    
    # 1. Crear o obtener usuario demo
    print("\n1. Creando/Obteniendo usuario demo...")
    demo_user, created = User.objects.get_or_create(
        username='demo',
        defaults={
            'email': 'demo@optikaapp.com',
            'first_name': 'Usuario',
            'last_name': 'Demo',
            'is_active': True,
        }
    )
    if created:
        demo_user.set_password('demo123')
        demo_user.save()
        print("   ✅ Usuario 'demo' creado")
    else:
        print("   ℹ️  Usuario 'demo' ya existe")
    
    # 2. Crear o obtener organización demo
    print("\n2. Creando/Obteniendo organización...")
    demo_org, created = Organization.objects.get_or_create(
        slug='optica-demo',
        defaults={
            'name': 'Óptica Demo',
            'legal_name': 'Óptica Demo S.A.S.',
            'tax_id_type': 'NIT',
            'tax_id': '900123456-7',
            'owner': demo_user,
            'address': 'Calle 123 #45-67',
            'city': 'Bogotá',
            'country': 'Colombia',
            'phone': '3001234567',
            'email': 'contacto@opticademo.com',
        }
    )
    if created:
        print(f"   ✅ Organización '{demo_org.name}' creada")
    else:
        print(f"   ℹ️  Organización '{demo_org.name}' ya existe")
    
    # 3. Crear doctores de ejemplo
    print("\n3. Creando doctores...")
    doctors_data = [
        {
            'first_name': 'Carlos',
            'last_name': 'Rodríguez',
            'specialty': 'Optometría',
            'license_number': 'OPT-12345',
            'email': 'carlos.rodriguez@opticademo.com',
            'phone': '3001111111',
        },
        {
            'first_name': 'Ana',
            'last_name': 'Martínez',
            'specialty': 'Oftalmología',
            'license_number': 'OFT-67890',
            'email': 'ana.martinez@opticademo.com',
            'phone': '3002222222',
        },
        {
            'first_name': 'Luis',
            'last_name': 'García',
            'specialty': 'Optometría',
            'license_number': 'OPT-54321',
            'email': 'luis.garcia@opticademo.com',
            'phone': '3003333333',
        },
    ]
    
    doctors = []
    for doc_data in doctors_data:
        doctor, created = Doctor.objects.get_or_create(
            email=doc_data['email'],
            organization=demo_org,
            defaults=doc_data
        )
        doctors.append(doctor)
        if created:
            print(f"   ✅ Doctor {doc_data['first_name']} {doc_data['last_name']} creado")
        else:
            print(f"   ℹ️  Doctor {doc_data['first_name']} {doc_data['last_name']} ya existe")
    
    # 4. Crear pacientes de ejemplo
    print("\n4. Creando pacientes...")
    patients_data = [
        {
            'first_name': 'María',
            'last_name': 'González',
            'document_type': 'CC',
            'document_number': '1234567890',
            'email': 'maria.gonzalez@example.com',
            'phone': '3004444444',
            'birth_date': '1985-05-15',
            'gender': 'F',
            'address': 'Calle 10 #20-30',
            'city': 'Bogotá',
        },
        {
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'document_type': 'CC',
            'document_number': '0987654321',
            'email': 'juan.perez@example.com',
            'phone': '3005555555',
            'birth_date': '1990-08-22',
            'gender': 'M',
            'address': 'Carrera 15 #25-35',
            'city': 'Medellín',
        },
        {
            'first_name': 'Sofía',
            'last_name': 'López',
            'document_type': 'CC',
            'document_number': '1122334455',
            'email': 'sofia.lopez@example.com',
            'phone': '3006666666',
            'birth_date': '1995-12-03',
            'gender': 'F',
            'address': 'Avenida 30 #40-50',
            'city': 'Cali',
        },
        {
            'first_name': 'Pedro',
            'last_name': 'Ramírez',
            'document_type': 'CC',
            'document_number': '5544332211',
            'email': 'pedro.ramirez@example.com',
            'phone': '3007777777',
            'birth_date': '1988-03-18',
            'gender': 'M',
            'address': 'Calle 50 #60-70',
            'city': 'Barranquilla',
        },
        {
            'first_name': 'Laura',
            'last_name': 'Torres',
            'document_type': 'CC',
            'document_number': '9988776655',
            'email': 'laura.torres@example.com',
            'phone': '3008888888',
            'birth_date': '1992-07-25',
            'gender': 'F',
            'address': 'Carrera 80 #90-100',
            'city': 'Cartagena',
        },
    ]
    
    patients = []
    for pat_data in patients_data:
        patient, created = Patient.objects.get_or_create(
            document_number=pat_data['document_number'],
            organization=demo_org,
            defaults=pat_data
        )
        patients.append(patient)
        if created:
            print(f"   ✅ Paciente {pat_data['first_name']} {pat_data['last_name']} creado")
        else:
            print(f"   ℹ️  Paciente {pat_data['first_name']} {pat_data['last_name']} ya existe")
    
    # 5. Crear categorías de productos
    print("\n5. Creando categorías de productos...")
    categories_data = [
        {'name': 'Monturas', 'description': 'Monturas de gafas'},
        {'name': 'Lentes', 'description': 'Lentes oftálmicos'},
        {'name': 'Gafas de Sol', 'description': 'Gafas de sol y accesorios'},
        {'name': 'Lentes de Contacto', 'description': 'Lentes de contacto y soluciones'},
        {'name': 'Accesorios', 'description': 'Estuches, paños, cordones'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            organization=demo_org,
            defaults=cat_data
        )
        categories.append(category)
        if created:
            print(f"   ✅ Categoría '{cat_data['name']}' creada")
        else:
            print(f"   ℹ️  Categoría '{cat_data['name']}' ya existe")
    
    # 6. Crear productos de ejemplo
    print("\n6. Creando productos...")
    products_data = [
        {
            'name': 'Montura Ray-Ban Aviador',
            'category': categories[0],
            'sku': 'MTR-RB-001',
            'price': Decimal('350000.00'),
            'cost': Decimal('200000.00'),
            'stock': 15,
            'description': 'Montura clásica estilo aviador',
        },
        {
            'name': 'Montura Oakley Deportiva',
            'category': categories[0],
            'sku': 'MTR-OK-002',
            'price': Decimal('420000.00'),
            'cost': Decimal('250000.00'),
            'stock': 10,
            'description': 'Montura deportiva de alto rendimiento',
        },
        {
            'name': 'Lente Antirreflejo Premium',
            'category': categories[1],
            'sku': 'LNT-AR-001',
            'price': Decimal('180000.00'),
            'cost': Decimal('90000.00'),
            'stock': 50,
            'description': 'Lente con tratamiento antirreflejo',
        },
        {
            'name': 'Lente Transitions',
            'category': categories[1],
            'sku': 'LNT-TR-002',
            'price': Decimal('280000.00'),
            'cost': Decimal('150000.00'),
            'stock': 30,
            'description': 'Lente fotocromático',
        },
        {
            'name': 'Gafas de Sol Polarizadas',
            'category': categories[2],
            'sku': 'SOL-POL-001',
            'price': Decimal('250000.00'),
            'cost': Decimal('120000.00'),
            'stock': 20,
            'description': 'Gafas con protección UV400',
        },
        {
            'name': 'Lentes de Contacto Mensuales',
            'category': categories[3],
            'sku': 'LC-MEN-001',
            'price': Decimal('85000.00'),
            'cost': Decimal('45000.00'),
            'stock': 100,
            'description': 'Pack de 6 lentes mensuales',
        },
        {
            'name': 'Solución Limpiadora 360ml',
            'category': categories[3],
            'sku': 'SOL-LIM-001',
            'price': Decimal('35000.00'),
            'cost': Decimal('18000.00'),
            'stock': 75,
            'description': 'Solución multipropósito para lentes de contacto',
        },
        {
            'name': 'Estuche Rígido Premium',
            'category': categories[4],
            'sku': 'ACC-EST-001',
            'price': Decimal('25000.00'),
            'cost': Decimal('10000.00'),
            'stock': 80,
            'description': 'Estuche rígido para gafas',
        },
        {
            'name': 'Paño Microfibra',
            'category': categories[4],
            'sku': 'ACC-PAN-001',
            'price': Decimal('8000.00'),
            'cost': Decimal('3000.00'),
            'stock': 200,
            'description': 'Paño de microfibra para limpieza',
        },
    ]
    
    products = []
    for prod_data in products_data:
        product, created = Product.objects.get_or_create(
            sku=prod_data['sku'],
            organization=demo_org,
            defaults=prod_data
        )
        products.append(product)
        if created:
            print(f"   ✅ Producto '{prod_data['name']}' creado")
        else:
            print(f"   ℹ️  Producto '{prod_data['name']}' ya existe")
    
    # 7. Crear citas de ejemplo
    print("\n7. Creando citas...")
    today = datetime.now().date()
    appointments_data = [
        {
            'patient': patients[0],
            'doctor': doctors[0],
            'date': today + timedelta(days=1),
            'time': '09:00:00',
            'duration': 30,
            'status': 'scheduled',
            'reason': 'Control de rutina',
        },
        {
            'patient': patients[1],
            'doctor': doctors[1],
            'date': today + timedelta(days=2),
            'time': '10:30:00',
            'duration': 45,
            'status': 'scheduled',
            'reason': 'Examen visual completo',
        },
        {
            'patient': patients[2],
            'doctor': doctors[0],
            'date': today + timedelta(days=3),
            'time': '14:00:00',
            'duration': 30,
            'status': 'scheduled',
            'reason': 'Adaptación de lentes de contacto',
        },
        {
            'patient': patients[3],
            'doctor': doctors[2],
            'date': today - timedelta(days=7),
            'time': '11:00:00',
            'duration': 30,
            'status': 'completed',
            'reason': 'Entrega de gafas',
        },
        {
            'patient': patients[4],
            'doctor': doctors[1],
            'date': today - timedelta(days=3),
            'time': '15:30:00',
            'duration': 60,
            'status': 'completed',
            'reason': 'Primera consulta',
        },
    ]
    
    for apt_data in appointments_data:
        appointment, created = Appointment.objects.get_or_create(
            patient=apt_data['patient'],
            doctor=apt_data['doctor'],
            date=apt_data['date'],
            time=apt_data['time'],
            organization=demo_org,
            defaults={
                'duration': apt_data['duration'],
                'status': apt_data['status'],
                'reason': apt_data['reason'],
            }
        )
        if created:
            print(f"   ✅ Cita para {apt_data['patient'].first_name} {apt_data['patient'].last_name} creada")
        else:
            print(f"   ℹ️  Cita para {apt_data['patient'].first_name} {apt_data['patient'].last_name} ya existe")
    
    print("\n" + "=" * 60)
    print("✅ DATOS DEMO CREADOS EXITOSAMENTE")
    print("=" * 60)
    print(f"\n📊 RESUMEN:")
    print(f"   • Usuario: demo / demo123")
    print(f"   • Organización: {demo_org.name}")
    print(f"   • Doctores: {len(doctors)}")
    print(f"   • Pacientes: {len(patients)}")
    print(f"   • Categorías: {len(categories)}")
    print(f"   • Productos: {len(products)}")
    print(f"   • Citas: {len(appointments_data)}")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    try:
        create_demo_data()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
