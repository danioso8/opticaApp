from datetime import datetime, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.patients.models_doctors import Doctor
from apps.patients.models import Patient
from apps.sales.models import Product, Category
from apps.appointments.models import Appointment

print("=" * 60)
print("CREANDO DATOS DEMO PARA OPTICAAPP")
print("=" * 60)

# 1. Usuario demo
print("\n1. Usuario demo...")
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

# 2. Organización
print("\n2. Organización...")
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
print(f"   ✅ Organización '{demo_org.name}'")

# 3. Doctores
print("\n3. Doctores...")
doctors_data = [
    {'full_name': 'Carlos Rodríguez', 'identification': '1234567890', 'specialty': 'optometrist', 'professional_card': 'OPT-12345', 'email': 'carlos.rodriguez@opticademo.com', 'phone': '3001111111'},
    {'full_name': 'Ana Martínez', 'identification': '0987654321', 'specialty': 'ophthalmologist', 'professional_card': 'OFT-67890', 'email': 'ana.martinez@opticademo.com', 'phone': '3002222222'},
    {'full_name': 'Luis García', 'identification': '1122334455', 'specialty': 'optometrist', 'professional_card': 'OPT-54321', 'email': 'luis.garcia@opticademo.com', 'phone': '3003333333'},
]
doctors = []
for doc_data in doctors_data:
    doctor, created = Doctor.objects.get_or_create(email=doc_data['email'], organization=demo_org, defaults=doc_data)
    doctors.append(doctor)
    print(f"   ✅ {doc_data['full_name']}")

# 4. Pacientes
print("\n4. Pacientes...")
patients_data = [
    {'full_name': 'María González', 'identification_type': 'CC', 'identification': '1234567890', 'email': 'maria.gonzalez@example.com', 'phone_number': '3004444444', 'date_of_birth': '1985-05-15', 'gender': 'F', 'address': 'Calle 10 #20-30'},
    {'full_name': 'Juan Pérez', 'identification_type': 'CC', 'identification': '0987654321', 'email': 'juan.perez@example.com', 'phone_number': '3005555555', 'date_of_birth': '1990-08-22', 'gender': 'M', 'address': 'Carrera 15 #25-35'},
    {'full_name': 'Sofía López', 'identification_type': 'CC', 'identification': '1122334455', 'email': 'sofia.lopez@example.com', 'phone_number': '3006666666', 'date_of_birth': '1995-12-03', 'gender': 'F', 'address': 'Avenida 30 #40-50'},
    {'full_name': 'Pedro Ramírez', 'identification_type': 'CC', 'identification': '5544332211', 'email': 'pedro.ramirez@example.com', 'phone_number': '3007777777', 'date_of_birth': '1988-03-18', 'gender': 'M', 'address': 'Calle 50 #60-70'},
    {'full_name': 'Laura Torres', 'identification_type': 'CC', 'identification': '9988776655', 'email': 'laura.torres@example.com', 'phone_number': '3008888888', 'date_of_birth': '1992-07-25', 'gender': 'F', 'address': 'Carrera 80 #90-100'},
]
patients = []
for pat_data in patients_data:
    patient, created = Patient.objects.get_or_create(identification=pat_data['identification'], organization=demo_org, defaults=pat_data)
    patients.append(patient)
    print(f"   ✅ {pat_data['full_name']}")

# 5. Categorías
print("\n5. Categorías...")
categories_data = [
    {'name': 'Monturas', 'description': 'Monturas de gafas'},
    {'name': 'Lentes', 'description': 'Lentes oftálmicos'},
    {'name': 'Gafas de Sol', 'description': 'Gafas de sol'},
    {'name': 'Lentes de Contacto', 'description': 'Lentes de contacto'},
    {'name': 'Accesorios', 'description': 'Accesorios varios'},
]
categories = []
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(name=cat_data['name'], organization=demo_org, defaults=cat_data)
    categories.append(category)
    print(f"   ✅ {cat_data['name']}")

# 6. Productos
print("\n6. Productos...")
products_data = [
    {'name': 'Montura Ray-Ban Aviador', 'category': categories[0], 'sku': 'MTR-RB-001', 'price': Decimal('350000.00'), 'cost': Decimal('200000.00'), 'stock': 15, 'description': 'Montura clásica estilo aviador'},
    {'name': 'Montura Oakley Deportiva', 'category': categories[0], 'sku': 'MTR-OK-002', 'price': Decimal('420000.00'), 'cost': Decimal('250000.00'), 'stock': 10, 'description': 'Montura deportiva'},
    {'name': 'Lente Antirreflejo Premium', 'category': categories[1], 'sku': 'LNT-AR-001', 'price': Decimal('180000.00'), 'cost': Decimal('90000.00'), 'stock': 50, 'description': 'Lente antirreflejo'},
    {'name': 'Lente Transitions', 'category': categories[1], 'sku': 'LNT-TR-002', 'price': Decimal('280000.00'), 'cost': Decimal('150000.00'), 'stock': 30, 'description': 'Lente fotocromático'},
    {'name': 'Gafas de Sol Polarizadas', 'category': categories[2], 'sku': 'SOL-POL-001', 'price': Decimal('250000.00'), 'cost': Decimal('120000.00'), 'stock': 20, 'description': 'Gafas UV400'},
    {'name': 'Lentes Contacto Mensuales', 'category': categories[3], 'sku': 'LC-MEN-001', 'price': Decimal('85000.00'), 'cost': Decimal('45000.00'), 'stock': 100, 'description': 'Pack 6 lentes'},
    {'name': 'Solución Limpiadora 360ml', 'category': categories[3], 'sku': 'SOL-LIM-001', 'price': Decimal('35000.00'), 'cost': Decimal('18000.00'), 'stock': 75, 'description': 'Solución multipropósito'},
    {'name': 'Estuche Rígido Premium', 'category': categories[4], 'sku': 'ACC-EST-001', 'price': Decimal('25000.00'), 'cost': Decimal('10000.00'), 'stock': 80, 'description': 'Estuche rígido'},
    {'name': 'Paño Microfibra', 'category': categories[4], 'sku': 'ACC-PAN-001', 'price': Decimal('8000.00'), 'cost': Decimal('3000.00'), 'stock': 200, 'description': 'Paño limpieza'},
]
for prod_data in products_data:
    product, created = Product.objects.get_or_create(sku=prod_data['sku'], organization=demo_org, defaults=prod_data)
    print(f"   ✅ {prod_data['name']}")

# 7. Citas
print("\n7. Citas...")
today = datetime.now().date()
appointments_data = [
    {'patient': patients[0], 'doctor': doctors[0], 'appointment_date': today + timedelta(days=1), 'appointment_time': '09:00:00', 'status': 'scheduled', 'notes': 'Control de rutina'},
    {'patient': patients[1], 'doctor': doctors[1], 'appointment_date': today + timedelta(days=2), 'appointment_time': '10:30:00', 'status': 'scheduled', 'notes': 'Examen visual completo'},
    {'patient': patients[2], 'doctor': doctors[0], 'appointment_date': today + timedelta(days=3), 'appointment_time': '14:00:00', 'status': 'scheduled', 'notes': 'Adaptación lentes'},
    {'patient': patients[3], 'doctor': doctors[2], 'appointment_date': today - timedelta(days=7), 'appointment_time': '11:00:00', 'status': 'completed', 'notes': 'Entrega de gafas'},
    {'patient': patients[4], 'doctor': doctors[1], 'appointment_date': today - timedelta(days=3), 'appointment_time': '15:30:00', 'status': 'completed', 'notes': 'Primera consulta'},
]
for apt_data in appointments_data:
    appointment, created = Appointment.objects.get_or_create(patient=apt_data['patient'], doctor=apt_data['doctor'], appointment_date=apt_data['appointment_date'], appointment_time=apt_data['appointment_time'], organization=demo_org, defaults={'status': apt_data['status'], 'notes': apt_data['notes']})
    print(f"   ✅ Cita {apt_data['patient'].full_name} - {apt_data['appointment_date']}")

print("\n" + "=" * 60)
print("✅ DATOS DEMO CREADOS EXITOSAMENTE")
print("=" * 60)
print(f"\n📊 RESUMEN:")
print(f"   • Usuario: demo / demo123")
print(f"   • Organización: {demo_org.name}")
print(f"   • Doctores: {len(doctors)}")
print(f"   • Pacientes: {len(patients)}")
print(f"   • Categorías: {len(categories)}")
print(f"   • Productos: {len(products_data)}")
print(f"   • Citas: {len(appointments_data)}")
print("=" * 60)
