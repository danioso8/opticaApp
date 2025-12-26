"""
Comando para eliminar usuarios y todos sus datos relacionados en cascada
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction


class Command(BaseCommand):
    help = 'Elimina un usuario y todos sus datos relacionados (organizaciones, pacientes, citas, etc.)'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username del usuario a eliminar')
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar eliminación sin confirmación',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular eliminación sin borrar datos (mostrar qué se eliminaría)',
        )

    def handle(self, *args, **options):
        username = options['username']
        force = options['force']
        dry_run = options['dry_run']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Usuario "{username}" no existe'))
            return
        
        self.stdout.write(self.style.WARNING('\n' + '=' * 70))
        self.stdout.write(self.style.WARNING(f'ELIMINAR USUARIO: {user.username} ({user.get_full_name() or "Sin nombre"})'))
        self.stdout.write(self.style.WARNING('=' * 70 + '\n'))
        
        # Obtener datos relacionados
        from apps.organizations.models import Organization, OrganizationMember
        from apps.patients.models import Patient
        from apps.appointments.models import Appointment
        from apps.sales.models import Sale
        
        # Organizaciones propias
        owned_orgs = Organization.objects.filter(owner=user)
        memberships = OrganizationMember.objects.filter(user=user)
        
        # Obtener IDs de organizaciones donde es miembro
        org_ids = set()
        org_ids.update(owned_orgs.values_list('id', flat=True))
        org_ids.update(memberships.values_list('organization_id', flat=True))
        
        # Contar datos relacionados
        patients_count = Patient.objects.filter(organization_id__in=org_ids).count()
        appointments_count = Appointment.objects.filter(organization_id__in=org_ids).count()
        sales_count = Sale.objects.filter(organization_id__in=org_ids).count()
        
        # Mostrar resumen
        self.stdout.write('📊 Datos que serán eliminados:')
        self.stdout.write(f'  • Organizaciones propias: {owned_orgs.count()}')
        self.stdout.write(f'  • Membresías: {memberships.count()}')
        self.stdout.write(f'  • Pacientes: {patients_count}')
        self.stdout.write(f'  • Citas: {appointments_count}')
        self.stdout.write(f'  • Ventas: {sales_count}')
        
        if owned_orgs.exists():
            self.stdout.write('\n🏢 Organizaciones:')
            for org in owned_orgs:
                self.stdout.write(f'  • {org.name} (ID: {org.id})')
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS('\n✅ Simulación completada (--dry-run)'))
            self.stdout.write(self.style.SUCCESS('No se eliminó ningún dato real'))
            return
        
        # Confirmación
        if not force:
            self.stdout.write(self.style.WARNING('\n⚠️  ADVERTENCIA: Esta acción NO se puede deshacer'))
            confirm = input('¿Está seguro que desea eliminar este usuario y TODOS sus datos? (escriba "ELIMINAR" para confirmar): ')
            
            if confirm != 'ELIMINAR':
                self.stdout.write(self.style.ERROR('\n❌ Cancelado por el usuario'))
                return
        
        # Eliminar usuario (cascada automática)
        try:
            with transaction.atomic():
                user_email = user.email
                user.delete()
                
                self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
                self.stdout.write(self.style.SUCCESS(f'✅ Usuario "{username}" ({user_email}) eliminado correctamente'))
                self.stdout.write(self.style.SUCCESS('✅ Todos los datos relacionados fueron eliminados en cascada'))
                self.stdout.write(self.style.SUCCESS('=' * 70))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error al eliminar usuario: {str(e)}'))
            import traceback
            traceback.print_exc()
