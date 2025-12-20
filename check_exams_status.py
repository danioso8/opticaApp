from django.db import connection

print("=" * 80)
print("VERIFICACIÓN DE EXÁMENES ESPECIALES EN PRODUCCIÓN")
print("=" * 80)

# Verificar tablas en la base de datos
cursor = connection.cursor()
cursor.execute("""
    SELECT tablename 
    FROM pg_tables 
    WHERE schemaname='public' 
    AND (tablename LIKE 'patients_%exam%' OR tablename LIKE '%tonometry%' OR tablename LIKE '%retinography%')
    ORDER BY tablename
""")
tables = cursor.fetchall()

print("\n📊 TABLAS DE EXÁMENES EN BASE DE DATOS:")
if tables:
    for table in tables:
        print(f"  ✅ {table[0]}")
else:
    print("  ❌ No se encontraron tablas de exámenes especiales")

print(f"\nTotal tablas encontradas: {len(tables)}")

# Verificar modelos importados
print("\n" + "=" * 80)
print("MODELOS DE EXÁMENES EN EL CÓDIGO")
print("=" * 80)

try:
    from apps.patients.models_clinical_exams import (
        ExamOrder, Tonometry, VisualFieldTest, Retinography,
        OCTExam, CornealTopography, Pachymetry, Keratometry,
        ColorVisionTest, MotilityExam
    )
    
    models_list = [
        ('ExamOrder', ExamOrder),
        ('Tonometry', Tonometry),
        ('VisualFieldTest', VisualFieldTest),
        ('Retinography', Retinography),
        ('OCTExam', OCTExam),
        ('CornealTopography', CornealTopography),
        ('Pachymetry', Pachymetry),
        ('Keratometry', Keratometry),
        ('ColorVisionTest', ColorVisionTest),
        ('MotilityExam', MotilityExam),
    ]
    
    print("\n✅ Modelos importados correctamente:")
    for name, model in models_list:
        print(f"  ✅ {name}")
        # Intentar contar registros
        try:
            count = model.objects.count()
            print(f"     Registros: {count}")
        except Exception as e:
            print(f"     ⚠️  Error al contar: {str(e)[:50]}")
            
except ImportError as e:
    print(f"\n❌ Error al importar modelos: {e}")

# Verificar migración
print("\n" + "=" * 80)
print("VERIFICACIÓN DE MIGRACIONES")
print("=" * 80)

cursor.execute("""
    SELECT app, name 
    FROM django_migrations 
    WHERE app = 'patients' 
    AND name LIKE '%exam%' OR name LIKE '%0020%'
    ORDER BY id DESC
    LIMIT 5
""")
migrations = cursor.fetchall()

if migrations:
    print("\n✅ Migraciones encontradas:")
    for app, name in migrations:
        print(f"  - {app}.{name}")
else:
    print("\n⚠️  No se encontraron migraciones de exámenes")

# Verificar última migración de patients
cursor.execute("""
    SELECT name 
    FROM django_migrations 
    WHERE app = 'patients' 
    ORDER BY id DESC 
    LIMIT 1
""")
last_migration = cursor.fetchone()
print(f"\n📋 Última migración de patients: {last_migration[0] if last_migration else 'N/A'}")

print("\n" + "=" * 80)
print("RESUMEN DEL ESTADO")
print("=" * 80)

print("\n📝 FASE 1: Modelos y Migraciones")
if tables and len(tables) >= 10:
    print("  ✅ COMPLETADA - Todas las tablas creadas")
elif tables:
    print(f"  ⚠️  PARCIAL - Solo {len(tables)}/10 tablas encontradas")
else:
    print("  ❌ NO APLICADA - Las migraciones no se han ejecutado en producción")

print("\n📝 FASE 2: Órdenes Médicas (Views, Forms, PDFs)")
print("  ⏳ PENDIENTE")

print("\n📝 FASE 3: Formularios de Ingreso")
print("  ⏳ PENDIENTE")

print("\n📝 FASE 4: PDFs de Resultados")
print("  ⏳ PENDIENTE")

print("\n📝 FASE 5: Integración en UI")
print("  ⏳ PENDIENTE")

print("\n" + "=" * 80)
print("PRÓXIMOS PASOS RECOMENDADOS")
print("=" * 80)

if not tables or len(tables) < 10:
    print("""
⚠️  URGENTE: Las migraciones no están aplicadas en producción

Ejecutar:
1. python manage.py makemigrations
2. python manage.py migrate

Esto creará las tablas necesarias en la base de datos.
""")
else:
    print("""
✅ Base de datos lista

Siguiente paso: Implementar FASE 2 - Órdenes Médicas
- Crear vistas para órdenes
- Crear formularios
- Generar PDFs de órdenes
- Integrar en interfaz de Historia Clínica
""")
