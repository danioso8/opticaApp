import json
from apps.patients.models import ClinicalHistory, Patient
from apps.appointments.models import Appointment
from django.contrib.auth.models import User

print("=" * 80)
print("ANÁLISIS DE DATOS CLÍNICOS EN BACKUP")
print("=" * 80)

with open('backup_final.json', 'r', encoding='latin-1') as f:
    backup_data = json.load(f)

# Contar datos clínicos
clinical_histories = [item for item in backup_data if item['model'] == 'patients.clinicalhistory']
appointments = [item for item in backup_data if item['model'] == 'appointments.appointment']

print(f"\n📋 Contenido del backup:")
print(f"  - Historias clínicas: {len(clinical_histories)}")
print(f"  - Citas: {len(appointments)}")

# Mostrar historias clínicas
if clinical_histories:
    print(f"\n{'='*80}")
    print("HISTORIAS CLÍNICAS EN BACKUP")
    print("=" * 80)
    for item in clinical_histories[:5]:  # Mostrar primeras 5
        fields = item['fields']
        print(f"\n  Historia ID: {item['pk']}")
        print(f"    Paciente ID: {fields.get('patient')}")
        print(f"    Fecha: {fields.get('date', 'N/A')}")
        print(f"    Motivo: {fields.get('reason', 'N/A')[:50]}...")
        
# Mostrar citas
if appointments:
    print(f"\n{'='*80}")
    print("CITAS EN BACKUP (primeras 10)")
    print("=" * 80)
    for item in appointments[:10]:
        fields = item['fields']
        print(f"\n  Cita ID: {item['pk']}")
        print(f"    Paciente ID: {fields.get('patient')}")
        print(f"    Doctor ID: {fields.get('doctor')}")
        print(f"    Fecha/Hora: {fields.get('appointment_date')} {fields.get('appointment_time')}")
        print(f"    Estado: {fields.get('status')}")
        print(f"    Organización: {fields.get('organization')}")

# Verificar estado actual en producción
print(f"\n{'='*80}")
print("ESTADO ACTUAL EN PRODUCCIÓN")
print("=" * 80)

print(f"\n📊 Datos actuales:")
print(f"  - Pacientes: {Patient.objects.count()}")
print(f"  - Historias clínicas: {ClinicalHistory.objects.count()}")
print(f"  - Citas: {Appointment.objects.count()}")

if ClinicalHistory.objects.exists():
    print(f"\n  Últimas historias clínicas:")
    for ch in ClinicalHistory.objects.all()[:5]:
        print(f"    - Paciente: {ch.patient.full_name}, Fecha: {ch.date}")

if Appointment.objects.exists():
    print(f"\n  Últimas citas:")
    for apt in Appointment.objects.all()[:5]:
        print(f"    - Paciente: {apt.patient.full_name}, Doctor: {apt.doctor.full_name}, Fecha: {apt.appointment_date}")

print(f"\n{'='*80}")
print("ANÁLISIS DE CAMPOS")
print("=" * 80)

# Analizar estructura de historias clínicas
if clinical_histories:
    print("\nCampos en Historia Clínica (backup):")
    sample = clinical_histories[0]['fields']
    for key in sorted(sample.keys()):
        value = sample[key]
        value_str = str(value)[:50] if value else "None"
        print(f"  - {key}: {value_str}")

# Analizar estructura de citas
if appointments:
    print("\nCampos en Appointment (backup):")
    sample = appointments[0]['fields']
    for key in sorted(sample.keys()):
        value = sample[key]
        value_str = str(value)[:50] if value else "None"
        print(f"  - {key}: {value_str}")
