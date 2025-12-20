import json
from datetime import datetime
from django.utils import timezone
from apps.patients.models import ClinicalHistory, Patient, Doctor
from apps.appointments.models import Appointment
from apps.organizations.models import Organization
from django.contrib.auth.models import User

print("=" * 80)
print("IMPORTANDO DATOS CLÍNICOS A PRODUCCIÓN")
print("=" * 80)

with open('backup_final.json', 'r', encoding='latin-1') as f:
    backup_data = json.load(f)

# Mapeo de IDs antiguas a nuevas (de los pacientes ya importados)
# Vamos a usar get_or_create con identificación para mapear correctamente

# 1. IMPORTAR HISTORIAS CLÍNICAS
print("\n1. IMPORTANDO HISTORIAS CLÍNICAS...")
print("-" * 80)

clinical_histories = [item for item in backup_data if item['model'] == 'patients.clinicalhistory']
imported_histories = 0
skipped_histories = 0
errors_histories = 0

for item in clinical_histories:
    fields = item['fields']
    old_patient_id = fields.get('patient')
    
    if not old_patient_id:
        skipped_histories += 1
        continue
    
    # Buscar el paciente en la nueva BD (por el ID de la organización y posición)
    # Como importamos 30 pacientes, debemos mapearlos correctamente
    try:
        # Intentar encontrar el paciente por organización
        org_id = fields.get('organization')
        
        # Si no podemos mapear exactamente, saltamos
        if not org_id:
            skipped_histories += 1
            continue
        
        # Obtener todos los pacientes de esa organización
        patients_in_org = Patient.objects.filter(organization_id=org_id)
        
        if old_patient_id <= patients_in_org.count():
            # Usar el paciente en esa posición
            patient = list(patients_in_org.order_by('id'))[old_patient_id - 1]
        else:
            # Buscar por el ID directo (si existe)
            patient = Patient.objects.filter(id=old_patient_id).first()
            if not patient:
                skipped_histories += 1
                continue
        
        # Preparar datos de la historia clínica
        history_data = {
            'patient': patient,
            'organization_id': org_id,
            'date': fields.get('date') or timezone.now().date(),
            
            # Datos básicos
            'chief_complaint': fields.get('chief_complaint', ''),
            'diagnosis': fields.get('diagnosis', ''),
            'treatment_plan': fields.get('treatment_plan', ''),
            
            # Diagnósticos checkbox
            'dx_myopia': fields.get('dx_myopia', False),
            'dx_hyperopia': fields.get('dx_hyperopia', False),
            'dx_astigmatism': fields.get('dx_astigmatism', False),
            'dx_presbyopia': fields.get('dx_presbyopia', False),
            'dx_amblyopia': fields.get('dx_amblyopia', False),
            'dx_strabismus': fields.get('dx_strabismus', False),
            'dx_cataracts': fields.get('dx_cataracts', False),
            'dx_glaucoma': fields.get('dx_glaucoma', False),
            'dx_conjunctivitis': fields.get('dx_conjunctivitis', False),
            'dx_keratoconus': fields.get('dx_keratoconus', False),
            'dx_dry_eye': fields.get('dx_dry_eye', False),
            
            # Refracción OD
            'refraction_od_sphere': fields.get('refraction_od_sphere') or '0.00',
            'refraction_od_cylinder': fields.get('refraction_od_cylinder') or '0.00',
            'refraction_od_axis': fields.get('refraction_od_axis') or 0,
            'refraction_od_add': fields.get('refraction_od_add') or '0.00',
            
            # Refracción OS
            'refraction_os_sphere': fields.get('refraction_os_sphere') or '0.00',
            'refraction_os_cylinder': fields.get('refraction_os_cylinder') or '0.00',
            'refraction_os_axis': fields.get('refraction_os_axis') or 0,
            'refraction_os_add': fields.get('refraction_os_add') or '0.00',
            
            # Distancia pupilar
            'pd_distance': fields.get('pd_distance'),
            'pd_near': fields.get('pd_near'),
            
            # Prescripción
            'prescription_glasses': fields.get('prescription_glasses', False),
            'prescription_contact_lenses': fields.get('prescription_contact_lenses', False),
            'lens_type': fields.get('lens_type', ''),
            'lens_material': fields.get('lens_material', ''),
            'lens_coating': fields.get('lens_coating', ''),
            
            # Presión intraocular
            'iop_od': fields.get('iop_od'),
            'iop_os': fields.get('iop_os'),
            'iop_method': fields.get('iop_method', ''),
            
            # Notas adicionales
            'additional_notes': fields.get('additional_notes', ''),
            'recommendations': fields.get('recommendations', ''),
        }
        
        # Crear la historia clínica
        history = ClinicalHistory.objects.create(**history_data)
        imported_histories += 1
        print(f"  ✅ Historia clínica importada para {patient.full_name} (Fecha: {history.date})")
        
    except Exception as e:
        errors_histories += 1
        print(f"  ❌ Error importando historia {item['pk']}: {str(e)}")

print(f"\nResumen Historias Clínicas:")
print(f"  ✅ Importadas: {imported_histories}")
print(f"  ⏭️  Omitidas: {skipped_histories}")
print(f"  ❌ Errores: {errors_histories}")

# 2. IMPORTAR CITAS
print("\n" + "=" * 80)
print("2. IMPORTANDO CITAS...")
print("-" * 80)

appointments = [item for item in backup_data if item['model'] == 'appointments.appointment']
imported_appointments = 0
skipped_appointments = 0
errors_appointments = 0

for item in appointments:
    fields = item['fields']
    
    try:
        org_id = fields.get('organization')
        if not org_id:
            skipped_appointments += 1
            continue
        
        # Preparar datos de la cita
        appointment_date = fields.get('appointment_date')
        appointment_time = fields.get('appointment_time')
        
        if not appointment_date or not appointment_time:
            skipped_appointments += 1
            continue
        
        # Buscar paciente si existe
        old_patient_id = fields.get('patient')
        patient = None
        if old_patient_id:
            patient = Patient.objects.filter(id=old_patient_id).first()
        
        # Buscar doctor si existe
        old_doctor_id = fields.get('doctor')
        doctor = None
        if old_doctor_id:
            doctor = Doctor.objects.filter(id=old_doctor_id).first()
        
        # Si no hay paciente pero hay nombre y teléfono, crear datos de contacto
        full_name = fields.get('full_name', '')
        phone = fields.get('phone_number', '')
        email = fields.get('email', '')
        
        if not patient and not full_name:
            skipped_appointments += 1
            continue
        
        # Crear la cita
        appointment_data = {
            'organization_id': org_id,
            'patient': patient,
            'doctor': doctor,
            'appointment_date': appointment_date,
            'appointment_time': appointment_time,
            'status': fields.get('status', 'pending'),
            'full_name': full_name,
            'phone_number': phone,
            'email': email,
            'notes': fields.get('notes', ''),
            'has_companion': fields.get('has_companion', False),
            'companion_name': fields.get('companion_name', ''),
            'companion_phone': fields.get('companion_phone', ''),
            'companion_relationship': fields.get('companion_relationship', ''),
        }
        
        appointment = Appointment.objects.create(**appointment_data)
        imported_appointments += 1
        
        patient_name = patient.full_name if patient else full_name
        print(f"  ✅ Cita importada: {patient_name} - {appointment_date} {appointment_time} ({appointment.status})")
        
    except Exception as e:
        errors_appointments += 1
        print(f"  ❌ Error importando cita {item['pk']}: {str(e)}")

print(f"\nResumen Citas:")
print(f"  ✅ Importadas: {imported_appointments}")
print(f"  ⏭️  Omitidas: {skipped_appointments}")
print(f"  ❌ Errores: {errors_appointments}")

# RESUMEN FINAL
print("\n" + "=" * 80)
print("RESUMEN FINAL DE IMPORTACIÓN")
print("=" * 80)

print(f"\n📊 Datos en producción después de importación:")
print(f"  - Pacientes: {Patient.objects.count()}")
print(f"  - Doctores: {Doctor.objects.count()}")
print(f"  - Historias Clínicas: {ClinicalHistory.objects.count()}")
print(f"  - Citas: {Appointment.objects.count()}")

print("\n✅ IMPORTACIÓN DE DATOS CLÍNICOS COMPLETADA")
