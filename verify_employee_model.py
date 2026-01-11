from apps.dashboard.models_employee import Employee

# Verificar campos
print("Campos del modelo Employee:")
for field in Employee._meta.fields:
    if 'nomina' in field.name or 'ciudad' in field.name or 'departamento' in field.name:
        print(f"  - {field.name}: {field.get_internal_type()}")

# Intentar hacer una consulta
try:
    count = Employee.objects.count()
    print(f"\nTotal empleados: {count}")
    print("✅ Modelo Employee funciona correctamente")
except Exception as e:
    print(f"\n❌ Error: {e}")
