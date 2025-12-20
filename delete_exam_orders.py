"""
Script para eliminar órdenes de exámenes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models import ExamOrder, Tonometry

def delete_all_exam_orders():
    """Eliminar todas las órdenes de exámenes"""
    
    # Eliminar resultados de tonometría
    tonometry_count = Tonometry.objects.all().count()
    Tonometry.objects.all().delete()
    print(f"✅ Eliminados {tonometry_count} registros de Tonometría")
    
    # Eliminar órdenes de exámenes
    exam_count = ExamOrder.objects.all().count()
    ExamOrder.objects.all().delete()
    print(f"✅ Eliminadas {exam_count} órdenes de exámenes")
    
    print("\n" + "="*50)
    print("LIMPIEZA COMPLETADA")
    print("="*50)
    print("\nAhora puedes crear nuevas órdenes de exámenes desde:")
    print("1. Historia Clínica del paciente → Botón 'Nueva Orden de Examen'")
    print("2. Dashboard → Exámenes Especiales → Nueva Orden")

if __name__ == '__main__':
    print("="*50)
    print("ELIMINAR ÓRDENES DE EXÁMENES")
    print("="*50)
    
    confirm = input("\n¿Estás seguro de eliminar TODAS las órdenes de exámenes? (si/no): ")
    
    if confirm.lower() == 'si':
        delete_all_exam_orders()
    else:
        print("\n❌ Operación cancelada")
