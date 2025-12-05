"""
Script para popular datos de ejemplo para AR Virtual Try-On
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from apps.dashboard.models_ar_tryon import FrameCategory, Frame, FaceShapeRecommendation
from apps.organizations.models import Organization


def populate_ar_tryon_data():
    org = Organization.objects.first()
    if not org:
        print("❌ No hay organizaciones")
        return
    
    print(f"✅ Usando organización: {org.name}")
    
    # Limpiar datos existentes
    FrameCategory.objects.filter(organization=org).delete()
    Frame.objects.filter(organization=org).delete()
    print("🗑️  Datos anteriores eliminados")
    
    # Crear categorías
    categories_data = [
        {'name': 'Clásicas', 'icon': 'fa-glasses', 'order': 1},
        {'name': 'Deportivas', 'icon': 'fa-running', 'order': 2},
        {'name': 'De Sol', 'icon': 'fa-sun', 'order': 3},
        {'name': 'Lectura', 'icon': 'fa-book-open', 'order': 4},
        {'name': 'Niños', 'icon': 'fa-child', 'order': 5},
        {'name': 'Premium', 'icon': 'fa-gem', 'order': 6},
    ]
    
    categories = {}
    for cat_data in categories_data:
        cat = FrameCategory.objects.create(
            organization=org,
            **cat_data,
            description=f"Monturas {cat_data['name'].lower()} de alta calidad"
        )
        categories[cat_data['name']] = cat
    
    print(f"✅ Creadas {len(categories)} categorías")
    
    # Crear monturas de ejemplo
    frames_data = [
        {
            'code': 'CL-001',
            'name': 'Classic Aviator',
            'category': categories['Clásicas'],
            'brand': 'Ray-Ban',
            'description': 'Estilo aviador clásico con marco metálico',
            'color': 'Dorado',
            'material': 'metal',
            'gender': 'unisex',
            'lens_width': 58,
            'bridge_width': 14,
            'temple_length': 140,
            'price': Decimal('899.99'),
            'stock': 15,
            'is_featured': True,
            'recommended_face_shapes': 'oval,square,heart',
        },
        {
            'code': 'CL-002',
            'name': 'Wayfarer Black',
            'category': categories['Clásicas'],
            'brand': 'Ray-Ban',
            'description': 'Icónico wayfarer en acetato negro',
            'color': 'Negro',
            'material': 'acetate',
            'gender': 'unisex',
            'lens_width': 50,
            'bridge_width': 22,
            'temple_length': 150,
            'price': Decimal('1099.99'),
            'stock': 20,
            'is_featured': True,
            'recommended_face_shapes': 'round,oval',
        },
        {
            'code': 'DP-001',
            'name': 'Sport Pro',
            'category': categories['Deportivas'],
            'brand': 'Oakley',
            'description': 'Monturas deportivas de alto rendimiento',
            'color': 'Negro Mate',
            'material': 'plastic',
            'gender': 'unisex',
            'lens_width': 64,
            'bridge_width': 12,
            'temple_length': 128,
            'price': Decimal('1499.99'),
            'stock': 10,
            'is_featured': True,
            'recommended_face_shapes': 'oval,square',
        },
        {
            'code': 'SOL-001',
            'name': 'Clubmaster Sol',
            'category': categories['De Sol'],
            'brand': 'Ray-Ban',
            'description': 'Clásico clubmaster con protección UV',
            'color': 'Havana',
            'material': 'mixed',
            'gender': 'unisex',
            'lens_width': 51,
            'bridge_width': 21,
            'temple_length': 145,
            'price': Decimal('1199.99'),
            'stock': 18,
            'is_featured': True,
            'recommended_face_shapes': 'round,heart,oval',
        },
        {
            'code': 'LEC-001',
            'name': 'Reader Classic',
            'category': categories['Lectura'],
            'brand': 'Persol',
            'description': 'Monturas para lectura con estilo',
            'color': 'Tortuga',
            'material': 'acetate',
            'gender': 'unisex',
            'lens_width': 48,
            'bridge_width': 20,
            'temple_length': 142,
            'price': Decimal('699.99'),
            'stock': 25,
            'is_featured': False,
            'recommended_face_shapes': 'oval,round,square',
        },
        {
            'code': 'KID-001',
            'name': 'Kids Fun',
            'category': categories['Niños'],
            'brand': 'Nano Vista',
            'description': 'Monturas flexibles y resistentes para niños',
            'color': 'Azul',
            'material': 'plastic',
            'gender': 'kids',
            'lens_width': 42,
            'bridge_width': 16,
            'temple_length': 125,
            'price': Decimal('399.99'),
            'stock': 30,
            'is_featured': False,
            'recommended_face_shapes': 'oval,round',
        },
        {
            'code': 'PREM-001',
            'name': 'Titanium Elite',
            'category': categories['Premium'],
            'brand': 'Lindberg',
            'description': 'Monturas de titanio ultra ligeras',
            'color': 'Plata',
            'material': 'titanium',
            'gender': 'unisex',
            'lens_width': 54,
            'bridge_width': 18,
            'temple_length': 145,
            'price': Decimal('2999.99'),
            'stock': 5,
            'is_featured': True,
            'recommended_face_shapes': 'oval,square,heart',
        },
        {
            'code': 'CL-003',
            'name': 'Round Vintage',
            'category': categories['Clásicas'],
            'brand': 'Oliver Peoples',
            'description': 'Monturas redondas estilo vintage',
            'color': 'Café',
            'material': 'acetate',
            'gender': 'unisex',
            'lens_width': 47,
            'bridge_width': 21,
            'temple_length': 145,
            'price': Decimal('1299.99'),
            'stock': 12,
            'is_featured': True,
            'recommended_face_shapes': 'square,triangle',
        },
        {
            'code': 'FEM-001',
            'name': 'Cat Eye Glamour',
            'category': categories['Clásicas'],
            'brand': 'Prada',
            'description': 'Elegantes monturas cat eye',
            'color': 'Rojo',
            'material': 'acetate',
            'gender': 'female',
            'lens_width': 52,
            'bridge_width': 18,
            'temple_length': 140,
            'price': Decimal('1799.99'),
            'stock': 8,
            'is_featured': True,
            'recommended_face_shapes': 'heart,round,oval',
        },
        {
            'code': 'MASC-001',
            'name': 'Bold Square',
            'category': categories['Clásicas'],
            'brand': 'Tom Ford',
            'description': 'Monturas cuadradas audaces',
            'color': 'Negro Brillante',
            'material': 'acetate',
            'gender': 'male',
            'lens_width': 56,
            'bridge_width': 16,
            'temple_length': 145,
            'price': Decimal('1899.99'),
            'stock': 10,
            'is_featured': True,
            'recommended_face_shapes': 'round,oval',
        },
    ]
    
    for frame_data in frames_data:
        Frame.objects.create(
            organization=org,
            **frame_data
        )
    
    print(f"✅ Creadas {len(frames_data)} monturas")
    
    # Crear recomendaciones por forma de rostro
    recommendations_data = [
        {
            'face_shape': 'oval',
            'recommended_styles': 'Casi cualquier estilo te queda bien. Prueba con monturas geométricas, cat-eye, aviador o wayfarer.',
            'avoid_styles': 'Evita monturas demasiado grandes que oculten las proporciones naturales de tu rostro.',
            'tips': 'Tu rostro tiene proporciones equilibradas. Experimenta con diferentes estilos para encontrar tu favorito.',
            'ideal_frame_width': 'Igual o ligeramente más ancho que la parte más ancha del rostro',
            'ideal_frame_shapes': 'Cuadradas, rectangulares, aviador, cat-eye',
        },
        {
            'face_shape': 'round',
            'recommended_styles': 'Monturas rectangulares, cuadradas o angulares para alargar el rostro visualmente.',
            'avoid_styles': 'Evita monturas redondas que acentúen la forma circular del rostro.',
            'tips': 'Busca monturas con líneas angulares y puentes altos para crear contraste.',
            'ideal_frame_width': 'Ligeramente más anchas que el rostro',
            'ideal_frame_shapes': 'Rectangulares, cuadradas, cat-eye angulado',
        },
        {
            'face_shape': 'square',
            'recommended_styles': 'Monturas redondas u ovaladas para suavizar los ángulos marcados del rostro.',
            'avoid_styles': 'Evita monturas cuadradas o rectangulares que acentúen la mandíbula angular.',
            'tips': 'Las monturas con bordes suaves ayudan a equilibrar las facciones angulares.',
            'ideal_frame_width': 'Igual al ancho del rostro',
            'ideal_frame_shapes': 'Redondas, ovaladas, aviador',
        },
        {
            'face_shape': 'heart',
            'recommended_styles': 'Monturas más anchas en la parte inferior, cat-eye sutil o monturas sin marco inferior.',
            'avoid_styles': 'Evita monturas muy anchas en la parte superior que acentúen la frente amplia.',
            'tips': 'Busca equilibrar la frente ancha con monturas que agreguen ancho en la parte inferior.',
            'ideal_frame_width': 'Ligeramente más estrechas que la frente',
            'ideal_frame_shapes': 'Cat-eye bajo, redondas, aviador',
        },
        {
            'face_shape': 'triangle',
            'recommended_styles': 'Monturas más anchas en la parte superior para equilibrar la mandíbula ancha.',
            'avoid_styles': 'Evita monturas estrechas en la parte superior o muy pesadas en la inferior.',
            'tips': 'Cat-eye pronunciado o monturas con detalles en la parte superior funcionan bien.',
            'ideal_frame_width': 'Más anchas en la parte superior',
            'ideal_frame_shapes': 'Cat-eye, semi-rimless superior',
        },
        {
            'face_shape': 'diamond',
            'recommended_styles': 'Monturas ovaladas, cat-eye o con detalles decorativos para destacar los ojos.',
            'avoid_styles': 'Evita monturas estrechas que no equilibren los pómulos prominentes.',
            'tips': 'Busca monturas que agreguen ancho en la línea de los ojos y el mentón.',
            'ideal_frame_width': 'Similar al ancho de los pómulos',
            'ideal_frame_shapes': 'Ovaladas, cat-eye, rimless',
        },
    ]
    
    for rec_data in recommendations_data:
        FaceShapeRecommendation.objects.create(**rec_data)
    
    print(f"✅ Creadas {len(recommendations_data)} recomendaciones por forma de rostro")
    
    print("\n🎉 ¡Datos de AR Try-On populados exitosamente!")
    print(f"\n🕶️  Accede al AR Try-On en: http://127.0.0.1:8000/dashboard/ar-tryon/")


if __name__ == '__main__':
    populate_ar_tryon_data()
