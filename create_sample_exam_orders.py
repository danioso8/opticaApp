"""
Script para crear órdenes de exámenes de prueba
"""
import os
import django
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models import Patient, ClinicalHistory, ExamOrder, Doctor
from django.contrib.auth import get_user_model

User = get_user_model()

def create_sample_exam_orders():
    """Crear órdenes de exámenes de muestra"""
    
    # Obtener un paciente y su historia clínica
    patients = Patient.objects.all()[:5]
    
    if not patients.exists():
        print("❌ No hay pacientes en la base de datos")
        print("   Por favor, crea pacientes primero")
        return
    
    # Obtener doctores
    doctors = Doctor.objects.all()
    if not doctors.exists():
        print("⚠️  No hay doctores registrados. Usando None como médico.")
        doctor = None
    else:
        doctor = doctors.first()
    
    exam_types = [
        ('tonometry', 'Tonometría'),
        ('retinography', 'Retinografía'),
        ('oct', 'Tomografía de Coherencia Óptica (OCT)'),
        ('motility', 'Prueba de Motilidad Ocular'),
        ('visual_field', 'Campo Visual'),
    ]
    
    priorities = ['low', 'normal', 'high', 'urgent']
    statuses = ['pending', 'scheduled', 'in_progress', 'completed']
    
    clinical_notes = [
        'Paciente con presión intraocular elevada. Verificar glaucoma.',
        'Control de rutina. Paciente asintomático.',
        'Seguimiento post-operatorio. Evaluar evolución.',
        'Paciente refiere visión borrosa. Descartar patologías retinianas.',
        'Control diabético. Evaluar retinopatía.',
        'Antecedentes familiares de glaucoma. Evaluación preventiva.',
    ]
    
    created_count = 0
    
    for patient in patients:
        # Obtener historia clínica existente
        histories = ClinicalHistory.objects.filter(patient=patient)
        
        if not histories.exists():
            print(f"⚠️  Paciente {patient.full_name} no tiene historia clínica. Saltando...")
            continue
        
        history = histories.first()
        
        # Crear 2-3 órdenes por paciente
        num_orders = random.randint(2, 3)
        
        for i in range(num_orders):
            exam_type, exam_name = random.choice(exam_types)
            priority = random.choice(priorities)
            status = random.choice(statuses)
            
            # Fecha de orden (últimos 30 días)
            order_date = datetime.now().date() - timedelta(days=random.randint(0, 30))
            
            order = ExamOrder.objects.create(
                clinical_history=history,
                organization=patient.organization,
                exam_type=exam_type,
                priority=priority,
                status=status,
                order_date=order_date,
                ordered_by=doctor,
                clinical_indication=random.choice(clinical_notes),
            )
            
            # Si está programado, agregar fecha programada
            if status == 'scheduled':
                order.scheduled_date = datetime.now() + timedelta(days=random.randint(1, 14))
                order.save()
            
            # Si está completado, agregar fecha de completado
            if status == 'completed':
                order.completed_date = order_date + timedelta(days=random.randint(1, 5))
                order.performed_by = doctor
                order.save()
            
            created_count += 1
            print(f"✅ Creada orden de {exam_name} para {patient.full_name}")
            print(f"   Estado: {order.get_status_display()} | Prioridad: {order.get_priority_display()}")
    
    print("\n" + "="*60)
    print(f"✅ ÓRDENES CREADAS: {created_count}")
    print("="*60)
    print("\nPuedes ver las órdenes en:")
    print("• Dashboard → Exámenes Especiales")
    print("• http://127.0.0.1:8000/dashboard/exam-orders/")

if __name__ == '__main__':
    print("="*60)
    print("CREAR ÓRDENES DE EXÁMENES DE PRUEBA")
    print("="*60)
    print()
    
    create_sample_exam_orders()
