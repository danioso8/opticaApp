"""
Script para copiar los conceptos de nómina DIAN a todas las organizaciones
Ejecutar: python manage.py shell < copy_concepts_to_all_orgs.py
"""

from apps.payroll.models import AccrualConcept, DeductionConcept
from apps.organizations.models import Organization

print("=" * 80)
print("COPIANDO CONCEPTOS DE NÓMINA A TODAS LAS ORGANIZACIONES")
print("=" * 80)

# Obtener la primera organización (que tiene los conceptos originales)
org_fuente = Organization.objects.first()
print(f"\n📋 Organización fuente: {org_fuente.name if org_fuente else 'Ninguna'}")

# Obtener todas las demás organizaciones
todas_orgs = Organization.objects.exclude(id=org_fuente.id) if org_fuente else Organization.objects.all()
print(f"📋 Organizaciones destino: {todas_orgs.count()}")

devengados_creados = 0
deducciones_creadas = 0

for org_destino in todas_orgs:
    print(f"\n🔄 Procesando: {org_destino.name}")
    
    # Copiar conceptos de devengados
    devengados_fuente = AccrualConcept.objects.filter(organization=org_fuente) if org_fuente else []
    for concepto in devengados_fuente:
        # Verificar si ya existe
        existe = AccrualConcept.objects.filter(
            codigo=concepto.codigo,
            organization=org_destino
        ).exists()
        
        if not existe:
            AccrualConcept.objects.create(
                organization=org_destino,
                codigo=concepto.codigo,
                nombre=concepto.nombre,
                tipo=concepto.tipo,
                descripcion=concepto.descripcion,
                activo=concepto.activo,
                aplica_seguridad_social=concepto.aplica_seguridad_social,
                aplica_prestaciones=concepto.aplica_prestaciones,
            )
            devengados_creados += 1
            print(f"  ✓ {concepto.codigo} - {concepto.nombre}")
    
    # Copiar conceptos de deducciones
    deducciones_fuente = DeductionConcept.objects.filter(organization=org_fuente) if org_fuente else []
    for concepto in deducciones_fuente:
        # Verificar si ya existe
        existe = DeductionConcept.objects.filter(
            codigo=concepto.codigo,
            organization=org_destino
        ).exists()
        
        if not existe:
            DeductionConcept.objects.create(
                organization=org_destino,
                codigo=concepto.codigo,
                nombre=concepto.nombre,
                tipo=concepto.tipo,
                descripcion=concepto.descripcion,
                activo=concepto.activo,
                es_obligatoria=concepto.es_obligatoria,
                porcentaje_base=concepto.porcentaje_base,
            )
            deducciones_creadas += 1
            print(f"  ✓ {concepto.codigo} - {concepto.nombre}")

print("\n" + "=" * 80)
print("✅ PROCESO COMPLETADO")
print(f"   Devengados copiados: {devengados_creados}")
print(f"   Deducciones copiadas: {deducciones_creadas}")
print("=" * 80)
