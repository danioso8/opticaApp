"""
Script para sincronizar miembros de la organización con empleados de nómina
"""
from django.core.management.base import BaseCommand
from apps.organizations.models import OrganizationMember
from apps.payroll.models import Employee
from django.db import transaction


class Command(BaseCommand):
    help = 'Sincroniza miembros de la organización con empleados de nómina'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--organization-id',
            type=int,
            help='ID de la organización específica'
        )
    
    def handle(self, *args, **kwargs):
        org_id = kwargs.get('organization_id')
        
        if org_id:
            members = OrganizationMember.objects.filter(organization_id=org_id, is_active=True)
        else:
            members = OrganizationMember.objects.filter(is_active=True)
        
        members = members.select_related('user', 'organization').filter(
            role__in=['doctor', 'staff', 'cashier', 'vendedor']
        )
        
        creados = 0
        actualizados = 0
        
        with transaction.atomic():
            for member in members:
                user = member.user
                
                # Verificar si ya existe empleado para este usuario
                employee, created = Employee.objects.get_or_create(
                    email=user.email,
                    organization=member.organization,
                    defaults={
                        'tipo_documento': 'CC',
                        'numero_documento': user.username if user.username.isdigit() else '0000000',
                        'nombres': user.first_name or 'Sin Nombre',
                        'apellidos': user.last_name or 'Sin Apellido',
                        'telefono': '',
                        'direccion': 'No especificada',
                        'ciudad': 'No especificada',
                        'departamento': 'No especificado',
                        'tipo_contrato': 'INDEFINIDO',
                        'cargo': member.get_role_display(),
                        'salario_basico': 1300000,  # Salario mínimo Colombia 2024
                        'activo': True,
                    }
                )
                
                if created:
                    creados += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Creado empleado: {employee.nombres} {employee.apellidos} ({member.organization.name})'
                        )
                    )
                else:
                    # Actualizar cargo y estado activo
                    employee.cargo = member.get_role_display()
                    employee.activo = member.is_active
                    employee.save()
                    actualizados += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'→ Actualizado empleado: {employee.nombres} {employee.apellidos}'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Proceso completado: {creados} creados, {actualizados} actualizados'
            )
        )
