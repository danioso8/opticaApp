"""
Script para probar el sistema de exámenes especiales
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models import (
    Patient, ClinicalHistory, ExamOrder, Tonometry
)
from apps.patients.models_doctors import Doctor
from django.utils import timezone
from datetime import timedelta

def test_exam_system():
    print("\n" + "="*70)
    print("PRUEBA DEL SISTEMA DE EXÁMENES ESPECIALES")
    print("="*70)
    
    # 1. Verificar que hay pacientes
    print("\n1. Verificando pacientes...")
    patients = Patient.objects.all()[:5]
    print(f"   ✓ {len(patients)} pacientes encontrados")
    for p in patients:
        print(f"     - {p.full_name}")
    
    if not patients:
        print("   ❌ No hay pacientes. Crea un paciente primero.")
        return
    
    # 2. Verificar que hay doctores
    print("\n2. Verificando doctores...")
    doctors = Doctor.objects.filter(is_active=True)[:3]
    print(f"   ✓ {len(doctors)} doctores activos encontrados")
    for d in doctors:
        print(f"     - {d.full_name} ({d.get_specialty_display() if d.specialty else 'Sin especialidad'})")
    
    if not doctors:
        print("   ❌ No hay doctores activos. Crea un doctor primero.")
        return
    
    # 3. Verificar historias clínicas
    print("\n3. Verificando historias clínicas...")
    histories = ClinicalHistory.objects.all()[:5]
    print(f"   ✓ {len(histories)} historias clínicas encontradas")
    for h in histories:
        print(f"     - {h.patient.full_name} - {h.date}")
    
    if not histories:
        print("   ❌ No hay historias clínicas. Crea una historia primero.")
        return
    
    # 4. Crear orden de examen de prueba
    print("\n4. Creando orden de examen de prueba...")
    try:
        test_history = histories[0]
        test_patient = test_history.patient
        test_doctor = doctors[0]
        
        # Verificar si ya existe una orden de prueba
        existing_order = ExamOrder.objects.filter(
            clinical_history=test_history,
            exam_type='tonometry',
            clinical_indication__icontains='Prueba del sistema'
        ).first()
        
        if existing_order:
            print(f"   ℹ Ya existe una orden de prueba: ID {existing_order.id}")
            test_order = existing_order
        else:
            test_order = ExamOrder.objects.create(
                clinical_history=test_history,
                exam_type='tonometry',
                order_date=timezone.now().date(),
                ordered_by=test_doctor,
                priority='routine',
                status='pending',
                clinical_indication='Prueba del sistema - Control de PIO',
                organization=test_history.organization
            )
            print(f"   ✓ Orden creada: ID {test_order.id}")
        
        print(f"     Paciente: {test_patient.full_name}")
        print(f"     Tipo: {test_order.get_exam_type_display()}")
        print(f"     Estado: {test_order.get_status_display()}")
        print(f"     Prioridad: {test_order.get_priority_display()}")
        
    except Exception as e:
        print(f"   ❌ Error al crear orden: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 5. Verificar órdenes existentes
    print("\n5. Verificando órdenes existentes...")
    all_orders = ExamOrder.objects.all()[:10]
    print(f"   ✓ {len(all_orders)} órdenes encontradas")
    
    for order in all_orders:
        status_emoji = {
            'pending': '🟡',
            'scheduled': '🔵',
            'in_progress': '🟠',
            'completed': '🟢',
            'cancelled': '❌'
        }.get(order.status, '⚪')
        
        priority_emoji = {
            'routine': '📋',
            'urgent': '⚠️',
            'STAT': '🚨'
        }.get(order.priority, '📋')
        
        print(f"     {status_emoji} {priority_emoji} ID:{order.id} - {order.get_exam_type_display()}")
        print(f"        Paciente: {order.clinical_history.patient.full_name}")
        print(f"        Fecha: {order.order_date} | Estado: {order.get_status_display()}")
    
    # 6. Verificar resultados de tonometría
    print("\n6. Verificando resultados de tonometría...")
    tonometries = Tonometry.objects.all()[:5]
    print(f"   ✓ {len(tonometries)} tonometrías registradas")
    
    for tono in tonometries:
        od_status = "🔴 ALTA" if tono.od_pressure > 21 else "🟢 Normal"
        os_status = "🔴 ALTA" if tono.os_pressure > 21 else "🟢 Normal"
        
        print(f"     📊 {tono.clinical_history.patient.full_name} - {tono.exam_date}")
        print(f"        OD: {tono.od_pressure} mmHg {od_status}")
        print(f"        OS: {tono.os_pressure} mmHg {os_status}")
        print(f"        Método: {tono.get_method_display()}")
    
    # 7. URLs importantes
    print("\n7. URLs para probar el sistema:")
    print("   📋 Dashboard de pendientes:")
    print("      http://localhost:8000/dashboard/exam-orders/pending/")
    
    print("\n   📝 Crear nueva orden:")
    print(f"      http://localhost:8000/dashboard/patients/{test_patient.id}/history/{test_history.id}/exam-order/create/")
    
    print("\n   📊 Lista de órdenes:")
    print("      http://localhost:8000/dashboard/exam-orders/")
    
    if test_order.status == 'pending':
        print("\n   ➕ Ingresar resultado de tonometría:")
        print(f"      http://localhost:8000/dashboard/patients/{test_patient.id}/history/{test_history.id}/tonometry/create/?order_id={test_order.id}")
    
    print("\n   👤 Ver historia clínica con exámenes:")
    print(f"      http://localhost:8000/dashboard/patients/{test_patient.id}/history/{test_history.id}/")
    
    # 8. Resumen final
    print("\n" + "="*70)
    print("RESUMEN DEL SISTEMA")
    print("="*70)
    print(f"✓ Pacientes: {Patient.objects.count()}")
    print(f"✓ Doctores activos: {Doctor.objects.filter(is_active=True).count()}")
    print(f"✓ Historias clínicas: {ClinicalHistory.objects.count()}")
    print(f"✓ Órdenes de exámenes: {ExamOrder.objects.count()}")
    print(f"  - Pendientes: {ExamOrder.objects.filter(status='pending').count()}")
    print(f"  - En proceso: {ExamOrder.objects.filter(status='in_progress').count()}")
    print(f"  - Completadas: {ExamOrder.objects.filter(status='completed').count()}")
    print(f"✓ Tonometrías: {Tonometry.objects.count()}")
    
    print("\n✅ SISTEMA LISTO PARA USAR")
    print("\nInicia el servidor con: python manage.py runserver")
    print("Luego visita: http://localhost:8000/dashboard/exam-orders/pending/")
    print("="*70 + "\n")

if __name__ == '__main__':
    test_exam_system()
