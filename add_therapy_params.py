import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models_clinical_config import ClinicalParameter

def add_therapy_parameters():
    """Agregar parámetros de terapias coadyuvantes (complementarias)"""
    
    print("🔧 Agregando Terapias Coadyuvantes...")
    
    # Terapias coadyuvantes (complementarias al tratamiento principal)
    therapies = [
        {
            'name': 'Lubricación Ocular',
            'code': 'LUB-OC',
            'description': 'Uso de lágrimas artificiales y lubricantes',
            'display_order': 1
        },
        {
            'name': 'Compresas Frías',
            'code': 'COMP-FRIA',
            'description': 'Para reducir inflamación y aliviar molestias',
            'display_order': 2
        },
        {
            'name': 'Compresas Calientes',
            'code': 'COMP-CAL',
            'description': 'Para blefaritis y mejora de glándulas de Meibomio',
            'display_order': 3
        },
        {
            'name': 'Higiene Palpebral',
            'code': 'HIG-PALP',
            'description': 'Limpieza regular de párpados y pestañas',
            'display_order': 4
        },
        {
            'name': 'Descanso Visual',
            'code': 'DESC-VIS',
            'description': 'Pausas frecuentes en actividades de visión cercana',
            'display_order': 5
        },
        {
            'name': 'Regla 20-20-20',
            'code': 'REGLA-20',
            'description': 'Cada 20 min, mirar 20 pies por 20 seg',
            'display_order': 6
        },
        {
            'name': 'Ergonomía Visual',
            'code': 'ERGO-VIS',
            'description': 'Ajuste de iluminación y distancia de trabajo',
            'display_order': 7
        },
        {
            'name': 'Protección UV',
            'code': 'PROT-UV',
            'description': 'Uso de lentes con filtro UV',
            'display_order': 8
        },
        {
            'name': 'Dieta y Suplementos',
            'code': 'DIETA',
            'description': 'Omega-3, vitaminas A, C, E para salud ocular',
            'display_order': 9
        },
        {
            'name': 'Masaje Palpebral',
            'code': 'MAS-PALP',
            'description': 'Masaje suave de párpados para drenar glándulas',
            'display_order': 10
        },
    ]
    
    created = 0
    updated = 0
    
    for therapy_data in therapies:
        therapy, created_flag = ClinicalParameter.objects.get_or_create(
            organization=None,
            parameter_type='therapy',
            name=therapy_data['name'],
            defaults={
                'code': therapy_data['code'],
                'description': therapy_data['description'],
                'display_order': therapy_data['display_order'],
                'is_active': True
            }
        )
        
        if created_flag:
            created += 1
            print(f"   ✅ Creada: {therapy_data['name']}")
        else:
            # Actualizar si ya existe
            therapy.code = therapy_data['code']
            therapy.description = therapy_data['description']
            therapy.display_order = therapy_data['display_order']
            therapy.is_active = True
            therapy.save()
            updated += 1
            print(f"   🔄 Actualizada: {therapy_data['name']}")
    
    print(f"\n✅ Proceso completado:")
    print(f"   - {created} terapias creadas")
    print(f"   - {updated} terapias actualizadas")
    print(f"   - Total: {created + updated} terapias coadyuvantes")

if __name__ == '__main__':
    add_therapy_parameters()
