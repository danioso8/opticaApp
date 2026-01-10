"""
Script para agregar conceptos de nómina según DIAN a la base de datos
Ejecutar: python manage.py shell < add_payroll_concepts_dian.py
"""

from apps.payroll.models import AccrualConcept, DeductionConcept
from apps.organizations.models import Organization

# Obtener organización por defecto
org = Organization.objects.first()

print("=" * 80)
print("AGREGANDO CONCEPTOS DE NÓMINA SEGÚN DIAN")
print("=" * 80)

# ============================================================================
# CONCEPTOS DE DEVENGADOS (INGRESOS)
# ============================================================================

accruals = [
    # SALARIO
    {
        'codigo': 'DEV001',
        'nombre': 'Salario Básico',
        'tipo': 'SALARIO',
        'descripcion': 'Salario mensual base del trabajador',
        'aplica_seguridad_social': True,
        'aplica_prestaciones': True,
    },
    
    # HORAS EXTRAS
    {
        'codigo': 'DEV002',
        'nombre': 'Horas Extras Diurnas',
        'tipo': 'HORAS_EXTRAS',
        'descripcion': 'Horas extras trabajadas en jornada diurna (25%)',
        'aplica_seguridad_social': True,
        'aplica_prestaciones': True,
    },
    {
        'codigo': 'DEV003',
        'nombre': 'Horas Extras Nocturnas',
        'tipo': 'HORAS_EXTRAS',
        'descripcion': 'Horas extras trabajadas en jornada nocturna (75%)',
        'aplica_seguridad_social': True,
        'aplica_prestaciones': True,
    },
    {
        'codigo': 'DEV004',
        'nombre': 'Horas Extras Dominicales y Festivas Diurnas',
        'tipo': 'HORAS_EXTRAS',
        'descripcion': 'Horas extras en dominicales/festivos diurnos (100%)',
        'aplica_seguridad_social': True,
        'aplica_prestaciones': True,
    },
    {
        'codigo': 'DEV005',
        'nombre': 'Horas Extras Dominicales y Festivas Nocturnas',
        'tipo': 'HORAS_EXTRAS',
        'descripcion': 'Horas extras en dominicales/festivos nocturnos (150%)',
        'aplica_seguridad_social': True,
        'aplica_prestaciones': True,
    },
    
    # RECARGOS
    {
        'codigo': 'DEV006',
        'nombre': 'Recargo Nocturno',
        'tipo': 'RECARGO',
        'descripcion': 'Recargo por trabajo nocturno (35%)',
        'aplica_seguridad_social': True,
        'aplica_prestaciones': True,
    },
    {
        'codigo': 'DEV007',
        'nombre': 'Recargo Dominical y Festivo',
        'tipo': 'RECARGO',
        'descripcion': 'Recargo por trabajo dominical o festivo (75%)',
        'aplica_seguridad_social': True,
        'aplica_prestaciones': True,
    },
    
    # AUXILIOS
    {
        'codigo': 'DEV008',
        'nombre': 'Auxilio de Transporte',
        'tipo': 'AUXILIO',
        'descripcion': 'Auxilio de transporte legal',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': True,
    },
    {
        'codigo': 'DEV009',
        'nombre': 'Auxilio de Alimentación',
        'tipo': 'AUXILIO',
        'descripcion': 'Auxilio de alimentación no salarial',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    {
        'codigo': 'DEV010',
        'nombre': 'Auxilio de Vivienda',
        'tipo': 'AUXILIO',
        'descripcion': 'Auxilio de vivienda',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    {
        'codigo': 'DEV011',
        'nombre': 'Auxilio de Educación',
        'tipo': 'AUXILIO',
        'descripcion': 'Auxilio para educación del trabajador o hijos',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    
    # COMISIONES
    {
        'codigo': 'DEV012',
        'nombre': 'Comisiones',
        'tipo': 'COMISION',
        'descripcion': 'Comisiones por ventas o gestión',
        'aplica_seguridad_social': True,
        'aplica_prestaciones': True,
    },
    
    # BONIFICACIONES
    {
        'codigo': 'DEV013',
        'nombre': 'Bonificación por Desempeño',
        'tipo': 'BONIFICACION',
        'descripcion': 'Bonificación por cumplimiento de metas',
        'aplica_seguridad_social': True,
        'aplica_prestaciones': True,
    },
    {
        'codigo': 'DEV014',
        'nombre': 'Bonificación Habitual',
        'tipo': 'BONIFICACION',
        'descripcion': 'Bonificaciones de carácter habitual',
        'aplica_seguridad_social': True,
        'aplica_prestaciones': True,
    },
    {
        'codigo': 'DEV015',
        'nombre': 'Bonificación Ocasional',
        'tipo': 'BONIFICACION',
        'descripcion': 'Bonificaciones ocasionales no constitutivas de salario',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    
    # PRESTACIONES SOCIALES
    {
        'codigo': 'DEV016',
        'nombre': 'Prima de Servicios',
        'tipo': 'PRESTACION',
        'descripcion': 'Prima de servicios semestral',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    {
        'codigo': 'DEV017',
        'nombre': 'Cesantías',
        'tipo': 'PRESTACION',
        'descripcion': 'Cesantías anuales',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    {
        'codigo': 'DEV018',
        'nombre': 'Intereses sobre Cesantías',
        'tipo': 'PRESTACION',
        'descripcion': 'Intereses sobre cesantías (12% anual)',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    {
        'codigo': 'DEV019',
        'nombre': 'Dotación',
        'tipo': 'PRESTACION',
        'descripcion': 'Dotación de uniformes y calzado',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    
    # VACACIONES
    {
        'codigo': 'DEV020',
        'nombre': 'Vacaciones',
        'tipo': 'VACACIONES',
        'descripcion': 'Pago de vacaciones disfrutadas',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    {
        'codigo': 'DEV021',
        'nombre': 'Compensación en Dinero de Vacaciones',
        'tipo': 'VACACIONES',
        'descripcion': 'Vacaciones compensadas en dinero',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    
    # INCAPACIDADES
    {
        'codigo': 'DEV022',
        'nombre': 'Incapacidad por Enfermedad General',
        'tipo': 'INCAPACIDAD',
        'descripcion': 'Incapacidad médica por enfermedad general',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    {
        'codigo': 'DEV023',
        'nombre': 'Incapacidad por Accidente de Trabajo',
        'tipo': 'INCAPACIDAD',
        'descripcion': 'Incapacidad por accidente laboral',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    {
        'codigo': 'DEV024',
        'nombre': 'Licencia de Maternidad',
        'tipo': 'LICENCIA',
        'descripcion': 'Licencia remunerada de maternidad',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    {
        'codigo': 'DEV025',
        'nombre': 'Licencia de Paternidad',
        'tipo': 'LICENCIA',
        'descripcion': 'Licencia remunerada de paternidad',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    {
        'codigo': 'DEV026',
        'nombre': 'Licencia Remunerada',
        'tipo': 'LICENCIA',
        'descripcion': 'Otras licencias remuneradas',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    
    # OTROS
    {
        'codigo': 'DEV027',
        'nombre': 'Viáticos',
        'tipo': 'OTRO',
        'descripcion': 'Viáticos permanentes',
        'aplica_seguridad_social': True,
        'aplica_prestaciones': True,
    },
    {
        'codigo': 'DEV028',
        'nombre': 'Viáticos Ocasionales',
        'tipo': 'OTRO',
        'descripcion': 'Viáticos ocasionales no constitutivos de salario',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    {
        'codigo': 'DEV029',
        'nombre': 'Indemnización por Despido',
        'tipo': 'OTRO',
        'descripcion': 'Indemnización por terminación de contrato',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
    {
        'codigo': 'DEV030',
        'nombre': 'Bonificación por Retiro',
        'tipo': 'BONIFICACION',
        'descripcion': 'Bonificación otorgada al momento del retiro',
        'aplica_seguridad_social': False,
        'aplica_prestaciones': False,
    },
]

print(f"\n📥 Creando {len(accruals)} conceptos de DEVENGADOS...")
created_accruals = 0
for data in accruals:
    obj, created = AccrualConcept.objects.get_or_create(
        codigo=data['codigo'],
        organization=org,
        defaults=data
    )
    if created:
        created_accruals += 1
        print(f"  ✓ {data['codigo']} - {data['nombre']}")
    else:
        print(f"  ⊙ {data['codigo']} - {data['nombre']} (ya existe)")

print(f"\n✅ {created_accruals} conceptos de devengados creados")

# ============================================================================
# CONCEPTOS DE DEDUCCIONES
# ============================================================================

deductions = [
    # SEGURIDAD SOCIAL
    {
        'codigo': 'DED001',
        'nombre': 'Aporte a Salud',
        'tipo': 'SALUD',
        'descripcion': 'Aporte del empleado a salud (4%)',
        'porcentaje_base': 4.00,
        'es_obligatoria': True,
    },
    {
        'codigo': 'DED002',
        'nombre': 'Aporte a Pensión',
        'tipo': 'PENSION',
        'descripcion': 'Aporte del empleado a pensión (4%)',
        'porcentaje_base': 4.00,
        'es_obligatoria': True,
    },
    {
        'codigo': 'DED003',
        'nombre': 'Fondo de Solidaridad Pensional',
        'tipo': 'PENSION',
        'descripcion': 'Aporte solidaridad pensional (1% o 2%)',
        'porcentaje_base': 1.00,
        'es_obligatoria': False,
    },
    
    # RETENCIÓN EN LA FUENTE
    {
        'codigo': 'DED004',
        'nombre': 'Retención en la Fuente',
        'tipo': 'RETENCION',
        'descripcion': 'Retención en la fuente por impuestos',
        'porcentaje_base': 0.00,
        'es_obligatoria': False,
    },
    
    # EMBARGOS
    {
        'codigo': 'DED005',
        'nombre': 'Embargo Judicial',
        'tipo': 'EMBARGO',
        'descripcion': 'Embargo ordenado por autoridad judicial',
        'porcentaje_base': 0.00,
        'es_obligatoria': False,
    },
    {
        'codigo': 'DED006',
        'nombre': 'Libranza',
        'tipo': 'LIBRANZA',
        'descripcion': 'Descuento por libranza',
        'porcentaje_base': 0.00,
        'es_obligatoria': False,
    },
    
    # CUOTAS Y PRÉSTAMOS
    {
        'codigo': 'DED007',
        'nombre': 'Préstamo Empresa',
        'tipo': 'PRESTAMO',
        'descripcion': 'Descuento por préstamo de la empresa',
        'porcentaje_base': 0.00,
        'es_obligatoria': False,
    },
    {
        'codigo': 'DED008',
        'nombre': 'Cuota Sindical',
        'tipo': 'CUOTA',
        'descripcion': 'Cuota sindical autorizada',
        'porcentaje_base': 0.00,
        'es_obligatoria': False,
    },
    {
        'codigo': 'DED009',
        'nombre': 'Cuota de Cooperativa',
        'tipo': 'CUOTA',
        'descripcion': 'Aporte a cooperativa',
        'porcentaje_base': 0.00,
        'es_obligatoria': False,
    },
    
    # ANTICIPOS
    {
        'codigo': 'DED010',
        'nombre': 'Anticipo de Nómina',
        'tipo': 'ANTICIPO',
        'descripcion': 'Anticipo de salario',
        'porcentaje_base': 0.00,
        'es_obligatoria': False,
    },
    
    # OTROS
    {
        'codigo': 'DED011',
        'nombre': 'Descuento por Tardanzas',
        'tipo': 'OTRO',
        'descripcion': 'Descuento por llegadas tarde',
        'porcentaje_base': 0.00,
        'es_obligatoria': False,
    },
    {
        'codigo': 'DED012',
        'nombre': 'Descuento por Ausencias',
        'tipo': 'OTRO',
        'descripcion': 'Descuento por días no trabajados',
        'porcentaje_base': 0.00,
        'es_obligatoria': False,
    },
    {
        'codigo': 'DED013',
        'nombre': 'Descuento por Daños',
        'tipo': 'OTRO',
        'descripcion': 'Descuento por daños a equipo o mercancía',
        'porcentaje_base': 0.00,
        'es_obligatoria': False,
    },
    {
        'codigo': 'DED014',
        'nombre': 'Retención de Cesantías',
        'tipo': 'RETENCION',
        'descripcion': 'Retención de cesantías por retiro antes de año',
        'porcentaje_base': 0.00,
        'es_obligatoria': False,
    },
    {
        'codigo': 'DED015',
        'nombre': 'Aporte Voluntario Pensión',
        'tipo': 'PENSION',
        'descripcion': 'Aporte voluntario a fondo de pensiones',
        'porcentaje_base': 0.00,
        'es_obligatoria': False,
    },
    {
        'codigo': 'DED016',
        'nombre': 'Aporte Fondo de Empleados',
        'tipo': 'CUOTA',
        'descripcion': 'Aporte a fondo de empleados',
        'porcentaje_base': 0.00,
        'es_obligatoria': False,
    },
    {
        'codigo': 'DED017',
        'nombre': 'Seguro de Vida',
        'tipo': 'OTRO',
        'descripcion': 'Descuento por póliza de seguro de vida',
        'porcentaje_base': 0.00,
        'es_obligatoria': False,
    },
    {
        'codigo': 'DED018',
        'nombre': 'Plan de Salud Complementario',
        'tipo': 'SALUD',
        'descripcion': 'Descuento por plan complementario de salud',
        'porcentaje_base': 0.00,
        'es_obligatoria': False,
    },
]

print(f"\n📥 Creando {len(deductions)} conceptos de DEDUCCIONES...")
created_deductions = 0
for data in deductions:
    obj, created = DeductionConcept.objects.get_or_create(
        codigo=data['codigo'],
        organization=org,
        defaults=data
    )
    if created:
        created_deductions += 1
        print(f"  ✓ {data['codigo']} - {data['nombre']}")
    else:
        print(f"  ⊙ {data['codigo']} - {data['nombre']} (ya existe)")

print(f"\n✅ {created_deductions} conceptos de deducciones creados")

print("\n" + "=" * 80)
print(f"✅ PROCESO COMPLETADO")
print(f"   Total devengados: {AccrualConcept.objects.filter(organization=org).count()}")
print(f"   Total deducciones: {DeductionConcept.objects.filter(organization=org).count()}")
print("=" * 80)
