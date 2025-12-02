import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("\n" + "="*60)
print("VERIFICACIÓN DE ORGANIZACIONES")
print("="*60)

# Consultar organizaciones
cursor.execute("SELECT id, name, slug, email, is_active FROM organizations_organization")
orgs = cursor.fetchall()

if orgs:
    print(f"\n✅ Organizaciones encontradas: {len(orgs)}\n")
    for org in orgs:
        print(f"ID: {org[0]}")
        print(f"Nombre: {org[1]}")
        print(f"Slug: {org[2]}")
        print(f"Email: {org[3]}")
        print(f"Activa: {org[4]}")
        print("-" * 60)
        
        # Consultar suscripción
        cursor.execute("""
            SELECT sp.name, s.payment_status 
            FROM organizations_subscription s
            JOIN organizations_subscriptionplan sp ON s.plan_id = sp.id
            WHERE s.organization_id = ?
        """, (org[0],))
        sub = cursor.fetchone()
        if sub:
            print(f"Suscripción: {sub[0]} ({sub[1]})")
        else:
            print("⚠️ Sin suscripción")
        print("=" * 60 + "\n")
else:
    print("\n❌ NO HAY ORGANIZACIONES EN LA BASE DE DATOS")
    print("\nPara crear una organización, ejecuta:")
    print("  python manage.py setup_plans")
    print("="*60 + "\n")

# Verificar también planes disponibles
cursor.execute("SELECT id, name FROM organizations_subscriptionplan")
plans = cursor.fetchall()
print(f"\nPlanes de suscripción disponibles: {len(plans)}")
for plan in plans:
    print(f"  - {plan[1]} (ID: {plan[0]})")

conn.close()
