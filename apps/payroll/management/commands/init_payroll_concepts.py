"""
Comando para crear los conceptos básicos de nómina
"""
from django.core.management.base import BaseCommand
from apps.payroll.models import AccrualConcept, DeductionConcept
from apps.organizations.models import Organization


class Command(BaseCommand):
    help = 'Crea los conceptos básicos de devengados y deducciones para todas las organizaciones'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--org-id',
            type=int,
            help='ID de organización específica (opcional)'
        )
    
    def handle(self, *args, **options):
        org_id = options.get('org_id')
        
        if org_id:
            organizations = Organization.objects.filter(id=org_id)
        else:
            organizations = Organization.objects.all()
        
        for org in organizations:
            self.stdout.write(f"\nCreando conceptos para: {org.name}")
            
            # Conceptos de Devengados
            accruals = [
                {
                    'codigo': 'SAL-BASICO',
                    'nombre': 'Salario Básico',
                    'tipo': 'BASICO',
                    'aplica_seguridad_social': True,
                    'descripcion': 'Salario básico mensual del empleado'
                },
                {
                    'codigo': 'AUX-TRANSPORTE',
                    'nombre': 'Auxilio de Transporte',
                    'tipo': 'AUXILIO_TRANSPORTE',
                    'aplica_seguridad_social': False,
                    'descripcion': 'Auxilio de transporte legal'
                },
                {
                    'codigo': 'HE-DIURNAS',
                    'nombre': 'Horas Extras Diurnas',
                    'tipo': 'HORAS_EXTRAS',
                    'aplica_seguridad_social': True,
                    'descripcion': 'Horas extras diurnas (25%)'
                },
                {
                    'codigo': 'HE-NOCTURNAS',
                    'nombre': 'Horas Extras Nocturnas',
                    'tipo': 'HORAS_EXTRAS',
                    'aplica_seguridad_social': True,
                    'descripcion': 'Horas extras nocturnas (75%)'
                },
                {
                    'codigo': 'REC-NOCTURNO',
                    'nombre': 'Recargo Nocturno',
                    'tipo': 'RECARGO_NOCTURNO',
                    'aplica_seguridad_social': True,
                    'descripcion': 'Recargo por trabajo nocturno (35%)'
                },
                {
                    'codigo': 'REC-DOMINICAL',
                    'nombre': 'Recargo Dominical/Festivo',
                    'tipo': 'RECARGO_DOMINICAL',
                    'aplica_seguridad_social': True,
                    'descripcion': 'Recargo por trabajo dominical o festivo (75%)'
                },
                {
                    'codigo': 'COMISION',
                    'nombre': 'Comisiones',
                    'tipo': 'COMISION',
                    'aplica_seguridad_social': True,
                    'descripcion': 'Comisiones por ventas'
                },
                {
                    'codigo': 'BONIFICACION',
                    'nombre': 'Bonificación',
                    'tipo': 'BONIFICACION',
                    'aplica_seguridad_social': True,
                    'descripcion': 'Bonificaciones adicionales'
                },
            ]
            
            for accrual_data in accruals:
                accrual, created = AccrualConcept.objects.get_or_create(
                    organization=org,
                    codigo=accrual_data['codigo'],
                    defaults=accrual_data
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Devengado creado: {accrual.nombre}"))
                else:
                    self.stdout.write(f"  - Devengado ya existe: {accrual.nombre}")
            
            # Conceptos de Deducciones
            deductions = [
                {
                    'codigo': 'DED-SALUD',
                    'nombre': 'Salud (4%)',
                    'tipo': 'SALUD',
                    'porcentaje_base': 4.0,
                    'descripcion': 'Aporte a salud del empleado (4%)'
                },
                {
                    'codigo': 'DED-PENSION',
                    'nombre': 'Pensión (4%)',
                    'tipo': 'PENSION',
                    'porcentaje_base': 4.0,
                    'descripcion': 'Aporte a pensión del empleado (4%)'
                },
                {
                    'codigo': 'DED-FSP',
                    'nombre': 'Fondo Solidaridad Pensional',
                    'tipo': 'FONDO_SOLIDARIDAD',
                    'porcentaje_base': 1.0,
                    'descripcion': 'Fondo de Solidaridad Pensional (1% si aplica)'
                },
                {
                    'codigo': 'DED-RETEFUENTE',
                    'nombre': 'Retención en la Fuente',
                    'tipo': 'RETENCION_FUENTE',
                    'porcentaje_base': None,
                    'descripcion': 'Retención en la fuente según tabla de retención'
                },
                {
                    'codigo': 'DED-LIBRANZA',
                    'nombre': 'Libranza',
                    'tipo': 'LIBRANZA',
                    'porcentaje_base': None,
                    'descripcion': 'Descuento por libranza'
                },
                {
                    'codigo': 'DED-PRESTAMO',
                    'nombre': 'Préstamo Empresa',
                    'tipo': 'PRESTAMO',
                    'porcentaje_base': None,
                    'descripcion': 'Descuento por préstamo de la empresa'
                },
                {
                    'codigo': 'DED-EMBARGO',
                    'nombre': 'Embargo Judicial',
                    'tipo': 'EMBARGO',
                    'porcentaje_base': None,
                    'descripcion': 'Descuento por embargo judicial'
                },
            ]
            
            for deduction_data in deductions:
                deduction, created = DeductionConcept.objects.get_or_create(
                    organization=org,
                    codigo=deduction_data['codigo'],
                    defaults=deduction_data
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Deducción creada: {deduction.nombre}"))
                else:
                    self.stdout.write(f"  - Deducción ya existe: {deduction.nombre}")
        
        self.stdout.write(self.style.SUCCESS('\n✅ Conceptos de nómina creados exitosamente'))
