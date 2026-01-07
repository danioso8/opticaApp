"""
Comando para sincronizar empleados de dashboard con nómina
"""
from django.core.management.base import BaseCommand
from apps.dashboard.models_employee import Employee
from apps.payroll.models import Employee as PayrollEmployee
from apps.organizations.models import Organization


class Command(BaseCommand):
    help = 'Sincroniza empleados de dashboard con el módulo de nómina'

    def add_arguments(self, parser):
        parser.add_argument(
            '--organization-id',
            type=int,
            help='ID de la organización específica a sincronizar'
        )

    def handle(self, *args, **options):
        organization_id = options.get('organization_id')
        
        if organization_id:
            organizations = Organization.objects.filter(id=organization_id)
            if not organizations.exists():
                self.stdout.write(self.style.ERROR(f'❌ Organización {organization_id} no encontrada'))
                return
        else:
            organizations = Organization.objects.all()
        
        total_created = 0
        total_updated = 0
        total_errors = 0
        
        for org in organizations:
            self.stdout.write(f'\n📋 Sincronizando empleados de: {org.name}')
            
            # Obtener empleados de dashboard que están marcados para nómina
            employees = Employee.objects.filter(
                organization=org, 
                is_active=True,
                incluir_en_nomina=True  # Solo sincronizar los que están marcados
            )
            
            for emp in employees:
                try:
                    # Separar nombres
                    first_name_parts = emp.first_name.strip().split()
                    primer_nombre = first_name_parts[0] if first_name_parts else ''
                    segundo_nombre = ' '.join(first_name_parts[1:]) if len(first_name_parts) > 1 else ''
                    
                    # Separar apellidos
                    last_name_parts = emp.last_name.strip().split()
                    primer_apellido = last_name_parts[0] if last_name_parts else ''
                    segundo_apellido = ' '.join(last_name_parts[1:]) if len(last_name_parts) > 1 else ''
                    
                    # Crear o actualizar en nómina
                    payroll_emp, created = PayrollEmployee.objects.update_or_create(
                        organization=org,
                        numero_documento=emp.identification,
                        defaults={
                            'tipo_documento': emp.document_type,
                            'primer_nombre': primer_nombre,
                            'segundo_nombre': segundo_nombre,
                            'primer_apellido': primer_apellido,
                            'segundo_apellido': segundo_apellido,
                            'email': emp.email or '',
                            'telefono': emp.phone or '',
                            'direccion': emp.address or '',
                            'ciudad': 'Bogotá',  # Valor por defecto
                            'departamento': 'Cundinamarca',  # Valor por defecto
                            'cargo': emp.position,
                            'fecha_ingreso': emp.hire_date,
                            'salario_basico': emp.salary if emp.salary else 1300000,
                            'activo': emp.is_active,
                        }
                    )
                    
                    if created:
                        total_created += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Creado: {emp.full_name} ({emp.identification})'
                            )
                        )
                    else:
                        total_updated += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ↻ Actualizado: {emp.full_name} ({emp.identification})'
                            )
                        )
                
                except Exception as e:
                    total_errors += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ✗ Error con {emp.full_name}: {str(e)}'
                        )
                    )
        
        # Resumen
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'✓ Proceso completado:'))
        self.stdout.write(f'  • Creados: {total_created}')
        self.stdout.write(f'  • Actualizados: {total_updated}')
        if total_errors > 0:
            self.stdout.write(self.style.ERROR(f'  • Errores: {total_errors}'))
        self.stdout.write('='*50)
