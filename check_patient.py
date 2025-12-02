import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("\n" + "="*60)
print("VERIFICACIÓN DE PACIENTES")
print("="*60)

# Buscar pacientes con identificación 71360801
cursor.execute("""
    SELECT p.id, p.full_name, p.identification, p.phone_number, p.email, 
           p.is_active, o.name
    FROM patients_patient p
    JOIN organizations_organization o ON p.organization_id = o.id
    WHERE p.identification = '71360801'
""")

patients = cursor.fetchall()

if patients:
    print(f"\n✅ Pacientes encontrados con identificación 71360801: {len(patients)}\n")
    for p in patients:
        print(f"ID: {p[0]}")
        print(f"Nombre: {p[1]}")
        print(f"Identificación: {p[2]}")
        print(f"Teléfono: {p[3]}")
        print(f"Email: {p[4]}")
        print(f"Activo: {'Sí' if p[5] else 'No'}")
        print(f"Organización: {p[6]}")
        print("-" * 60)
else:
    print("\n❌ No se encontró ningún paciente con esa identificación")

# Contar todos los pacientes
cursor.execute("SELECT COUNT(*) FROM patients_patient")
total = cursor.fetchone()[0]
print(f"\nTotal de pacientes en el sistema: {total}")

conn.close()
