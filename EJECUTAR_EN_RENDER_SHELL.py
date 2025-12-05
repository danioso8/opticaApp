"""
SOLUCIÓN RÁPIDA PARA RENDER - Ejecutar en Shell de Render
"""

# PASOS A SEGUIR:

# 1. Ve a tu dashboard de Render
# 2. Abre el Shell de tu servicio web
# 3. Ejecuta estos comandos en orden:

# Paso 1: Ver qué migraciones están aplicadas
python manage.py showmigrations patients

# Paso 2: Marcar la migración problemática como aplicada (fake)
python manage.py migrate patients 0015_auto_20251205_1231 --fake

# Paso 3: Verificar que se aplicó
python manage.py showmigrations patients

# Paso 4: Intentar aplicar cualquier migración pendiente
python manage.py migrate

# Si aún falla, prueba esto:
# python manage.py migrate patients --fake
# python manage.py migrate

print("""
╔═══════════════════════════════════════════════════════════╗
║  COMANDOS PARA EJECUTAR EN RENDER SHELL                  ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  1. python manage.py showmigrations patients             ║
║                                                           ║
║  2. python manage.py migrate patients 0015 --fake        ║
║                                                           ║
║  3. python manage.py migrate                              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
