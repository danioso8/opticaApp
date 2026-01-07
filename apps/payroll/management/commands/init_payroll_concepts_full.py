"""
Inicialización completa de conceptos de nómina según legislación colombiana 2024-2026
Incluye deducciones legales, aportes del empleador y conceptos de devengos
"""
from django.core.management.base import BaseCommand
from apps.payroll.models import AccrualConcept, DeductionConcept
from apps.organizations.models import Organization
from django.db import transaction


class Command(BaseCommand):
    help = 'Inicializa todos los conceptos de nómina según legislación colombiana'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--organization-id',
            type=int,
            help='ID de la organización específica'
        )
    
    def handle(self, *args, **kwargs):
        org_id = kwargs.get('organization_id')
        
        if org_id:
            organizations = Organization.objects.filter(id=org_id)
        else:
            organizations = Organization.objects.filter(is_active=True)
        
        for organization in organizations:
            self.stdout.write(f'\n📋 Configurando conceptos para: {organization.name}')
            self.create_accrual_concepts(organization)
            self.create_deduction_concepts(organization)
            self.stdout.write(self.style.SUCCESS(f'✓ Conceptos configurados exitosamente\n'))
    
    def create_accrual_concepts(self, organization):
        """Crea conceptos de devengos (ingresos del empleado)"""
        concepts = [
            # DEVENGOS SALARIALES
            {
                'codigo': 'SAL001',
                'nombre': 'Salario Básico',
                'descripcion': 'Salario mensual base del empleado',
                'tipo': 'SALARIO',
                'aplica_seguridad_social': True,
                'aplica_prestaciones': True,
                'activo': True
            },
            {
                'codigo': 'HED001',
                'nombre': 'Horas Extras Diurnas',
                'descripcion': 'Horas extras diurnas (25% adicional)',
                'tipo': 'HORAS_EXTRAS',
                'aplica_seguridad_social': True,
                'aplica_prestaciones': True,
                'activo': True
            },
            {
                'codigo': 'HEN001',
                'nombre': 'Horas Extras Nocturnas',
                'descripcion': 'Horas extras nocturnas (75% adicional)',
                'tipo': 'HORAS_EXTRAS',
                'aplica_seguridad_social': True,
                'aplica_prestaciones': True,
                'activo': True
            },
            {
                'codigo': 'HEDF001',
                'nombre': 'Horas Extras Diurnas Festivas',
                'descripcion': 'Horas extras diurnas en festivos (100% adicional)',
                'tipo': 'HORAS_EXTRAS',
                'aplica_seguridad_social': True,
                'aplica_prestaciones': True,
                'activo': True
            },
            {
                'codigo': 'HENF001',
                'nombre': 'Horas Extras Nocturnas Festivas',
                'descripcion': 'Horas extras nocturnas en festivos (150% adicional)',
                'tipo': 'HORAS_EXTRAS',
                'aplica_seguridad_social': True,
                'aplica_prestaciones': True,
                'activo': True
            },
            {
                'codigo': 'RN001',
                'nombre': 'Recargo Nocturno',
                'descripcion': 'Recargo por trabajo nocturno (35% adicional)',
                'tipo': 'RECARGO',
                'aplica_seguridad_social': True,
                'aplica_prestaciones': True,
                'activo': True
            },
            {
                'codigo': 'RF001',
                'nombre': 'Recargo Festivo',
                'descripcion': 'Recargo por trabajo en festivo (75% adicional)',
                'tipo': 'RECARGO',
                'aplica_seguridad_social': True,
                'aplica_prestaciones': True,
                'activo': True
            },
            
            # AUXILIOS Y SUBSIDIOS
            {
                'codigo': 'AUX001',
                'nombre': 'Auxilio de Transporte',
                'descripcion': 'Auxilio de transporte para empleados que ganen hasta 2 SMMLV',
                'tipo': 'AUXILIO',
                'aplica_seguridad_social': False,  # No se incluye en base para SS
                'aplica_prestaciones': True,  # Sí se incluye en prestaciones
                'activo': True
            },
            {
                'codigo': 'AUX002',
                'nombre': 'Auxilio de Alimentación',
                'descripcion': 'Auxilio de alimentación (hasta 50% SMMLV no constituye salario)',
                'tipo': 'AUXILIO',
                'aplica_seguridad_social': False,
                'aplica_prestaciones': False,
                'activo': True
            },
            {
                'codigo': 'AUX003',
                'nombre': 'Auxilio de Conectividad',
                'descripcion': 'Auxilio para internet y servicios (no salarial)',
                'tipo': 'AUXILIO',
                'aplica_seguridad_social': False,
                'aplica_prestaciones': False,
                'activo': True
            },
            
            # COMISIONES Y BONIFICACIONES
            {
                'codigo': 'COM001',
                'nombre': 'Comisiones por Ventas',
                'descripcion': 'Comisiones por cumplimiento de metas de ventas',
                'tipo': 'COMISION',
                'aplica_seguridad_social': True,
                'aplica_prestaciones': True,
                'activo': True
            },
            {
                'codigo': 'BON001',
                'nombre': 'Bonificación por Desempeño',
                'descripcion': 'Bonificación ocasional por desempeño excepcional',
                'tipo': 'BONIFICACION',
                'aplica_seguridad_social': False,  # Si es ocasional
                'aplica_prestaciones': False,
                'activo': True
            },
            
            # PRESTACIONES SOCIALES (LIQUIDACIÓN)
            {
                'codigo': 'PRIM001',
                'nombre': 'Prima de Servicios',
                'descripcion': 'Prima de servicios semestral (Junio y Diciembre)',
                'tipo': 'PRESTACION',
                'aplica_seguridad_social': False,
                'aplica_prestaciones': False,
                'activo': True
            },
            {
                'codigo': 'CES001',
                'nombre': 'Cesantías',
                'descripcion': 'Cesantías acumuladas (8.33% mensual)',
                'tipo': 'PRESTACION',
                'aplica_seguridad_social': False,
                'aplica_prestaciones': False,
                'activo': True
            },
            {
                'codigo': 'INTCES001',
                'nombre': 'Intereses de Cesantías',
                'descripcion': 'Intereses sobre cesantías (1% mensual = 12% anual)',
                'tipo': 'PRESTACION',
                'aplica_seguridad_social': False,
                'aplica_prestaciones': False,
                'activo': True
            },
            {
                'codigo': 'VAC001',
                'nombre': 'Vacaciones',
                'descripcion': 'Vacaciones anuales (15 días hábiles)',
                'tipo': 'VACACIONES',
                'aplica_seguridad_social': False,
                'aplica_prestaciones': False,
                'activo': True
            },
            
            # INCAPACIDADES Y LICENCIAS
            {
                'codigo': 'INCGEN001',
                'nombre': 'Incapacidad General',
                'descripcion': 'Incapacidad por enfermedad general (EPS paga desde día 3)',
                'tipo': 'INCAPACIDAD',
                'aplica_seguridad_social': False,
                'aplica_prestaciones': False,
                'activo': True
            },
            {
                'codigo': 'INCLAB001',
                'nombre': 'Incapacidad Laboral',
                'descripcion': 'Incapacidad por accidente de trabajo (ARL paga 100%)',
                'tipo': 'INCAPACIDAD',
                'aplica_seguridad_social': False,
                'aplica_prestaciones': False,
                'activo': True
            },
            {
                'codigo': 'LICMAT001',
                'nombre': 'Licencia de Maternidad',
                'descripcion': 'Licencia de maternidad (18 semanas - 126 días)',
                'tipo': 'LICENCIA',
                'aplica_seguridad_social': False,
                'aplica_prestaciones': False,
                'activo': True
            },
            {
                'codigo': 'LICPAT001',
                'nombre': 'Licencia de Paternidad',
                'descripcion': 'Licencia de paternidad (8 días hábiles)',
                'tipo': 'LICENCIA',
                'aplica_seguridad_social': False,
                'aplica_prestaciones': False,
                'activo': True
            },
        ]
        
        created_count = 0
        for concept_data in concepts:
            concept, created = AccrualConcept.objects.get_or_create(
                codigo=concept_data['codigo'],
                organization=organization,
                defaults=concept_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'  ✓ Devengos: {created_count} conceptos creados')
        )
    
    def create_deduction_concepts(self, organization):
        """Crea conceptos de deducciones (descuentos del empleado)"""
        concepts = [
            # DEDUCCIONES LEGALES (OBLIGATORIAS)
            {
                'codigo': 'SALUD001',
                'nombre': 'Salud (EPS)',
                'descripcion': 'Aporte a Salud - Empleado: 4% del salario base',
                'tipo': 'SALUD',
                'porcentaje_base': 4.0,
                'base_calculo': 'SALARIO',
                'es_obligatoria': True,
                'activo': True
            },
            {
                'codigo': 'PENSION001',
                'nombre': 'Pensión',
                'descripcion': 'Aporte a Pensión - Empleado: 4% del salario base',
                'tipo': 'PENSION',
                'porcentaje_base': 4.0,
                'base_calculo': 'SALARIO',
                'es_obligatoria': True,
                'activo': True
            },
            {
                'codigo': 'FSP001',
                'nombre': 'Fondo de Solidaridad Pensional',
                'descripcion': 'FSP: 1% para salarios > 4 SMMLV, 1.5% para > 16 SMMLV, 2% para > 20 SMMLV',
                'tipo': 'FSP',
                'porcentaje_base': 1.0,  # Variable según salario
                'base_calculo': 'SALARIO',
                'es_obligatoria': True,
                'activo': True
            },
            
            # RETENCIÓN EN LA FUENTE
            {
                'codigo': 'RETEFUE001',
                'nombre': 'Retención en la Fuente',
                'descripcion': 'Retención en la fuente por renta (tabla DIAN)',
                'tipo': 'RETENCION',
                'porcentaje_base': 0.0,  # Variable según tabla DIAN
                'base_calculo': 'SALARIO',
                'es_obligatoria': True,
                'activo': True
            },
            
            # DESCUENTOS AUTORIZADOS
            {
                'codigo': 'PRE001',
                'nombre': 'Préstamo Empresa',
                'descripcion': 'Descuento de préstamo otorgado por la empresa',
                'tipo': 'PRESTAMO',
                'porcentaje_base': 0.0,
                'base_calculo': 'VALOR_FIJO',
                'es_obligatoria': False,
                'activo': True
            },
            {
                'codigo': 'EMB001',
                'nombre': 'Embargo Judicial',
                'descripcion': 'Embargo por orden judicial (máx 50% salario)',
                'tipo': 'EMBARGO',
                'porcentaje_base': 0.0,
                'base_calculo': 'VALOR_FIJO',
                'es_obligatoria': True,
                'activo': True
            },
            {
                'codigo': 'COOP001',
                'nombre': 'Cooperativa',
                'descripcion': 'Aportes a cooperativa autorizada por el empleado',
                'tipo': 'COOPERATIVA',
                'porcentaje_base': 0.0,
                'base_calculo': 'VALOR_FIJO',
                'es_obligatoria': False,
                'activo': True
            },
            {
                'codigo': 'SIND001',
                'nombre': 'Sindicato',
                'descripcion': 'Cuota sindical (1-2% del salario)',
                'tipo': 'SINDICATO',
                'porcentaje_base': 1.0,
                'base_calculo': 'SALARIO',
                'es_obligatoria': False,
                'activo': True
            },
            {
                'codigo': 'AHORR001',
                'nombre': 'Ahorro Programado',
                'descripcion': 'Ahorro voluntario descontado de nómina',
                'tipo': 'AHORRO',
                'porcentaje_base': 0.0,
                'base_calculo': 'VALOR_FIJO',
                'es_obligatoria': False,
                'activo': True
            },
            {
                'codigo': 'LIB001',
                'nombre': 'Libranza',
                'descripcion': 'Descuento por crédito de libranza',
                'tipo': 'LIBRANZA',
                'porcentaje_base': 0.0,
                'base_calculo': 'VALOR_FIJO',
                'es_obligatoria': False,
                'activo': True
            },
            
            # OTROS DESCUENTOS
            {
                'codigo': 'DESC001',
                'nombre': 'Descuento por Ausencias',
                'descripcion': 'Descuento por inasistencias no justificadas',
                'tipo': 'OTRO',
                'porcentaje_base': 0.0,
                'base_calculo': 'VALOR_FIJO',
                'es_obligatoria': False,
                'activo': True
            },
            {
                'codigo': 'DESC002',
                'nombre': 'Fondo de Empleados',
                'descripcion': 'Aporte voluntario a fondo de empleados',
                'tipo': 'FONDO',
                'porcentaje_base': 0.0,
                'base_calculo': 'VALOR_FIJO',
                'es_obligatoria': False,
                'activo': True
            },
        ]
        
        created_count = 0
        for concept_data in concepts:
            concept, created = DeductionConcept.objects.get_or_create(
                codigo=concept_data['codigo'],
                organization=organization,
                defaults=concept_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'  ✓ Deducciones: {created_count} conceptos creados')
        )
