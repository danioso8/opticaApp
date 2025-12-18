import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name, data_type, numeric_precision, numeric_scale 
        FROM information_schema.columns 
        WHERE table_name = 'patients_clinicalhistory' 
        AND column_name LIKE '%add%'
    """)
    
    print("Campos ADD en la tabla patients_clinicalhistory:")
    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]}({row[2]},{row[3]})")
