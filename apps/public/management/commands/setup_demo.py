"""
Management command para crear cuenta demo con datos de prueba
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization, OrganizationMember
from apps.patients.models import Patient
from apps.appointments.models import Appointment
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea o actualiza la cuenta demo con datos de prueba'

    def handle(self, *args, **options):
        self.stdout.write('Creando cuenta demo...')
        
        # Crear usuario demo
        demo_user, created = User.objects.get_or_create(
            email='demo@optikaapp.com',
            defaults={
                'username': 'demo',
                'first_name': 'Usuario',
                'last_name': 'Demo',
                'is_active': True,
            }
        )
        
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            self.stdout.write(self.style.SUCCESS(f'Usuario demo creado: {demo_user.email}'))
        else:
            self.stdout.write(f'Usuario demo ya existe: {demo_user.email}')
        
        # Crear organización demo
        demo_org, created = Organization.objects.get_or_create(
            slug='demo-optica',
            defaults={
                'name': 'Óptica Demo - OptikaApp',
                'nit': '900000000-0',
                'email': 'contacto@opticademo.com',
                'phone': '+57 300 123 4567',
                'address': 'Calle Demo 123, Bogotá',
                'city': 'Bogotá',
                'country': 'Colombia',
                'is_active': True,
                'subscription_status': 'trial',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Organización demo creada: {demo_org.name}'))
        
        # Asignar usuario a organización
        membership, created = OrganizationMember.objects.get_or_create(
            organization=demo_org,
            user=demo_user,
            defaults={
                'role': 'owner',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Usuario asignado a organización demo'))
        
        # Crear pacientes de ejemplo
        patients_data = [
            {'first_name': 'Juan', 'last_name': 'Pérez', 'email': 'juan.perez@example.com', 'phone': '3001234567'},
            {'first_name': 'María', 'last_name': 'García', 'email': 'maria.garcia@example.com', 'phone': '3007654321'},
            {'first_name': 'Carlos', 'last_name': 'Rodríguez', 'email': 'carlos.rodriguez@example.com', 'phone': '3009876543'},
        ]
        
        for patient_data in patients_data:
            patient, created = Patient.objects.get_or_create(
                email=patient_data['email'],
                organization=demo_org,
                defaults={
                    **patient_data,
                    'identification_type': 'CC',
                    'identification_number': f'10000{patients_data.index(patient_data)}',
                }
            )
            if created:
                self.stdout.write(f'Paciente creado: {patient.get_full_name()}')
        
        # Crear citas de ejemplo
        today = timezone.now()
        for i in range(5):
            appointment_date = today + timedelta(days=i+1, hours=10)
            Appointment.objects.get_or_create(
                organization=demo_org,
                patient=Patient.objects.filter(organization=demo_org).first(),
                appointment_date=appointment_date,
                defaults={
                    'status': 'scheduled',
                    'reason': 'Consulta de control visual',
                    'duration': 30,
                }
            )
        
        self.stdout.write(self.style.SUCCESS('\n✓ Cuenta demo configurada exitosamente'))
        self.stdout.write(self.style.SUCCESS('  Usuario: demo@optikaapp.com'))
        self.stdout.write(self.style.SUCCESS('  Contraseña: demo123'))
        self.stdout.write(self.style.SUCCESS('  Organización: Óptica Demo - OptikaApp'))
