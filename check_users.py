import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("\n" + "="*60)
print("VERIFICACIÓN DE USUARIOS Y ORGANIZACIONES")
print("="*60)

# Consultar usuarios
cursor.execute("SELECT id, username, email, is_active, is_superuser FROM auth_user")
users = cursor.fetchall()

print(f"\n✅ Usuarios en el sistema: {len(users)}\n")
for user in users:
    print(f"ID: {user[0]}")
    print(f"Username: {user[1]}")
    print(f"Email: {user[2]}")
    print(f"Activo: {user[3]}")
    print(f"Superuser: {user[4]}")
    
    # Verificar si es owner de alguna organización
    cursor.execute("""
        SELECT id, name 
        FROM organizations_organization 
        WHERE owner_id = ?
    """, (user[0],))
    owned = cursor.fetchall()
    if owned:
        print(f"Owner de: {', '.join([o[1] for o in owned])}")
    
    # Verificar membresía
    cursor.execute("""
        SELECT o.name, om.role 
        FROM organizations_organizationmember om
        JOIN organizations_organization o ON om.organization_id = o.id
        WHERE om.user_id = ?
    """, (user[0],))
    memberships = cursor.fetchall()
    if memberships:
        print(f"Miembro de:")
        for m in memberships:
            print(f"  - {m[0]} (Rol: {m[1]})")
    else:
        print("⚠️ NO es miembro de ninguna organización")
    
    print("-" * 60)

conn.close()
