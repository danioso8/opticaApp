import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models_clinical_config import ClinicalParameter

def add_follow_up_parameters():
    """Agregar parámetros de motivos de seguimiento"""
    
    print("📅 Agregando Motivos de Seguimiento...")
    
    follow_up_reasons = [
        {
            'name': 'Control de Refracción',
            'code': 'CTRL-REF',
            'description': 'Verificar cambios en graduación',
            'display_order': 1
        },
        {
            'name': 'Adaptación de Lentes',
            'code': 'ADAP-LENT',
            'description': 'Evaluar adaptación a nuevos lentes',
            'display_order': 2
        },
        {
            'name': 'Control de Presión Intraocular',
            'code': 'CTRL-PIO',
            'description': 'Monitoreo de presión ocular',
            'display_order': 3
        },
        {
            'name': 'Seguimiento de Tratamiento',
            'code': 'SEG-TTO',
            'description': 'Evaluar evolución del tratamiento',
            'display_order': 4
        },
        {
            'name': 'Control Post-Cirugía',
            'code': 'POST-CX',
            'description': 'Seguimiento después de cirugía',
            'display_order': 5
        },
        {
            'name': 'Adaptación Lentes de Contacto',
            'code': 'ADAP-LC',
            'description': 'Control de adaptación a LC',
            'display_order': 6
        },
        {
            'name': 'Ojo Seco',
            'code': 'OJO-SECO',
            'description': 'Seguimiento de ojo seco',
            'display_order': 7
        },
        {
            'name': 'Revisión Anual',
            'code': 'REV-ANUAL',
            'description': 'Control periódico preventivo',
            'display_order': 8
        },
        {
            'name': 'Control de Retina',
            'code': 'CTRL-RET',
            'description': 'Monitoreo de condición retiniana',
            'display_order': 9
        },
        {
            'name': 'Evaluación Pediátrica',
            'code': 'EVAL-PED',
            'description': 'Seguimiento en niños',
            'display_order': 10
        },
    ]
    
    created = 0
    updated = 0
    
    for reason_data in follow_up_reasons:
        reason, created_flag = ClinicalParameter.objects.get_or_create(
            organization=None,
            parameter_type='follow_up_reason',
            name=reason_data['name'],
            defaults={
                'code': reason_data['code'],
                'description': reason_data['description'],
                'display_order': reason_data['display_order'],
                'is_active': True
            }
        )
        
        if created_flag:
            created += 1
            print(f"   ✅ Creado: {reason_data['name']}")
        else:
            reason.code = reason_data['code']
            reason.description = reason_data['description']
            reason.display_order = reason_data['display_order']
            reason.is_active = True
            reason.save()
            updated += 1
            print(f"   🔄 Actualizado: {reason_data['name']}")
    
    print(f"\n✅ Proceso completado:")
    print(f"   - {created} motivos creados")
    print(f"   - {updated} motivos actualizados")
    print(f"   - Total: {created + updated} motivos de seguimiento")

if __name__ == '__main__':
    add_follow_up_parameters()
